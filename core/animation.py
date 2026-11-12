"""Animation sequencing independent of PyTorch."""

from __future__ import annotations

from .selection import apply_selection

PLAYBACK_MODES = ("Forward", "Reverse", "Ping-pong")


def _validate_hold(value: int, name: str) -> int:
    value = int(value)
    if value < 1:
        raise ValueError(f"{name} must be at least 1.")
    return value


def build_frame_indices(
    frame_count: int,
    playback_mode: str = "Forward",
    hold_each_frame: int = 1,
    frame_range: str = "",
    skip_frames: str = "",
    custom_order: str = "",
    hold_first: int = 1,
    hold_last: int = 1,
) -> list[int]:
    """Build the final frame-index sequence for the animation node."""
    if int(frame_count) < 1:
        raise ValueError("At least one source frame is required.")
    if playback_mode not in PLAYBACK_MODES:
        raise ValueError(f"Unsupported playback mode: {playback_mode}")

    hold_each_frame = _validate_hold(hold_each_frame, "hold_each_frame")
    hold_first = _validate_hold(hold_first, "hold_first")
    hold_last = _validate_hold(hold_last, "hold_last")

    ordered = apply_selection(
        range(int(frame_count)),
        frame_range=frame_range,
        skip_frames=skip_frames,
        custom_order=custom_order,
    )

    if playback_mode == "Reverse":
        ordered.reverse()
    elif playback_mode == "Ping-pong" and len(ordered) > 2:
        ordered = ordered + ordered[-2:0:-1]

    expanded = [index for index in ordered for _ in range(hold_each_frame)]
    if hold_first > 1:
        expanded = [expanded[0]] * (hold_first - 1) + expanded
    if hold_last > 1:
        expanded = expanded + [expanded[-1]] * (hold_last - 1)
    return expanded
