# H3GIF 50 组批量测试报告

## 总览

- 总任务：50
- 技术验收通过：50
- 失败：0
- 平均耗时：50.001 秒/组
- 平均 GIF：4.2 MiB
- GIF 总量：209.998 MiB
- 统一规格：2048×2048 宫格、3×3=9 帧源图、Ping-pong 16 帧 GIF、无限循环

## 帧率量化

GIF 时间精度为 10ms，请求帧率会被量化：

| 请求 FPS | 实际 FPS | 实际帧时长 |
|---:|---:|---:|
| 4 | 4.000 | 250ms |
| 6 | 6.250 | 160ms |
| 8 | 8.333 | 120ms |
| 10 | 10.000 | 100ms |
| 12 | 12.500 | 80ms |

## 画风汇总

| 画风 | 组数 | 平均耗时 | 平均 GIF |
|---|---:|---:|---:|
| anime_cel | 5 | 50.12s | 3.92 MiB |
| cinematic_3d | 5 | 52.1s | 3.97 MiB |
| claymation | 5 | 50.07s | 4.09 MiB |
| cyberpunk_comic | 5 | 49.1s | 4.44 MiB |
| film_noir | 5 | 50.1s | 4.69 MiB |
| ink_wash | 5 | 50.07s | 4.49 MiB |
| low_poly | 5 | 50.08s | 3.8 MiB |
| oil_painting | 5 | 49.14s | 4.87 MiB |
| paper_cut | 5 | 49.14s | 3.81 MiB |
| watercolor | 5 | 50.09s | 3.91 MiB |

## 动作汇总

| 动作 | 组数 | 平均耗时 | 平均 GIF |
|---|---:|---:|---:|
| martial_arts | 10 | 50.09s | 4.29 MiB |
| partner_dance | 10 | 50.08s | 4.54 MiB |
| spin_jump | 10 | 49.61s | 3.41 MiB |
| sprint | 10 | 49.12s | 3.77 MiB |
| street_walk | 10 | 51.1s | 4.98 MiB |

## 逐组结果

