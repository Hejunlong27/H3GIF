"""ComfyUI node for deterministic storyboard animation sequencing."""

from __future__ import annotations

import torch

from ..core.animation import PLAYBACK_MODES, build_frame_indices


class StoryboardAnimation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "playback_mode": (list(PLAYBACK_MODES), {"default": "Forward"}),
                "hold_each_frame": ("INT", {"default": 1, "min": 1, "max": 120, "step": 1}),
                "frame_range": ("STRING", {"default": "", "multiline": False}),
                "skip_frames": ("STRING", {"default": "", "multiline": False}),
                "custom_order": ("STRING", {"default": "", "multiline": False}),
                "hold_first": ("INT", {"default": 1, "min": 1, "max": 120, "step": 1}),
                "hold_last": ("INT", {"default": 1, "min": 1, "max": 120, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("animation_frames", "output_frame_count")
    FUNCTION = "build"
    CATEGORY = "H3GIF"

    def build(
        self,
        frames,
        playback_mode,
        hold_each_frame,
        frame_range="",
        skip_frames="",
        custom_order="",
        hold_first=1,
        hold_last=1,
    ):
        if not isinstance(frames, torch.Tensor) or frames.ndim != 4:
            raise ValueError("H3GIF: expected an IMAGE batch with shape [N,H,W,C].")
        if int(frames.shape[0]) < 1:
            raise ValueError("H3GIF: at least one frame is required.")

        indices = build_frame_indices(
            int(frames.shape[0]),
            playback_mode=playback_mode,
            hold_each_frame=hold_each_frame,
            frame_range=frame_range,
            skip_frames=skip_frames,
            custom_order=custom_order,
            hold_first=hold_first,
            hold_last=hold_last,
        )
        index_tensor = torch.tensor(indices, dtype=torch.long, device=frames.device)
        sequence = frames.index_select(0, index_tensor)
        return (sequence, int(sequence.shape[0]))
