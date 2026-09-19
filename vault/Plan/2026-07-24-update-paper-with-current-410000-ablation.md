---
status: completed
created: 2026-07-24
updated: 2026-07-25
---

# 用原生 perRun+0..+4 配对结果更新论文

## 目标

将 `vault/Writing/paper_draft.md` 中 RK-HMA 主结果和 Hybrid 消融统一更新为原生 `perRun+0..+4` 的全场景五次配对运行。其中论文方法使用 `410000={4,1,0,0,0,0}`，单算法消融使用 `4=DE/rand/1` 与 `1=PSO`。

## 步骤

- [x] 核对算法编号、正式运行合同和当前论文结果段。
- [x] 修正批处理 seed 合同，并完成 ID1 原生首轮/第五次 preflight：四配置分别在 index 9、13 使用同一最终 seed。
- [x] 删除错误 seed 批次及其派生分析产物。
- [x] 用原生 `perRun+0..+4` 重跑 `410000`、`290002`、Parent `4`、Parent `1` 的 200 个场景运行；200/200 状态为 `ok`，同一场景同一轮 seed 一致。
- [x] 分析新数据，建立轻量 Evidence 包与结果简报，并生成 PNG/SVG 对比图。
- [x] 将 Evidence 图和数值映射到论文 Fig. 6 与 Fig. 9。
- [x] 更新 Tab. IV、Tab. V、Tab. VI 及其解释段。
- [x] 同步摘要、贡献、结论中的数值和结论强度。
- [x] 对本轮改写段落执行轻量 `writing-anti-ai` 检查。
- [x] 验证数值、图路径、Markdown/LaTeX 结构和残留旧结果。

## 决策

- 旧批次虽然在四套配置间保持了相同 seed，但使用了非原生 `evaluation.runSeedBase`，不作为本轮论文证据。
- 原生序列以 `410000` 为锚：每场景先无显式 seed 属性运行当前源码的第五次，核对其 `[RunSeed]` 后推导五个有效 index；其余三套使用同一最终 seed。
- Tab. IV 采用每场景第五次（`perRun+4`）的 `410000` 结果；Tab. VI 使用当前 1D Parent 路径五次的 Max/Ave/Min。
- 外部 R-ALNS、A-ALNS 数值仍来自论文已有引用，只更新 RK-HMA 列及由该列导出的差值和文字。
- 当前稿件缺失的静态图片从用户指定的 `8D_dynamic_version/vault/` 源目录按原文件复制；Fig. 6 和 Fig. 9 不复用旧结果图，而是由 `scripts/plot_paper_native_perrun_results.py` 从本次 Evidence 数据重新生成。

## 错误记录

- `python scripts/analyze_native_paired_ablation.py` 首次运行在 NumPy 2.x 的只读数组视图上写入零容差归一值，触发 `ValueError: assignment destination is read-only`。分析数组改为显式 `copy=True`；以后对 pandas `to_numpy()` 返回值做原地修改前先复制。
- `python scripts/plot_paper_native_perrun_results.py` 首次生成 Fig. 9 时向 `pubfig.box()` 传入 Python 嵌套列表，触发 `ValueError: Input must be a list of 1D ndarrays or a 1D/2D ndarray.`；同时 `nature` theme 和导出 `FigureSpec` 默认 Helvetica 在本机缺失。各组数据现显式转为一维 `ndarray`，theme 与 `FigureSpec` 均固定为 Matplotlib 自带的 `DejaVu Sans`，重跑后无字体 fallback。
- 首轮 Markdown 数学配对检查使用负向回看排除反斜杠后的 `$`，误把 LaTeX `\\$...$` 中位于换行命令后的数学起始符当成转义美元符。最终检查改为核对原始美元符总数，并单独核对 LaTeX 环境起止数量。

## 状态

原生 seed 批次、结果分析和论文映射均已完成。Canonical Evidence 见 [[Results/Evidence/paired-native-perrun0-4-10scene-20260724-r01/evidence|原生 perRun 五轮配对消融证据]]，人读简报见 [[Results/Reports/paired-native-perrun0-4-10scene-20260724-r01|Native Paired Ablation 总结]]。

`vault/Writing/paper_draft.md` 已更新 Fig. 6、Fig. 9、Tab. IV、Tab. V、Tab. VI、摘要、贡献、结果解释和结论。三张表均从 canonical `data.csv` 逐行回算通过；9 个图片链接有效；新图为 400 DPI PNG+SVG；Markdown/LaTeX 结构、旧结果残留和 `git diff --check` 均通过。
