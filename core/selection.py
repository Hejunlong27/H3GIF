"""Parsing and application of user-facing frame selectors."""

from __future__ import annotations

import re
from collections.abc import Iterable

_SELECTOR_RE = re.compile(r"^\s*(\d+)(?:\s*-\s*(\d+))?\s*$")


def parse_selector(spec: str | None, count: int, *, allow_duplicates: bool = False) -> list[int]:
    """Parse a 1-based selector such as ``1,3,5-8`` into 0-based indices.

    Empty input selects every available item. Descending ranges are supported.
    """
    if count < 0:
        raise ValueError("Frame count cannot be negative.")
    if not spec or not str(spec).strip():
        return list(range(count))

    result: list[int] = []
    for token in str(spec).split(","):
        token = token.strip()
        if not token:
            continue
        match = _SELECTOR_RE.fullmatch(token)
        if match is None:
            raise ValueError(
                f"Invalid frame selector '{token}'. Use values like 1,3,5-8."
            )
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start < 1 or end < 1 or start > count or end > count:
            raise ValueError(
                f"Frame selector '{token}' is outside the valid range 1-{count}."
            )
        step = 1 if end >= start else -1
        result.extend(number - 1 for number in range(start, end + step, step))

    if not result:
        raise ValueError("Frame selector did not select any frames.")
    if not allow_duplicates:
        result = list(dict.fromkeys(result))
    return result


def apply_selection(
    indices: Iterable[int],
    frame_range: str | None = "",
    skip_frames: str | None = "",
    custom_order: str | None = "",
) -> list[int]:
    """Apply range, skip and custom-order controls to an ordered index list.

    Range and skip selectors are interpreted against the original sequence using
    1-based positions. Custom order is applied last and may repeat indices.
    """
    tagged = list(enumerate(indices))
    source_count = len(tagged)

    # Range and skip selectors both refer to the original ordered sequence.
    if frame_range and str(frame_range).strip():
        allowed = set(parse_selector(frame_range, source_count))
        tagged = [(position, value) for position, value in tagged if position in allowed]
        if not tagged:
            raise ValueError("frame_range did not select any frames.")

    if skip_frames and str(skip_frames).strip():
        skipped = set(parse_selector(skip_frames, source_count))
        tagged = [(position, value) for position, value in tagged if position not in skipped]
        if not tagged:
            raise ValueError("All frames were removed by skip_frames.")

    selected = [value for _, value in tagged]
    if custom_order and str(custom_order).strip():
        positions = parse_selector(custom_order, len(selected), allow_duplicates=True)
        selected = [selected[position] for position in positions]

    return selected
