# H3GIF

**Turn one storyboard contact sheet into a looping GIF. No video model required.**

H3GIF is a model-agnostic ComfyUI custom-node extension. It splits a storyboard/contact sheet into frames, controls playback order, and exports an optimized GIF. It works with any node that produces a standard ComfyUI `IMAGE` tensor.

**Current status:** `v0.3.1-beta`. Core unit and node-interface tests pass. Browser-level workflow import against a live ComfyUI server is still part of release validation.

## Features

- A built-in H3-Image storyboard pipeline: scene/actions → exact grid prompt → H3-Image sampling → GIF.
- `H3GIF Storyboard Director` generates a strict R×C contact-sheet prompt and wires rows/columns/gutters into the splitter.
- Automatic regular-grid detection with explicit confidence and manual fallback.
- Manual 1x1 to 64x64 row/column configuration.
- 4096x4096 presets: 2x2, 4x4 and 8x8.
- Configurable gutters, four-side margins, offsets and exact tile size.
- Row-major, column-major, serpentine and reverse ordering.
- Frame range, skipped frames and blank-frame filtering.
- Forward, reverse and endpoint-safe ping-pong playback.
- Per-frame repeats plus independent first/last-frame holds.
- Endpoint loop analysis with optional Ping-pong or crossfade transition generation.
- GIF FPS or explicit frame duration, loop count, custom longest edge, palette size, dithering, alpha background and optional maximum file size.
- GIF output metadata: actual frame count, width, height, file size, requested FPS and effective GIF FPS.
- GIF timing is normalized to Pillow/GIF centisecond precision; `effective_fps` reports the rate actually stored in the file.
- One formal workflow only: `workflows/H3GIF_Complete.json`.
- Built-in SaveImage branch for previewing and saving every split frame as PNG.
- Visible Chinese instructions inside the workflow.
- No external API, telemetry, uploads or API-key handling.

## Requirements

- A ComfyUI build that supports standard custom-node `NODE_CLASS_MAPPINGS`.
- Python 3.10 or newer.
- PyTorch provided by the ComfyUI environment.
- Pillow 9.2+.
- NumPy 1.23+.

The development verification environment used Python 3.13.12, PyTorch 2.12.1+cu130, NumPy 2.5.2, Pillow 12.3.0 and ComfyUI v0.44.2.

## Installation

### Manual installation

1. Clone this repository into ComfyUI's custom-node directory:

   ```bash
   git clone https://github.com/Hejunlong27/H3GIF.git custom_nodes/H3GIF
   ```

2. Install dependencies with the Python interpreter used by ComfyUI:

   ```bash
   python -m pip install -r custom_nodes/H3GIF/requirements.txt
   ```

3. Restart ComfyUI completely.
4. Search the node menu for `H3GIF`.
5. Import the formal workflow from `workflows/H3GIF_Complete.json`.

### ComfyUI Manager

Manager installation is available only after the project is published and indexed. No public Registry Publisher ID is configured in this repository yet.

## Nodes

### H3GIF Storyboard Director

Builds one strict storyboard contact-sheet prompt for H3-Image.

| Input | Meaning |
|---|---|
| `scene_description` | Overall scene, character, location and camera description. |
| `panel_actions` | One action per line or semicolon, in reading order. |
| `rows`, `columns` | Required contact-sheet grid. |
| `gutter_pixels` | Requested black gutter width and the value sent to Grid Split. |
| `character_lock` | Identity/outfit/proportion continuity instructions. |
| `style_prompt` | Shared visual style and lighting. |
| `extra_instructions` | Additional layout or content constraints. |

Outputs the positive prompt, rows, columns, gutters, panel count and a JSON information string.

### H3GIF Grid Split

Splits every `IMAGE` in the input batch into equal-size storyboard tiles.

