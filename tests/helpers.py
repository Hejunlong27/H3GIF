"""Test helpers for loading the plugin without a running ComfyUI server."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure_folder_paths() -> types.ModuleType:
    if "folder_paths" not in sys.modules:
        module = types.ModuleType("folder_paths")
        module.get_output_directory = lambda: str(ROOT / "test-output")
        sys.modules["folder_paths"] = module
    return sys.modules["folder_paths"]


def load_package():
    ensure_folder_paths()
    if str(ROOT.parent) not in sys.path:
        sys.path.insert(0, str(ROOT.parent))
    module_name = "H3GIF"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(
        module_name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the H3GIF package.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
