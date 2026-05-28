---
type: meta
title: 代码库概览
project: 6d-dynamic-version-mfea
updated: 2026-05-15
---

# 代码库概览

- **仓库根目录**：`6D_dynamic_version_mfea/`
- **语言**：Java
- **构建方式**：Maven，入口配置见 `pom.xml`

## 模块架构

```text
main → core → strategy → algorithm → operator → common → model/utils
```

### model（叶子层，无上层依赖）

领域对象层，包含 `Task`、`Satellite`、`TimeWindow`、`AttitudeRecord`、`ScheduledTask`、`SchedulingPlan`、`SatelliteTaskPair`。

### utils（依赖 model 和 operator.insertion）

`PlanUtils.decode()` 将连续向量映射为任务序列；`evaluatePlan()` 通过插入启发式生成具体调度方案。

### common（依赖 model 和 utils）

共享基础设施包括 `AlgorithmConstants`、`BoundaryHandler`、`HybridInitial`、`EliteConfigArchive`、`RandomProvider`、`ResizePop`、`TuningConfig/Defaults`、`ConfigStringUtils`。

### operator（依赖 model、utils、common）

包含五类算子：

- `assignment/`：9 种卫星选择策略，统一接口为 `AssignmentStrategy`。
- `insertion/`：8 种任务插入策略，统一接口为 `InsertionStrategy`，并由单例工厂管理。
- `crossover/`：DE 二项交叉和基于特征分解的旋转交叉。
- `mutation/`：7 种 DE 变异公式，以及混合整数数组变异。
- `selection/`：操作级掩码、锦标赛选择和 4 种生存选择策略。

### algorithm（依赖 operator 和 common）

实现库保留 16 个算法索引，但当前 6D 混合搜索只暴露 ID 0 到 10 的 11 个主动父算法：

- 主动父算法：GA、PSO、EDA、ACO、DE/rand/1、DE/best/1、DE/current-to-rand/1、ABC、SA、L-SHADE、ALNS。
- 归档尾部算法：DE/rand/2、DE/best/2、DE/current-to-best/1、DE/rand-to-best/1、SHADE。

### strategy（依赖 algorithm）

把算法实现统一封装到 `ParentStrategy.apply(ParentContext, StrategyInput)` 后面。当前 6D 搜索只从前 11 个主动父算法中选取；归档尾部算法保留实现和索引，但不作为 `RunSingleHybridConfig` 与外层 MFEA 的候选父算法。ABC、SA、SHADE/L-SHADE 等带副作用算法通过 `StateUpdater` 回写状态。

### core（依赖 strategy、common、model、utils）

核心执行层包括 `HybCec` 主循环、`HybCecState` 运行状态、`CreditManager` 自适应信用路由、`FitnessManager`、`PopulationManager`、`PopulationResizer` 和 `HybridLevelCalculator`。其中 `HybridLevelCalculator` 负责 G2/G3 update policy 掩码；`TOP_SUBSET` / `MIXED_SUBSET` 使用固定 `0.5` 子集比例，`RANDOM_DECAY` 使用递减随机子集，`MIXED_SUBSET` 可由 `hybcec.mixedTopRatio` 控制 top-fitness 个体占比。`HybCec.updateEnableParents()` 负责 G4 operation-order policy，当前包含 serial、periodic、stage、best-no-improvement、process-no-improvement、diversity、parallel 和 adaptive-credit 八类。

### main（依赖 core、utils、model、common、operator.assignment）

- `MainMFEAMOPHOA`：自动设计主入口，在 11 个主动父算法的 6D 空间内搜索混合配置，用于寻找超过固定基线 `{4,1,0,0,0,0}` 的候选配置。
- `RunSingleHybridConfig`：程序入口，默认 6D 配置为 `{4,1,0,0,0,0}`。
- `TaskAllocationCoordinator`：动态重分配引擎，包含标准迁移、替换、交换、任务束 4 类移动的级联；当前不维护 tabu 表，也不做回迁禁忌过滤；小规模任务刷新 best 后立即用热启动 HybCec 做完整校准，大规模任务才延迟到 final calibration 兜底；大规模 `profitGain > bestTotalProfit * 0.005` 触发条件已删除。
- `TargetSatelliteRanker`：单阶段低成本候选目标星排序器，按固定 Top-K 返回目标星；卫星侧 `B_j` 通路已删除，排序只保留任务-卫星配对特征和任务侧条件项。
- `DeltaFastRefiner`：基于上一轮锚点计划做有限候选插入和邻接交换；新增任务数、单轮变化比例和累计变化比例 eligibility guard 均已移除。新增任务数 cap 从 `3` 放宽到 `2147483647` 的 A/B 在 ID1/ID3/ID5 上未发现行为差异，删除后 ID1 固定基线仍不变；额外补充候选位置已删除以对齐 8D。

## 适应度桥接

```text
double[nPop][D] 连续种群
  → PlanUtils.decode()
  → 任务序列
  → evaluatePlan() 插入启发式
  → SchedulingPlan
  → 以总任务优先级收益作为适应度
```

## 运行时开关

- `hybcec.mixedTopRatio`：控制 `MIXED_SUBSET` update policy 中 top-fitness 个体占比。
- `taskcoord.deltaFastRefine.enabled`：控制 delta fast refine 是否启用；关闭后受影响卫星回退到局部 HybCec 重算。
- `eval.tabuTenure` 已删除，不再是运行时配置项。
