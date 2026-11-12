# Changelog

All notable changes to H3GIF are documented here.

## [0.3.1-beta] - 2026-11-12

### Fixed

- GIF frame delays are normalized to the 10ms precision supported by GIF/Pillow.
- GIF metadata now reports the effective rate read back from the written file instead of echoing the requested timing.
- Added the new `effective_fps` FLOAT output while preserving all existing output indices.

### Validated

- 50/50 batch matrix passed: 10 art styles × 5 motion profiles × FPS values 4/6/8/10/12.
- All generated source sheets were 2048×2048, all 50 outputs contained 9 split frames, and all GIFs contained 16 frames with infinite looping.
- Actual effective FPS values: 4.0, 6.25, 8.333, 10.0 and 12.5.
- Automated suite expanded to 88 tests.

## [0.3.0-beta] - 2026-11-11

### Added

- `H3GIF Storyboard Director` for strict R×C contact-sheet prompt generation and layout metadata.
- Full H3-Image text-to-image generation chain using `MiniMaxH3ImageConditioning`, BasicGuider, exact 6-step PDD sigmas, SamplerCustomAdvanced and VAEDecode.
- Director rows, columns and gutter values are wired directly into Grid Split.
- Separate SaveImage outputs for the generated H3 contact sheet and split storyboard frames.
- Validated model configuration for the local H3 Image install and `CLIPLoader.type=minimax`.
- Complete 19-node workflow from H3-Image generation through GIF export.

### Validated

- Full ComfyUI v0.45.2 API prompt validation with all H3-Image and H3GIF nodes.
- 87 automated tests pass.

## [0.2.1-beta] - 2026-11-11

### Fixed

- Automatic grid detection errors now include image dimensions, confidence and explicit single-image/manual-grid guidance.
- The formal workflow now provides a visible explanation for detection failures instead of leaving users with an unexplained exception.

### Added

- Native `SaveImage` branch for previewing and saving every split frame under `ComfyUI/output/H3GIF/frames/`.
- Chinese instruction note embedded directly in the formal workflow.
- Detailed Chinese quick-start: `使用说明.md`.
- Automated test suite expanded to 79 tests.

## [0.2.0-beta] - 2026-11-11

### Added

- Automatic regular-grid detection with confidence and manual fallback.
- Four-side margins, exact tile dimensions, frame ranges, skipped frames and blank-frame filtering.
- Animation frame ranges, skip controls, custom order and first/last-frame holds.
- Loop endpoint analysis, optional Ping-pong and crossfade transition generation.
- GIF palette color count, explicit frame duration, alpha background, custom resize edge and optional maximum file size.
- GIF width, height, file size and actual frame count outputs.
- One formal workflow: `workflows/H3GIF_Complete.json`.
- English and Chinese documentation, project metadata, changelog and release scaffolding.
- 76 automated tests covering grid, detection, selection, animation, loop analysis, GIF, nodes and workflow structure.

### Fixed

- GIF frames could collapse because the shared palette was generated only from the first frame.
- Exported frame count could disagree with the actual GIF file.
- Empty or malformed IMAGE batches now produce explicit validation errors.
- Output path construction is sanitized and constrained to the ComfyUI output directory.
- Ping-pong endpoint duplication and 1/2-frame edge cases are covered by tests.

### Performance

- Verified a 4096x4096 to 8x8 CPU split smoke test (64 tiles) in the development environment.

### Changed

- Product, node display names and category are now H3GIF.
- Existing `StoryboardGridSplit`, `StoryboardAnimation` and `StoryboardGIFExport` class IDs are retained for workflow compatibility.
- The two v0.1 Basic workflow files were replaced by a single complete workflow.

## [0.1.0] - 2026-11-11

### Added

- Initial grid split, animation and GIF export nodes.
- Basic English documentation, MIT license and two basic workflow examples.
