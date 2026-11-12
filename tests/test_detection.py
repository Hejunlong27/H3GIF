import unittest

import torch

from core.grid import detect_grid


def synthetic_grid(rows, columns, cell=24, gap=2):
    height = rows * cell + (rows - 1) * gap
    width = columns * cell + (columns - 1) * gap
    image = torch.zeros((1, height, width, 3), dtype=torch.float32)
    for row in range(rows):
        for column in range(columns):
            y = row * (cell + gap)
            x = column * (cell + gap)
            image[0, y:y + cell, x:x + cell] = torch.tensor(
                [0.15 + 0.05 * ((row + column) % 8), 0.45, 0.75]
            )
    return image


class GridDetectionTests(unittest.TestCase):
    def test_detect_2x2(self):
        result = detect_grid(synthetic_grid(2, 2))
        self.assertTrue(result.detected)
        self.assertEqual((result.rows, result.columns), (2, 2))
        self.assertGreaterEqual(result.confidence, 0.55)

    def test_detect_4x4(self):
        result = detect_grid(synthetic_grid(4, 4))
        self.assertTrue(result.detected)
        self.assertEqual((result.rows, result.columns), (4, 4))

    def test_detect_8x8(self):
        result = detect_grid(synthetic_grid(8, 8, cell=12))
        self.assertTrue(result.detected)
        self.assertEqual((result.rows, result.columns), (8, 8))

    def test_detect_non_square_grid(self):
        result = detect_grid(synthetic_grid(3, 2))
        self.assertTrue(result.detected)
        self.assertEqual((result.rows, result.columns), (3, 2))

    def test_uniform_image_fails_without_guessing(self):
        result = detect_grid(torch.ones((1, 128, 128, 3)))
        self.assertFalse(result.detected)
        self.assertEqual((result.rows, result.columns), (1, 1))
        self.assertEqual(result.confidence, 0.0)

    def test_detection_json_shape(self):
        data = detect_grid(synthetic_grid(2, 2)).as_dict()
        self.assertIn("row_boundaries", data)
        self.assertIn("column_boundaries", data)
        self.assertIn("detected", data)


if __name__ == "__main__":
    unittest.main()