| # | 画风 | 动作 | 请求 FPS | 实际 FPS | 耗时 | GIF |
|---:|---|---|---:|---:|---:|---:|
| 01 | cinematic_3d | street_walk | 4 | 4.0 | 60.096s | `output/H3GIF/batch50\v01_cinematic_3d_street_walk_4fps\animation_1794415392211797600.gif` |
| 02 | anime_cel | street_walk | 6 | 6.25 | 50.353s | `output/H3GIF/batch50\v02_anime_cel_street_walk_6fps\animation_1794415445479688100.gif` |
| 03 | ink_wash | street_walk | 8 | 8.333 | 50.056s | `output/H3GIF/batch50\v03_ink_wash_street_walk_8fps\animation_1794415495846906600.gif` |
| 04 | claymation | street_walk | 10 | 10.0 | 50.057s | `output/H3GIF/batch50\v04_claymation_street_walk_10fps\animation_1794415545698991400.gif` |
| 05 | watercolor | street_walk | 12 | 12.5 | 50.072s | `output/H3GIF/batch50\v05_watercolor_street_walk_12fps\animation_1794415596039261800.gif` |
| 06 | cyberpunk_comic | street_walk | 4 | 4.0 | 50.086s | `output/H3GIF/batch50\v06_cyberpunk_comic_street_walk_4fps\animation_1794415646898502100.gif` |
| 07 | low_poly | street_walk | 6 | 6.25 | 50.087s | `output/H3GIF/batch50\v07_low_poly_street_walk_6fps\animation_1794415697592729300.gif` |
| 08 | oil_painting | street_walk | 8 | 8.333 | 50.049s | `output/H3GIF/batch50\v08_oil_painting_street_walk_8fps\animation_1794415748015838900.gif` |
| 09 | paper_cut | street_walk | 10 | 10.0 | 50.096s | `output/H3GIF/batch50\v09_paper_cut_street_walk_10fps\animation_1794415799644275800.gif` |
| 10 | film_noir | street_walk | 12 | 12.5 | 50.072s | `output/H3GIF/batch50\v10_film_noir_street_walk_12fps\animation_1794415850471257500.gif` |
| 11 | cinematic_3d | sprint | 4 | 4.0 | 50.127s | `output/H3GIF/batch50\v11_cinematic_3d_sprint_4fps\animation_1794415901388301800.gif` |
| 12 | anime_cel | sprint | 6 | 6.25 | 50.083s | `output/H3GIF/batch50\v12_anime_cel_sprint_6fps\animation_1794415952596270700.gif` |
| 13 | ink_wash | sprint | 8 | 8.333 | 50.071s | `output/H3GIF/batch50\v13_ink_wash_sprint_8fps\animation_1794416003700106800.gif` |
| 14 | claymation | sprint | 10 | 10.0 | 50.099s | `output/H3GIF/batch50\v14_claymation_sprint_10fps\animation_1794416054440236700.gif` |
| 15 | watercolor | sprint | 12 | 12.5 | 50.088s | `output/H3GIF/batch50\v15_watercolor_sprint_12fps\animation_1794416105263753600.gif` |
| 16 | cyberpunk_comic | sprint | 4 | 4.0 | 45.226s | `output/H3GIF/batch50\v16_cyberpunk_comic_sprint_4fps\animation_1794416155858959000.gif` |
| 17 | low_poly | sprint | 6 | 6.25 | 50.089s | `output/H3GIF/batch50\v17_low_poly_sprint_6fps\animation_1794416202844185500.gif` |
| 18 | oil_painting | sprint | 8 | 8.333 | 45.3s | `output/H3GIF/batch50\v18_oil_painting_sprint_8fps\animation_1794416253135543600.gif` |
| 19 | paper_cut | sprint | 10 | 10.0 | 50.058s | `output/H3GIF/batch50\v19_paper_cut_sprint_10fps\animation_1794416299864489900.gif` |
| 20 | film_noir | sprint | 12 | 12.5 | 50.087s | `output/H3GIF/batch50\v20_film_noir_sprint_12fps\animation_1794416351124200200.gif` |
| 21 | cinematic_3d | partner_dance | 4 | 4.0 | 50.079s | `output/H3GIF/batch50\v21_cinematic_3d_partner_dance_4fps\animation_1794416403610234100.gif` |
| 22 | anime_cel | partner_dance | 6 | 6.25 | 50.056s | `output/H3GIF/batch50\v22_anime_cel_partner_dance_6fps\animation_1794416454631011800.gif` |
| 23 | ink_wash | partner_dance | 8 | 8.333 | 50.082s | `output/H3GIF/batch50\v23_ink_wash_partner_dance_8fps\animation_1794416506775875200.gif` |
| 24 | claymation | partner_dance | 10 | 10.0 | 50.104s | `output/H3GIF/batch50\v24_claymation_partner_dance_10fps\animation_1794416556435288300.gif` |
| 25 | watercolor | partner_dance | 12 | 12.5 | 50.083s | `output/H3GIF/batch50\v25_watercolor_partner_dance_12fps\animation_1794416607498694600.gif` |
| 26 | cyberpunk_comic | partner_dance | 4 | 4.0 | 50.086s | `output/H3GIF/batch50\v26_cyberpunk_comic_partner_dance_4fps\animation_1794416659268633700.gif` |
| 27 | low_poly | partner_dance | 6 | 6.25 | 50.102s | `output/H3GIF/batch50\v27_low_poly_partner_dance_6fps\animation_1794416709898795500.gif` |
| 28 | oil_painting | partner_dance | 8 | 8.333 | 50.096s | `output/H3GIF/batch50\v28_oil_painting_partner_dance_8fps\animation_1794416760402765100.gif` |
| 29 | paper_cut | partner_dance | 10 | 10.0 | 50.052s | `output/H3GIF/batch50\v29_paper_cut_partner_dance_10fps\animation_1794416811521847000.gif` |
| 30 | film_noir | partner_dance | 12 | 12.5 | 50.073s | `output/H3GIF/batch50\v30_film_noir_partner_dance_12fps\animation_1794416862470357600.gif` |
| 31 | cinematic_3d | martial_arts | 4 | 4.0 | 50.074s | `output/H3GIF/batch50\v31_cinematic_3d_martial_arts_4fps\animation_1794416913406303300.gif` |
| 32 | anime_cel | martial_arts | 6 | 6.25 | 50.071s | `output/H3GIF/batch50\v32_anime_cel_martial_arts_6fps\animation_1794416964341331800.gif` |
| 33 | ink_wash | martial_arts | 8 | 8.333 | 50.057s | `output/H3GIF/batch50\v33_ink_wash_martial_arts_8fps\animation_1794417015457887500.gif` |
| 34 | claymation | martial_arts | 10 | 10.0 | 50.069s | `output/H3GIF/batch50\v34_claymation_martial_arts_10fps\animation_1794417066274333700.gif` |
| 35 | watercolor | martial_arts | 12 | 12.5 | 50.094s | `output/H3GIF/batch50\v35_watercolor_martial_arts_12fps\animation_1794417117251607900.gif` |
| 36 | cyberpunk_comic | martial_arts | 4 | 4.0 | 50.069s | `output/H3GIF/batch50\v36_cyberpunk_comic_martial_arts_4fps\animation_1794417168863739000.gif` |
| 37 | low_poly | martial_arts | 6 | 6.25 | 50.077s | `output/H3GIF/batch50\v37_low_poly_martial_arts_6fps\animation_1794417221504832500.gif` |
| 38 | oil_painting | martial_arts | 8 | 8.333 | 50.117s | `output/H3GIF/batch50\v38_oil_painting_martial_arts_8fps\animation_1794417272152412900.gif` |
| 39 | paper_cut | martial_arts | 10 | 10.0 | 50.081s | `output/H3GIF/batch50\v39_paper_cut_martial_arts_10fps\animation_1794417323467821100.gif` |
| 40 | film_noir | martial_arts | 12 | 12.5 | 50.155s | `output/H3GIF/batch50\v40_film_noir_martial_arts_12fps\animation_1794417373357904100.gif` |
| 41 | cinematic_3d | spin_jump | 4 | 4.0 | 50.114s | `output/H3GIF/batch50\v41_cinematic_3d_spin_jump_4fps\animation_1794417424866668900.gif` |
| 42 | anime_cel | spin_jump | 6 | 6.25 | 50.061s | `output/H3GIF/batch50\v42_anime_cel_spin_jump_6fps\animation_1794417476764652300.gif` |
| 43 | ink_wash | spin_jump | 8 | 8.333 | 50.087s | `output/H3GIF/batch50\v43_ink_wash_spin_jump_8fps\animation_1794417526838262200.gif` |
| 44 | claymation | spin_jump | 10 | 10.0 | 50.042s | `output/H3GIF/batch50\v44_claymation_spin_jump_10fps\animation_1794417578289960500.gif` |
| 45 | watercolor | spin_jump | 12 | 12.5 | 50.092s | `output/H3GIF/batch50\v45_watercolor_spin_jump_12fps\animation_1794417628392136200.gif` |
| 46 | cyberpunk_comic | spin_jump | 4 | 4.0 | 50.046s | `output/H3GIF/batch50\v46_cyberpunk_comic_spin_jump_4fps\animation_1794417679584455900.gif` |
| 47 | low_poly | spin_jump | 6 | 6.25 | 50.052s | `output/H3GIF/batch50\v47_low_poly_spin_jump_6fps\animation_1794417730948878600.gif` |
| 48 | oil_painting | spin_jump | 8 | 8.333 | 50.114s | `output/H3GIF/batch50\v48_oil_painting_spin_jump_8fps\animation_1794417782061742200.gif` |
| 49 | paper_cut | spin_jump | 10 | 10.0 | 45.407s | `output/H3GIF/batch50\v49_paper_cut_spin_jump_10fps\animation_1794417832214276000.gif` |
| 50 | film_noir | spin_jump | 12 | 12.5 | 50.093s | `output/H3GIF/batch50\v50_film_noir_spin_jump_12fps\animation_1794417879004010100.gif` |

## 视觉检查结论

- 十种画风均有明显差异，赛博朋克漫画、黑白电影、黏土、水彩和油画的视觉区分最明显。
- 单人走路、冲刺和旋转跳跃的连续性整体较稳定。
- 双人舞和武术在 3×3 高密度宫格中仍会出现单人化、比例变化或肢体异常，这是 H3-Image 宫格生成能力限制，不是切割或 GIF 编码错误。
- 所有 50 组均完成宫格原图、9 张分镜帧、16 帧 GIF 的实际输出。

## 文件位置

- CSV：`.\batch50_report.csv`
- 画风对照图：`.\batch50_style_sheet.jpg`
- 动作对照图：`.\batch50_motion_sheet.jpg`
- 审计 JSON：`.\batch50_audit.json`
- GIF 输出目录：`output/H3GIF/batch50`
