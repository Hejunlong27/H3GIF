from __future__ import annotations

import json
import os
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BASE = os.environ.get("H3GIF_SERVER", "http://127.0.0.1:8189")
ARTIFACTS = Path(os.environ.get("H3GIF_BENCH_OUTPUT", str(Path(__file__).resolve().parent)))
MANIFEST_PATH = ARTIFACTS / "batch50_manifest.json"
RESULTS_PATH = ARTIFACTS / "batch50_results.json"
SUMMARY_PATH = ARTIFACTS / "batch50_summary.json"
PROGRESS_PATH = ARTIFACTS / "batch50_progress.jsonl"

STYLES = [
    ("cinematic_3d", "cinematic high-end 3D animated feature film, soft global illumination, detailed materials, Pixar-like appeal"),
    ("anime_cel", "Japanese 2D anime, crisp cel shading, expressive linework, dramatic painted backgrounds"),
    ("ink_wash", "Chinese ink-wash animation, flowing brush texture, restrained color, poetic negative space"),
    ("claymation", "handmade claymation stop-motion, visible fingerprints and miniature set textures, tactile lighting"),
    ("watercolor", "soft watercolor children's storybook illustration, paper grain, delicate edges"),
    ("cyberpunk_comic", "high-contrast cyberpunk comic art, bold inking, neon color accents, dramatic perspective"),
    ("low_poly", "stylized low-poly 3D game art, clean geometric forms, vivid lighting"),
    ("oil_painting", "expressive oil painting, visible brushstrokes, rich chiaroscuro, cinematic composition"),
    ("paper_cut", "layered paper-cut collage animation, crafted paper edges, soft drop shadows"),
    ("film_noir", "black-and-white film noir, hard directional light, deep shadows, dramatic atmosphere"),
]

MOTIONS = [
    {
        "key": "street_walk",
        "scene": "A lone traveler walks across a rain-soaked city street at night, medium-wide full-body view.",
        "character_lock": "same young traveler, bright yellow raincoat, black umbrella, black boots, same face and proportions",
        "actions": [
            "steps off the curb into the crosswalk",
            "moves the left foot forward",
            "moves the right foot forward",
            "passes beneath a street lamp",
            "glances to the left",
            "glances to the right",
            "tilts the umbrella against the rain",
            "steps onto the opposite curb",
            "turns back toward the street",
        ],
    },
    {
        "key": "sprint",
        "scene": "An athlete sprints along an empty waterfront track at sunrise, side three-quarter view, full body visible.",
        "character_lock": "same athlete, red track suit, white running shoes, short dark hair, same face and proportions",
        "actions": [
            "explodes forward from a crouched start",
            "drives the left knee upward",
            "reaches forward with the right arm",
            "lands the left foot at full stride",
            "drives the right knee upward",
            "reaches forward with the left arm",
            "accelerates through a strong stride",
            "leans into the final ten meters",
            "crosses the finish line and slows down",
        ],
    },
    {
        "key": "partner_dance",
        "scene": "Two young adults perform one continuous energetic partner dance in a neon city crosswalk at night, locked medium-wide view, both full bodies visible.",
        "character_lock": "Character A: short black hair, red rain jacket, black skirt, white sneakers. Character B: curly brown hair, blue bomber jacket, gray pants, black shoes. Same faces, outfits and proportions in every panel.",
        "actions": [
            "face each other and clap the first beat",
            "step toward each other with raised hands",
            "spin apart while keeping eye contact",
            "reconnect with a shoulder-to-shoulder bounce",
            "the man spins the woman under his arm",
            "the woman kicks one leg forward and laughs",
            "the man moonwalks backward",
            "they jump into the air together",
            "land in a matching final dance pose",
        ],
    },
    {
        "key": "martial_arts",
        "scene": "Two martial artists perform a fast but non-graphic sparring exchange in a traditional training hall, locked medium-wide view, both full bodies visible.",
        "character_lock": "Fighter A wears a white gi with a red belt. Fighter B wears a dark blue gi with a black belt. Keep the same two fighters, faces, uniforms and proportions in every panel.",
        "actions": [
            "bow to each other in ready stance",
            "Fighter A steps in with a straight punch",
            "Fighter B blocks and counters",
            "Fighter A pivots away from the counter",
            "Fighter B throws a high kick",
            "Fighter A ducks under the kick",
            "Fighter A sweeps low while Fighter B jumps",
            "they exchange a fast close-range block",
            "both step back and freeze in guarded poses",
        ],
    },
    {
        "key": "spin_jump",
        "scene": "A contemporary dancer performs a rapid continuous spin-and-jump sequence in a bright rehearsal studio, locked medium-wide view, full body visible.",
        "character_lock": "same dancer, silver jacket, black pants, white dance shoes, short hair, same face and proportions",
        "actions": [
            "starts in a low preparation pose",
            "extends one arm and begins to turn",
            "spins through the first quarter turn",
            "accelerates through the half turn",
            "lifts one leg into a spin",
            "plants the foot and launches upward",
            "arches through the airborne jump",
            "lands in a deep controlled crouch",
            "rises into a final balanced pose",
        ],
    },
]

