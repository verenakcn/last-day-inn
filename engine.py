"""The Last Day Inn engine: a deterministic state machine driven by world.json.

The engine holds no story text. Every line the player reads comes from the world file.
Shared interface for human players and the playtest agent:
    observe() -> str        what the player currently sees
    actions() -> list[str]  valid action ids, e.g. "move:lobby", "examine:drawer", "present:note>mira"
    act(id)   -> str        result text; state updates in place
"""

import json
import os
import random
import time

PER_PHASE_KEY = "actions_per_phase"


class Game:
    def __init__(self, world_path="world.json", seed=0, journal=True, log_dir=None):
        with open(world_path, encoding="utf-8") as f:
            self.w = json.load(f)
        self.seed = seed
        self.rng = random.Random(seed)  # unused so far; kept so runs stay seedable
        self.journal_on = journal
        self.ui = self.w["ui"]
        self.loop = 1
        self.inventory = []
        self.journal = []
        self.ended = None  # None, "anomaly_seen" or "loop_limit"
        self.end_answer = None
        self.mira_near_clock_last = False
        self.last_loop_flags = set()
        self.introduced = set()  # NPCs the player has met; their one-line intro shows once per game
        self.log = {"seed": seed, "journal": journal, "world_version": self.w["meta"]["schema_version"], "events": []}
        self.log_path = None
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            self.log_path = os.path.join(log_dir, time.strftime("session-%Y%m%d-%H%M%S.json"))
        self.opening = self.ui["morning_banner"] + "\n\n" + self._start_loop()

    # ---------- shared interface ----------

    def observe(self):
        if self.ended:
            return self.w["loops"]["end_screen"]["prompt"]
        loc = self.w["locations"][self.location]
        # No loop counter on screen: the player has to discover that the day repeats.
        # The room description shows on arrival, not every turn.
        lines = [self.ui["status"].format(place=loc["name"], phase=self._phase_name(),
                                          action=self.actions_done + 1, per_phase=self._per_phase())]
        people = [self._presence(n) for n in self._npcs_here()]
        lines.append(" ".join([self.ui["here"]] + people) if people else self.ui["nobody_here"])
        here = [f["name"] for f in loc["features"].values()
                if self._phase_id() in f.get("available_phases", [self._phase_id()])]
        lines.append(self.ui["examine_list"].format(list=", ".join(here)))
        lines.append(self.ui["exits"].format(list=", ".join(self.w["locations"][c]["name"] for c in loc["connections"])))
        if self.inventory:
            lines.append(self.ui["inventory"].format(list=", ".join(self._name(i) for i in self.inventory)))
        else:
            lines.append(self.ui["inventory_empty"])
        if self.journal_on:
            before = [j for j in self.journal if j["loop"] < self.loop]
            today = [j for j in self.journal if j["loop"] == self.loop]
            if not self.journal:
                lines.append(self.ui["journal_empty"])
            elif not before:  # first day: a plain list, nothing that hints at repetition
                lines.append(self.ui["journal_header"])
                lines += ["  " + self.ui["journal_entry"].format(**j) for j in today]
            else:  # after waking again: what you remember vs. what you learned today
                lines += [self.ui["journal_header"], "  " + self.ui["journal_before"]]
                lines += ["    " + self.ui["journal_entry"].format(**j) for j in before]
                lines.append("  " + self.ui["journal_today"])
                lines += ["    " + self.ui["journal_entry"].format(**j) for j in today] or \
                         ["    " + self.ui["journal_today_empty"]]
        return "\n".join(lines)

    def actions(self):
        if self.ended:
            return []
        loc = self.w["locations"][self.location]
        acts = ["move:" + c for c in loc["connections"]]
        # A feature that only exists at some times of day (the pie) is only offered then.
        acts += ["examine:" + f for f, feat in loc["features"].items()
                 if self._phase_id() in feat.get("available_phases", [self._phase_id()])]
        targets = self._npcs_here()  # MVP: no "show to a place" options (decision E1)
        for item in self.inventory:
            if self._presentable(item):
                acts += ["present:%s>%s" % (item, t) for t in targets]
        return acts

    def describe_action(self, action):
        """Menu label; actions already taken this loop get a mark (cleared at each reset)."""
        mark = self.ui["done_mark"] if action in self.done else ""
        verb, _, rest = action.partition(":")
        if verb == "move":
            return mark + self.ui["action_move"].format(place=self.w["locations"][rest]["name"])
        if verb == "examine":
            return mark + self.ui["action_examine"].format(thing=self._feature(rest)["name"])
        item, _, target = rest.partition(">")
        return mark + self.ui["action_present"].format(item=self._name(item), target=self._target_name(target))

    def act(self, action):
        if action not in self.actions():
            raise ValueError("Not a valid action now: %s" % action)
        before = self._snapshot()
        verb, _, rest = action.partition(":")
        self.done.add(action)
        if verb == "move":
            self.location = rest
            out = [self.ui["move"].format(place=self.w["locations"][rest]["name"]), self._room_text()]
        elif verb == "examine":
            out = self._examine(rest)
        else:
            item, _, target = rest.partition(">")
            out = self._present(item, target)

        if self.escaped:
            out += self._midnight()
        else:
            out += self._spend_action()
        out += self._introductions()
        out += self._check_meeting()
        text = "\n\n".join(t for t in out if t)
        self._log({"type": "action", "action": action, "text": text, "before": before, "after": self._snapshot()})
        return text

    def answer_end_prompt(self, answer):
        self.end_answer = answer
        self._log({"type": "end_answer", "answer": answer})

    # ---------- loop and time ----------

    def _start_loop(self):
        self.location = self.w["player"]["start_location"]
        self.phase = 0
        self.actions_done = 0
        self.flags = set()
        self.taken = set()
        self.done = set()  # actions taken this loop, for the menu mark
        self.mira_trigger = False
        self.mira_met = False
        self.escaped = False
        # Only anchored objects survive a reset.
        self.inventory = [i for i in self.inventory if self.w["evidence"].get(i, {}).get("anchored")]
        note = self.w["evidence"]["note"]
        if note.get("auto_pickup_on_wake") and "note" not in self.inventory:
            self.inventory.append("note")
            self._add_fact(note["journal_fact"])
        wake = self._first_match(self.w["loops"]["wake"])
        self._log({"type": "loop_start", "loop": self.loop})
        return wake["text"] + "\n\n" + self._room_text()

    def _room_text(self):
        return self.ui["room_on_enter"].format(text=self.w["locations"][self.location]["description"]["text"])

    def _introductions(self):
        """One line per NPC the first time the player is in the same place as them."""
        if self.ended:
            return []
        new = [n for n in self._npcs_here() if n not in self.introduced]
        self.introduced.update(new)
        return [self.w["npcs"][n]["intro"]["text"] for n in new]

    def _per_phase(self):
        return self.w["time"][PER_PHASE_KEY]

    def _phase_id(self):
        return self.w["time"]["phases"][self.phase]

    def _phase_name(self):
        return self.w["time"]["phase_names"][self._phase_id()]

    def _spend_action(self):
        self.actions_done += 1
        if self.actions_done < self._per_phase():
            return []
        self.actions_done = 0
        self.phase += 1
        if self.phase < len(self.w["time"]["phases"]):
            return []
        return self._midnight()

    def _midnight(self):
        scenes = self.w["loops"]["midnight_scenes"]
        if self.escaped:
            scene = scenes["escaped"]
        elif self.location == "lobby":
            scene = scenes["in_lobby"]
        else:
            scene = scenes["elsewhere"]
        self.mira_near_clock_last = self._npc_location("mira", "night") == "lobby"
        self.last_loop_flags = set(self.flags)
        self._log({"type": "reset", "loop": self.loop, "escaped": self.escaped,
                   "mira_near_clock": self.mira_near_clock_last})
        out = [self.ui["midnight_banner"], scene["text"]]
        if self.loop >= self.w["time"]["max_loops"]:
            self.ended = "loop_limit"
            out.append(self.w["loops"]["end_screen"]["prompt"])
            return out
        self.loop += 1
        out += [self.ui["morning_banner"], self._start_loop()]
        return out

    # ---------- NPCs ----------

    def _npc_location(self, npc, phase_id=None):
        slot = self._schedule_slot(npc, phase_id or self._phase_id())
        return slot["location"]

    def _schedule_slot(self, npc, phase_id):
        data = self.w["npcs"][npc]
        if npc == "mira" and self.mira_trigger:
            override = data["schedule_triggers"][0]["effect"]["schedule"]
            if phase_id in override:
                return override[phase_id]
        return data["schedule"][phase_id]

    def _npcs_here(self):
        if self.phase >= len(self.w["time"]["phases"]):
            return []
        return [n for n in self.w["npcs"] if self._npc_location(n) == self.location]

    def _presence(self, npc):
        slot = self._schedule_slot(npc, self._phase_id())
        return slot.get("presence", {}).get("text", self.w["npcs"][npc]["name"])

    def _check_meeting(self):
        """Mira's first line in each loop, the first time the player is in the same place as her."""
        if self.ended or self.mira_met or "mira" not in self._npcs_here():
            return []
        self.mira_met = True
        mira = self.w["npcs"]["mira"]
        if self.loop == 1:
            entry = mira["first_meeting_line"]["default"]
        else:
            entry = self._first_match(self.w["loops"]["loop_2_opening"]["mira_first_meeting_line"])
        out = []
        narration = entry.get("narration") or mira["first_meeting_line"]["default"].get("narration")
        if narration and self._matches(narration.get("conditions")):
            out.append(narration["text"])
        out += [self.ui["pause"] if l == "(pause)" else '"%s"' % l for l in entry["lines"]]
        if entry.get("journal_fact"):
            self._add_fact(entry["journal_fact"])
        if entry.get("is_anomaly"):
            self.ended = "anomaly_seen"
            self._log({"type": "anomaly_seen", "loop": self.loop})
            out.append(self.w["loops"]["end_screen"]["prompt"])
        return ["\n".join(out)]

    # ---------- examine and present ----------

    def _examine(self, fid):
        feature = self._feature(fid)
        phases = feature.get("available_phases")
        if phases and self._phase_id() not in phases:
            return [feature["unavailable_text"]["text"]]
        entry = self._first_match(feature["examine"])
        out = [entry["text"]]
        self.flags.update(entry.get("set_flags", []))
        if entry.get("journal_fact"):
            self._add_fact(entry["journal_fact"])
        if entry.get("effect") == "escape":
            self.escaped = True
        gives = feature.get("gives")
        if gives and gives not in self.inventory and gives not in self.taken:
            self.taken.add(gives)
            self.inventory.append(gives)
            thing = self._thing(gives)
            # Show what a picked-up item says or depicts, so the clue doesn't depend on the journal.
            if isinstance(thing.get("text"), dict):
                out.append(self.ui["read_text"].format(text=thing["text"]["text"]))
            elif isinstance(thing.get("description"), dict):
                d = thing["description"]["text"]
                out.append(self.ui["shows_text"].format(text=d[0].lower() + d[1:]))
            fact = thing.get("journal_fact")
            if fact:
                self._add_fact(fact.replace("{inscription}", thing.get("text", {}).get("text", "")))
        for amb in self.w["npcs"]["mira"]["ambient"]:
            on = amb.get("on", {})
            if on.get("examine") == fid and self._matches(on.get("conditions", {})):
                out.append(amb["text"])
                self._add_fact(amb.get("journal_fact"))
        return out

    def _present(self, item, target):
        if target in self.w["npcs"]:
            for r in self.w["reactions"]:
                if r["evidence"] == item and r["target"] == target and self._matches(r["conditions"]):
                    text = r["text"]
                    if r.get("locked_text"):
                        text = '"%s"' % text
                    if r.get("narration"):
                        text = r["narration"]["text"] + " " + text
                    self._add_fact(r.get("journal_fact"))
                    for e in r.get("effects", []):
                        if e["type"] == "fire_schedule_trigger" and e["npc"] == "mira":
                            self.mira_trigger = True
                    return [text]
            return [self.w["npcs"][target]["fallback"]["text"]]
        line = self.w["reaction_fallbacks"]["present_to_location"]["text"]
        return [line.format(item=self._name(item), place=self._feature(target)["name"])]

    # ---------- helpers ----------

    def _matches(self, cond):
        for key, val in (cond or {}).items():
            ok = {
                "loop": lambda v: self.loop == v,
                "location": lambda v: self.location == v,
                "loop_min": lambda v: self.loop >= v,
                "has": lambda v: v in self.inventory,
                "has_not": lambda v: v not in self.inventory,
                "flag": lambda v: v in self.flags,
                "flag_not": lambda v: v not in self.flags,
                "flag_last_loop": lambda v: v in self.last_loop_flags,
                "flag_last_loop_not": lambda v: v not in self.last_loop_flags,
                "npc_present": lambda v: v in self._npcs_here(),
                "mira_near_clock_last_midnight": lambda v: self.mira_near_clock_last == v,
            }[key](val)
            if not ok:
                return False
        return True

    def _first_match(self, entries):
        for e in entries:
            if self._matches(e.get("conditions")):
                return e
        raise ValueError("No matching entry in world.json: %r" % entries)

    def _feature(self, fid):
        return self.w["locations"][self.location]["features"][fid]

    def _thing(self, tid):
        return self.w["evidence"].get(tid) or self.w["items"][tid]

    def _name(self, tid):
        return self._thing(tid)["name"]

    def _presentable(self, tid):
        return tid in self.w["evidence"] or self.w["items"][tid].get("presentable")

    def _target_name(self, target):
        if target in self.w["npcs"]:
            return self.w["npcs"][target]["name"]
        return self._feature(target)["name"]

    def _add_fact(self, fact):
        if fact and fact not in [j["fact"] for j in self.journal]:
            self.journal.append({"loop": self.loop, "fact": fact})

    def _snapshot(self):
        return {"loop": self.loop, "phase": self.phase, "actions_done": self.actions_done,
                "location": self.location, "inventory": list(self.inventory),
                "flags": sorted(self.flags), "mira_trigger": self.mira_trigger, "ended": self.ended}

    def _log(self, event):
        self.log["events"].append(event)
        if self.log_path:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(self.log, f, indent=2, ensure_ascii=False)
