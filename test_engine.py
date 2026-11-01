"""Run with: python3 -m unittest -v"""

import unittest

from engine import Game

ESCAPE = ["move:lobby", "move:garden", "examine:back_gate", "examine:flowerpot", "examine:back_gate"]
PHOTO_THEN_ESCAPE = ["examine:drawer", "move:lobby", "move:garden", "present:old_photo>mira",
                     "examine:flowerpot", "examine:back_gate"]


def play(actions, **kw):
    g = Game(**kw)
    texts = [g.act(a) for a in actions]
    return g, texts


class Loop1(unittest.TestCase):
    def test_starts_in_guest_room_with_note(self):
        g = Game()
        self.assertEqual(g.location, "guest_room")
        self.assertEqual(g.inventory, ["note"])
        self.assertIn("Leave before midnight.", g.opening)

    def test_shortest_escape_resets_to_loop_2(self):
        g, texts = play(ESCAPE)
        self.assertIn("under the flowerpot", texts[2])  # Mira's key hint
        self.assertIn("a clock begins to chime", texts[-1])
        self.assertEqual((g.loop, g.location, g.phase), (2, "guest_room", 0))
        self.assertEqual(g.inventory, ["note"])  # key reset, anchored note kept
        self.assertFalse(g.ended)

    def test_gate_is_locked_without_key(self):
        g, _ = play(["move:lobby", "move:garden", "examine:back_gate"])
        self.assertEqual(g.loop, 1)

    def test_eight_actions_reach_midnight(self):
        g, texts = play(["examine:window"] * 8)
        self.assertEqual(g.loop, 2)
        self.assertIn("faint and far away", texts[-1])

    def test_mira_narration_fits_the_room(self):
        _, texts = play(["examine:window", "move:lobby", "move:garden"])  # first meet her in the Garden
        self.assertIn("You haven't tried the pie.", texts[-1])
        self.assertNotIn("armchair", texts[-1])

    def test_no_show_to_place_options(self):
        g, _ = play(["examine:drawer", "move:lobby", "move:garden"])
        shows = [a for a in g.actions() if a.startswith("present:")]
        self.assertEqual(shows, ["present:note>mira", "present:old_photo>mira"])

    def test_note_cannot_be_dropped(self):
        self.assertFalse(any(a.startswith("drop") for a in Game().actions()))


class Loop2(unittest.TestCase):
    def test_mira_repeats_line_without_photo(self):
        g, _ = play(ESCAPE + ["move:lobby"])
        self.assertFalse(g.ended)

    def test_photo_puts_mira_by_clock_and_shows_anomaly(self):
        g, texts = play(PHOTO_THEN_ESCAPE + ["move:lobby"])
        self.assertIn("You still haven't tried the pie.", texts[-1])
        self.assertEqual(g.ended, "anomaly_seen")
        self.assertEqual(g.actions(), [])

    def test_innkeeper_has_never_seen_note_in_loop_2(self):
        g, texts = play(ESCAPE + ["move:lobby", "present:note>innkeeper"])
        self.assertIn("never seen it", texts[-1])

    def test_ends_after_loop_3(self):
        g, _ = play(["examine:window"] * 24)
        self.assertEqual(g.ended, "loop_limit")


class Engine(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(play(PHOTO_THEN_ESCAPE)[1], play(PHOTO_THEN_ESCAPE)[1])

    def test_every_listed_action_works(self):
        g = Game()
        for a in g.actions():
            Game().act(a)  # each from a fresh start; must not raise

    def test_journal_off_hides_journal(self):
        self.assertNotIn("Journal", Game(journal=False).observe())


if __name__ == "__main__":
    unittest.main()
