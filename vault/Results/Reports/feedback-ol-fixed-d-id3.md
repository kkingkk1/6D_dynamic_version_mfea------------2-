---
type: results-report
status: active
evidence_package: Results/Evidence/feedback-ol-fixed-d-id3
---

# ID3 旧 D 的计分与轮换对照

以旧 D 为基线做了两项单独改动。保留 16 次窗口、25% 名额下限、每轮 98 次评估和完整重分配。每项各跑 ID3 的五个同 seed。

| 方法 | 合法收益均值 | 相对旧 D | 实际评估均值 |
|---|---:|---:|---:|
| 自动设计 A | 2,669.2 | +1.0 | 1,117,200 |
| 旧 D | 2,668.2 | — | 1,078,000 |
| 线下提分计分 | 2,650.8 | −17.4 | 1,038,800 |
| EDA、GA 独立轮换 | 2,668.6 | +0.4 | 1,136,800 |

线下提分计分在五个 seed 上都低于旧 D。独立轮换均值距自动设计 0.6 分，实际评估量比旧 D 多 5.45%。保留旧 D 为默认。

[逐 seed 证据与复现清单](../Evidence/feedback-ol-fixed-d-id3/evidence.md)
