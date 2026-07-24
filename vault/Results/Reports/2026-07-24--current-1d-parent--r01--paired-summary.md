---
type: results-report
date: 2026-07-24
experiment_line: current-1d-parent
round: 1
purpose: paired-summary
status: completed
source_artifacts:
  - ../analysis-output/2026-07-24-current-1d-parent-paired/analysis-report.md
  - ../analysis-output/2026-07-24-current-1d-parent-paired/stats-appendix.md
  - ../analysis-output/2026-07-24-current-1d-parent-paired/figure-catalog.md
  - ../data/2026-07-24-current-1d-parent-paired-scene-summary.csv
  - ../data/2026-07-24-current-1d-parent-paired-comparisons.csv
linked_experiments:
  - ../../Plan/2026-07-24-current-1d-parent-all-scenes-perrun0-4.md
linked_results:
  - ../data/2026-07-24-current-1d-parent-paired-comparisons.csv
---

# 当前 1D Parent / Round 1 / paired-summary / 2026-07-24

## 1. 执行摘要

- 四配置在 ID1-ID10、`perRun=0..4` 的 200 次 full-budget 配对运行全部完成；缺失、重复、失败和 seed 配对错误均为 0。
- 自动设计 Hybrid `{2,9,0,0,0,2}` 相对固定 Hybrid `{4,1,0,0,0,0}` 的场景宏平均收益率为 `77.0542%` 对 `76.5742%`，差 `+0.4800` pp。
- 当前 1D Parent 的算法 `4` 相对算法 `1` 为 `75.5166%` 对 `74.4338%`，差 `+1.0828` pp。
- 两项场景级对比均为 6 胜、4 平、0 负；但两项一起 Holm 校正后均为 `p=0.0625`，未达到校正后 0.05 门槛。
- 决策：保留 `hybrid-290002` 与 `parent-4` 为当前候选；不要把本轮写成校正后显著胜出，也不要把旧 3D OA1-only Parent 数值混入当前 1D Parent 基线。

## 2. 实验身份与决策背景

本报告记录当前 `RunSingleParentConfig` 1D `algorithmIndex` 路径第一次全场景配对基线。它回答两个独立但预先定义的问题：自动设计 Hybrid 是否仍优于固定 Hybrid，以及当前独立 Parent 路径中算法 4 是否优于算法 1。

历史 `paired-configs-10scene-5perrun-20260724` 的 Parent 使用已退役的 3D OA1-only 入口。本报告只使用当前 `parent-4` 与 `parent-1`，不复用历史 Parent 结论。

## 3. 设置与评估协议

- 场景：ID1-ID10，规模从 500 任务 / 5 卫星到 10000 任务 / 100 卫星。
- 配置：`hybrid-410000={4,1,0,0,0,0}`、`hybrid-290002={2,9,0,0,0,2}`、`parent-4={4}`、`parent-1={1}`。
- 重复：每场景五个 `perRun=0..4`。同一 `(sceneId, perRun)` 的四个配置共享一个实际 seed。
- 指标：优化调度收益率 `profitRatio`，越高越好；耗时只作运行成本描述。
- 运行：`autohyb.deterministic=true`、`Normal` 优先级、28 个逻辑处理器；运行时 class 从隔离目录加载。
- 主统计单位：场景内五次配对 run 的均值，共 10 个配对场景。场景级差值不满足正态性，使用双侧 Wilcoxon signed-rank，并对两项主对比做 Holm 校正。

## 4. 主要发现

### Hybrid

`hybrid-290002` 的场景宏平均收益率为 `77.0542%`，比 `hybrid-410000` 高 `0.4800` pp。它在 6 个非平局场景获胜，在 4 个收益饱和场景持平；没有场景级负差。最大增益出现在 ID7，为 `+2.976` pp。

运行成本也没有恶化：`hybrid-290002` 的 50 次总耗时为 `1090.22 s`，单次平均 `21.80 s`；`hybrid-410000` 分别为 `1301.13 s` 和 `26.02 s`。这只是本机同一实验合同下的描述性结果，不外推为通用性能结论。

### 当前 1D Parent

`parent-4` 的场景宏平均收益率为 `75.5166%`，比 `parent-1` 高 `1.0828` pp。它同样为 6 胜、4 平、0 负；最大增益是 ID9 的 `+2.828` pp，ID3、ID5、ID7、ID10 也有正差。

两者耗时接近：`parent-4` 单次平均 `29.87 s`，`parent-1` 为 `30.18 s`。算法 4 的收益优势不是以明显更高平均耗时换来的。

