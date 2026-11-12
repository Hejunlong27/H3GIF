import unittest

import torch

from core.grid import plan_grid, split_grid, split_grid_detailed


def indexed_image(rows, columns, cell_width=2, cell_height=2):
    height = rows * cell_height
    width = columns * cell_width
    image = torch.zeros((1, height, width, 1), dtype=torch.float32)
    for row in range(rows):
        for column in range(columns):
            image[0, row * cell_height, column * cell_width, 0] = row * columns + column
    return image


class GridSplitTests(unittest.TestCase):
    def test_1x1_split(self):
        image = torch.arange(1 * 4 * 5 * 1, dtype=torch.float32).reshape(1, 4, 5, 1)
        frames, width, height = split_grid(image, 1, 1)
        self.assertEqual(tuple(frames.shape), (1, 4, 5, 1))
        self.assertEqual((width, height), (5, 4))

    def test_2x2_split(self):
        frames, width, height = split_grid(indexed_image(2, 2, 4, 4), 2, 2)
        self.assertEqual(tuple(frames.shape), (4, 4, 4, 1))
        self.assertEqual((width, height), (4, 4))

    def test_4x4_split(self):
        frames, width, height = split_grid(indexed_image(4, 4), 4, 4)
        self.assertEqual(tuple(frames.shape), (16, 2, 2, 1))
        self.assertEqual((width, height), (2, 2))

    def test_8x8_split(self):
        frames, width, height = split_grid(indexed_image(8, 8), 8, 8)
        self.assertEqual(tuple(frames.shape), (64, 2, 2, 1))
        self.assertEqual((width, height), (2, 2))

    def test_non_square_grid_and_aspect_ratio(self):
        frames, width, height = split_grid(indexed_image(2, 3, 3, 2), 3, 2)
        self.assertEqual(tuple(frames.shape), (6, 2, 3, 1))
        self.assertEqual((width, height), (3, 2))

    def test_rows_columns(self):
        image = indexed_image(3, 2)
        frames, _, _ = split_grid(image, columns=2, rows=3)
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(6)], [0, 1, 2, 3, 4, 5])

    def test_column_major_order(self):
        frames, _, _ = split_grid(indexed_image(2, 2), 2, 2, order="Column-major")
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(4)], [0, 2, 1, 3])

    def test_serpentine_order(self):
        frames, _, _ = split_grid(indexed_image(2, 2), 2, 2, order="Serpentine")
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(4)], [0, 1, 3, 2])

    def test_reverse_order(self):
        frames, _, _ = split_grid(indexed_image(2, 2), 2, 2, reverse=True)
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(4)], [3, 2, 1, 0])

    def test_gap_handling(self):
        image = torch.zeros((1, 8, 8, 1), dtype=torch.float32)
        for row in range(2):
            for column in range(2):
                image[0, row * 5, column * 5, 0] = row * 2 + column
        frames, width, height = split_grid(image, 2, 2, gap_x=2, gap_y=2)
        self.assertEqual(tuple(frames.shape), (4, 3, 3, 1))
        self.assertEqual((width, height), (3, 3))
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(4)], [0, 1, 2, 3])

    def test_margins_and_offset(self):
        image = torch.zeros((1, 10, 10, 1), dtype=torch.float32)
        image[0, 2, 2, 0] = 11
        frames, width, height = split_grid(
            image,
            2,
            2,
            margin_left=1,
            margin_right=1,
            margin_top=1,
            margin_bottom=1,
            offset_x=1,
            offset_y=1,
        )
        self.assertEqual((width, height), (3, 3))
        self.assertEqual(float(frames[0, 0, 0, 0]), 11.0)

    def test_custom_tile_size(self):
        image = torch.zeros((1, 7, 7, 1), dtype=torch.float32)
        image[0, 0, 0, 0] = 1
        image[0, 4, 4, 0] = 2
        frames, width, height = split_grid(
            image, 2, 2, gap_x=1, gap_y=1, tile_width=3, tile_height=3
        )
        self.assertEqual((width, height), (3, 3))
        self.assertEqual([float(frames[0, 0, 0, 0]), float(frames[3, 0, 0, 0])], [1.0, 2.0])

    def test_frame_range_and_skip(self):
        image = indexed_image(2, 3)
        frames, _, _ = split_grid(image, 3, 2, frame_range="2-5", skip_frames="2")
        self.assertEqual([int(frames[i, 0, 0, 0]) for i in range(3)], [2, 3, 4])

    def test_skip_blank_frames(self):
        image = torch.zeros((1, 4, 4, 1), dtype=torch.float32)
        image[0, 2:4, 2:4, 0] = torch.tensor([[0.0, 1.0], [1.0, 0.0]])
        frames, _, _ = split_grid(image, 2, 2, skip_blank_frames=True, blank_threshold=0.01)
        self.assertEqual(tuple(frames.shape), (1, 2, 2, 1))

    def test_multiple_batches_are_flattened(self):
        image = torch.cat([indexed_image(2, 2), indexed_image(2, 2) + 10], dim=0)
        frames, _, _ = split_grid(image, 2, 2)
        self.assertEqual(tuple(frames.shape), (8, 2, 2, 1))

    def test_layout_bounds(self):
        layout = plan_grid(indexed_image(2, 2), 2, 2)
        self.assertEqual(layout.frame_count, 4)
        self.assertEqual((layout.bounds[0].x0, layout.bounds[0].y0), (0, 0))
        self.assertEqual((layout.bounds[3].x1, layout.bounds[3].y1), (4, 4))

    def test_empty_batch_rejected(self):
        with self.assertRaises(ValueError):
            split_grid(torch.zeros((0, 8, 8, 1)), 2, 2)

    def test_non_tensor_rejected(self):
        with self.assertRaises(ValueError):
            split_grid([[0.0]], 2, 2)

    def test_invalid_grid_settings_rejected(self):
        with self.assertRaises(ValueError):
            split_grid(indexed_image(2, 2), 0, 2)
        with self.assertRaises(ValueError):
            split_grid(indexed_image(2, 2), 2, 2, gap_x=-1)

    def test_oversized_custom_tile_rejected(self):
        with self.assertRaises(ValueError):
            split_grid(indexed_image(2, 2), 2, 2, tile_width=8, tile_height=8)

    def test_all_blank_frames_rejected(self):
        with self.assertRaises(ValueError):
            split_grid(
                torch.zeros((1, 4, 4, 1)),
                2,
                2,
                skip_blank_frames=True,
                blank_threshold=0.01,
            )


if __name__ == "__main__":
    unittest.main()
