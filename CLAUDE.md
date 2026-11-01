# The Last Day Inn — Project Brief for Claude Code

A small, playable time-loop cozy mystery: an experiment in player-driven investigation and AI-assisted game development. The original design doc lives in `docs/design-doc.md`; it predates the Phase 2 decisions, so its examples may differ. This file is the working brief and the source of truth for build decisions.

## 1. Goal

**Goal:** prove that after the first reset, players naturally want to try again to understand what is happening.

**What this project explores:**
- Systems and narrative design for player-driven investigation
- A data-driven world where the designer owns the truth
- An **agentic playtest workflow**: an AI agent plays the game, reports problems, the designer fixes them, the agent re-tests

## 2. Design pillars (do not break these)

1. **Follow your curiosity.** No quest checklist. The player chooses what to investigate.
2. **Evidence creates questions, not answers.** Clues narrow possibilities while opening new questions.
3. **Actions change the investigation.** Wrong moves shift NPC behaviour or schedules; they never create dead ends.
4. **Discovery is inferred, not stumbled upon.** Hidden events can be missed, but attentive players get hints.
5. **Curious, not frightening.** Cozy tone. Warm, a little strange, a little funny. Never horror.
6. **AI is not the player fantasy.** The player should think "I discovered the rule", never "this AI is clever".

**Core interaction:** `Present <Evidence> → <Character or Location>`. No free-text input in the MVP (cognitive load, localisation, and it turns solving into prompting).

## 3. Locked story truth

**The wish.** The inn closes for good tomorrow. Last night, the innkeeper stood before the lobby's grandfather clock and wished that today would never end. Since then, at every midnight, the clock resets everything to the morning.

**The memory rule.** At the moment of midnight, anyone touching or near the clock keeps a fragment of memory. Objects that are inside or touching the clock at midnight also persist through the reset ("anchored" objects). Anyone carrying an anchored object at midnight also keeps their memory.

**The innkeeper does not know.** He always leaves the lobby for bed before midnight, so he never remembers. The wisher does not know the wish came true, so the loop never ends.

**Mira's secret.** Mira grew up at the inn as a child; the innkeeper cared for her like family. She left, and years later began returning every year as a regular guest. He has never recognised her, and she has never told him. She came this year to reveal who she is and to take over the inn **tomorrow**.

**The irony.** The innkeeper wished for today to last because he believes tomorrow holds nothing. But tomorrow holds Mira coming home to save the inn.

**The handwritten note.** In an earlier loop the player (who does not remember it) hid a note reading *"Leave before midnight."* inside the clock, sealed in an envelope with the player's name on it. The note became anchored. Each morning the innkeeper finds it while winding the clock, does not open it, and because it bears the player's name, slides it under the player's door. The player remembers loops from Loop 1 onward because they carry the anchored note at midnight. In the MVP the note cannot be dropped (prevents soft-lock). After Loop 1 the note stays in the player's inventory.

## 4. World

### Locations (3)

| Location | Contents |
|---|---|
| **Guest Room** | Starting point. Note under the door. Old photo in a drawer. |
| **Lobby** | Grandfather clock (inscription on its base), reception desk with the closing notice, front door (snowed in until tomorrow), pie served here. |
| **Garden** | Back gate (the Loop 1 escape route). Torn blue ribbon caught on a bush. Gate key under a flowerpot. |

### Time

Each loop has four phases: **Morning → Afternoon → Evening → Night**, then the **Midnight** event. Each phase allows two actions (8 per loop). Each action (move, present, examine) costs one action, including fallback reactions. Tunable.

### NPCs

**Innkeeper** — warm, a little tired, proud of his inn. Knows: the inn closes tomorrow; he made a "silly wish" at the clock last night; a little girl once lived here long ago. Does not know: the loop, that Mira is that girl.

| Morning | Afternoon | Evening | Night |
|---|---|---|---|
| Lobby (winds clock) | Lobby | Lobby (serves pie) | Leaves to his room (off-map) |

**Mira** — friendly, playful, knows the inn suspiciously well. Knows: she is the girl from the photo; her plan for tomorrow. Senses déjà vu but cannot explain it.

| Morning | Afternoon | Evening | Night |
|---|---|---|---|
| Lobby | Garden | Lobby | Garden |

**Schedule change (memory trigger):** after the player presents the **Old Photo** to Mira, her Night location changes to **Lobby** (she waits to tell the innkeeper who she is). She is therefore near the clock at midnight.

## 5. Evidence (5) and key reactions

| Evidence | Found in |
|---|---|
| Handwritten note *"Leave before midnight."* | Guest Room (start) |
| Closing notice | Lobby, reception |
| Torn blue ribbon | Garden |
| Old photo (innkeeper and a little girl with a blue ribbon, beside the clock) | Guest Room drawer |
| Clock inscription | Lobby, clock base (examined, not carried) |

Draft reactions (tone and wording are tunable; intent is locked):

| Present | To Innkeeper | To Mira |
|---|---|---|
| Note | Found it in the clock this morning while winding it. **(Points at the clock.)** | Puzzled; mild déjà vu about midnight. |
| Closing notice | Sad; wishes today would never end. **(Hint of the wish.)** | "Tomorrow might surprise you." **(Mystery.)** |
| Blue ribbon | Reminds him of a little girl who stayed here long ago. | Hesitates, changes the subject. |
| Old photo | Nostalgic about the girl; does not connect her to Mira. | **TRIGGER:** goes quiet, decides it is time to tell him. Night schedule → Lobby. |
| Clock inscription | Deflects; admits he "said something silly to that clock last night". | Says she used to hide inside its case as a child. |

