---
type: meta
title: 架构深挖
project: 6d-dynamic-version-mfea
updated: 2026-05-16
---

# 架构深挖

## 数据流

```text
DataLoader → Initialize（任务-卫星初始分配）
  → MainMFEAMOPHOA（外层 MFEA 自动设计，搜索 6D 配置）
    → EvaluationHyb（评估候选 6D 配置的平均收益）
    → 保存超过固定基线的候选配置，用于后续复现实验
  → RunSingleHybridConfig（固定 6D 配置复现与基线对照）
    → TaskAllocationCoordinator.scheduleWithReassignment()
      → 初始评估：每颗卫星运行 2 次独立 HybCec，取最优结果
      → 每颗卫星执行 HybCec.run()
        → double[nPop][D] → PlanUtils.decode() → evaluatePlan() → 适应度
        → HybridLevelCalculator 构造 G2/G3 update policy 掩码
      → 收集未调度任务
      → 停滞达到 1 轮后触发重分配级联：
        1. 标准迁移（TargetSatelliteRanker：低成本排序 -> 固定 Top-K）
        2. 替换移动（一对一替换 → 最多移除 3 个任务的批量替换）
        3. 交换移动（2 到 3 颗卫星的联合增量评估）
        4. 任务束移动（2 到 3 个任务的聚簇联合增量评估）
      → 当前不使用 tabu 回迁过滤；候选目标星只由时间窗可行性、低成本排序和固定 Top-K 控制
      → 增量评估：可继承状态走快速微调，不适用时走 HybCec 重优化
      → 返回历史最优
```

## 6D 配置向量

| 维度 | 含义 |
|---|---|
| 0 | 父算法 1（当前主动库 ID 为 0 到 10） |
| 1 | 父算法 2（当前主动库 ID 为 0 到 10，且不同于维度 0） |
| 2 | update policy 1 |
| 3 | update policy 2 |
| 4 | 执行顺序 |
| 5 | 生存选择策略 |

默认配置为 `{4, 1, 0, 0, 0, 0}`。运行时插入策略固定为 `GREEDY`，DE 缩放因子固定为单一取值。

G2/G3 当前暴露 7 个 update policy：`FULL`、`TOP_SUBSET`、`MIXED_SUBSET`、`RANDOM_DECAY`、`ABOVE_MEAN`、`LOCAL_SEARCH`、`WORST_REPAIR`。其中 `TOP_SUBSET` 和 `MIXED_SUBSET` 使用固定子集比例 `0.5`；`RANDOM_DECAY` 是唯一带 decay schedule 的随机子集；旧 70%、50%、30%、15% 不再作为组件库档位。

G4 当前暴露 8 个 operation-order policy：`SERIAL`、`PERIODIC_SWITCH`、`STAGE_SWITCH`、`BEST_NO_IMPROVEMENT_SWITCH`、`PROCESS_NO_IMPROVEMENT_SWITCH`、`DIVERSITY_SWITCH`、`PARALLEL`、`ADAPTIVE_CREDIT`。`BEST_NO_IMPROVEMENT_SWITCH` 使用 `gbest` 停滞计数；`PROCESS_NO_IMPROVEMENT_SWITCH` 使用 `itera - lastProcessImproveItera`；`DIVERSITY_SWITCH` 使用连续种群向量 normalized std，默认阈值为 `0.02`。

## 主动父算法与归档尾部

| 范围 | ID | 算法 |
|---|---|---|
| 当前 6D 搜索主动父算法 | 0-10 | GA、PSO、EDA、ACO、DE/rand/1、DE/best/1、DE/current-to-rand/1、ABC、SA、L-SHADE、ALNS |
| 实现库归档尾部 | 11-15 | DE/rand/2、DE/best/2、DE/current-to-best/1、DE/rand-to-best/1、SHADE |

主动父算法数量由 `AlgorithmConstants.HYBCEC_ACTIVE_PARENT_ALGORITHM_COUNT = 11` 控制。归档尾部保留代码路径和索引，主要用于兼容、对照和历史实验，不进入当前混合配置搜索空间。

## 策略模式

所有算法都封装在 `ParentStrategy.apply(ParentContext, StrategyInput)` 后面：

- `ParentContext` 保存共享状态，包括维度、领域对象、随机数、迭代计数和算法专用子上下文。
- `StrategyInput` 保存种群、被选中个体索引、适应度、pbest 和 gbest。
- 带副作用的算法通过 `StateUpdater` 回写运行时状态。

## 目标星排序器 TargetSatelliteRanker

候选目标星排序使用单阶段固定预算：

1. 低成本排序：使用任务优先级、约束紧度、未调度压力、窗口数量、窗口长度、最早开始时间和 `k_sat(i,s)`；卫星侧 `B_j` 通路已删除，不再维护候选星负载、积压或成功率 prior。
2. 固定 Top-K 输出：普通任务默认 Top-2，prioritized 任务默认 Top-4。
3. 排序器输出的候选星数量只由 `ranker.ordinaryTopK` 和 `ranker.prioritizedTopK` 控制。

## 动态重分配裁剪策略

- 每轮迁移预算保留为工程 guard：默认每轮最多接受 `min(ceil(未调度任务数 * 0.20), 12)` 个迁移，至少 1 个。
- tabu 回迁禁忌已删除。系统不再维护任务-卫星 tabu 表，也不再记录 blocked-history；standard、replacement、swap 和 bundle 移动都直接使用当前候选星集合。
- 2026-05-15 的 no-tabu 消融显示：ID1 均值比原 `tabuTenure=2` 高 2.00，ID3/ID5 无差异。删除后 ID1 固定基线为 `Avg profit=2738.67`、`Best profit=2741.00`。

## 关键运行时开关

- `DEFAULT_ENABLE_DELTA_FAST_REFINE`：基于锚点计划做插入和邻接交换。
- `DEFAULT_ENABLE_LOCAL_REFINE_HOT_START_BUDGET`：回退重跑 HybCec 时使用热启动预算。
- `hybcec.mixedTopRatio`：`MIXED_SUBSET` 中 top-fitness 个体占比，默认 `0.8`。
- 前两个开关可通过命令行参数覆盖。

## Delta Fast Refine 与 8D 对齐结论

- `feedback/effective score` 标量语义与 8D 一致：`effective = clip01(baseScore(task,sat) + feedbackDelta(task,sat))`。`baseScore` 由窗口数量、总窗口长度、最早开始时间和随机项生成；成功反馈为 `+0.08`，失败反馈为 `-0.01`。
- 6D 与 8D 在 ID1 同 seed 下从 `99.56%` 对齐到 `99.64%` 的关键不是 feedback 标量，而是去掉 6D 额外加入的 limited insertion 候选位置。
- 该候选增强曾只在基础 limited insertion 未成功插入新增任务时触发，会补充窗口重叠附近、窗口时间边界附近和当前 schedule gap 附近的插入下标；该实现和配置键已删除。
- 当前默认对齐 8D：保留基础候选位置、被移除任务原位置附近采样、窗口偏好和邻接交换；不再保留额外补充候选开关。
- Delta fast refine 的新增任务数、单轮变化比例和累计变化比例 eligibility guard 均已删除。删除新增任务数 guard 后，ID1 固定基线仍为 `Avg profit=2738.67`、`Best profit=2741.00`。
