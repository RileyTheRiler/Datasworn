import unittest

from src.tutorial import TutorialEngine, TutorialState, get_new_player_scenario


class TestTutorialOnboarding(unittest.TestCase):
    def setUp(self):
        self.engine = TutorialEngine(get_new_player_scenario())
        self.state = TutorialState()
        self.engine.start(self.state)

    def test_tutorial_progression_and_comprehension_notes(self):
        # Step 1 completes when a character exists
        self.engine.evaluate_progress(self.state, {"character_created": True})
        self.assertIn("create-character", self.state.completed_steps)

        # Step 2 completes after first action is submitted
        self.engine.evaluate_progress(self.state, {"submitted_action": True})
        self.assertIn("submit-action", self.state.completed_steps)

        # Step 3 waits for narrative text
        self.engine.evaluate_progress(self.state, {"received_narrative": True})
        self.assertIn("review-outcome", self.state.completed_steps)

        # Final checkpoint records comprehension notes
        comprehension = "accept keeps the scene, retry rewrites it"
        self.engine.evaluate_progress(
            self.state, {"acknowledged_guidance": True, "comprehension": comprehension}
        )
        self.assertIn("checkpoint", self.state.completed_steps)
        self.assertEqual(self.state.comprehension_notes.get("checkpoint"), comprehension)

        self.assertAlmostEqual(self.engine.progress_percent(self.state), 100.0)

    def test_repeat_and_skip_affordances(self):
        # Repeat should keep the current step in place
        current = self.engine.current_step(self.state)
        self.assertEqual(current.id, "create-character")
        self.engine.repeat_step(self.state)
        self.assertEqual(self.engine.current_step(self.state).id, "create-character")

        # Skip advances to the next gated item
        self.engine.skip_step(self.state)
        self.assertIn("create-character", self.state.skipped_steps)
        self.assertEqual(self.engine.current_step(self.state).id, "submit-action")


if __name__ == "__main__":
    unittest.main()