FPS_VALUES = [4, 6, 8, 10, 12]


def get_json(path: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=timeout) as response:
        return json.loads(response.read())


def post_json(path: str, payload: dict, timeout: int = 60) -> dict:
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def build_variants() -> list[dict]:
    variants = []
    for index in range(50):
        style_key, style_prompt = STYLES[index % len(STYLES)]
        motion = MOTIONS[(index // len(STYLES)) % len(MOTIONS)]
        fps = FPS_VALUES[index % len(FPS_VALUES)]
        number = index + 1
        slug = f"v{number:02d}_{style_key}_{motion['key']}_{fps}fps"
        variants.append({
            "number": number,
            "id": f"{number:02d}",
            "slug": slug,
            "style_key": style_key,
            "style_prompt": style_prompt,
            "motion_key": motion["key"],
            "rows": 3,
            "columns": 3,
            "panel_count": 9,
            "gutter_pixels": 6,
            "fps": fps,
            "seed": 20261112 + index,
            "scene": motion["scene"],
            "character_lock": motion["character_lock"],
            "actions": motion["actions"],
        })
    return variants


def build_prompt(variant: dict) -> dict:
    actions = "\n".join(f"{i + 1}. {action}" for i, action in enumerate(variant["actions"]))
    prefix = f"H3GIF/batch50/{variant['slug']}"
    return {
        "1": {"class_type": "H3GIFStoryboardDirector", "inputs": {
            "scene_description": variant["scene"],
            "panel_actions": actions,
            "rows": variant["rows"],
            "columns": variant["columns"],
            "gutter_pixels": variant["gutter_pixels"],
            "character_lock": variant["character_lock"],
            "style_prompt": variant["style_prompt"],
            "extra_instructions": (
                "Strict equal 3x3 contact sheet, exactly 9 panels, one sequential action phase per panel, "
                "left-to-right then top-to-bottom, uniform thin dark gutters, full bodies visible where applicable, "
                "no text, no captions, no speech bubbles, no merged panels, no wardrobe changes."
            ),
        }},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_image_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_image_vae_fp16.safetensors"}},
        "5": {"class_type": "ResolutionSelector", "inputs": {"aspect_ratio": "1:1 (Square)", "megapixels": 4, "multiple": 32}},
        "6": {"class_type": "MiniMaxH3ImageConditioning", "inputs": {"clip": ["3", 0], "vae": ["4", 0], "prompt": ["1", 0], "width": ["5", 0], "height": ["5", 1]}},
        "7": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["6", 0]}},
        "8": {"class_type": "RandomNoise", "inputs": {"noise_seed": variant["seed"]}},
        "9": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "10": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.9675236940383911, 0.8875485062599182, 0.75, 0.5327739119529724, 0.23200887441635132, 0.0"}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["8", 0], "guider": ["7", 0], "sampler": ["9", 0], "sigmas": ["10", 0], "latent_image": ["6", 1]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["4", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": f"{prefix}/source/storyboard"}},
        "14": {"class_type": "StoryboardGridSplit", "inputs": {
            "image": ["12", 0], "resolution_preset": "Custom grid", "columns": ["1", 2], "rows": ["1", 1],
            "gap_x": ["1", 3], "gap_y": ["1", 3], "offset_x": 0, "offset_y": 0,
            "reading_order": "Row-major", "reverse": False, "margin_left": 0, "margin_right": 0,
            "margin_top": 0, "margin_bottom": 0, "tile_width": 0, "tile_height": 0,
            "frame_range": "", "skip_frames": "", "skip_blank_frames": False, "blank_threshold": 0.005,
        }},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": f"{prefix}/frames/frame"}},
        "16": {"class_type": "StoryboardAnimation", "inputs": {"frames": ["14", 0], "playback_mode": "Ping-pong", "hold_each_frame": 1, "frame_range": "", "skip_frames": "", "custom_order": "", "hold_first": 1, "hold_last": 1}},
        "17": {"class_type": "StoryboardLoopOptimizer", "inputs": {"frames": ["16", 0], "mode": "Analyze only", "transition_frames": 4, "endpoint_difference_threshold": 0.02}},
        "18": {"class_type": "StoryboardGIFExport", "inputs": {"frames": ["17", 0], "fps": variant["fps"], "loop_count": 0, "resize": "Original", "dither": "FLOYDSTEINBERG", "optimize": True, "filename_prefix": f"{prefix}/animation", "frame_duration_ms": 0, "colors": 256, "alpha_background": "White", "resize_edge": 0, "max_file_size_mb": 0.0}},
    }


