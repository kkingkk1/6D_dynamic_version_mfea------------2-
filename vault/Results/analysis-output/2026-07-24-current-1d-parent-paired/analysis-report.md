# 当前 1D Parent 四配置配对实验：严格分析

## 分析问题

在 ID1-ID10 的五个配对 `perRun` 上，以下两个预先定义的收益率对比是否保持同方向：

- `hybrid-290002` 相对 `hybrid-410000`。
- `parent-4` 相对 `parent-1`。

指标为 `profitRatio`，单位为百分点，越高越好。

## 数据与完整性

- 原始运行：200 条，预期 200 条，唯一 `runKey` 200 条。
- 每个 `(sceneId, perRun)` 有四条配置和一个共同 `effectiveSeed`；共 50 个有效配对组。
- `run-status.csv` 有 200 条成功 attempt，失败 attempt 为 0。
- 每个配置 50 次运行。每个场景每个配置 5 次运行。

主推断单位是“场景内五个配对 run 的平均收益率”，因此每项主对比有 10 个配对场景。50 个 `(scene, perRun)` 的 seed 级检验仅作敏感性证据，不当作 50 个独立场景。

## 主发现

- `hybrid-290002` 的场景宏平均收益率为 `77.0542%`，高于 `hybrid-410000` 的 `76.5742%`；平均增益 `+0.4800` 个百分点。
- `parent-4` 的场景宏平均收益率为 `75.5166%`，高于 `parent-1` 的 `74.4338%`；平均增益 `+1.0828` 个百分点。
- 两项对比都在 10 个场景中取得 6 胜、4 平、0 负。增益集中在非饱和场景，尤其是 ID7；收益饱和场景的差值为 0。

## 支持边界

场景级差值未满足正态性，主检验采用双侧 Wilcoxon signed-rank。两项原始 `p=0.03125`，但对两个预先定义对比做 Holm 校正后均为 `p=0.0625`。因此：

- 方向、场景胜负和 seed 级敏感性结果一致。
- 在这两个并列主对比的 family-wise 0.05 门槛下，尚不能称为校正后显著。
- 结果支持将 `hybrid-290002` 保留为自动设计主线的候选，将 `parent-4` 保留为当前 1D Parent 的优先候选；不支持据此终止其他机制分析或直接写入论文显著性主张。

## 产物

- 场景级摘要：`vault/Results/data/2026-07-24-current-1d-parent-paired-scene-summary.csv`。
- 主对比统计：`vault/Results/data/2026-07-24-current-1d-parent-paired-comparisons.csv`。
- 完整统计：`stats-appendix.md`。
- 图与说明：`figure-catalog.md` 和 `figures/`。
