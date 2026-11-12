"""Safe GIF output-path construction for ComfyUI."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

DEFAULT_PREFIX = "H3GIF/animation"
_INVALID_PART = re.compile(r"[^A-Za-z0-9_-]+")


def sanitize_output_prefix(prefix: str | None) -> str:
    raw = str(prefix or "").replace("\\", "/").strip("/")
    parts: list[str] = []
    for part in raw.split("/"):
        if part in ("", ".", ".."):
            continue
        cleaned = _INVALID_PART.sub("_", part).strip("._-")
        if cleaned:
            parts.append(cleaned)
    return "/".join(parts) or DEFAULT_PREFIX


def build_output_path(output_directory: str | os.PathLike[str], prefix: str | None) -> Path:
    output_root = Path(output_directory).resolve()
    safe_prefix = sanitize_output_prefix(prefix)
    relative = Path(*safe_prefix.split("/"))
    if relative.suffix.lower() == ".gif":
        relative = relative.with_suffix("")

    target_dir = (output_root / relative.parent).resolve()
    if target_dir != output_root and output_root not in target_dir.parents:
        raise ValueError("Output prefix resolves outside the ComfyUI output directory.")
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{relative.name}_{time.time_ns()}.gif"
