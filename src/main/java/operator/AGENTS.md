# operator 模块摘要

本模块实现卫星调度优化中所需的全部进化算子，包括卫星分配策略、窗口插入策略、差分进化（DE）交叉/变异算子以及种群选择算子。该模块同时服务于外层 6D 纯语义 MFEA 自动设计配置的编码变异，以及内层 HybCec/重分配流程中的实际调度与选择。

## 模块结构

```
operator/
├── assignment/    卫星-任务分配策略（策略模式）
├── crossover/     DE 交叉算子
├── insertion/     窗口插入策略（策略模式 + 工厂模式）
├── mutation/      DE 变异算子 + 混合编码变异 + 工具类
├── selection/     种群/个体选择算子
└── AGENTS.md      本文件
```

## 成员清单

### assignment — 卫星分配策略

| 类名 | 类型 | 说明 |
|------|------|------|
| `AssignmentStrategy` | 接口 | 所有分配策略的根接口 |
| `AbstractAssignmentStrategy` | 抽象类 | 提供时间窗查找、可用卫星筛选等共享工具方法 |
| `RandomStrategy` | 具体策略 | 从可用卫星中随机选择 |
| `MinTaskCountStrategy` | 具体策略 | 选择已分配任务数最少的卫星 |
| `MinRollAngleStrategy` | 具体策略 | 选择滚转角绝对值最小的卫星 |
| `MinPriorityStrategy` | 具体策略 | 选择已分配任务平均优先级最低的卫星 |
| `EarliestTimeStrategy` | 具体策略 | 选择最早可用时间窗的卫星 |
| `MaxWindowLengthStrategy` | 具体策略 | 选择可用窗口总长度最大的卫星 |
| `MaxWindowCountStrategy` | 具体策略 | 选择可用时间窗数量最多的卫星 |
| `CompositeStrategy` | 具体策略 | 多维度加权 + 冲突感知 + 稀缺性自适应：综合窗口长度、窗口数量、负载均衡、时间窗口冲突度评分选星；候选卫星越少的任务（稀缺任务）自动放大窗口长度权重、缩小负载均衡权重，调节幅度由 `SCARCITY_BOOST` 控制 |
| `CompositeWithCapacityStrategy` | 具体策略 | 增强版 Composite 策略：综合窗口长度、窗口数量、负载均衡、冲突度评分 + 稀缺性自适应加权 + 容量感知惩罚，选 composite 得分最高的候选卫星 |

### crossover — DE 交叉算子

| 类名 | 类型 | 说明 |
|------|------|------|
| `CrossoverDE` | 工具类(final) | 标准 DE 二项式交叉，支持索引模式和无校验快速模式 |
| `EigenCrossover` | 工具类(final) | 基于协方差特征分解的坐标旋转交叉，失败时回退到标准二项式交叉 |

### insertion — 窗口插入策略

