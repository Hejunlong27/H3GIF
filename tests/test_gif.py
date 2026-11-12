import tempfile
import unittest
from pathlib import Path

import torch
from PIL import Image

from core.gif import (
    resize_image,
    save_gif,
    tensor_to_rgb_image,
    validate_image_batch,
)
from core.paths import build_output_path, sanitize_output_prefix


def color_frames(count=4, size=8):
    frames = torch.zeros((count, size, size, 3), dtype=torch.float32)
    for index in range(count):
        frames[index, :, :, 0] = 0.1 + 0.8 * index / max(count - 1, 1)
        frames[index, :, :, 1] = 0.2
    return frames


class GifExportTests(unittest.TestCase):
    def test_gif_frames_survive_shared_palette(self):
        with tempfile.TemporaryDirectory() as directory:
            images = [tensor_to_rgb_image(frame) for frame in color_frames()]
            path = Path(directory) / "frames.gif"
            metadata = save_gif(images, path, fps=8, loop_count=0)
            self.assertEqual(metadata.frame_count, 4)
            with Image.open(path) as gif:
                self.assertEqual(gif.n_frames, 4)

    def test_gif_loop_and_fps(self):
        with tempfile.TemporaryDirectory() as directory:
            images = [tensor_to_rgb_image(frame) for frame in color_frames(3)]
            path = Path(directory) / "loop.gif"
            metadata = save_gif(images, path, fps=10, loop_count=2, frame_duration_ms=80)
            self.assertEqual(metadata.frame_count, 3)
            self.assertEqual(metadata.frame_duration_ms, 80)
            self.assertEqual(metadata.effective_fps, 12.5)
            with Image.open(path) as gif:
                self.assertEqual(gif.info.get("loop"), 2)

    def test_gif_duration_quantized_to_centiseconds(self):
        with tempfile.TemporaryDirectory() as directory:
            images = [tensor_to_rgb_image(frame) for frame in color_frames(3)]
            path = Path(directory) / "quantized.gif"
            metadata = save_gif(images, path, fps=8)
            self.assertEqual(metadata.frame_duration_ms, 120)
            self.assertAlmostEqual(metadata.effective_fps, 8.333, places=3)
            with Image.open(path) as gif:
                gif.seek(0)
                self.assertEqual(gif.info.get("duration"), 120)

    def test_gif_resize_preserves_aspect_ratio(self):
        image = Image.new("RGB", (100, 50), (255, 0, 0))
        resized = resize_image(image, 20)
        self.assertEqual(resized.size, (20, 10))

    def test_gif_alpha_composites_on_background(self):
        frame = torch.ones((2, 2, 4), dtype=torch.float32)
        frame[:, :, 3] = 0.0
        white = tensor_to_rgb_image(frame, "White")
        black = tensor_to_rgb_image(frame, "Black")
        self.assertEqual(white.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(black.getpixel((0, 0)), (0, 0, 0))

    def test_invalid_channels_rejected(self):
        with self.assertRaises(ValueError):
            validate_image_batch(torch.zeros((1, 8, 8, 1)))

    def test_empty_batch_rejected(self):
        with self.assertRaises(ValueError):
            validate_image_batch(torch.zeros((0, 8, 8, 3)))

    def test_output_prefix_sanitized(self):
        self.assertEqual(sanitize_output_prefix("../../bad:name"), "bad_name")
        self.assertEqual(sanitize_output_prefix(""), "H3GIF/animation")

    def test_output_path_stays_inside_output_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = build_output_path(directory, "../escape")
            self.assertEqual(Path(directory).resolve(), path.parent.resolve())
            self.assertEqual(path.suffix, ".gif")

    def test_max_file_size_removes_rejected_output(self):
        with tempfile.TemporaryDirectory() as directory:
            images = [tensor_to_rgb_image(frame) for frame in color_frames(2)]
            path = Path(directory) / "too-large.gif"
            with self.assertRaises(ValueError):
                save_gif(images, path, fps=8, max_file_size_bytes=1)
            self.assertFalse(path.exists())

    def test_invalid_fps_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            images = [tensor_to_rgb_image(color_frames(1)[0])]
            with self.assertRaises(ValueError):
                save_gif(images, Path(directory) / "bad.gif", fps=0)


if __name__ == "__main__":
    unittest.main()
