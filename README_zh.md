# H3GIF

**把一张分镜联系表转换成循环 GIF，不需要视频模型。**

H3GIF 是一个与图片生成模型无关的 ComfyUI 自定义节点插件。它可以把 Storyboard / Contact Sheet 切割为独立帧，控制播放顺序，并导出优化后的 GIF。任何输出标准 ComfyUI `IMAGE` Tensor 的节点都可以接入。

> **新手请先阅读：[使用说明.md](使用说明.md)。**
>
> **重要：输入必须是同一张图中包含多个连续画面的分镜联系表。单人物立绘、单张插画不能直接生成有意义的动画。**

**当前状态：** `v0.3.1-beta`。核心单元测试和节点接口测试已通过；真实 ComfyUI 浏览器工作流导入仍属于发布前验收项。

## 功能

- 内置 H3-Image 宫格生成链：场景/动作 → 严格宫格提示词 → H3-Image 精准 Sigma → GIF。
- `H3GIF Storyboard Director` 自动生成严格 R×C 联系表提示词，并把行列和黑边宽度直接传给切割节点。
- 自动识别规则网格，输出置信度，失败时明确要求手动模式。
- 手动支持 1x1 到 64x64 行列配置。
- 4096x4096 常用预设：2x2、4x4、8x8。
- 支持横向/纵向间距、四周边距、偏移和精确单元格尺寸。
- 支持 Row-major、Column-major、Serpentine 和 Reverse。
- 支持帧范围、跳帧和空白帧过滤。
- 支持 Forward、Reverse 和无首尾重复帧的 Ping-pong。
- 支持逐帧重复、首帧停留和末帧停留。
- 支持首尾循环差异分析，以及可选 Ping-pong 或交叉淡化过渡帧。
- GIF 支持 FPS 或指定帧时长、循环次数、自定义最长边、调色板颜色数、抖动、透明背景和可选文件体积上限。
- GIF 返回实际帧数、宽高、文件大小、请求 FPS 和实际生效 FPS。
- GIF 时间会按 Pillow/GIF 的 10ms 精度归一化；`effective_fps` 返回文件实际生效帧率。
- 只提供一套正式工作流：`workflows/H3GIF_Complete.json`。
- 工作流内置原生 `SaveImage` 分支，可直接预览并保存每一张切割帧。
- 工作流内包含中文使用便签。
- 不依赖外部 API，不上传图片，不包含遥测或 API Key 处理。

## 环境要求

- 支持标准自定义节点 `NODE_CLASS_MAPPINGS` 的 ComfyUI。
- Python 3.10 或更高版本。
- PyTorch 由 ComfyUI 环境提供。
- Pillow 9.2+。
- NumPy 1.23+。

本次开发验证环境：Python 3.13.12、PyTorch 2.12.1+cu130、NumPy 2.5.2、Pillow 12.3.0、ComfyUI v0.44.2。

## 安装

### 手动安装

1. 将仓库克隆到 ComfyUI 自定义节点目录：

   ```bash
   git clone https://github.com/Hejunlong27/H3GIF.git custom_nodes/H3GIF
   ```

2. 在 ComfyUI 安装目录中使用 ComfyUI 对应的 Python 安装依赖：

   ```bash
   python -m pip install -r custom_nodes/H3GIF/requirements.txt
   ```

3. 完全重启 ComfyUI。
4. 在节点菜单中搜索 `H3GIF`。
5. 导入 `workflows/H3GIF_Complete.json`。

### ComfyUI Manager

只有项目发布并进入 Registry 后才支持 Manager 安装。当前仓库尚未填写公开 Registry Publisher ID。

## 节点说明

### H3GIF Storyboard Director

为 H3-Image 生成严格的宫格联系表提示词。

| 参数 | 含义 |
|---|---|
| `scene_description` | 整体场景、角色、环境、镜头描述。 |
| `panel_actions` | 按阅读顺序填写每个格子的动作，一行一个或用分号分隔。 |
| `rows`、`columns` | 要求 H3-Image 生成的宫格行列数。 |
| `gutter_pixels` | 宫格黑边宽度，同时直接连接到 Grid Split。 |
| `character_lock` | 角色身份、服装、比例和脸部一致性要求。 |
| `style_prompt` | 统一画风、光线和色彩。 |
| `extra_instructions` | 额外布局或内容约束。 |

输出 positive prompt、rows、columns、gutter、panel_count 和 JSON 信息。

