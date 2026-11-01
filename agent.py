"""Playtest agent v1: an LLM plays through the same observe/actions/act interface as a human.

    pip install anthropic
    echo "ANTHROPIC_API_KEY=..." > .env
    python3 agent.py                      # one run: curious explorer, journal on
    python3 agent.py --persona escape --no-journal
    python3 agent.py --dry-run            # fake model, no API calls: tests the pipeline for free
    python3 agent.py --all                # opt-in: both personas x journal on/off + aggregate report
    python3 agent.py --interview reports/<run>.json questions.txt   # ask that run's player questions

Gemini instead of Claude: pip install google-genai, put GEMINI_API_KEY=... in .env,
then add --provider gemini to any command above.

Limits: one run per command unless --all; each run stops after MAX_ACTIONS actions.
Every report records how many API calls the run made.

The report's facts (escaped, evidence found/used, trigger, anomaly, turns) are computed from the
game log, not from the model. The model only plays and states hypotheses.
"""

import datetime
import json
import os
import random
import re
import sys
import time

from engine import Game

MODEL = "claude-opus-5-5"
MAX_ACTIONS = 40

PERSONAS = {
    "curious": "You are a curious explorer. You examine everything, show evidence to everyone, "
               "and follow whatever seems strange.",
    "escape": "You want to leave this place as fast as possible. You do the minimum needed to get out "
              "and don't linger on side details.",
}

RULES = """You are playtesting a short text mystery game. Play it as a real player would.
Each turn you see what your character sees and a numbered list of actions. You don't know anything
beyond what the game has shown you.

Reply in exactly this format:
NOTE: <one short sentence: what you noticed or why you chose this>
CHOICE: <the number of one action>"""


def load_env(path=".env"):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.startswith("#"):
                key, _, val = line.strip().partition("=")
                os.environ.setdefault(key, val)


def claude_model():
    """Returns ask(system, messages) -> text, using the Anthropic SDK."""
    import anthropic
    client = anthropic.Anthropic()

    def ask(system, messages):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=system,
            messages=messages,
            # Server-side fallback if a request is declined (see README note).
            extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"},
            extra_body={"fallbacks": "default"},
        )
        if response.stop_reason == "refusal":
            raise RuntimeError("Model declined the request")
        return "".join(b.text for b in response.content if b.type == "text")

    return ask


def to_gemini(messages):
    """Our user/assistant message list in Gemini's user/model format."""
    return [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in messages]


def gemini_model():
    """Returns ask(system, messages) -> text, using Google's google-genai SDK.
    Needs GEMINI_API_KEY in .env; GEMINI_MODEL overrides the model name."""
    from google import genai
    from google.genai import types
    # 60 s per request, 2 tries: a stuck request fails loudly instead of hanging.
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(
        timeout=60000, retry_options=types.HttpRetryOptions(attempts=2)))
    # gemini-3.8-flash is listed but never answered with our free-tier key (2026-11-01).
    model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    # Free tier allows 5 requests per minute: space calls out, and wait out a 429 or 503 if one happens.
    gap = float(os.environ.get("GEMINI_SECONDS_BETWEEN_CALLS", "13"))
    last = [0.0]

    def ask(system, messages):
        for attempt in range(5):
            time.sleep(max(0.0, last[0] + gap - time.time()))
            last[0] = time.time()
            try:
                response = client.models.generate_content(
                    model=model, contents=to_gemini(messages),
                    config=types.GenerateContentConfig(system_instruction=system))
                return "".join(p.text for p in response.candidates[0].content.parts if p.text)
            except (genai.errors.ClientError, genai.errors.ServerError) as e:
                # 429 = over the free-tier rate, 503/504 = Google overloaded or timed out: all temporary.
                # A per-day quota is not: waiting a minute won't help, so stop at once.
                if e.code not in (429, 503, 504) or attempt == 4 or "per day" in str(e):
                    raise
                time.sleep(60)

    return ask


def fake_model(seed=0):
    """Returns ask(system, messages) -> text with no API calls: picks a random listed action (seeded)."""
    rng = random.Random(seed)

    def ask(system, messages):
        text = messages[-1]["content"]
        if "HYPOTHESIS" in text:
            return "HYPOTHESIS: (dry run) The day seems to repeat."
        if "The game is over" in text:
            return "(dry run) No real answer: this run used a fake model."
        count = len(re.findall(r"^\d+\. ", text, re.M))
        return "NOTE: (dry run) random pick\nCHOICE: %d" % rng.randint(1, max(count, 1))

    ask.fake = True  # not counted as an API call
    return ask


