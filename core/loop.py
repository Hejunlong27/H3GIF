"""Endpoint-loop analysis and optional transition generation."""

from __future__ import annotations

from dataclasses import dataclass

import torch

from .animation import build_frame_indices


@dataclass(frozen=True)
class LoopAnalysis:
    similarity: float
    endpoint_difference: float
    recommendation: str


def _downsample(frame: torch.Tensor, max_dimension: int = 64) -> torch.Tensor:
    height, width = int(frame.shape[0]), int(frame.shape[1])
    step = max(1, (max(height, width) + max_dimension - 1) // max_dimension)
    sampled = frame[::step, ::step, :]
    if int(sampled.shape[-1]) >= 3:
        sampled = sampled[..., :3]
    return sampled.to(dtype=torch.float32)


def analyze_loop(frames: torch.Tensor, difference_threshold: float = 0.02) -> LoopAnalysis:
    if not isinstance(frames, torch.Tensor) or frames.ndim != 4 or int(frames.shape[0]) < 1:
        raise ValueError("H3GIF loop analysis expects a non-empty IMAGE batch [N,H,W,C].")
    threshold = float(difference_threshold)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Endpoint difference threshold must be between 0 and 1.")

    if int(frames.shape[0]) == 1:
        difference = 0.0
    else:
        first = _downsample(frames[0])
        last = _downsample(frames[-1])
        difference = float((first - last).abs().mean().clamp(0.0, 1.0))
    similarity = max(0.0, min(1.0, 1.0 - difference))

    if difference <= threshold:
        recommendation = "Forward loop is likely compatible; verify motion continuity visually."
    else:
        recommendation = "Endpoint difference is high; consider Ping-pong or a short crossfade."

    return LoopAnalysis(similarity, difference, recommendation)


def pingpong_frames(frames: torch.Tensor) -> torch.Tensor:
    indices = build_frame_indices(int(frames.shape[0]), playback_mode="Ping-pong")
    index_tensor = torch.tensor(indices, dtype=torch.long, device=frames.device)
    return frames.index_select(0, index_tensor)


def crossfade_loop(frames: torch.Tensor, transition_frames: int = 4) -> torch.Tensor:
    """Append last-to-first blends so the loop returns near its first frame."""
    count = int(frames.shape[0])
    transition_frames = int(transition_frames)
    if count < 2 or transition_frames <= 0:
        return frames
    if transition_frames > 120:
        raise ValueError("transition_frames cannot exceed 120.")

    first = frames[0]
    last = frames[-1]
    transitions = []
    for step in range(1, transition_frames + 1):
        alpha = step / (transition_frames + 1)
        blended = torch.lerp(last, first, alpha).unsqueeze(0)
        transitions.append(blended)
    return torch.cat([frames, torch.cat(transitions, dim=0)], dim=0)