### H3GIF Grid Split

把输入 `IMAGE` batch 中的每张图切割成等尺寸分镜帧。

| 参数 | 含义 |
|---|---|
| `resolution_preset` | `Auto detect`、2048/1024/512 预设或 `Custom grid`。 |
| `columns`、`rows` | 手动行列数，同时作为自动检测失败后的回退参数。 |
| `gap_x`、`gap_y` | 单元格之间的像素间距。 |
| `margin_left/right/top/bottom` | 布局计算前排除的四周边距。 |
| `offset_x`、`offset_y` | 在边距范围基础上额外增加的左上偏移。 |
| `tile_width`、`tile_height` | 精确单元格尺寸；两项都为 0 时自动等分。 |
| `reading_order` | 行优先、列优先或蛇形顺序。 |
| `reverse` | 在阅读顺序展开后整体反向。 |
| `frame_range` | 可选的 1-based 帧选择，例如 `1-16`、`2,4,6-10`。 |
| `skip_frames` | 按原始帧序号跳过指定帧。 |
| `skip_blank_frames` | 跳过接近纯色的空白单元格。 |
| `blank_threshold` | 空白判断的归一化亮度范围阈值。 |

选择规则：

- `frame_range` 和 `skip_frames` 都按原始排序后的帧序号解释。
- `frame_range` 不改变原始顺序。
- 空白帧过滤发生在切割之后。
- 自动等分时，右侧和底部无法整除的剩余像素会被忽略。

输出包括帧 batch、尺寸、识别行列数、置信度、成功标记，以及包含所有单元格边界的 JSON `grid_info`。

#### 自动识别

检测器使用灰度横向、纵向投影峰值识别规则网格。分隔线证据不足时会明确失败，不会强行猜测。失败后请切换预设或 `Custom grid` 手动填写行列数。

自动识别不适用于不规则漫画分格、拼贴、重叠画框或没有可测量分隔线的布局。

### H3GIF Animation

| 参数 | 含义 |
|---|---|
| `playback_mode` | Forward、Reverse 或 Ping-pong。 |
| `frame_range` | 1-based 源帧选择。 |
| `skip_frames` | 按源帧序号跳过。 |
| `custom_order` | 范围与跳帧后的最终顺序，例如 `4,2,1,3`，允许重复。 |
| `hold_each_frame` | 每帧重复次数。 |
| `hold_first`、`hold_last` | 动画首帧和末帧的额外重复次数。 |

Ping-pong 不重复首尾端点。4 帧对应 `1,2,3,4,3,2`；64 帧对应 126 个动画帧。

### H3GIF Loop Optimizer

| 参数 | 含义 |
|---|---|
| `mode` | `Analyze only`、`Ping-pong if needed` 或 `Crossfade if needed`。 |
| `transition_frames` | 交叉淡化模式下从末帧过渡回首帧的融合帧数。 |
| `endpoint_difference_threshold` | 首尾差异超过该阈值时执行所选优化。 |

输出包括优化后的帧、循环相似度、首尾差异和建议文本。相似度不能证明运动连续，必须结合画面检查结果。

### H3GIF GIF Export

| 参数 | 含义 |
|---|---|
| `fps` | `frame_duration_ms=0` 时使用的播放帧率。 |
| `frame_duration_ms` | 指定 GIF 帧时长，优先于 FPS。 |
| `loop_count` | `0` 表示无限循环。 |
| `resize` | 保持原尺寸，或把最长边缩放到 2048/1024/768/512/256。 |
| `resize_edge` | 自定义最长边；大于 0 时覆盖 `resize`。 |
| `colors` | 共享 GIF 调色板颜色数，2-256。 |
| `dither` | Floyd-Steinberg 或无抖动。 |
| `alpha_background` | RGBA 输入合成到白色或黑色背景。 |
| `optimize` | 启用 Pillow GIF 优化。 |
| `filename_prefix` | ComfyUI 输出目录下的相对路径和文件名前缀。 |
| `max_file_size_mb` | 可选文件体积上限；`0` 表示关闭，超限文件会被删除并报错。 |

调色板从所有输入帧采样，避免 v0.1.0 只因第一帧生成调色板而导致不同帧被合并。返回的帧数从实际 GIF 文件重新读取。

## 唯一正式工作流

