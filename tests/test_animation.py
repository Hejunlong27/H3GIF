import unittest

from core.animation import build_frame_indices


class AnimationTests(unittest.TestCase):
    def test_forward(self):
        self.assertEqual(build_frame_indices(4), [0, 1, 2, 3])

    def test_reverse(self):
        self.assertEqual(build_frame_indices(4, "Reverse"), [3, 2, 1, 0])

    def test_pingpong_one_frame(self):
        self.assertEqual(build_frame_indices(1, "Ping-pong"), [0])

    def test_pingpong_two_frames(self):
        self.assertEqual(build_frame_indices(2, "Ping-pong"), [0, 1])

    def test_pingpong_three_frames(self):
        self.assertEqual(build_frame_indices(3, "Ping-pong"), [0, 1, 2, 1])

    def test_pingpong_four_frames(self):
        self.assertEqual(build_frame_indices(4, "Ping-pong"), [0, 1, 2, 3, 2, 1])

    def test_pingpong_16_frames(self):
        result = build_frame_indices(16, "Ping-pong")
        self.assertEqual(len(result), 30)
        self.assertEqual(result[-1], 1)
        self.assertEqual(len(set(result)), 16)

    def test_pingpong_64_frames(self):
        result = build_frame_indices(64, "Ping-pong")
        self.assertEqual(len(result), 126)
        self.assertEqual(result[:4], [0, 1, 2, 3])
        self.assertEqual(result[-4:], [4, 3, 2, 1])

    def test_frame_range_skip_and_custom_order(self):
        result = build_frame_indices(
            8,
            frame_range="2-7",
            skip_frames="2,5",
            custom_order="4,1-3",
        )
        self.assertEqual(result, [6, 2, 3, 5])

    def test_repeat_holds(self):
        result = build_frame_indices(
            3,
            hold_each_frame=2,
            hold_first=2,
            hold_last=3,
        )
        self.assertEqual(result, [0, 0, 0, 1, 1, 2, 2, 2, 2])

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            build_frame_indices(4, "Unknown")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            build_frame_indices(0)

    def test_invalid_hold_rejected(self):
        with self.assertRaises(ValueError):
            build_frame_indices(4, hold_each_frame=0)


if __name__ == "__main__":
    unittest.main()