def extract_outputs(history_item: dict) -> dict:
    outputs = history_item.get("outputs", {})
    source_images = outputs.get("13", {}).get("images", [])
    split_images = outputs.get("15", {}).get("images", [])
    gif_text = outputs.get("18", {}).get("text", [])
    gif_path = None
    for line in gif_text:
        if line.startswith("Saved GIF: "):
            gif_path = line.removeprefix("Saved GIF: ")
    return {
        "source_images": source_images,
        "split_frame_count": len(split_images),
        "gif_path": gif_path,
        "gif_text": gif_text,
    }


def wait_for_history(prompt_id: str, timeout_seconds: int = 600) -> dict:
    start = time.time()
    while time.time() - start < timeout_seconds:
        history = get_json(f"/history/{prompt_id}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(5)
    raise TimeoutError(f"Prompt {prompt_id} exceeded {timeout_seconds} seconds")


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    variants = build_variants()
    MANIFEST_PATH.write_text(json.dumps(variants, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    results = {}
    if RESULTS_PATH.exists():
        try:
            results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            results = {}

    def save_results() -> None:
        RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def progress(event: dict) -> None:
        event = {"timestamp": datetime.now().isoformat(timespec="seconds"), **event}
        with PROGRESS_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(json.dumps(event, ensure_ascii=False), flush=True)

    for variant in variants:
        variant_id = variant["id"]
        previous = results.get(variant_id)
        if previous and previous.get("status") == "success":
            print(f"SKIP {variant_id} {variant['slug']} (already successful)", flush=True)
            continue
        print(f"START {variant_id}/50 {variant['slug']}", flush=True)
        started_at = datetime.now().isoformat(timespec="seconds")
        start_time = time.time()
        record = {
            "id": variant_id,
            "slug": variant["slug"],
            "style": variant["style_key"],
            "motion": variant["motion_key"],
            "fps": variant["fps"],
            "seed": variant["seed"],
            "rows": variant["rows"],
            "columns": variant["columns"],
            "started_at": started_at,
            "status": "running",
        }
        try:
            prompt = build_prompt(variant)
            submit = post_json("/prompt", {"prompt": prompt, "client_id": f"h3gif-batch50-{variant_id}"})
            if submit.get("node_errors"):
                raise RuntimeError(f"node_errors: {submit['node_errors']}")
            prompt_id = submit["prompt_id"]
            record["prompt_id"] = prompt_id
            results[variant_id] = record
            save_results()
            history_item = wait_for_history(prompt_id)
            execution_status = history_item.get("status", {})
            if execution_status.get("status_str") != "success":
                raise RuntimeError(f"execution status: {execution_status}")
            record.update(extract_outputs(history_item))
            record["wall_seconds"] = round(time.time() - start_time, 3)
            record["completed_at"] = datetime.now().isoformat(timespec="seconds")
            record["status"] = "success"
            results[variant_id] = record
            save_results()
            progress({"event": "success", "id": variant_id, "slug": variant["slug"], "seconds": record["wall_seconds"], "gif": record.get("gif_path")})
        except Exception as exc:
            record["wall_seconds"] = round(time.time() - start_time, 3)
            record["completed_at"] = datetime.now().isoformat(timespec="seconds")
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            results[variant_id] = record
            save_results()
            progress({"event": "error", "id": variant_id, "slug": variant["slug"], "error": record["error"]})
        time.sleep(1)

    successes = [item for item in results.values() if item.get("status") == "success"]
    failures = [item for item in results.values() if item.get("status") == "error"]
    by_style = defaultdict(lambda: Counter())
    by_motion = defaultdict(lambda: Counter())
    by_fps = defaultdict(lambda: Counter())
    for item in results.values():
        bucket = "success" if item.get("status") == "success" else "error"
        by_style[item.get("style", "unknown")][bucket] += 1
        by_motion[item.get("motion", "unknown")][bucket] += 1
        by_fps[str(item.get("fps", "unknown"))][bucket] += 1
    summary = {
        "total": len(results),
        "success": len(successes),
        "error": len(failures),
        "average_wall_seconds": round(sum(float(item.get("wall_seconds", 0)) for item in successes) / max(len(successes), 1), 3),
        "by_style": {key: dict(value) for key, value in sorted(by_style.items())},
        "by_motion": {key: dict(value) for key, value in sorted(by_motion.items())},
        "by_fps": {key: dict(value) for key, value in sorted(by_fps.items(), key=lambda pair: int(pair[0]) if pair[0].isdigit() else 999)},
        "errors": [{"id": item["id"], "slug": item["slug"], "error": item.get("error")} for item in failures],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BATCH_SUMMARY", json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
