import unittest

import torch

from core.loop import analyze_loop, crossfade_loop, pingpong_frames


def loop_frames(first_value=0.1, last_value=0.1):
    frames = torch.zeros((4, 16, 16, 3), dtype=torch.float32)
    frames[:, :, :, 0] = 0.5
    frames[0, :, :, 0] = first_value
    frames[-1, :, :, 0] = last_value
    return frames


class LoopOptimizerTests(unittest.TestCase):
    def test_identical_endpoints_recommend_forward(self):
        result = analyze_loop(loop_frames(0.2, 0.2))
        self.assertEqual(result.endpoint_difference, 0.0)
        self.assertEqual(result.similarity, 1.0)
        self.assertIn("Forward", result.recommendation)

    def test_different_endpoints_recommend_transition(self):
        result = analyze_loop(loop_frames(0.0, 1.0))
        self.assertGreater(result.endpoint_difference, 0.02)
        self.assertIn("Ping-pong", result.recommendation)

    def test_crossfade_adds_transition_frames(self):
        result = crossfade_loop(loop_frames(0.0, 1.0), 3)
        self.assertEqual(tuple(result.shape), (7, 16, 16, 3))
        self.assertLess(float((result[-1] - result[0]).abs().mean()), 0.5)

    def test_pingpong_sequence(self):
        result = pingpong_frames(loop_frames())
        self.assertEqual(tuple(result.shape), (6, 16, 16, 3))

    def test_single_frame_has_perfect_similarity(self):
        result = analyze_loop(torch.zeros((1, 8, 8, 3)))
        self.assertEqual(result.similarity, 1.0)

    def test_invalid_batch_rejected(self):
        with self.assertRaises(ValueError):
            analyze_loop(torch.zeros((0, 8, 8, 3)))


if __name__ == "__main__":
    unittest.main()
