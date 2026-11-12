import unittest

from core.director import build_storyboard_direction, parse_panel_actions


class StoryboardDirectorTests(unittest.TestCase):
    def test_builds_exact_grid_prompt(self):
        direction = build_storyboard_direction(
            scene_description="A detective enters a rainy alley.",
            panel_actions=(
                "1. He opens the door.\n"
                "2. He sees a clue.\n"
                "3. He kneels down.\n"
                "4. He looks back."
            ),
            rows=2,
            columns=2,
            gutter_pixels=8,
        )
        self.assertEqual((direction.rows, direction.columns), (2, 2))
        self.assertEqual(direction.panel_count, 4)
        self.assertIn("exactly 2 rows and 2 columns", direction.positive_prompt)
        self.assertIn("He opens the door.", direction.positive_prompt)
        self.assertIn("He looks back.", direction.positive_prompt)
        self.assertIn("8 pixels", direction.positive_prompt)
        self.assertIn("Do not include captions", direction.positive_prompt)

    def test_missing_actions_are_filled(self):
        actions = parse_panel_actions("First action", 4)
        self.assertEqual(actions[0], "First action")
        self.assertEqual(len(actions), 4)
        self.assertTrue(all(actions[1:]))

    def test_action_numbering_and_bullets_are_removed(self):
        actions = parse_panel_actions("- 1. First\n* 2: Second; Panel 3: Third", 3)
        self.assertEqual(actions, ["First", "Second", "Third"])

    def test_empty_scene_rejected(self):
        with self.assertRaises(ValueError):
            build_storyboard_direction("", "", 2, 2)

    def test_invalid_grid_rejected(self):
        with self.assertRaises(ValueError):
            build_storyboard_direction("scene", "", 0, 2)
        with self.assertRaises(ValueError):
            build_storyboard_direction("scene", "", 2, 9)


if __name__ == "__main__":
    unittest.main()