| Input | Meaning |
|---|---|
| `resolution_preset` | `Auto detect`, 2048/1024/512 presets, or `Custom grid`. |
| `columns`, `rows` | Manual grid dimensions; also used as fallback parameters. |
| `gap_x`, `gap_y` | Pixel gutters between cells. |
| `margin_left/right/top/bottom` | Outer margins excluded before layout calculation. |
| `offset_x`, `offset_y` | Additional top-left offset inside the margin-adjusted area. |
| `tile_width`, `tile_height` | Exact cell size. Set both to `0` for automatic equal division. |
| `reading_order` | `Row-major`, `Column-major`, or `Serpentine`. |
| `reverse` | Reverse the selected order after reading-order expansion. |
| `frame_range` | Optional 1-based selection, for example `1-16` or `2,4,6-10`. |
| `skip_frames` | Optional 1-based original frame numbers to remove. |
| `skip_blank_frames` | Remove nearly uniform cells. |
| `blank_threshold` | Normalized intensity-range threshold for blank detection. |

Selection rules:

- `frame_range` and `skip_frames` refer to the original ordered frame numbers.
- `frame_range` preserves the original order.
- Blank filtering runs after cropping.
- Remainder pixels at the right/bottom edge are ignored when automatic equal division is used.

Outputs include the frame batch, dimensions, detected rows/columns, confidence, success flag and a JSON `grid_info` string containing all tile bounds.

#### Automatic detection

The detector analyzes grayscale horizontal and vertical projection peaks. It supports common regular grids and deliberately fails on weak separator evidence instead of guessing. If detection fails, choose a preset or `Custom grid` and enter rows/columns manually.

Automatic detection is not intended for irregular comic panels, collage layouts, overlapping frames or grids without measurable separators.

### H3GIF Animation

| Input | Meaning |
|---|---|
| `playback_mode` | `Forward`, `Reverse`, or `Ping-pong`. |
| `frame_range` | 1-based source-frame selection. |
| `skip_frames` | 1-based source-frame numbers to skip. |
| `custom_order` | Final order after range/skip, for example `4,2,1,3`. Duplicates are allowed. |
| `hold_each_frame` | Repeat every frame N times. |
| `hold_first`, `hold_last` | Additional repeats for the first and last animation frame. |

Ping-pong avoids duplicate endpoints. For 4 source frames the sequence is `1,2,3,4,3,2`; for 64 frames it contains 126 frames.

### H3GIF Loop Optimizer

| Input | Meaning |
|---|---|
| `mode` | `Analyze only`, `Ping-pong if needed`, or `Crossfade if needed`. |
| `transition_frames` | Number of last-to-first blend frames for crossfade mode. |
| `endpoint_difference_threshold` | Normalized endpoint difference above which an optimization is applied. |

Outputs include the optimized frame batch, loop similarity, endpoint difference and a recommendation string. Similarity alone does not prove motion continuity; always inspect the result.

### H3GIF GIF Export

| Input | Meaning |
|---|---|
| `fps` | Playback rate when `frame_duration_ms` is `0`. |
| `frame_duration_ms` | Explicit GIF frame duration; overrides FPS timing. |
| `loop_count` | `0` means infinite looping. |
| `resize` | Preserve original size or fit the longest edge to 2048/1024/768/512/256. |
| `resize_edge` | Custom longest edge; values above 0 override `resize`. |
| `colors` | Shared GIF palette size, 2-256. |
| `dither` | Floyd-Steinberg or none. |
| `alpha_background` | Composite RGBA input on white or black. |
| `optimize` | Enable Pillow GIF optimization. |
| `filename_prefix` | Relative path and filename stem under the ComfyUI output directory. |
| `max_file_size_mb` | Optional size limit. `0` disables the check; oversized output is removed with an error. |

The palette is sampled from all frames, avoiding the v0.1.0 bug where a first-frame-only palette could collapse different frames into one image. The returned frame count is read back from the actual GIF file.

## Formal workflow

Only one workflow is provided:

```text
H3GIF Storyboard Director
  -> H3-Image Conditioning
  -> Exact 6-step Sigma sampling
  -> VAEDecode
  -> SaveImage (generated contact sheet)
  -> H3GIF Grid Split
       -> SaveImage (split-frame preview / PNG output)
       -> H3GIF Animation
            -> H3GIF Loop Optimizer
            -> H3GIF GIF Export
```

