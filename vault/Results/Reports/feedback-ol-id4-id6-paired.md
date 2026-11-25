---
type: results-report
status: active
evidence_package: Results/Evidence/feedback-ol-id4-id6-paired
---

# ID4 和 ID6 旧反馈与自动设计对照

## 研究问题

ID3 筛选出的旧反馈在两个新场景上，能否提高相对于已归档自动设计配置的整数调度收益？

## 发现

- ID4 五个 seed 的 A 与 D 都是 5,050 分，收益率为 92.59%。ID6 五个 seed 均为 10,693 分，收益率为 98.44%。
- D 两场景都在初始调度排完已分配的任务。每次尝试 7 轮重分配，接受迁移计数为 0，收益仍与初始值相同。
- D 在优化中按反馈调整名额，ID4 记录 424 次，ID6 记录 668 次。

## 限制

两场景各五个 seed。A 取归档适应度四舍五入所得的整数收益，D 取终局核验后的合法收益。A 和 D 的种群规模与每星名义评估预算不同。

## 决策

两场景均记录为旧反馈与已归档自动设计的整数收益相同。

## 后续

保留现有基线来源和逐 seed 配对数据，供后续场景比较。

## 证据

[对照合同、逐 seed 数据与复现清单](../Evidence/feedback-ol-id4-id6-paired/evidence.md)
