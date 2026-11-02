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
        self.assertIn("MORNING", g.opening)
        screen = g.observe()
        self.assertTrue(screen.startswith("Morning · 2 actions left\n**GUEST ROOM**\n(A small room"))
        self.assertLess(screen.index("Leave before midnight."), screen.index("Nobody else is here."))

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
        self.assertIn("You're new here. Try the pie tonight; it's the best thing about this place.", texts[-1])
        self.assertNotIn("armchair", texts[-1])

    def test_no_show_to_place_options(self):
        g, _ = play(["examine:drawer", "move:lobby", "move:garden"])
        shows = [a for a in g.actions() if a.startswith("present:")]
        self.assertEqual(shows, ["present:note>mira", "present:old_photo>mira"])

    def test_room_text_then_intros_once_per_game(self):
        g, texts = play(["move:lobby"])
        screen = g.observe()  # time, place, room text, then what happened
        self.assertLess(screen.index("**LOBBY**"), screen.index("(The heart of the inn"))
        self.assertLess(screen.index("(The heart of the inn"), screen.index("Mira: a fellow guest"))
        self.assertLess(texts[0].index("Mira: a fellow guest"), texts[0].index("You're new here. Try the pie tonight; it's the best thing about this place."))
        g.act("move:garden")
        g.act("move:lobby")
        self.assertNotIn("Mira: a fellow guest", g.act("move:garden") + g.act("move:lobby"))

    def test_done_mark_clears_at_reset(self):
        g, _ = play(["examine:window"])
        self.assertTrue(g.describe_action("examine:window").startswith("✓ "))
        self.assertFalse(g.describe_action("examine:drawer").startswith("✓ "))
        for _ in range(7):
            g.act("examine:window")
        self.assertEqual(g.loop, 2)
        self.assertFalse(g.describe_action("examine:window").startswith("✓ "))

    def test_picked_up_items_show_their_content_with_journal_off(self):
        g = Game(journal=False)
        photo = g.act("examine:drawer")
        self.assertIn("It shows the innkeeper and a little girl with a blue ribbon, beside the clock.", photo)
        g.act("move:lobby")
        notice = g.act("examine:reception_desk")
        self.assertIn('It reads: "After many happy years, the inn closes its doors for good tomorrow.', notice)
        self.assertNotIn("Journal", g.observe())

    def test_clock_promises_no_door(self):
        g, texts = play(["move:lobby", "examine:grandfather_clock", "examine:grandfather_clock"])
        self.assertIn("tall enough to hide a child", texts[1])
        self.assertIn("just as before", texts[2])
        self.assertNotIn("door", texts[1] + texts[2])

    def test_pie_only_offered_in_the_evening(self):
        g, _ = play(["move:lobby"])
        self.assertNotIn("examine:pie", g.actions())
        self.assertNotIn("Pie", g.observe())
        g.act("examine:front_door")  # -> Afternoon
        g.act("examine:front_door")
        g.act("examine:front_door")  # -> Evening
        self.assertIn("examine:pie", g.actions())
        self.assertIn("still warm", g.act("examine:pie"))

    def test_player_never_sees_a_loop_counter(self):
        g = Game()
        seen = [g.opening, g.observe()]
        for a in ESCAPE + ["move:lobby"]:
            seen += [g.act(a), g.observe()] + [g.describe_action(x) for x in g.actions()]
        text = "\n".join(seen)
        self.assertNotRegex(text, r"\bLoop\b|\bDay \d")
        self.assertIn("MIDNIGHT", text)
        self.assertEqual(text.count("MORNING"), 2)  # first morning + waking again

    def test_warning_before_the_last_action_of_the_night(self):
        g, _ = play(["move:lobby", "move:guest_room"] * 3)  # 6 of 8 actions used
        self.assertNotIn("strike twelve soon", g.observe())
        g.act("move:lobby")
        self.assertIn("**The clock will strike twelve soon.**", g.observe())

    def test_midnight_fades_out_and_waking_again_asks_a_question(self):
        g, texts = play(ESCAPE)
        self.assertIn("**The snow tilts", texts[-1])  # fade line after the escape scene
        self.assertIn("**Something isn't right.", texts[-1])
        self.assertNotIn("Something isn't right", Game().opening)  # not on the first morning

    def test_day_running_out_has_a_lead_in_and_day_3_wakes_differently(self):
        g, texts = play(["move:lobby", "move:guest_room"] * 4)  # day 1 runs out in the Guest Room
        self.assertIn("You lose track of time.", texts[-1])
        self.assertIn("Somewhere in the inn", texts[-1])
        self.assertIn("What happened last night", texts[-1])
        texts = [g.act(a) for a in ["move:lobby", "move:guest_room"] * 4]  # day 2 runs out
        self.assertIn("Again? Something about this day", texts[-1])

    def test_screen_does_not_repeat_the_menu(self):
        obs = Game().observe()
        self.assertNotIn("You could examine", obs)
        self.assertNotIn("Exits:", obs)
        self.assertIn("You carry: Handwritten note", obs)

    def test_journal_splits_before_and_today_after_waking(self):
        g, _ = play(ESCAPE)
        obs = g.observe()
        self.assertIn("From before you woke:", obs)
        self.assertIn("The gate key was under the flowerpot.", obs)
        self.assertIn("(nothing yet)", obs)
        self.assertNotIn("From before", Game().observe())

    def test_inscription_is_known_not_carried(self):
        g, _ = play(["move:lobby", "examine:grandfather_clock"])
        obs = g.observe()
        self.assertIn("You carry: Handwritten note", obs)
        self.assertNotIn("You carry: Handwritten note, Clock inscription", obs)
        self.assertIn('You know: Clock inscription ("Mind the hours you wish away.")', obs)
        self.assertIn("present:clock_inscription>innkeeper", g.actions())

    def test_sessions_started_together_get_separate_logs(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            a, b = Game(log_dir=d), Game(log_dir=d)  # same second
            self.assertNotEqual(a.log_path, b.log_path)
            a.act("move:lobby")
            b.act("examine:window")
            self.assertEqual(len(os.listdir(d)), 2)

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
