"""ComfyUI node for automatic or manual storyboard grid splitting."""

from __future__ import annotations

import json

from ..core.grid import detect_grid, split_grid_detailed, validate_image_tensor

_RESOLUTION_PRESETS = (
    "Auto detect",
    "2048 (2x2)",
    "1024 (4x4)",
    "512 (8x8)",
    "Custom grid",
)


class StoryboardGridSplit:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution_preset": (_RESOLUTION_PRESETS, {"default": "Auto detect"}),
                "columns": ("INT", {"default": 4, "min": 1, "max": 64, "step": 1}),
                "rows": ("INT", {"default": 4, "min": 1, "max": 64, "step": 1}),
                "gap_x": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "gap_y": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1}),
                "offset_x": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "offset_y": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "reading_order": (["Row-major", "Column-major", "Serpentine"],),
                "reverse": ("BOOLEAN", {"default": False}),
                "margin_left": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "margin_right": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "margin_top": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "margin_bottom": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "tile_width": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "tile_height": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 1}),
                "frame_range": ("STRING", {"default": "", "multiline": False}),
                "skip_frames": ("STRING", {"default": "", "multiline": False}),
                "skip_blank_frames": ("BOOLEAN", {"default": False}),
                "blank_threshold": ("FLOAT", {
                    "default": 0.005,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "INT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = (
        "frames",
        "frame_count",
        "tile_width",
        "tile_height",
        "detected_rows",
        "detected_columns",
        "detection_confidence",
        "detection_success",
        "grid_info",
    )
    FUNCTION = "split"
    CATEGORY = "H3GIF"

    @staticmethod
    def _preset_grid(width, height, target, gap_x, gap_y, margin_left, margin_right, margin_top, margin_bottom, offset_x, offset_y):
        available_w = width - margin_left - margin_right - offset_x
        available_h = height - margin_top - margin_bottom - offset_y
        if available_w < 1 or available_h < 1:
            raise ValueError("Margins and offsets leave no usable image area.")
        columns = max(1, round((available_w + gap_x) / (target + gap_x)))
        rows = max(1, round((available_h + gap_y) / (target + gap_y)))
        return columns, rows

    def split(
        self,
        image,
        resolution_preset,
        columns,
        rows,
        gap_x,
        gap_y,
        offset_x,
        offset_y,
        reading_order,
        reverse,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        tile_width=0,
        tile_height=0,
        frame_range="",
        skip_frames="",
        skip_blank_frames=False,
        blank_threshold=0.005,
    ):
        validate_image_tensor(image)
        detection = None
        mode = "auto" if resolution_preset == "Auto detect" else "manual"

        if mode == "auto":
            detection = detect_grid(image)
            if not detection.detected:
                height, width = int(image.shape[1]), int(image.shape[2])
                raise ValueError(
                    "H3GIF: automatic grid detection was inconclusive "
                    f"(image {width}x{height}, confidence {detection.confidence:.0%}). "
                    "If this is one single image, select 'Custom grid' and set rows=1, columns=1. "
                    "If you need an animation, the input must be a storyboard/contact sheet containing "
                    "multiple sequential panels; enter its actual rows and columns in 'Custom grid'."
                )
            columns, rows = detection.columns, detection.rows
        elif resolution_preset != "Custom grid":
            target = int(str(resolution_preset).split()[0])
            height, width = int(image.shape[1]), int(image.shape[2])
            columns, rows = self._preset_grid(
                width,
                height,
                target,
                int(gap_x),
                int(gap_y),
                int(margin_left),
                int(margin_right),
                int(margin_top),
                int(margin_bottom),
                int(offset_x),
                int(offset_y),
            )

        frames, tile_w, tile_h, layout = split_grid_detailed(
            image,
            columns=columns,
            rows=rows,
            gap_x=gap_x,
            gap_y=gap_y,
            offset_x=offset_x,
            offset_y=offset_y,
            order=reading_order,
            reverse=reverse,
            margin_left=margin_left,
            margin_right=margin_right,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            tile_width=tile_width,
            tile_height=tile_height,
            frame_range=frame_range,
            skip_frames=skip_frames,
            skip_blank_frames=skip_blank_frames,
            blank_threshold=blank_threshold,
        )

        info = {
            "mode": mode,
            "source_width": int(image.shape[2]),
            "source_height": int(image.shape[1]),
            "rows": int(layout.rows),
            "columns": int(layout.columns),
            "tile_width": int(tile_w),
            "tile_height": int(tile_h),
            "selected_cell_count": int(layout.frame_count),
            "frame_count": int(frames.shape[0]),
            "blank_frames_skipped": bool(skip_blank_frames),
            "bounds": [bounds.as_dict() for bounds in layout.bounds],
            "detection": detection.as_dict() if detection is not None else None,
        }
        detected_rows = int(detection.rows) if detection is not None else int(layout.rows)
        detected_columns = int(detection.columns) if detection is not None else int(layout.columns)
        confidence = float(detection.confidence) if detection is not None else 0.0
        success = bool(detection.detected) if detection is not None else False

        return (
            frames,
            int(frames.shape[0]),
            int(tile_w),
            int(tile_h),
            detected_rows,
            detected_columns,
            confidence,
            success,
            json.dumps(info, ensure_ascii=False, separators=(",", ":")),
        )