Usage:

1. Import `workflows/H3GIF_Complete.json`.
2. In `H3GIF Storyboard Director`, fill `scene_description` and one action per line in `panel_actions`.
3. Set the required `rows` and `columns`; the default is 2×2.
4. Keep the validated H3-Image model trio: `minimax_h3_image_pruned_int8_convrot`, `qwen3vl_32b_minimax_h3_nvfp4_awq` with CLIP type `minimax`, and `minimax_h3_image_vae_fp16`.
5. Queue the workflow. The generated contact sheet is saved under `ComfyUI/output/H3GIF/source/`.
6. Inspect the split frames under `ComfyUI/output/H3GIF/frames/`.
7. Find the GIF under `ComfyUI/output/H3GIF/`.

The Director outputs rows/columns/gutters directly to Grid Split, so this workflow does not depend on automatic detection.

A detailed Chinese quick-start is available in `使用说明.md`. See `workflows/README.md` for the compact workflow guide.

## Output

Generated H3 contact sheet:

```text
ComfyUI/output/H3GIF/source/
```

Split frames:

```text
ComfyUI/output/H3GIF/frames/
```

Final GIF:

```text
ComfyUI/output/H3GIF/
```

The final path includes a unique timestamp and `.gif` extension. The prefix is sanitized and cannot escape the ComfyUI output directory.

## Troubleshooting

### Automatic detection fails

This means the input image does not contain a reliably measurable regular grid. Select `Custom grid` and enter the actual rows/columns. A single character image or ordinary illustration is not a storyboard; with `rows=1, columns=1` it produces only a one-frame GIF.

### Tiles are shifted or include parts of neighboring panels

Check `gap_x`, `gap_y`, all four margins and offsets. Use `grid_info` to inspect the exact tile bounds.

### Too many or too few frames

Check `frame_range`, `skip_frames`, blank filtering and the selected reading order. Selectors are 1-based.

### GIF is too large

Use a smaller resize target or `resize_edge`, lower `colors`, keep `optimize=True`, or reduce frame count and output dimensions. `max_file_size_mb` can reject an oversized result.

### GIF frames look duplicated or missing

The exporter returns the actual frame count after writing. If optimization merges frames, their quantized pixels are identical. Increase palette size or verify source frames really differ.

### The output directory is not writable

Run ComfyUI under an account with write access to `ComfyUI/output`, or correct its configured output directory.

## Development

Run the automated suite with the Python interpreter used by ComfyUI:

```bash
python -m unittest discover -s tests -v
```

The tests use CPU tensors and temporary output directories. They do not require a running ComfyUI server, model files or a GPU.

## Compatibility and limitations

Verified against the local ComfyUI environment:

- Official `load_custom_node()` registration for all four nodes.
- Full five-node API prompt validation through `execution.validate_prompt()` with no node errors.
- Node registration mappings.
- Standard ComfyUI IMAGE shape `[N,H,W,C]`.
- RGB and RGBA conversion.
- GIF writing through the ComfyUI output directory API.
- 88 automated tests.

Still requires release validation:

- Browser import of `H3GIF_Complete.json` in a live ComfyUI build.
- Visual checks across common browser GIF players.
- Very large 4K/64-frame memory profiling on representative hardware.

GIF supports at most 256 palette colors per image. Gradients may band. H3GIF cannot guarantee visually seamless loops because source-frame motion continuity is outside its control.

## Performance check

A local CPU smoke test split a synthetic 4096x4096 RGB image into an 8x8 grid (64 tiles of 512x512) in 0.14 seconds. Process RSS was approximately 887 MiB after input and output staging, versus approximately 500 MiB before the test. This measurement excludes model runtime, ComfyUI web overhead and GIF encoding; actual memory depends on the loaded workflow and device.

## Contributing

Issues and pull requests are welcome after the repository is published. Keep changes focused, add tests for behavior changes, and do not add telemetry or external uploads.

## License

MIT. See `LICENSE`.
