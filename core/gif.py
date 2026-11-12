"""Pillow-based GIF encoding and metadata inspection."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Sequence

import numpy as np
import torch
from PIL import Image


@dataclass(frozen=True)
class GifMetadata:
    path: str
    frame_count: int
    width: int
    height: int
    file_size_bytes: int
    fps: int
    frame_duration_ms: int
    effective_fps: float


def validate_image_batch(frames: torch.Tensor) -> tuple[int, int, int, int]:
    if not isinstance(frames, torch.Tensor):
        raise ValueError("Expected a ComfyUI IMAGE tensor with shape [N,H,W,C].")
    if frames.ndim != 4:
        raise ValueError("Expected a ComfyUI IMAGE tensor with shape [N,H,W,C].")
    count, height, width, channels = (int(value) for value in frames.shape)
    if count < 1:
        raise ValueError("The IMAGE batch is empty.")
    if height < 1 or width < 1:
        raise ValueError("Image width and height must be at least 1 pixel.")
    if channels not in (3, 4):
        raise ValueError("H3GIF GIF export expects RGB or RGBA IMAGE frames (3 or 4 channels).")
    return count, height, width, channels


def tensor_to_rgb_image(frame: torch.Tensor, alpha_background: str = "White") -> Image.Image:
    if frame.ndim != 3 or int(frame.shape[-1]) not in (3, 4):
        raise ValueError("Each frame must have shape [H,W,3] or [H,W,4].")
    values = frame.detach().to(dtype=torch.float32, device="cpu").numpy()
    values = np.nan_to_num(values, nan=0.0, posinf=1.0, neginf=0.0)
    values = np.clip(values * 255.0, 0, 255).astype(np.uint8)
    if values.shape[-1] == 4:
        rgba = Image.fromarray(values, "RGBA")
        color = (0, 0, 0, 255) if alpha_background == "Black" else (255, 255, 255, 255)
        background = Image.new("RGBA", rgba.size, color)
        background.alpha_composite(rgba)
        return background.convert("RGB")
    return Image.fromarray(values, "RGB")


def resize_image(image: Image.Image, longest_edge: int | None) -> Image.Image:
    if longest_edge is None:
        return image
    longest_edge = int(longest_edge)
    if longest_edge < 1:
        raise ValueError("Resize target must be at least 1 pixel.")
    width, height = image.size
    scale = longest_edge / max(width, height)
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def build_shared_palette(images: Sequence[Image.Image], colors: int, sample_limit: int = 65536) -> Image.Image:
    """Build a palette from all frames rather than the first frame alone."""
    if not images:
        raise ValueError("At least one image is required to build a palette.")
    colors = int(colors)
    if not 2 <= colors <= 256:
        raise ValueError("GIF color count must be between 2 and 256.")

    samples: list[np.ndarray] = []
    for image in images:
        width, height = image.size
        scale = min(1.0, 96.0 / max(width, height))
        thumb = image.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.Resampling.BILINEAR,
        )
        samples.append(np.asarray(thumb.convert("RGB"), dtype=np.uint8).reshape(-1, 3))

    all_samples = np.concatenate(samples, axis=0)
    if len(all_samples) > sample_limit:
        positions = np.linspace(0, len(all_samples) - 1, sample_limit, dtype=np.int64)
        all_samples = all_samples[positions]

    side = int(np.ceil(np.sqrt(len(all_samples))))
    padding = side * side - len(all_samples)
    if padding:
        all_samples = np.concatenate(
            [all_samples, np.repeat(all_samples[-1:], padding, axis=0)], axis=0
        )
    sample_image = Image.fromarray(all_samples.reshape(side, side, 3), "RGB")
    return sample_image.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)


def quantize_images(
    images: Sequence[Image.Image],
    colors: int,
    dither: str = "FLOYDSTEINBERG",
) -> list[Image.Image]:
    palette = build_shared_palette(images, colors)
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither == "FLOYDSTEINBERG" else Image.Dither.NONE
    return [image.quantize(palette=palette, dither=dither_mode) for image in images]


def save_gif(
    frames: Sequence[Image.Image],
    output_path: str | os.PathLike[str],
    *,
    fps: int,
    loop_count: int = 0,
    colors: int = 256,
    dither: str = "FLOYDSTEINBERG",
    optimize: bool = True,
    frame_duration_ms: int = 0,
    max_file_size_bytes: int = 0,
) -> GifMetadata:
    if not frames:
        raise ValueError("At least one frame is required for GIF export.")
    fps = int(fps)
    loop_count = int(loop_count)
    if not 1 <= fps <= 60:
        raise ValueError("FPS must be between 1 and 60.")
    if not 0 <= loop_count <= 9999:
        raise ValueError("Loop count must be between 0 and 9999.")
    if dither not in ("FLOYDSTEINBERG", "NONE"):
        raise ValueError(f"Unsupported dither mode: {dither}")

    duration_ms = int(frame_duration_ms)
    if duration_ms < 0:
        raise ValueError("frame_duration_ms cannot be negative.")
    if duration_ms == 0:
        duration_ms = max(10, round(1000 / fps))
    # GIF stores delays in centiseconds. Match Pillow's actual file timing.
    duration_ms = max(10, (int(duration_ms) // 10) * 10)
    max_file_size_bytes = int(max_file_size_bytes)
    if max_file_size_bytes < 0:
        raise ValueError("max_file_size_bytes cannot be negative.")

    converted = quantize_images(frames, colors, dither)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=".h3gif-", suffix=".gif", dir=target.parent
    )
    os.close(file_descriptor)
    temporary = Path(temporary_name)
    try:
        converted[0].save(
            temporary,
            format="GIF",
            save_all=True,
            append_images=converted[1:],
            duration=duration_ms,
            loop=loop_count,
            optimize=bool(optimize),
            disposal=2,
        )
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()

    with Image.open(target) as gif:
        frame_count = int(getattr(gif, "n_frames", 1))
        width, height = gif.size
        gif.seek(0)
        actual_duration_ms = int(gif.info.get("duration", duration_ms))
    if frame_count < 1:
        raise ValueError("GIF encoder produced no frames.")
    file_size_bytes = target.stat().st_size
    if max_file_size_bytes and file_size_bytes > max_file_size_bytes:
        target.unlink(missing_ok=True)
        raise ValueError(
            f"GIF is {file_size_bytes / 1024 / 1024:.2f} MiB, above the configured "
            f"{max_file_size_bytes / 1024 / 1024:.2f} MiB limit. Reduce resize_edge, "
            "colors or frame count."
        )

    return GifMetadata(
        path=str(target),
        frame_count=frame_count,
        width=int(width),
        height=int(height),
        file_size_bytes=file_size_bytes,
        fps=max(1, round(1000 / actual_duration_ms)),
        frame_duration_ms=actual_duration_ms,
        effective_fps=round(1000 / actual_duration_ms, 3),
    )