| 类名 | 类型 | 说明 |
|------|------|------|
| `InsertionMode` | 枚举 | 定义 8 种插入策略模式：GREEDY, MIN_TRANSITION, MAX_SLACK, SHORTEST_WINDOW_FIRST, EARLIEST_DEADLINE_FIRST, RANDOM, LONGEST_WINDOW_FIRST, MAX_REMAINING_CAPACITY |
| `InsertionStrategy` | 接口 | 插入策略根接口，定义 `findBestPosition()` 方法和 `InsertionResult` 内部类 |
| `AbstractInsertionStrategy` | 抽象类 | 提供 `findInsertionIndex()` 和 `isOverlapping()` 共享辅助方法 |
| `GreedyInsertion` | 具体策略 | 贪婪插入：默认逐窗尝试第一个可行起点；窗口偏好路径会先按独立 `windowScore` 排序，再按排序结果尝试；窗口评分当前由更长窗口、更早开始时刻与稳定噪声共同决定；窗口偏好统计可通过 `planutils.windowPreferenceStats=true` opt-in 打开；热路径避免 `RankedInsertionAttemptResult` 包装、窗口 foreach iterator，并为 GREEDY 调度生成路径提供可复用结果 carrier 以跳过 `InsertionResult` 分配；`DecodeWorkspace` 直评路径可注入 workspace-owned `ScheduledTask` provider 复用临时调度对象；空 schedule 直接使用第一个可容纳窗口的第一个可行起点；候选起点复用单调推进的 insertion index 并缓存相邻任务与时间边界，跨窗口 start time 回退时回到 binary search；对相邻任务间隔先用最小姿态转换时间下界剪枝，候选起点跳跃先用姿态记录时间估算索引并做有界局部校正，校正失败再回退 binary search |
| `MinTransitionInsertion` | 具体策略 | 最小转换时间插入：选择转换时间最小的窗口位置 |
| `MaxSlackInsertion` | 具体策略 | 最大松弛度插入：选择转换时间最大的可行位置，为后续任务留出最大间隙 |
| `ShortestWindowFirstInsertion` | 具体策略 | 最短窗口优先：优先选择时间跨度最短的窗口 |
| `EarliestDeadlineFirstInsertion` | 具体策略 | 最早截止时间优先：优先选择截止时间最早的窗口 |
| `RandomInsertion` | 具体策略 | 随机插入：从所有可行窗口中随机选择一个 |
| `LongestWindowFirstInsertion` | 具体策略 | 最长窗口优先：优先选择时间跨度最长的窗口 |
| `MaxRemainingCapacityInsertion` | 具体策略 | 最大剩余容量：选择插入后剩余空闲时间最多的窗口 |
| `InsertionStrategyFactory` | 工厂类(final) | 根据 InsertionMode 返回对应的策略实例（单例缓存） |

### mutation — DE 变异算子

| 类名 | 类型 | 说明 |
|------|------|------|
| `DEUtils` | 工具类(final) | 变异算子共享工具：随机索引选择、适应度索引查找等 |
| `MutationDERand1` | 工具类(final) | DE/rand/1: `v = x_r1 + F*(x_r2 - x_r3)` |
| `MutationDERand2` | 工具类(final) | DE/rand/2: `v = x_r1 + F1*(x_r2-x_r3) + F2*(x_r4-x_r5)` |
| `MutationDEBest1` | 工具类(final) | DE/best/1: `v = x_best + F*(x_r1 - x_r2)` |
| `MutationDEBest2` | 工具类(final) | DE/best/2: `v = x_best + F1*(x_r1-x_r2) + F2*(x_r3-x_r4)` |
| `MutationDECurrentToBest` | 工具类(final) | DE/current-to-best/1: `v = x_i + F1*(x_best-x_i) + F2*(x_r1-x_r2)` |
| `MutationDECurrentToRand` | 工具类(final) | DE/current-to-rand/1: `v = x_i + F1*(x_r1-x_i) + F2*(x_r2-x_r3)` |
| `MutationDERandToBest` | 工具类(final) | DE/rand-to-best/1: `v = x_r1 + F1*(x_best-x_r1) + F2*(x_r2-x_r3)` |
| `MutationHyb` | 工具类 | 混合算法编码变异，仅公开当前 6D 纯语义编码变异入口 `mutationHyb`，供外层自动设计搜索使用 |

### selection — 选择算子

| 类名 | 类型 | 说明 |
|------|------|------|
| `Tournament` | 工具类 | k-锦标赛选择，支持单亲/双亲/多亲选择 |
| `SurvivorSelect` | 工具类 | 环境选择：`ELITIST_BEST_N`、`TOURNAMENT`、`PAIRWISE_GREEDY`、`RANK_WEIGHTED`，旧方法名保留为兼容 wrapper |

## 核心接口说明

### AssignmentStrategy 接口

```java
public interface AssignmentStrategy {
    Satellite selectSatellite(Task task, List<Satellite> availableSatellites,
                              List<Satellite> allSatellites, Map<Integer, Integer> satelliteIndexMap);
    String getName();
}
```

### InsertionStrategy 接口

```java
public interface InsertionStrategy {
    InsertionResult findBestPosition(Task task, int satelliteId, List<ScheduledTask> currentSchedule);

    // 内部类
    class InsertionResult {
        ScheduledTask getTask();
        int getInsertIndex();
    }
}
```

