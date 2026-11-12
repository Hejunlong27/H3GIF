import tempfile
import unittest
from pathlib import Path

import torch
from PIL import Image

from tests.helpers import load_package


class NodeInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = load_package()

    def test_node_mappings(self):
        self.assertEqual(
            set(self.package.NODE_CLASS_MAPPINGS),
            {
                "StoryboardGridSplit",
                "StoryboardAnimation",
                "StoryboardGIFExport",
                "StoryboardLoopOptimizer",
                "H3GIFStoryboardDirector",
            },
        )
        self.assertEqual(
            self.package.NODE_DISPLAY_NAME_MAPPINGS["StoryboardGridSplit"],
            "H3GIF Grid Split",
        )

    def test_manual_split_node(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardGridSplit"]()
        image = torch.zeros((1, 8, 8, 3), dtype=torch.float32)
        result = node.split(
            image,
            "Custom grid",
            4,
            4,
            0,
            0,
            0,
            0,
            "Row-major",
            False,
        )
        self.assertEqual(tuple(result[0].shape), (16, 2, 2, 3))
        self.assertEqual(result[1], 16)
        self.assertEqual(result[8][0], "{")

    def test_storyboard_director_node(self):
        node = self.package.NODE_CLASS_MAPPINGS["H3GIFStoryboardDirector"]()
        prompt, rows, columns, gutter, panel_count, info = node.compose(
            "A character crosses a rainy street.",
            "1. Steps forward\n2. Looks left\n3. Raises an umbrella\n4. Continues walking",
            2,
            2,
            8,
            "same character and outfit",
            "cinematic 3D animation",
            "",
        )
        self.assertIn("exactly 2 rows and 2 columns", prompt)
        self.assertEqual((rows, columns, gutter, panel_count), (2, 2, 8, 4))
        self.assertIn('"layout":"2x2"', info)

    def test_auto_detection_failure_is_actionable(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardGridSplit"]()
        with self.assertRaisesRegex(ValueError, "rows=1, columns=1"):
            node.split(
                torch.ones((1, 64, 64, 3)),
                "Auto detect",
                4,
                4,
                0,
                0,
                0,
                0,
                "Row-major",
                False,
            )

    def test_manual_split_rejects_non_tensor(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardGridSplit"]()
        with self.assertRaises(ValueError):
            node.split(
                [[0.0]],
                "Custom grid",
                2,
                2,
                0,
                0,
                0,
                0,
                "Row-major",
                False,
            )

    def test_animation_node(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardAnimation"]()
        frames = torch.arange(4, dtype=torch.float32).reshape(4, 1, 1, 1).repeat(1, 2, 2, 3)
        result, count = node.build(frames, "Ping-pong", 1)
        self.assertEqual(count, 6)
        self.assertEqual([int(result[i, 0, 0, 0]) for i in range(count)], [0, 1, 2, 3, 2, 1])

    def test_gif_export_node_returns_actual_metadata(self):
        import folder_paths

        original = folder_paths.get_output_directory
        with tempfile.TemporaryDirectory() as directory:
            folder_paths.get_output_directory = lambda: directory
            try:
                node = self.package.NODE_CLASS_MAPPINGS["StoryboardGIFExport"]()
                frames = torch.zeros((4, 8, 8, 3), dtype=torch.float32)
                for index in range(4):
                    frames[index, :, :, 0] = 0.1 + 0.2 * index
                result = node.export(
                    frames,
                    8,
                    0,
                    "Original",
                    "FLOYDSTEINBERG",
                    True,
                    "review/test",
                    0,
                    256,
                    "White",
                )
                output = result["result"]
                self.assertTrue(Path(output[0]).exists())
                self.assertEqual(output[1], 4)
                self.assertEqual(len(output), 7)
                self.assertIsInstance(output[6], float)
                with Image.open(output[0]) as gif:
                    self.assertEqual(gif.n_frames, 4)
            finally:
                folder_paths.get_output_directory = original

    def test_loop_optimizer_node(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardLoopOptimizer"]()
        frames = torch.zeros((4, 8, 8, 3), dtype=torch.float32)
        frames[0, :, :, 0] = 0.0
        frames[-1, :, :, 0] = 1.0
        result, similarity, recommendation, difference = node.optimize(
            frames,
            "Ping-pong if needed",
            2,
            0.02,
        )
        self.assertEqual(tuple(result.shape), (6, 8, 8, 3))
        self.assertGreater(difference, 0.02)
        self.assertIsInstance(similarity, float)
        self.assertIn("Ping-pong", recommendation)

    def test_auto_detection_node(self):
        node = self.package.NODE_CLASS_MAPPINGS["StoryboardGridSplit"]()
        image = torch.zeros((1, 50, 50, 3), dtype=torch.float32)
        for row in range(2):
            for column in range(2):
                y = row * 27
                x = column * 27
                image[0, y:y + 23, x:x + 23] = torch.tensor([0.2, 0.5, 0.8])
        result = node.split(
            image,
            "Auto detect",
            4,
            4,
            2,
            2,
            0,
            0,
            "Row-major",
            False,
        )
        self.assertTrue(result[7])
        self.assertEqual((result[4], result[5]), (2, 2))


if __name__ == "__main__":
    unittest.main()
