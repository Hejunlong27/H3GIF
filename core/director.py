"""Prompt and layout direction for H3-Image storyboard contact sheets."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

_NUMBER_PREFIX = re.compile(r"^\s*(?:panel\s*)?\d+\s*[\].:)-]?\s*", re.IGNORECASE)
_BULLET_PREFIX = re.compile(r"^\s*[-*•]\s*")


@dataclass(frozen=True)
class StoryboardDirection:
    positive_prompt: str
    rows: int
    columns: int
    gutter_pixels: int
    panel_count: int

    def as_info(self) -> dict[str, int | str]:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "panel_count": self.panel_count,
            "gutter_pixels": self.gutter_pixels,
            "layout": f"{self.rows}x{self.columns}",
            "reading_order": "left-to-right, top-to-bottom",
        }


def _clean_action(value: str) -> str:
    value = _BULLET_PREFIX.sub("", value.strip())
    value = _NUMBER_PREFIX.sub("", value).strip()
    return value


def parse_panel_actions(panel_actions: str, panel_count: int) -> list[str]:
    """Parse newline/semicolon separated actions and fill missing panels."""
    raw_parts: list[str] = []
    for line in str(panel_actions or "").splitlines():
        raw_parts.extend(line.split(";"))

    actions = [_clean_action(part) for part in raw_parts if _clean_action(part)]
    if len(actions) > panel_count:
        actions = actions[:panel_count]
    while len(actions) < panel_count:
        if not actions:
            actions.append("Continue the scene with a clear pose and expression change.")
        else:
            actions.append("Continue the same action naturally from the previous panel.")
    return actions


def build_storyboard_direction(
    scene_description: str,
    panel_actions: str,
    rows: int = 2,
    columns: int = 2,
    gutter_pixels: int = 8,
    character_lock: str = "same character design, same face, same hairstyle, same outfit, consistent proportions",
    style_prompt: str = "cinematic 3D animated film still, consistent lighting and color palette, high detail",
    extra_instructions: str = "",
) -> StoryboardDirection:
    scene_description = str(scene_description or "").strip()
    if not scene_description:
        raise ValueError("H3GIF Director: scene_description cannot be empty.")

    rows, columns, gutter_pixels = int(rows), int(columns), int(gutter_pixels)
    if not 1 <= rows <= 8:
        raise ValueError("H3GIF Director: rows must be between 1 and 8.")
    if not 1 <= columns <= 8:
        raise ValueError("H3GIF Director: columns must be between 1 and 8.")
    if not 0 <= gutter_pixels <= 64:
        raise ValueError("H3GIF Director: gutter_pixels must be between 0 and 64.")

    panel_count = rows * columns
    actions = parse_panel_actions(panel_actions, panel_count)
    character_lock = str(character_lock or "").strip()
    style_prompt = str(style_prompt or "").strip()
    extra_instructions = str(extra_instructions or "").strip()

    action_lines = "\n".join(f"{index + 1}. {action}" for index, action in enumerate(actions))
    layout_rule = (
        f"Create ONE single storyboard contact sheet containing exactly {rows} rows and "
        f"{columns} columns, for {panel_count} equal-sized panels in total. "
        "The image must be a finished contact sheet, not one full-frame scene and not multiple separate files."
    )
    gutter_rule = (
        f"Use straight, uniform, pure-black gutters approximately {gutter_pixels} pixels wide between panels. "
        "Keep the grid perfectly aligned and each panel fully visible."
        if gutter_pixels > 0
        else "Use clean straight boundaries between equally sized panels with no overlapping artwork."
    )

    prompt_parts = [
        layout_rule,
        "Panel order is left-to-right, top-to-bottom.",
        f"Scene: {scene_description}",
        f"Panel sequence:\n{action_lines}",
        f"Continuity lock: {character_lock}." if character_lock else "",
        f"Visual style: {style_prompt}." if style_prompt else "",
        f"Layout rules: {gutter_rule}",
        "Do not include captions, subtitles, letters, numbers, speech bubbles, watermarks, logos, panel labels or UI.",
        "Avoid merged panels, uneven grids, duplicated characters, inconsistent clothing, deformed anatomy and random collage layout.",
        extra_instructions,
    ]
    prompt = "\n\n".join(part for part in prompt_parts if part)
    return StoryboardDirection(prompt, rows, columns, gutter_pixels, panel_count)
