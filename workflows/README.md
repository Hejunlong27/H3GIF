# H3GIF Formal Workflow: H3-Image to GIF

Use `H3GIF_Complete.json`. It is the only formal workflow.

## Pipeline

1. `H3GIF Storyboard Director` builds a strict R×C storyboard prompt from the scene and per-panel actions.
2. `MiniMaxH3ImageConditioning` uses the H3-Image CLIP/VAE pair to create conditioning and latent.
3. Exact 6-step PDD sigmas are sampled with `BasicGuider` and `SamplerCustomAdvanced`.
4. `VAEDecode` produces the contact sheet and saves it under `ComfyUI/output/H3GIF/source/`.
5. Director rows, columns and gutters drive `H3GIF Grid Split`, with no automatic grid guessing.
6. Split frames are saved under `ComfyUI/output/H3GIF/frames/`.
7. Animation, loop optimization and GIF export produce `ComfyUI/output/H3GIF/animation_*.gif`.
8. GIF Export returns both the requested FPS and the effective FPS actually stored in the GIF.

## Required validated models

- UNET: `minimax_h3_image_pruned_int8_convrot.safetensors`
- CLIP: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- CLIP type: `minimax`
- VAE: `minimax_h3_image_vae_fp16.safetensors`

## First run

1. Open the workflow and read the visible Chinese note.
2. Fill `scene_description` and `panel_actions`.
3. Keep `rows=2`, `columns=2`, `gutter_pixels=8` for the first 8 GB VRAM test.
4. Keep the validated sampler, seed and Sigma fields unchanged unless you know the model requirements.
5. Queue the workflow.
6. Inspect the generated contact sheet before tuning GIF settings.

The full Chinese guide is `使用说明.md` in the plugin root.
