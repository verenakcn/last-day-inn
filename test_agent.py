"""Tests the agent loop and report with a scripted stand-in for the model (no API calls)."""

import unittest

import os
import tempfile

from agent import aggregate_md, facts, fake_model, play, report_md, save_report, to_gemini
from engine import Game


def scripted(choices):
    """A fake model that picks actions by id, in order, and answers prompts plainly."""
    state = {"game": None, "queue": list(choices)}

    def ask(system, messages):
        text = messages[-1]["content"]
        if "HYPOTHESIS" in text:
            return "HYPOTHESIS: The day repeats."
        if "The game is over" in text:
            return "Mira remembers the loop too."
        if not state["queue"]:
            return "NOTE: out of ideas\nCHOICE: 1"
        want = state["queue"].pop(0)
        acts = state["game"].actions()
        return "NOTE: trying %s\nCHOICE: %d" % (want, acts.index(want) + 1)

    return state, ask


class AgentRun(unittest.TestCase):
    def test_photo_path_reports_trigger_and_anomaly(self):
        state, ask = scripted(["examine:drawer", "move:lobby", "move:garden", "present:old_photo>mira",
                               "examine:flowerpot", "examine:back_gate", "move:lobby"])
        game = state["game"] = Game()
        run = play(game, ask)
        f = facts(game, run)
        self.assertTrue(f["escaped_loop_1"])
        self.assertTrue(f["memory_trigger_hit"])
        self.assertTrue(f["anomaly_shown"])
        self.assertEqual(f["total_turns"], 7)
        self.assertEqual(run["hypotheses"][0]["text"], "The day repeats.")
        self.assertIn("note", f["evidence_found_but_never_shown"])
        self.assertIn("blue_ribbon", f["evidence_never_found"])
        self.assertIn("| Escaped in Loop 1? | yes |", report_md(run, f))

    def test_wasted_turns_are_flagged(self):
        moves = ["move:lobby", "examine:front_door", "examine:front_door", "present:note>innkeeper"]
        state, ask = scripted(moves + ["examine:grandfather_clock"] * 4)
        game = state["game"] = Game()
        run = play(game, ask)
        f = facts(game, run)
        self.assertIn("examine:front_door (repeat in loop 1)", f["wasted_turns"])

    def test_aggregate_compares_runs(self):
        results = []
        for persona, journal, moves in [("curious", True, ["examine:drawer", "move:lobby", "move:garden",
                                                           "present:old_photo>mira", "examine:flowerpot",
                                                           "examine:back_gate", "move:lobby"]),
                                        ("escape", False, ["move:lobby", "move:garden", "examine:back_gate",
                                                           "examine:flowerpot", "examine:back_gate"])]:
            state, ask = scripted(moves)
            game = state["game"] = Game(journal=journal)
            run = play(game, ask, persona)
            results.append((run, facts(game, run)))
        md = aggregate_md(results)
        self.assertIn("| curious | on | yes | yes | yes | 7 |", md)
        self.assertIn("| escape | off | yes | no |", md)
        self.assertIn("**Evidence no run found:** blue_ribbon, clock_inscription, closing_notice", md)

    def test_dry_run_makes_no_api_calls_and_finishes(self):
        game = Game()
        run = play(game, fake_model(seed=1))
        self.assertTrue(game.ended)
        self.assertEqual(run["api_calls"], 0)

    def test_api_calls_counted_and_actions_capped(self):
        state, ask = scripted([])  # always picks action 1
        game = state["game"] = Game()
        run = play(game, ask, max_actions=5)
        self.assertTrue(run["capped"])
        self.assertEqual(len(run["turns"]), 5)
        self.assertEqual(run["api_calls"], 6)  # 5 actions + final answer (no reset reached)

    def test_error_mid_run_keeps_a_partial_report(self):
        calls = {"n": 0}

        def ask(system, messages):
            calls["n"] += 1
            if calls["n"] == 3:
                raise RuntimeError("quota per day exceeded")
            return "NOTE: go\nCHOICE: 1"

        game = Game()
        run = play(game, ask)
        f = facts(game, run)
        self.assertEqual(len(run["turns"]), 2)
        self.assertIn("quota per day", f["stopped_by_error"])
        self.assertIn("INCOMPLETE", report_md(run, f))

    def test_reports_never_overwrite(self):
        game = Game()
        run = play(game, fake_model())
        run["model"] = "dry-run"
        f = facts(game, run)
        with tempfile.TemporaryDirectory() as d:
            first, second = save_report(run, f, d), save_report(run, f, d)
            self.assertNotEqual(first, second)
            self.assertTrue(first.endswith("-curious-journal-on-dry-run.md"))
            self.assertEqual(len(os.listdir(d)), 4)  # two .md + two .json

    def test_gemini_message_format(self):
        msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "CHOICE: 1"}]
        self.assertEqual(to_gemini(msgs), [{"role": "user", "parts": [{"text": "hi"}]},
                                           {"role": "model", "parts": [{"text": "CHOICE: 1"}]}])

    def test_bad_reply_falls_back_to_first_action(self):
        game = Game()
        calls = {"n": 0}

        def ask(system, messages):
            calls["n"] += 1
            return "I'm not sure." if calls["n"] < 30 else "Done."

        run = play(game, ask)
        self.assertEqual(run["turns"][0]["action"], "move:lobby")
        self.assertGreater(facts(game, run)["unparsed_replies"], 0)


if __name__ == "__main__":
    unittest.main()
