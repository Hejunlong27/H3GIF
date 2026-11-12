"""Grid detection, layout calculation and IMAGE batch splitting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

from .selection import apply_selection

READING_ORDERS = ("Row-major", "Column-major", "Serpentine")


@dataclass(frozen=True)
class GridDetection:
    rows: int
    columns: int
    confidence: float
    detected: bool
    row_boundaries: tuple[int, ...]
    column_boundaries: tuple[int, ...]
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "confidence": round(float(self.confidence), 4),
            "detected": bool(self.detected),
            "row_boundaries": list(self.row_boundaries),
            "column_boundaries": list(self.column_boundaries),
            "message": self.message,
        }


@dataclass(frozen=True)
class TileBounds:
    row: int
    column: int
    x0: int
    y0: int
    x1: int
    y1: int

    def as_dict(self) -> dict[str, int]:
        return {
            "row": self.row + 1,
            "column": self.column + 1,
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
        }


@dataclass(frozen=True)
class GridLayout:
    rows: int
    columns: int
    tile_width: int
    tile_height: int
    bounds: tuple[TileBounds, ...]

    @property
    def frame_count(self) -> int:
        return len(self.bounds)


def validate_image_tensor(image: torch.Tensor) -> tuple[int, int, int, int]:
    if not isinstance(image, torch.Tensor):
        raise ValueError("Expected a ComfyUI IMAGE tensor with shape [B,H,W,C].")
    if image.ndim != 4:
        raise ValueError("Expected a ComfyUI IMAGE tensor with shape [B,H,W,C].")
    batch, height, width, channels = (int(value) for value in image.shape)
    if batch < 1:
        raise ValueError("The IMAGE batch is empty.")
    if height < 1 or width < 1:
        raise ValueError("Image width and height must be at least 1 pixel.")
    if channels < 1:
        raise ValueError("The IMAGE tensor must contain at least one channel.")
    return batch, height, width, channels


def _order_positions(rows: int, columns: int, order: str) -> list[tuple[int, int]]:
    if order not in READING_ORDERS:
        raise ValueError(f"Unsupported reading order: {order}")

    positions: list[tuple[int, int]] = []
    if order == "Column-major":
        for column in range(columns):
            for row in range(rows):
                positions.append((row, column))
    elif order == "Serpentine":
        for row in range(rows):
            row_columns = range(columns) if row % 2 == 0 else range(columns - 1, -1, -1)
            positions.extend((row, column) for column in row_columns)
    else:
        for row in range(rows):
            positions.extend((row, column) for column in range(columns))
    return positions


def plan_grid(
    image: torch.Tensor,
    columns: int,
    rows: int,
    gap_x: int = 0,
    gap_y: int = 0,
    offset_x: int = 0,
    offset_y: int = 0,
    order: str = "Row-major",
    reverse: bool = False,
    margin_left: int = 0,
    margin_right: int = 0,
    margin_top: int = 0,
    margin_bottom: int = 0,
    tile_width: int = 0,
    tile_height: int = 0,
    frame_range: str = "",
    skip_frames: str = "",
) -> GridLayout:
    """Validate grid settings and calculate all selected tile bounds."""
    _, height, width, _ = validate_image_tensor(image)
    columns, rows = int(columns), int(rows)
    gap_x, gap_y = int(gap_x), int(gap_y)
    offset_x, offset_y = int(offset_x), int(offset_y)
    margin_left, margin_right = int(margin_left), int(margin_right)
    margin_top, margin_bottom = int(margin_top), int(margin_bottom)
    tile_width, tile_height = int(tile_width), int(tile_height)

    if columns < 1 or rows < 1:
        raise ValueError("Rows and columns must be at least 1.")
    if min(gap_x, gap_y, offset_x, offset_y, margin_left, margin_right, margin_top, margin_bottom) < 0:
        raise ValueError("Gaps, offsets and margins cannot be negative.")
    if tile_width < 0 or tile_height < 0:
        raise ValueError("Custom tile width and height cannot be negative.")
    if (tile_width == 0) != (tile_height == 0):
        raise ValueError("Set both custom tile width and height, or leave both at 0 for automatic sizing.")

    start_x = margin_left + offset_x
    start_y = margin_top + offset_y
    available_w = width - start_x - margin_right
    available_h = height - start_y - margin_bottom
    if available_w < 1 or available_h < 1:
        raise ValueError("Margins and offsets leave no usable image area.")

    if tile_width == 0:
        usable_w = available_w - (columns - 1) * gap_x
        usable_h = available_h - (rows - 1) * gap_y
        tile_width = usable_w // columns
        tile_height = usable_h // rows
    if tile_width < 1 or tile_height < 1:
        raise ValueError("Grid settings leave no usable tile area. Check rows, columns, gaps, margins and offsets.")

    required_w = columns * tile_width + (columns - 1) * gap_x
    required_h = rows * tile_height + (rows - 1) * gap_y
    if required_w > available_w or required_h > available_h:
        raise ValueError(
            "The configured grid exceeds the usable image area. "
            "Reduce custom tile size, gaps, margins or offsets."
        )

    positions = _order_positions(rows, columns, order)
    if reverse:
        positions.reverse()
    positions = apply_selection(
        positions,
        frame_range=frame_range,
        skip_frames=skip_frames,
    )

    bounds = tuple(
        TileBounds(
            row=row,
            column=column,
            x0=start_x + column * (tile_width + gap_x),
            y0=start_y + row * (tile_height + gap_y),
            x1=start_x + column * (tile_width + gap_x) + tile_width,
            y1=start_y + row * (tile_height + gap_y) + tile_height,
        )
        for row, column in positions
    )
    return GridLayout(rows, columns, tile_width, tile_height, bounds)


def _is_blank_tile(tile: torch.Tensor, threshold: float) -> bool:
    values = tile.detach().to(dtype=torch.float32, device="cpu")
    if values.shape[-1] >= 3:
        values = values[..., :3].mean(dim=-1)
    else:
        values = values[..., 0]
    return bool(float(values.max() - values.min()) <= threshold)


def split_grid_detailed(
    image: torch.Tensor,
    columns: int,
    rows: int,
    gap_x: int = 0,
    gap_y: int = 0,
    offset_x: int = 0,
    offset_y: int = 0,
    order: str = "Row-major",
    reverse: bool = False,
    margin_left: int = 0,
    margin_right: int = 0,
    margin_top: int = 0,
    margin_bottom: int = 0,
    tile_width: int = 0,
    tile_height: int = 0,
    frame_range: str = "",
    skip_frames: str = "",
    skip_blank_frames: bool = False,
    blank_threshold: float = 0.005,
) -> tuple[torch.Tensor, int, int, GridLayout]:
    """Split an IMAGE batch and return the calculated layout metadata."""
    layout = plan_grid(
        image,
        columns=columns,
        rows=rows,
        gap_x=gap_x,
        gap_y=gap_y,
        offset_x=offset_x,
        offset_y=offset_y,
        order=order,
        reverse=reverse,
        margin_left=margin_left,
        margin_right=margin_right,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        tile_width=tile_width,
        tile_height=tile_height,
        frame_range=frame_range,
        skip_frames=skip_frames,
    )
    batch = int(image.shape[0])
    threshold = float(blank_threshold)
    if threshold < 0:
        raise ValueError("blank_threshold cannot be negative.")

    tiles: list[torch.Tensor] = []
    for batch_index in range(batch):
        for bounds in layout.bounds:
            tile = image[batch_index, bounds.y0:bounds.y1, bounds.x0:bounds.x1, :]
            if skip_blank_frames and _is_blank_tile(tile, threshold):
                continue
            tiles.append(tile)

    if not tiles:
        raise ValueError("No frames remain after blank-frame filtering.")
    return torch.stack(tiles, dim=0), layout.tile_width, layout.tile_height, layout


def split_grid(
    image: torch.Tensor,
    columns: int,
    rows: int,
    gap_x: int = 0,
    gap_y: int = 0,
    offset_x: int = 0,
    offset_y: int = 0,
    order: str = "Row-major",
    reverse: bool = False,
    margin_left: int = 0,
    margin_right: int = 0,
    margin_top: int = 0,
    margin_bottom: int = 0,
    tile_width: int = 0,
    tile_height: int = 0,
    frame_range: str = "",
    skip_frames: str = "",
    skip_blank_frames: bool = False,
    blank_threshold: float = 0.005,
) -> tuple[torch.Tensor, int, int]:
    """Backward-compatible splitting API returning frames, width and height."""
    frames, width, height, _ = split_grid_detailed(
        image,
        columns,
        rows,
        gap_x,
        gap_y,
        offset_x,
        offset_y,
        order,
        reverse,
        margin_left,
        margin_right,
        margin_top,
        margin_bottom,
        tile_width,
        tile_height,
        frame_range,
        skip_frames,
        skip_blank_frames,
        blank_threshold,
    )
    return frames, width, height


def _gray_array(image: torch.Tensor, max_dimension: int = 768) -> np.ndarray:
    validate_image_tensor(image)
    values = image[0].detach().to(dtype=torch.float32, device="cpu").numpy()
    values = np.nan_to_num(values, nan=0.0, posinf=1.0, neginf=0.0)
    values = np.clip(values, 0.0, 1.0)
    if values.shape[-1] >= 3:
        gray = values[..., :3].mean(axis=-1)
    else:
        gray = values[..., 0]
    step = max(1, int(np.ceil(max(gray.shape) / max_dimension)))
    return gray[::step, ::step]


def _candidate_score(profile: np.ndarray, divisions: int) -> float:
    if divisions <= 1 or profile.size < divisions * 2:
        return 0.0
    baseline = float(np.median(profile))
    high = float(np.percentile(profile, 95))
    scale = high - baseline
    if scale <= 1e-8:
        return 0.0

    radius = max(1, min(5, profile.size // max(divisions * 20, 1)))
    peaks: list[float] = []
    center = (profile.size + 1) / divisions
    for boundary_index in range(1, divisions):
        position = int(round(boundary_index * center)) - 1
        start = max(0, position - radius)
        end = min(profile.size, position + radius + 1)
        peaks.append(float(np.max(profile[start:end])))

    strengths = np.clip((np.asarray(peaks) - baseline) / scale, 0.0, 1.0)
    coverage = float(np.mean(strengths >= 0.35))
    return float(0.75 * np.mean(strengths) + 0.25 * coverage)


def _detect_axis(profile: np.ndarray, max_grid: int) -> tuple[int, float]:
    if profile.size == 0:
        return 1, 0.0
    scores = {divisions: _candidate_score(profile, divisions) for divisions in range(2, max_grid + 1)}
    best_score = max(scores.values(), default=0.0)
    if best_score <= 0.0:
        return 1, 0.0
    eligible = [divisions for divisions, score in scores.items() if score >= best_score * 0.94]
    return max(eligible), best_score


def _expected_boundaries(size: int, divisions: int) -> tuple[int, ...]:
    return tuple(int(round(index * size / divisions)) for index in range(divisions + 1))


def detect_grid(
    image: torch.Tensor,
    max_grid: int = 8,
    threshold: float = 0.55,
) -> GridDetection:
    """Detect a regular grid using grayscale projection peaks.

    The detector intentionally fails instead of guessing when separator evidence
    is weak. Callers should offer a manual rows/columns fallback.
    """
    _, height, width, _ = validate_image_tensor(image)
    max_grid = int(max_grid)
    if max_grid < 2 or max_grid > 16:
        raise ValueError("max_grid must be between 2 and 16.")
    threshold = float(threshold)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Detection threshold must be between 0 and 1.")

    gray = _gray_array(image)
    column_profile = np.abs(np.diff(gray, axis=1)).mean(axis=0) if gray.shape[1] > 1 else np.array([])
    row_profile = np.abs(np.diff(gray, axis=0)).mean(axis=1) if gray.shape[0] > 1 else np.array([])
    for profile in (column_profile, row_profile):
        if profile.size >= 3:
            profile[:] = np.convolve(profile, np.ones(3) / 3.0, mode="same")

    columns, column_score = _detect_axis(column_profile, max_grid)
    rows, row_score = _detect_axis(row_profile, max_grid)
    confidence = float(min(column_score, row_score)) if columns > 1 and rows > 1 else 0.0
    if columns > 1 and rows == 1:
        confidence = float(column_score * 0.75)
    elif rows > 1 and columns == 1:
        confidence = float(row_score * 0.75)

    detected = confidence >= threshold
    if detected:
        message = f"Detected a {rows}x{columns} grid with {confidence:.0%} confidence."
    else:
        message = "Automatic grid detection was inconclusive. Use manual rows and columns."

    return GridDetection(
        rows=rows,
        columns=columns,
        confidence=confidence,
        detected=detected,
        row_boundaries=_expected_boundaries(height, rows),
        column_boundaries=_expected_boundaries(width, columns),
        message=message,
    )
