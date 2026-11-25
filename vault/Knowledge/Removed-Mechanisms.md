---
type: knowledge
title: 已移除机制
project: 6d-dynamic-version-mfea
updated: 2026-11-24
---

# 已移除机制

本页记录已从主线移除、但后续容易误恢复的机制。根 `AGENTS.md` 只写当前行为；删除理由、证据入口和恢复条件放在这里。

## D 的整场等评估量试验

撤回 ID3 试验的 `sceneFesBudget` 开关、预算截停和末尾补足。D 恢复此前的重分配停机和校准路径。若需复核历史试验，使用[等评估量证据与当时源码](../Results/Evidence/feedback-ol-equal-fes-id3/evidence.md)。

## 3D OA1-only 单算法入口

- 已移除：`RunSingleParentConfig` 的 `{algorithmIndex,updateRatioCode,survivorStrategy}` 配置、`HybCec.singleParentMode` 和 OA1-only 执行路径。
- 当前行为：入口只接收 `{algorithmIndex}`；`TaskAllocationCoordinator` 保留动态重分配，并直接调用 `SingleAlgorithmOptimizer.optimize()`；候选使用一对一 greedy replacement。
- 证据入口：旧 OA1-only 调参与配对结果保留在 `vault/Results/Reports/` 和 `vault/Knowledge/Source-Inventory.md`，只解释历史决策，不作为新 1D 路径的收益基线。
- 恢复条件：若需要复查旧结果，应使用独立历史 checkout；不要在当前入口恢复多维兼容解析或 `singleParentMode`。

## 校准 bigGain 触发条件

- 已移除：`profitGain > bestTotalProfit * 0.005` 大规模任务中途校准触发条件。
- 当前行为：大规模任务中途校准只按 `CALIBRATION_INTERVAL` 和最后一轮触发；末尾 final calibration 保留。
- 证据入口：`vault/Results/Reports/2026-05-19-plan-stage-details-archive.md` 和 `vault/Knowledge/Source-Inventory.md`。
- 恢复条件：同预算跨场景证据显示稳定收益，且 wall time 不回退。

## Delta Fast Refine 额外插入候选

- 已移除：6D 专属的额外 limited insertion 候选位置通路。
- 当前行为：delta fast refine 的 limited insertion 使用基础候选位置，以及 replacement/swap 原任务位置附近的锚点候选。
- 证据入口：`vault/Results/Reports/2026-05-19-plan-stage-details-archive.md` 和 `vault/Knowledge/Source-Inventory.md`。
- 恢复条件：作为独立 opt-in 实验分支重新引入，并重新检查 8D 语义对齐。

## 候选星卫星侧 B_j

- 已移除：候选星排序中的卫星侧 `B_j` 通路。
- 当前行为：cheap rank 使用任务-卫星配对特征和任务侧条件项；`k_sat(i,s)` 读取 `clip01(baseScore(i,s)+feedbackDelta(i,s))`。
- 证据入口：`vault/Results/Reports/2026-05-19-plan-stage-details-archive.md` 和 `vault/Knowledge/Source-Inventory.md`。
- 恢复条件：新证据证明卫星侧条件项能改善跨场景结果，且不破坏 6D/8D 语义对齐。

## 重分配 tabu 机制

- 已移除：`eval.tabuTenure`、tabu 表、blocked-history 指标、目标星回迁过滤和 tabu 写回。
- 当前行为：候选目标星选择不做 tabu 过滤。
- 证据入口：`vault/Results/Reports/2026-05-19-plan-stage-details-archive.md` 和 `vault/Knowledge/Source-Inventory.md`。
- 恢复条件：可比固定基线批次观测到 no-tabu 明确回退。

## Delta Fast Refine eligibility guards

- 已移除：新增任务数、单轮变化比例和累计变化比例 eligibility guard。
- 当前行为：这些 eligibility guard 不参与当前主线行为；相关运行时键不属于当前主线配置。
- 证据入口：`vault/Results/Reports/2026-05-19-plan-stage-details-archive.md` 和 `vault/Knowledge/Source-Inventory.md`。
- 恢复条件：guard-on vs guard-off A/B 显示稳定收益，或能阻止已确认的失败模式。
