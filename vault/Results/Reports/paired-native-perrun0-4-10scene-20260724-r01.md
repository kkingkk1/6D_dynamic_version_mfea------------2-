---
type: results-report
date: 2026-07-25
experiment_line: native-paired-ablation
round: 1
purpose: results-summary
status: complete
source_artifacts:
  - Results/Evidence/paired-native-perrun0-4-10scene-20260724-r01/evidence.md
  - Results/Evidence/paired-native-perrun0-4-10scene-20260724-r01/data.csv
  - Results/Evidence/paired-native-perrun0-4-10scene-20260724-r01/manifest.json
linked_experiments:
  - Plan/2026-07-24-update-paper-with-current-410000-ablation.md
linked_results:
  - Results/Evidence/paired-native-perrun0-4-10scene-20260724-r01/evidence.md
---

# Native Paired Ablation / Round 1 / results-summary / 2026-07-25

## Executive Summary

- 正确的原生 `perRun=0..4` 批次已通过 200/200 完整性和 seed 配对验收。
- `410000` 相对 Parent 4 和 Parent 1 的场景宏平均分别提高 `1.0526 pp` 和 `2.1078 pp`，均为 6 胜、4 平、0 负。
- `410000` 相对 `290002` 低 `0.4272 pp`，为 0 胜、4 平、6 负；不能把 `410000` 写成四配置中的整体最优。
- 三个对比的 raw Wilcoxon `p=0.03125`，但 Holm 校正后均为 `p=0.09375`。结果支持一致方向和实际效应，不支持 family-wise 显著性表述。
- 下一步可以按既定口径更新论文：Tab. IV 使用 `410000` 的第五次结果，Tab. VI 使用 `410000` 与 Parent 4/1 的五次 Max/Ave/Min。

## Experiment Identity / Protocol

实验 ID 为 `paired-native-perrun0-4-10scene-20260724-r01`。四配置覆盖 ID1–ID10，每场景运行五个原生 `perRun`。同一场景同一轮四配置共享最终 seed；有效 index 为 9–13。运行使用 `Normal` 优先级、28 个逻辑处理器和 deterministic 模式。

主指标为 `profitRatio`。描述统计保留全部 50 条运行/配置；推断统计以每场景五次均值为一个配对单位，共 10 个场景。三个预先定义对比统一使用 exact Wilcoxon signed-rank test，并做 Holm 校正。

## Main Findings

`410000` 的场景宏平均为 `76.5608%`。`290002`、Parent 4 和 Parent 1 分别为 `76.9880%`、`75.5082%` 和 `74.4530%`。差异全部来自 6 个 Regional 非饱和场景；ID2/4/6/8 四个 Global 场景均达到相同饱和值。

对单 Parent，`410000` 同时提高收益并缩短平均耗时：相对 Parent 4 的收益为 `+1.0526 pp`、耗时少 `16.99%`；相对 Parent 1 的收益为 `+2.1078 pp`、耗时少 `25.58%`。这支持混合配置优于单独父算法的消融结论。

与 `290002` 相比，`410000` 在 6 个非饱和场景全部较低，Regional 平均差为 `-0.7120 pp`。其总体平均耗时多 `6.95%`，但在 7/10 个场景更快；ID7/9/10 的高耗时使总平均反转。

[场景收益图](../Evidence/paired-native-perrun0-4-10scene-20260724-r01/figures/figure-01-scene-profit-means.png) 用于识别绝对收益和饱和场景。[配对差值图](../Evidence/paired-native-perrun0-4-10scene-20260724-r01/figures/figure-02-paired-deltas.png) 显示 `410000` 对 Parent 的六个正差值和对 `290002` 的六个负差值。两图共同把结论限定在非饱和场景，而不是把 Global 并列误算为算法优势。

## Statistical Validation / Limitations

四配置 Friedman omnibus test 为 `χ²(3)=17.00, p=0.000707`。三个计划对比的 exact Wilcoxon 均为 `W=0, raw p=0.03125`；Holm 校正后均为 `p=0.09375`。对应 rank-biserial effect 为 `-1.0`、`+1.0`、`+1.0`，反映 6 个非零场景方向完全一致，但不消除样本小和 4 个饱和并列造成的检验功效限制。

bootstrap 95% CI 分别为 `[-1.0046, -0.0650]`、`[+0.4176, +1.7136]` 和 `[+0.9090, +3.3636]`。这些区间描述差异大小；多重比较后的显著性判断仍以 Holm `p` 为准。结论只覆盖当前 10 场景、预算、源码和 seed 序列。

## Decision / Next Actions

- 保留 `410000` 对 Parent 4/1 的论文消融方向，但措辞使用“在 6 个非饱和场景一致提高”，不写“校正后显著优于”。
- `290002` 作为内部对照保留在 Evidence；论文若不展示该配置，也不能据此宣称 `410000` 是所有已测配置中的最优。
- 后续论文更新必须从本 Evidence 的 `data.csv` 取值。Tab. IV 采用 `perRun+4`；ID1 为 `99.64%`。Tab. VI 使用五次 Max/Ave/Min。
- `paper_draft.md` 已于 2026-07-25 从本 Evidence 更新 Fig. 6、Fig. 9、Tab. IV–VI、摘要、结果解释和结论；主结果与消融仍保持各自的单次/五次统计口径。

## Artifact Index

- [完整 Evidence](../Evidence/paired-native-perrun0-4-10scene-20260724-r01/evidence.md)
- [Canonical data](../Evidence/paired-native-perrun0-4-10scene-20260724-r01/data.csv)
- [Reproducibility manifest](../Evidence/paired-native-perrun0-4-10scene-20260724-r01/manifest.json)
- [任务计划](../../Plan/2026-07-24-update-paper-with-current-410000-ablation.md)
- [论文草稿](../../Writing/paper_draft.md)
