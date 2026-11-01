"""Playtest agent v1: an LLM plays through the same observe/actions/act interface as a human.

    pip install anthropic
    echo "ANTHROPIC_API_KEY=..." > .env
    python3 agent.py                      # curious explorer, journal on
    python3 agent.py --persona escape --no-journal
    python3 agent.py --all                # both personas x journal on/off + aggregate report

Gemini instead of Claude: pip install google-genai, put GEMINI_API_KEY=... in .env,
then add --provider gemini to any command above.

The report's facts (escaped, evidence found/used, trigger, anomaly, turns) are computed from the
game log, not from the model. The model only plays and states hypotheses.
"""

import datetime
import json
import os
import re
import sys

from engine import Game

MODEL = "claude-opus-5-5"

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

    def ask(system, messages):
        response = client.models.generate_content(
            model=model, contents=to_gemini(messages),
            config=types.GenerateContentConfig(system_instruction=system))
        return "".join(p.text for p in response.candidates[0].content.parts if p.text)

    return ask


def play(game, ask, persona="curious"):
    """Plays one session. Returns the run record used for the report."""
    system = RULES + "\n\n" + PERSONAS[persona]
    messages = []
    run = {"persona": persona, "journal": game.journal_on, "turns": [], "hypotheses": [], "final_answer": None}

    def say(text):
        messages.append({"role": "user", "content": text})
        reply = ask(system, messages)
        messages.append({"role": "assistant", "content": reply})
        return reply

    screen = game.opening
    while not game.ended:
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
    run["final_answer"] = say(screen + "\n\nThe game is over. It asks you: " +
                              game.w["loops"]["end_screen"]["prompt"] + " Answer in two or three sentences.")
    game.answer_end_prompt(run["final_answer"])
    run["ended"] = game.ended
    return run


def facts(game, run):
    """Report facts computed from the game log and world file only."""
    events = game.log["events"]
    actions = [e for e in events if e["type"] == "action"]
    evidence = set(game.w["evidence"])
    found = {i for e in actions for i in e["after"]["inventory"] if i in evidence}
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
    }


def report_md(run, f):
    yes = lambda b: "yes" if b else "no"
    lines = [
        "# Playtest report: %s, journal %s" % (run["persona"], "on" if run["journal"] else "off"),
        "",
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


def save_report(run, f, out_dir="reports"):
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = os.path.join(out_dir, "%s-%s-journal-%s" % (stamp, run["persona"], "on" if run["journal"] else "off"))
    with open(base + ".md", "w", encoding="utf-8") as fh:
        fh.write(report_md(run, f))
    with open(base + ".json", "w", encoding="utf-8") as fh:
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


def main():
    """python3 agent.py [--provider claude|gemini] [--persona curious|escape] [--no-journal] [--all]"""
    load_env()
    provider = sys.argv[sys.argv.index("--provider") + 1] if "--provider" in sys.argv else "claude"
    ask = gemini_model() if provider == "gemini" else claude_model()
    if "--all" in sys.argv:
        combos = [(p, j) for p in PERSONAS for j in (True, False)]
    else:
        persona = sys.argv[sys.argv.index("--persona") + 1] if "--persona" in sys.argv else "curious"
        combos = [(persona, "--no-journal" not in sys.argv)]
    results = []
    for persona, journal in combos:
        game = Game(journal=journal, log_dir="logs")
        run = play(game, ask, persona)
        f = facts(game, run)
        results.append((run, f))
        print("Report: %s" % save_report(run, f))
    if len(results) > 1:
        path = os.path.join("reports", datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-aggregate.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(aggregate_md(results))
        print("Aggregate: %s" % path)


if __name__ == "__main__":
    main()
