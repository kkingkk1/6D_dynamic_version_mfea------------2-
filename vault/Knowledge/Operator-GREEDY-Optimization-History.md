---
type: knowledge
title: Operator GREEDY 优化历史
project: 6d-dynamic-version-mfea
updated: 2026-07-01
---

# Operator GREEDY 优化历史

本文件保存 `operator.insertion.GreedyInsertion` 相关历史证据。
模块级 `src/main/java/operator/AGENTS.md` 只保留当前判断和本文件链接。

## 当前结论

- `GreedyInsertion` 默认是逐窗“第一个可行点”实现。
- 窗口偏好路径会先做窗口排序，再逐窗尝试可行起点。
- 继续优化时优先看 `findFirstFeasibleInsertion()` 的窗口内起点剪枝、边界过滤和 `ScheduledTask` 分配。
- `MAX_REMAINING_CAPACITY` 更偏窗口级选择，不适合作为主要优化方向。

## 历史证据

- 2026-05-20 ALNS JFR 显示，直接把 `InsertionResult` 改成 PlanUtils 内部 direct insert 会使 ID1 `10,1,0` 三连跑变慢到 `70.69s / 71.41s / 67.76s`，no-stats split 也变慢到 `68.76s / 61.81s / 62.13s`，均已撤回。
- 保留的安全改动先删除 `RankedInsertionAttemptResult`，并把窗口 foreach 改为 index loop。
- 2026-05-22 保留通用 `InsertionStrategy` 合约，仅让 `PlanUtils` 的 GREEDY 调度生成路径复用 `GreedyInsertion.ReusableInsertionResult`；JFR 中 `InsertionStrategy$InsertionResult` 已退出 allocation-by-class，`ScheduledTask` 仍是必要输出对象。
- 2026-05-22 后续把同一窗口内的重复 `findInsertionIndex` binary search 改为单调推进；A0 在 ID1/ID3/ID5 同 seed 利润不变，Avg elapsed 分别为 `71.23s -> 38.39s`、`21.30s -> 13.33s`、`14.62s -> 9.68s`。
- 后续 JFR 显示 `advanceInsertionIndex()` 成为主 CPU 热点，继续缓存相邻任务与时间边界后，A0 利润仍逐 run 不变，Avg elapsed 进一步为 ID1 `24.00s`、ID3 `9.57s`、ID5 `6.56s`。
- 再把 cursor 扩到跨窗口单调复用后，`findInsertionIndex()` JFR 样本从 `64.25%` 降到 `0.76%`，A0 标准口径 Avg elapsed 为 ID1 `23.72s`、ID3 `9.67s`、ID5 `6.52s`。
- 再加入最小姿态转换时间下界剪枝后，A0 利润仍逐 run 不变，Avg elapsed 为 ID1 `19.02s`、ID3 `6.38s`、ID5 `4.76s`。
- A37 默认下继续把窗口偏好统计改为 opt-in，并让最小间隔下界失败时二分跳到下一个可能起点；ID1/ID3/ID5 `nRun=5` 同 seed 收益保持，Avg elapsed 为 `15.57s / 5.61s / 3.88s`。
- 空 schedule 快路径直接返回第一个可容纳窗口的第一个可行起点，ID1 A37 `nRun=5` 收益保持 `2737.80/2741.00`，Avg elapsed `15.57s -> 14.43s`；ID3/ID5 `nRun=3` 收益保持 `2656.33/4374.34`。
- 共享 `findInsertionIndex()` 首尾边界 fast path、延迟读取 `candidateEnd`、预计算 interval 的 `TimeUtils` overload、primitive window-rank 均未产生稳定收益，已撤回。
- 2026-05-23 保留 start-index estimate：候选起点跳跃先按姿态记录时间估算索引，再做有界局部校正，校正失败回退 binary search；ID1/ID3/ID5 A37 `nRun=10` 收益保持 `2735.50/2639.90/4373.30`，总 wall `223.83s`，低于 current confirm `242.85s`。
