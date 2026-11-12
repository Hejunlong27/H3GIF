"""ComfyUI node for loop endpoint analysis and optional transitions."""

from __future__ import annotations

import torch

from ..core.loop import analyze_loop, crossfade_loop, pingpong_frames


class StoryboardLoopOptimizer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "mode": (["Analyze only", "Ping-pong if needed", "Crossfade if needed"],),
                "transition_frames": ("INT", {"default": 4, "min": 1, "max": 120, "step": 1}),
                "endpoint_difference_threshold": ("FLOAT", {
                    "default": 0.02,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "FLOAT", "STRING", "FLOAT")
    RETURN_NAMES = ("optimized_frames", "loop_similarity", "recommendation", "endpoint_difference")
    FUNCTION = "optimize"
    CATEGORY = "H3GIF"

    def optimize(self, frames, mode, transition_frames, endpoint_difference_threshold):
        if not isinstance(frames, torch.Tensor) or frames.ndim != 4:
            raise ValueError("H3GIF: loop optimizer expects an IMAGE batch [N,H,W,C].")
        if int(frames.shape[0]) < 1:
            raise ValueError("H3GIF: at least one frame is required.")

        analysis = analyze_loop(frames, endpoint_difference_threshold)
        optimized = frames
        if analysis.endpoint_difference > float(endpoint_difference_threshold):
            if mode == "Ping-pong if needed":
                optimized = pingpong_frames(frames)
            elif mode == "Crossfade if needed":
                optimized = crossfade_loop(frames, transition_frames)
        return (
            optimized,
            float(analysis.similarity),
            analysis.recommendation,
            float(analysis.endpoint_difference),
        )
