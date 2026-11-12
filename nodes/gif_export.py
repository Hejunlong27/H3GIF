"""ComfyUI node for deterministic, metadata-rich GIF export."""

from __future__ import annotations

import torch
import folder_paths

from ..core.gif import (
    resize_image,
    save_gif,
    tensor_to_rgb_image,
    validate_image_batch,
)
from ..core.paths import build_output_path

_RESIZE_OPTIONS = ("Original", "2048", "1024", "768", "512", "256", "原始尺寸")


class StoryboardGIFExport:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "fps": ("INT", {"default": 8, "min": 1, "max": 60, "step": 1}),
                "loop_count": ("INT", {"default": 0, "min": 0, "max": 9999, "step": 1}),
                "resize": (_RESIZE_OPTIONS, {"default": "Original"}),
                "dither": (["FLOYDSTEINBERG", "NONE"], {"default": "FLOYDSTEINBERG"}),
                "optimize": ("BOOLEAN", {"default": True}),
                "filename_prefix": ("STRING", {"default": "H3GIF/animation"}),
                "frame_duration_ms": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "colors": ("INT", {"default": 256, "min": 2, "max": 256, "step": 1}),
                "alpha_background": (["White", "Black"], {"default": "White"}),
                "resize_edge": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "max_file_size_mb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1024.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "INT", "INT", "FLOAT")
    RETURN_NAMES = (
        "saved_path",
        "frame_count",
        "width",
        "height",
        "file_size_bytes",
        "fps",
        "effective_fps",
    )
    FUNCTION = "export"
    CATEGORY = "H3GIF"
    OUTPUT_NODE = True

    def export(
        self,
        frames,
        fps,
        loop_count,
        resize,
        dither,
        optimize,
        filename_prefix,
        frame_duration_ms=0,
        colors=256,
        alpha_background="White",
        resize_edge=0,
        max_file_size_mb=0.0,
    ):
        validate_image_batch(frames)
        if alpha_background not in ("White", "Black"):
            raise ValueError("H3GIF: alpha_background must be White or Black.")

        target_edge = None
        resize_edge = int(resize_edge)
        if resize_edge > 0:
            target_edge = resize_edge
        elif resize not in ("Original", "原始尺寸"):
            try:
                target_edge = int(resize)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"H3GIF: unsupported resize value '{resize}'.") from exc
        max_file_size_mb = float(max_file_size_mb)
        if max_file_size_mb < 0:
            raise ValueError("H3GIF: max_file_size_mb cannot be negative.")

        try:
            output_path = build_output_path(folder_paths.get_output_directory(), filename_prefix)
        except OSError as exc:
            raise ValueError(f"H3GIF: cannot prepare the output directory: {exc}") from exc

        frames_cpu = frames.detach().to(device="cpu") if frames.device.type != "cpu" else frames
        images = []
        for frame in frames_cpu:
            image = tensor_to_rgb_image(frame, alpha_background=alpha_background)
            images.append(resize_image(image, target_edge))

        try:
            metadata = save_gif(
                images,
                output_path,
                fps=fps,
                loop_count=loop_count,
                colors=colors,
                dither=dither,
                optimize=optimize,
                frame_duration_ms=frame_duration_ms,
                max_file_size_bytes=round(max_file_size_mb * 1024 * 1024),
            )
        except (OSError, ValueError) as exc:
            raise ValueError(f"H3GIF: GIF export failed: {exc}") from exc

        text = [
            f"Saved GIF: {metadata.path}",
            f"Frames: {metadata.frame_count}",
            f"Size: {metadata.width}x{metadata.height}",
            f"File size: {metadata.file_size_bytes / 1024 / 1024:.2f} MiB",
            f"Effective FPS: {metadata.effective_fps:.3f}",
        ]
        return {
            "ui": {"text": text},
            "result": (
                metadata.path,
                metadata.frame_count,
                metadata.width,
                metadata.height,
                metadata.file_size_bytes,
                metadata.fps,
                metadata.effective_fps,
            ),
        }