### InsertionStrategyFactory 工厂方法

```java
public static InsertionStrategy getStrategy(InsertionMode mode)
```

### CrossoverDE 公共方法

```java
// 推荐使用，含完整参数校验
static List<double[]> crossoverIndexed(List<double[]> mutantPop, List<double[]> fullTargetPop,
    int[] selectIndices, double crossRate, Random customRand)

// 无校验版本，适用于性能敏感的紧密循环
static List<double[]> crossoverIndexedUnsafe(List<double[]> mutantPop, List<double[]> fullTargetPop,
    int[] selectIndices, double crossRate, Random customRand)
```

### EigenCrossover 公共方法

```java
static List<double[]> performEigenCrossover(List<double[]> pop, int[] selectedIndices,
    List<double[]> vi, double[] shadeCR, List<Integer> sortIndex,
    int neighbourSelectSize, Random random)
static String getEigenCrossoverStats()
static void resetEigenCrossoverStats()
```

### DE 变异算子通用签名

所有 DE 变异类均提供 `mutate` 静态方法（`MutationDECurrentToRand` 为 `mutateIndexed`），参数模式：
```java
static List<double[]> mutate(List<double[]> pop, int[] selectIndices,
    [int bestIndex,] double F [, double F2],
    double upperBound, double lowerBound, Random customRand)
```

### SurvivorSelect 公共方法

```java
static SurvivorSelectResult survivorSelect(List<double[]> offspringPop, List<double[]> parentPop,
    List<Double> offspringFit, List<Double> parentFit, int nPop, int strSurvive [, Random random])
```
`strSurvive` 当前语义为：0=`ELITIST_BEST_N`，1=`TOURNAMENT`，2=`PAIRWISE_GREEDY`，3=`RANK_WEIGHTED`；旧命名仅作兼容别名。

### GREEDY 现状与优化判断

- GREEDY 的普通与窗口偏好扫描使用 `TimeWindow.getAttitudeRecordTimesUnsafe()` 读取秒数缓存，先检查最小转换时间间隔，再获取姿态记录对象。缓存不适用时走原对象读取路径；候选顺序和首个可行点规则不变。
- `GreedyInsertion` 默认是逐窗“第一个可行点”实现；窗口偏好路径会先做窗口排序，再逐窗尝试可行起点。
- `PlanUtils.generateSchedule(..., true, ...)` 和 `buildPlanByLimitedInsertion(..., true, ...)` 可以把同一条窗口偏好路径只开给选定任务；`DeltaFastRefiner` 默认也会把这条路径接到有限候选插入上。
- 如果继续优化 `GREEDY`，优先看 `findFirstFeasibleInsertion()` 的窗口内起点剪枝、边界过滤和 `ScheduledTask` 分配；`MAX_REMAINING_CAPACITY` 更偏窗口级选择，不适合作为主要优化方向。
- 详细 GREEDY 优化历史、撤回项和 JFR 证据见 `vault/Knowledge/Operator-GREEDY-Optimization-History.md`；模块摘要只保留当前实现判断。

## 外部依赖

| 依赖 | 使用者 | 用途 |
|------|--------|------|
| `src.common.BoundaryHandler` | 所有 DE 变异类 | 越界修复 |
| `src.common.AlgorithmConstants` | Tournament, SurvivorSelect | 策略/操作级常量 |
| `src.common.RandomProvider` | MutationHyb, Tournament, SurvivorSelect, RandomInsertion | 共享随机数实例 |
| `model.Satellite / Task / TimeWindow` | assignment 子包, insertion 子包 | 领域模型 |
| `model.ScheduledTask / AttitudeRecord` | insertion 子包 | 调度任务和姿态记录 |
| `common.AlgorithmConstants` | SurvivorSelect | G5 survivor policy 常量 |
| `utils.TimeUtils` | insertion 子包 | 姿态转换时间检查 |
| `org.apache.commons.math3` | EigenCrossover | 特征分解、协方差、欧氏距离 |

