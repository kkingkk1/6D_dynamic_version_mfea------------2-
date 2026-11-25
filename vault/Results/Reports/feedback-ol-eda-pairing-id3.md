---
type: results-report
status: active
evidence_package: Results/Evidence/feedback-ol-eda-pairing-id3
---

# ID3 旧 D 的 EDA 精英重配对照

旧 D 在 ID3（1,000 任务 / 10 星）有可挽回的 EDA 精英样本。五个同 seed 的审计复现旧 D，共识别 6,961 个可重配样本，其中 3,909 个提高下一轮精英的整数收益。每次父算法更新沿用原评估数量。

| 指标 | 旧 D | 启用重配 | 归档自动设计 A |
|---|---:|---:|---:|
| 首轮全星原始收益 | 2,513.6 | 2,514.2 | 2,525.8 |
| 终局合法收益 | 2,668.2 | 2,661.8 | 2,669.2 |
| 实际评估次数 | 1,078,000 | 940,800 | 1,117,200 |

开启后实际应用 5,750 次重配。完整调度的合法收益对旧 D 三胜两负，均值低 6.4 分。实际评估量少 12.73%，两次退步都伴随少三次校准。全场景实际评估量随重分配路径变化。

保留旧 D 为默认。重配可通过 `-Dautohyb.olTarget.edaPairing=ELITE` 单独复现。

[逐 seed 证据、审计口径与复现清单](../Evidence/feedback-ol-eda-pairing-id3/evidence.md)