## 5. 统计验证

Hybrid 场景级差的 Shapiro-Wilk `p=0.0000485`，Parent 对比为 `p=0.02292`，因此两项主检验均使用 Wilcoxon signed-rank。

- Hybrid：`W=0.0`，原始 `p=0.03125`，Holm `p=0.0625`，rank-biserial `r=1.0000`，均值差 95% CI `[-0.1826, 1.1426]` pp。
- Parent：`W=0.0`，原始 `p=0.03125`，Holm `p=0.0625`，rank-biserial `r=1.0000`，均值差 95% CI `[0.2821, 1.8835]` pp。

50 个 `(scene, perRun)` 配对的敏感性 Wilcoxon 均给出更小的 p 值，但这些值不能替代以 10 个场景为统计单位的主结论。完整数字见 [[../analysis-output/2026-07-24-current-1d-parent-paired/stats-appendix|统计附录]]。

## 6. 图逐项解释

[[../analysis-output/2026-07-24-current-1d-parent-paired/figures/figure-01-scene-means.png|图 1]] 解释两组方法在每个场景中的绝对收益水平。其主要观察是候选方法只在非饱和场景拉开差距，饱和场景不能提供区分证据。这意味着下一轮应增加非饱和任务-卫星体系，而不是重复更多已饱和场景。

[[../analysis-output/2026-07-24-current-1d-parent-paired/figures/figure-02-scene-deltas.png|图 2]] 将候选减基线的收益直接置于零线。它显示两项对比没有场景级负差，但图本身不处理多重比较，不能替代 Holm 校正后的统计边界。

## 7. 失败、负结果与限制

- 运行本身没有失败，这只能证明实验合同被执行，不证明候选方法普适有效。
- 四个场景收益饱和，贡献平局而不是方法区分信息。
- 只有 10 个场景，两个主对比一起 Holm 校正后都未通过 `0.05`。因此不能使用“显著优于”的论文表述。
- `parent-4` 与 `parent-1` 是当前独立 1D 优化器的结果；它们不能和历史 3D OA1-only Parent 数值拼接或直接作横向趋势判断。
- 不同场景的五个实际 seed base 不同，但同一场景、同一 `perRun` 下四配置 seed 完全相同；本轮的因果比较边界是该配对合同内，而不是跨场景统一 seed 值。

## 8. 认知更新

- 之前：`hybrid-290002` 的 Hybrid 优势由旧四配置回放支持，但当前 1D Parent 路径没有全场景基线。
- 之后：当前 1D 入口下，算法 4 相对算法 1 与 Hybrid 候选相对固定 Hybrid 都显示相同方向的场景级非劣模式，且没有场景级反例。
- 剩余不确定性：多重校正后没有正式显著性；必须在更多非饱和场景或独立场景族中复验，才能升级为稳定主线结论。

## 9. 下一步

1. 将 `hybrid-290002` 保持为自动设计主线候选，将 `parent-4` 作为当前 1D Parent 的优先算法。
2. 若需要统计上的主张，新增独立的非饱和场景，而不是只继续增加 ID2、ID4、ID6、ID8 的重复次数。
3. 进行机制分析时以 `hybrid-290002` 对 `hybrid-410000` 为 Hybrid 主对比；不要把 Parent 结果当作 6D 基因机制的证据。

## 10. 产物与可复现性索引

- 原始 run：`outputs/paired-current-1d-parent-10scene-5perrun-20260724/run-details.csv`。
- 预期矩阵、状态与合同：同一目录的 `expected-runs.csv`、`run-status.csv`、`experiment-contract.json`、`seed-reference.csv`。
- 分析脚本：`scripts/analyze_current_1d_parent_paired.py`。
- 场景摘要与对比：[[../data/2026-07-24-current-1d-parent-paired-scene-summary.csv|场景摘要]]、[[../data/2026-07-24-current-1d-parent-paired-comparisons.csv|对比统计]]。
- 严格分析包：[[../analysis-output/2026-07-24-current-1d-parent-paired/analysis-report|分析报告]]、[[../analysis-output/2026-07-24-current-1d-parent-paired/stats-appendix|统计附录]]、[[../analysis-output/2026-07-24-current-1d-parent-paired/figure-catalog|图表目录]]。
- 实验合同：Git HEAD `4ed283c86bdb8a754b65ed42b4c31a7f05ddc111`；运行时、source hash、场景 manifest hash 与精确命令均已写入 `experiment-contract.json` 和 `commands/`。