**Gate key:** in the Garden, Mira mentions the key is under the flowerpot (another hint that she knows the inn too well).

## 6. Loop flow for the MVP

**Loop 1 (target 2–4 minutes):** wake, find the note → explore and meet NPCs → learn of the back gate and key → escape through the garden. **Midnight:** while walking away, the clock's chime sounds as if right beside the player; the inn is ahead again. Reset.

**Loop 2 opening:** wake in the same bed. NPCs repeat Loop 1 lines exactly.
- If Mira was **not** near the clock at midnight: "You haven't tried the pie."
- If Mira **was** near the clock: "Morning…" *(pause)* "You still haven't tried the pie." **← MVP reveal moment.**

**MVP ends** when the player sees the memory anomaly, or at the end of Loop 3. End screen asks: *"What do you think is happening?"* (captured for playtests).

**Journal:** records confirmed facts only (e.g., "The innkeeper found the note in the clock."). Never records conclusions or hypotheses. Must be toggleable for testing.

## 7. Architecture

**The world file is the single source of truth.** `world.json` holds locations, NPCs (knowledge, schedules, schedule triggers), evidence, reactions (keyed by evidence × target × conditions), and rules (reset, memory, anchoring). The engine contains no story content.

**Engine:** Python, text-based, deterministic, seedable. Pure state machine.

**Interface shared by human players and the agent:**
- `observe()` → current text description of location, time, people present, inventory, journal
- `actions()` → list of valid actions
- `act(action)` → result text and updated state

A CLI wraps this for humans. The agent uses the same interface, so it sees exactly what a player sees.

**Logging:** every session writes a JSON log (actions, reactions, state changes, resets).

## 8. Playtest agent

An LLM agent plays the game through the shared interface, keeps notes, and states hypotheses at each reset.

**Personas (at least two):**
- **Curious explorer** — examines everything, presents evidence widely
- **Escape-focused** — tries to leave as fast as possible
- **Hypothesis tester** (optional) — forms a theory and tests it in the next loop

**Conditions:** run with Journal on and off.

**Report per run:** escaped in Loop 1? Which evidence found and which never used? Was the memory trigger hit? Was the anomaly noticed? Hypotheses at each reset. Dead ends or wasted turns. Total turns.

**Aggregate report:** compares personas and Journal on/off; flags clues no persona found and anything making the mystery too easy or too hard.

**Workflow that must be demonstrated:** run agent → read report → change `world.json` → re-run → compare before and after.

**API keys** live in `.env`, never committed. `.env` goes in `.gitignore`.

## 9. Build plan

**Milestone 1: playable core**
1. `world.json` from this brief
2. Engine + CLI; Loop 1 playable end to end, including reset
3. Loop 2 opening with memory anomaly
4. Agent v1 with one persona producing a report

**Milestone 2: agentic playtest loop**
1. Second persona, Journal on/off, aggregate report
2. One design fix driven by the report, re-run, compare
3. README case study: goal, design pillars, why data-driven, what the agent found, what changed, next steps

**Milestone 3 (later):** polish the memory anomaly and Loop 2–3, run human playtests, then start the AI experiment below.

## 9a. Settled design decisions (2026-11-01)

Resolved gaps in this brief. Full log with reasons: the "Dev Status" doc.

- **Map:** Guest Room ↔ Lobby ↔ Garden; the Lobby is the hub. The Guest Room window shows the garden but cannot be used.
- **Note:** picked up automatically on waking in Loop 1. In Loop 2+ nothing is under the door (the player carries the note), and the innkeeper says he has never seen it. A pile of notes is a Milestone 3 idea.
- **Back gate:** always locked; the gate key opens it. Escaping skips straight to midnight.
- **Near the clock:** being in the Lobby at midnight.
- **Mira:** her photo-triggered Night move resets every loop. Examining the back gate while she is in the Garden makes her mention the key. She senses the loop but barely recalls it; in Loop 2+, after being near the clock, she may mention a vague myth about the clock.
- **Pie:** served in the Lobby in the Evening; the player can try it. "You haven't tried the pie." is also Mira's Loop 1 line on first meeting. If the player tried the pie and Mira was near the clock, her Loop 2 line changes and hints at her past.
- **Reactions:** no location reactions in the MVP beyond one default line; one fallback line per NPC for uncovered combinations.
- **Journal:** every evidence found and every listed reaction adds one brief factual line; it carries across loops, tagged by loop.
- **Player:** an unnamed guest ("you") on a last stay before the inn closes. The player does not know who the girl in the photo is.
- **Midnight:** the chime is loud in the Lobby, faint elsewhere. Past-you's motive for the note stays unexplained.
- **Text:** Claude writes first drafts of all lines (marked as drafts in `world.json`); the designer reviews.

## 10. Out of scope for the MVP

Unity or any graphics. Art. Free-text input. Player-facing AI. More than 3 loops. A full ending. Public web demo.

## 11. Next phase: AI experiment

**Hypothesis:** the combinations of Evidence × Character × World State × Player History outgrow what hand-authored branching can cover. AI can generate a sensible reaction for each combination within designer-defined constraints, without ever changing the ground truth in `world.json`.

**Measure:** compare the rule-based and AI versions on how often players judge NPC reactions as sensible and useful, and how many hypotheses players actively test. The playtest agent also checks AI output against `world.json` for leaked or invented facts.
