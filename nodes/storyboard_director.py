"""ComfyUI node that prepares H3-Image storyboard prompts and grid metadata."""

from __future__ import annotations

import json

from ..core.director import build_storyboard_direction


class H3GIFStoryboardDirector:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_description": ("STRING", {
                    "default": "A short cinematic scene with one clearly readable character.",
                    "multiline": True,
                }),
                "panel_actions": ("STRING", {
                    "default": "1. The character notices something off-screen.\n2. The character turns toward it.\n3. The character reacts with surprise.\n4. The character moves toward the source of the reaction.",
                    "multiline": True,
                }),
                "rows": ("INT", {"default": 2, "min": 1, "max": 8, "step": 1}),
                "columns": ("INT", {"default": 2, "min": 1, "max": 8, "step": 1}),
                "gutter_pixels": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                "character_lock": ("STRING", {
                    "default": "same character design, same face, same hairstyle, same outfit, consistent proportions",
                    "multiline": True,
                }),
                "style_prompt": ("STRING", {
                    "default": "cinematic 3D animated film still, consistent lighting and color palette, high detail",
                    "multiline": True,
                }),
                "extra_instructions": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "positive_prompt",
        "rows",
        "columns",
        "gutter_pixels",
        "panel_count",
        "director_info",
    )
    FUNCTION = "compose"
    CATEGORY = "H3GIF"

    def compose(
        self,
        scene_description,
        panel_actions,
        rows,
        columns,
        gutter_pixels,
        character_lock,
        style_prompt,
        extra_instructions,
    ):
        direction = build_storyboard_direction(
            scene_description=scene_description,
            panel_actions=panel_actions,
            rows=rows,
            columns=columns,
            gutter_pixels=gutter_pixels,
            character_lock=character_lock,
            style_prompt=style_prompt,
            extra_instructions=extra_instructions,
        )
        return (
            direction.positive_prompt,
            direction.rows,
            direction.columns,
            direction.gutter_pixels,
            direction.panel_count,
            json.dumps(direction.as_info(), ensure_ascii=False, separators=(",", ":")),
        )