```text
H3GIF Storyboard Director
  -> H3-Image Conditioning
  -> 精准 6 步 Sigma 采样
  -> VAEDecode
  -> SaveImage（保存 H3 宫格原图）
  -> H3GIF Grid Split
       -> SaveImage（分镜帧预览 / PNG 保存）
       -> H3GIF Animation
            -> H3GIF Loop Optimizer
            -> H3GIF GIF Export
```

使用方法：

1. 导入 `workflows/H3GIF_Complete.json`。
2. 在 `H3GIF Storyboard Director` 中填写 `scene_description`，并在 `panel_actions` 中一行填写一个动作。
3. 设置需要的 `rows` 和 `columns`，默认 2×2。
4. 使用已验证模型：`minimax_h3_image_pruned_int8_convrot`、`qwen3vl_32b_minimax_h3_nvfp4_awq`（CLIP type=`minimax`）、`minimax_h3_image_vae_fp16`。
5. 排队执行，H3 宫格原图会保存到 `ComfyUI/output/H3GIF/source/`。
6. 在 `ComfyUI/output/H3GIF/frames/` 查看切割帧。
7. 在 `ComfyUI/output/H3GIF/` 中查找 GIF。

Director 的行列数和黑边宽度会直接连线到 Grid Split，因此默认工作流不再依赖自动检测。

完整中文操作说明见 `使用说明.md`，简要说明见 `workflows/README.md`。

## 输出位置

H3 生成的宫格原图：

```text
ComfyUI/output/H3GIF/source/
```

切割帧：

```text
ComfyUI/output/H3GIF/frames/
```

最终 GIF：

```text
ComfyUI/output/H3GIF/
```

最终文件包含唯一时间戳和 `.gif` 后缀。文件名前缀会被清理，不能逃逸出 ComfyUI 输出目录。

## 常见问题

### 自动识别失败

说明输入图中没有可靠、规则的网格。请选择 `Custom grid` 并填写实际行列数。单人物立绘或普通插画不是 Storyboard；设置 `rows=1, columns=1` 只会生成一张单帧 GIF。

### 切割错位或包含相邻画面

检查 `gap_x`、`gap_y`、四周边距和偏移。可以通过 `grid_info` 查看实际切割边界。

### 帧数过多或过少

检查 `frame_range`、`skip_frames`、空白帧过滤和阅读顺序。所有选择器均从 1 开始。

### GIF 文件过大

降低 `resize` 或 `resize_edge`、`colors`，保持 `optimize=True`，或减少帧数与输出分辨率。可用 `max_file_size_mb` 拒绝超限结果。

### GIF 看起来缺帧或重复

导出器返回实际写入帧数。开启优化后，量化结果完全相同的帧会被合并；可提高颜色数，并确认源帧本身确实不同。

### 输出目录不可写

使用对 `ComfyUI/output` 有写权限的账号运行 ComfyUI，或修正 ComfyUI 的输出目录配置。

## 开发与测试

使用 ComfyUI 对应的 Python 执行：

```bash
python -m unittest discover -s tests -v
```

测试使用 CPU Tensor 和临时输出目录，不需要启动 ComfyUI、模型文件或 GPU。

## 兼容性与限制

已在本地 ComfyUI 环境验证：

- 通过官方 `load_custom_node()` 注册全部 4 个节点。
- 完整 5 节点 API Prompt 通过 `execution.validate_prompt()`，无节点错误。
- 节点注册映射。
- 标准 ComfyUI `IMAGE` `[N,H,W,C]` 格式。
- RGB/RGBA 转换。
- 通过 ComfyUI 输出目录 API 写入 GIF。
- 88 项自动化测试。

仍需发布前验证：

- 在真实 ComfyUI 浏览器中导入 `H3GIF_Complete.json`。
- 常见浏览器 GIF 播放器视觉检查。
- 代表性硬件上的 4K/64 帧内存剖析。

GIF 单帧最多 256 色，渐变可能出现色带。H3GIF 无法保证源帧运动本身必然形成视觉无缝循环。

## 性能检查

本机 CPU 试跑将一张合成的 4096x4096 RGB 图切成 8x8（64 个 512x512 单元），耗时 0.14 秒。输入与输出驻留后，进程 RSS 约为 887 MiB，测试前约为 500 MiB。该数据不包含模型运行、ComfyUI 网页开销和 GIF 编码；实际内存取决于工作流和硬件。

## 贡献

仓库公开后欢迎提交 Issue 和 Pull Request。请保持改动范围清晰，行为变化必须附带测试，不得加入遥测或外部上传。

## License

MIT，详见 `LICENSE`。