def play(game, ask, persona="curious", max_actions=MAX_ACTIONS):
    """Plays one session, at most max_actions actions. Returns the run record used for the report."""
    system = RULES + "\n\n" + PERSONAS[persona]
    messages = []
    run = {"persona": persona, "journal": game.journal_on, "turns": [], "hypotheses": [], "final_answer": None,
           "api_calls": 0, "capped": False, "error": None,
           "transcript": messages}  # exact conversation, so --interview can replay it word for word
    try:
        _play(game, ask, system, messages, run, max_actions)
    except Exception as e:  # keep what was played: the report is saved, marked incomplete
        run["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    run["ended"] = game.ended
    return run


def _play(game, ask, system, messages, run, max_actions):

    def say(text):
        messages.append({"role": "user", "content": text})
        if not getattr(ask, "fake", False):
            run["api_calls"] += 1
        reply = ask(system, messages)
        messages.append({"role": "assistant", "content": reply})
        return reply

    screen = game.opening
    while not game.ended:
        if len(run["turns"]) >= max_actions:
            run["capped"] = True
            break
        acts = game.actions()
        menu = "\n".join("%d. %s" % (i, game.describe_action(a)) for i, a in enumerate(acts, 1))
        reply = say("%s\n\n%s\n\nActions:\n%s" % (screen, game.observe(), menu))
        match = re.search(r"CHOICE:\s*(\d+)", reply)
        n = int(match.group(1)) if match else 0
        if not 1 <= n <= len(acts):
            n = 1  # unparseable reply: take the first action and record it
        note = re.search(r"NOTE:\s*(.*)", reply)
        loop_before = game.loop
        screen = game.act(acts[n - 1])
        run["turns"].append({"loop": loop_before, "action": acts[n - 1], "note": note.group(1) if note else reply,
                             "result": screen, "parsed": bool(match)})
        if game.loop != loop_before and not game.ended:
            h = say(screen + "\n\nA new loop seems to have started. Before you continue, write your current "
                    "theory of what is happening, in one or two sentences. Start with HYPOTHESIS:")
            run["hypotheses"].append({"after_loop": loop_before, "text": h.replace("HYPOTHESIS:", "").strip()})
            screen = ""
    if run["capped"]:
        screen += "\n\n(The playtest stopped after %d actions.)" % max_actions
    run["final_answer"] = say(screen + "\n\nThe game is over. It asks you: " +
                              game.w["loops"]["end_screen"]["prompt"] + " Answer in two or three sentences.")
    game.answer_end_prompt(run["final_answer"])


def facts(game, run):
    """Report facts computed from the game log and world file only."""
    events = game.log["events"]
    actions = [e for e in events if e["type"] == "action"]
    evidence = set(game.w["evidence"])
    found = {i for e in actions for i in e["after"]["inventory"] if i in evidence}
    found |= {i for i in game.inventory if i in evidence}  # the note is held from the start
    used = {e["action"].split(":")[1].split(">")[0] for e in actions if e["action"].startswith("present:")}
    resets = [e for e in events if e["type"] == "reset"]
    fallbacks = {n["fallback"]["text"] for n in game.w["npcs"].values()}
    wasted, seen = [], set()
    for t in run["turns"]:
        key = (t["loop"], t["action"])
        if t["result"].split("\n\n")[0] in fallbacks:
            wasted.append("%s (no reaction written)" % t["action"])
        elif key in seen and t["action"].startswith("examine:"):
            wasted.append("%s (repeat in loop %d)" % (t["action"], t["loop"]))
        seen.add(key)
    return {
        "escaped_loop_1": any(r["loop"] == 1 and r["escaped"] for r in resets),
        "evidence_found": sorted(found),
        "evidence_never_found": sorted(evidence - found),
        "evidence_found_but_never_shown": sorted(found - used),
        "memory_trigger_hit": any(e["after"]["mira_trigger"] for e in actions),
        "anomaly_shown": game.ended == "anomaly_seen",
        "loops_played": game.loop,
        "total_turns": len(actions),
        "wasted_turns": wasted,
        "unparsed_replies": sum(1 for t in run["turns"] if not t["parsed"]),
        "api_calls": run["api_calls"],
        "capped_at_max_actions": run["capped"],
        "stopped_by_error": run.get("error"),
    }


def report_md(run, f):
    yes = lambda b: "yes" if b else "no"
    lines = [
        "# Playtest report: %s, journal %s" % (run["persona"], "on" if run["journal"] else "off"),
        "",
        "Model: %s" % run.get("model", "unknown"),
        "",
    ] + (["**INCOMPLETE: the run stopped early.** %s" % f["stopped_by_error"], ""] if f["stopped_by_error"] else []) + [
        "| Question | Result |",
        "| --- | --- |",
        "| Escaped in Loop 1? | %s |" % yes(f["escaped_loop_1"]),
        "| Evidence found | %s |" % (", ".join(f["evidence_found"]) or "none"),
        "| Evidence never found | %s |" % (", ".join(f["evidence_never_found"]) or "none"),
        "| Found but never shown to anyone | %s |" % (", ".join(f["evidence_found_but_never_shown"]) or "none"),
        "| Memory trigger hit (photo shown to Mira)? | %s |" % yes(f["memory_trigger_hit"]),
        "| Anomaly shown (Mira's \"still\" line)? | %s |" % yes(f["anomaly_shown"]),
        "| Loops played | %d |" % f["loops_played"],
        "| Total turns | %d |" % f["total_turns"],
        "| Wasted turns | %s |" % (len(f["wasted_turns"])),
        "| Stopped at the %d-action cap? | %s |" % (MAX_ACTIONS, yes(f["capped_at_max_actions"])),
        "| API calls | %d |" % f["api_calls"],
        "",
        "## Did the player notice the anomaly?",
        "",
        "Judge from the answers below (the report doesn't decide this for you).",
        "",
        "## Hypotheses at each reset",
        "",
    ]
    lines += ["- After loop %d: %s" % (h["after_loop"], h["text"]) for h in run["hypotheses"]] or ["- (no reset reached)"]
    lines += ["", "## Final answer to \"What do you think is happening?\"", "", run["final_answer"] or "", ""]
    if f["wasted_turns"]:
        lines += ["## Wasted turns", ""] + ["- " + w for w in f["wasted_turns"]] + [""]
    lines += ["## Turn by turn", "", "| Loop | Action | Player's note |", "| --- | --- | --- |"]
    lines += ["| %d | %s | %s |" % (t["loop"], t["action"], t["note"].replace("|", "/")) for t in run["turns"]]
    return "\n".join(lines) + "\n"


def new_base(out_dir, name):
    """reports/<name>, with -2, -3... added if that name is taken: old reports are never overwritten."""
    os.makedirs(out_dir, exist_ok=True)
    base, n = os.path.join(out_dir, name), 2
    while any(os.path.exists(base + ext) for ext in (".md", ".json")):
        base, n = os.path.join(out_dir, "%s-%d" % (name, n)), n + 1
    return base


def save_report(run, f, out_dir="reports"):
    """Saves <date-time>-<persona>-journal-<on|off>[-dry-run].md and .json. Returns the .md path."""
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = "%s-%s-journal-%s%s%s" % (stamp, run["persona"], "on" if run["journal"] else "off",
                                     "-dry-run" if run.get("model") == "dry-run" else "",
                                     "-INCOMPLETE" if run.get("error") else "")
    base = new_base(out_dir, name)
    with open(base + ".md", "x", encoding="utf-8") as fh:  # "x": fail rather than overwrite
        fh.write(report_md(run, f))
    with open(base + ".json", "x", encoding="utf-8") as fh:
        json.dump({"facts": f, "run": run}, fh, indent=2, ensure_ascii=False)
    return base + ".md"


def aggregate_md(results):
    """One table comparing runs: (run, facts) pairs."""
    yes = lambda b: "yes" if b else "no"
    lines = ["# Aggregate playtest report", "",
             "| Persona | Journal | Escaped L1 | Trigger hit | Anomaly shown | Turns | Wasted | Never found |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for run, f in results:
        lines.append("| %s | %s | %s | %s | %s | %d | %d | %s |" % (
            run["persona"], "on" if run["journal"] else "off", yes(f["escaped_loop_1"]),
            yes(f["memory_trigger_hit"]), yes(f["anomaly_shown"]), f["total_turns"],
            len(f["wasted_turns"]), ", ".join(f["evidence_never_found"]) or "none"))
    never = set.intersection(*[set(f["evidence_never_found"]) for _, f in results]) if results else set()
    lines += ["", "**Evidence no run found:** %s" % (", ".join(sorted(never)) or "none"),
              "**Runs that saw the anomaly:** %d of %d" % (sum(f["anomaly_shown"] for _, f in results), len(results)),
              "", "## Final answers", ""]
    lines += ["- %s, journal %s: %s" % (r["persona"], "on" if r["journal"] else "off", r["final_answer"])
              for r, _ in results]
    return "\n".join(lines) + "\n"


INTERVIEW = """You just finished playtesting a short text mystery game as the player described below.
A designer is interviewing you about your playthrough. Answer each question honestly, in character,
in 2-4 sentences, based only on what the game showed you. If you don't remember or didn't notice
something, say so."""


def interview(report_path, questions, ask):
    """Asks a finished run's player questions about its playthrough. Returns [(question, answer)]."""
    data = json.load(open(report_path, encoding="utf-8"))
    run = data["run"]
    history = run.get("transcript")
    if not history:  # older reports: rebuild from the saved moves, notes and results
        lines = ["Here is your playthrough, move by move:"]
        for t in run["turns"]:
            lines.append("Loop %d. You chose %s. Your note: %s\nThe game said: %s"
                         % (t["loop"], t["action"], t["note"], t["result"]))
        lines += ["Your theory after loop %d: %s" % (h["after_loop"], h["text"]) for h in run["hypotheses"]]
        lines.append("Your final answer: %s" % run["final_answer"])
        history = [{"role": "user", "content": "\n\n".join(lines)},
                   {"role": "assistant", "content": "Understood. I remember my playthrough."}]
    system = INTERVIEW + "\n\nThe player: " + PERSONAS[run["persona"]]
    messages, qa = list(history), []
    for q in questions:
        messages.append({"role": "user", "content": "Interview question: " + q})
        a = ask(system, messages)
        messages.append({"role": "assistant", "content": a})
        qa.append((q, a))
    return qa


def save_interview(report_path, qa, model):
    base = new_base(os.path.dirname(report_path), os.path.basename(report_path)[:-len(".json")] + "-interview"
                    + ("-dry-run" if model == "dry-run" else ""))
    lines = ["# Interview: %s" % os.path.basename(report_path), "", "Model: %s" % model, "",
             "Answers are the player's own explanation after the fact: useful hints, not proof.", ""]
    for i, (q, a) in enumerate(qa, 1):
        lines += ["## %d. %s" % (i, q), "", a.strip(), ""]
    with open(base + ".md", "x", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return base + ".md"


def main():
    """python3 agent.py [--provider claude|gemini] [--persona curious|escape] [--no-journal] [--all] [--dry-run]"""
    load_env()
    provider = sys.argv[sys.argv.index("--provider") + 1] if "--provider" in sys.argv else "claude"
    if "--dry-run" in sys.argv:
        ask, model = fake_model(), "dry-run"
    elif provider == "gemini":
        ask, model = gemini_model(), "gemini: " + os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
    else:
        ask, model = claude_model(), "claude: " + MODEL
    if "--interview" in sys.argv:  # --interview reports/<run>.json questions.txt (one question per line)
        i = sys.argv.index("--interview")
        report, qfile = sys.argv[i + 1], sys.argv[i + 2]
        questions = [q.strip() for q in open(qfile, encoding="utf-8") if q.strip()]
        print("Interview: %s  (%d API calls)" % (save_interview(report, interview(report, questions, ask), model),
                                                  0 if model == "dry-run" else len(questions)))
        return
    if "--all" in sys.argv:
        combos = [(p, j) for p in PERSONAS for j in (True, False)]
    else:
        persona = sys.argv[sys.argv.index("--persona") + 1] if "--persona" in sys.argv else "curious"
        combos = [(persona, "--no-journal" not in sys.argv)]
    results = []
    for persona, journal in combos:
        game = Game(journal=journal, log_dir="logs")
        run = play(game, ask, persona)
        run["model"] = model
        f = facts(game, run)
        results.append((run, f))
        print("Report: %s  (%d API calls)" % (save_report(run, f), run["api_calls"]))
    if len(results) > 1:
        base = new_base("reports", datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-aggregate")
        with open(base + ".md", "x", encoding="utf-8") as fh:
            fh.write(aggregate_md(results))
        print("Aggregate: %s.md" % base)


if __name__ == "__main__":
    main()
