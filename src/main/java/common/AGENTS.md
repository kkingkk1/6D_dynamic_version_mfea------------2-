# common 模块摘要

## 模块职责

`common` 模块是 AutoHyb 进化算法框架的共享基础设施层，提供常量定义、参数校验、边界处理、随机数管理、6D 纯语义混合配置初始化、种群缩减与调优参数读取等通用能力，被外层 Global MFEA 自动设计、内层 HybCec 以及 GA、DE、PSO、ABC、SA、EDA、ACO、SHADE 等算法实现广泛依赖。

## 成员清单

| 文件 | 类名 | 职责 |
|------|------|------|
| AlgorithmConstants.java | `AlgorithmConstants` | 集中管理所有魔法数字、算法索引、操作级别码、操作顺序类型、混合级别、生存选择策略 |
| AlgorithmParameterValidator.java | `AlgorithmParameterValidator` | 通用参数校验工具，提供种群、适应度、索引、边界、配置、随机数生成器的守卫检查 |
| BoundaryHandler.java | `BoundaryHandler` | 多策略边界修复工具（裁剪、中点、反射、折叠、随机、收缩），含 PSO 速度/位置修复 |
| ConfigStringUtils.java | `ConfigStringUtils` | 数组与逗号分隔字符串之间的序列化/反序列化工具 |
| FastGaussian.java | `FastGaussian` | opt-in Gaussian 采样器；仅当 `autohyb.fastGaussian=true` 时由算法热路径调用，默认不影响 `Random.nextGaussian()` |
| HybridInitial.java | `HybridInitial` | 当前 6D 纯语义全局混合配置初始化器，供外层 MFEA 自动设计生成初始种群，插入策略固定为 GREEDY |
| RandomProvider.java | `RandomProvider` | 线程安全、确定性随机数提供器，固定种子(42)保证实验可复现 |
| ResizePop.java | `ResizePop` | L-SHADE 风格线性种群缩减（LPSR），含外部存档按比例裁剪 |
| TuningConfig.java | `TuningConfig` | 统一参数调优配置读取工具；加载 `.properties` 配置文件，提供带默认值的 `getInt/getDouble/getBoolean/getLong/getString(key, default)` 与无默认值的 `getInt/getDouble/getBoolean/getLong/getString(key)`（未配置时抛异常）两组方法；加载优先级：配置文件 > System Property > 默认值/异常 |
| TuningDefaults.java | `TuningDefaults` | 可调参数的硬编码默认值集中定义；纯常量类（`public final class`），所有字段均为 `public static final`；涵盖运行控制、重分配循环、迁移策略、候选排序、k_sat 权重、星内排序、高价值任务排序、Fast Refine、k_sat 反馈、热启动预算、Delta Fast Refine、Replacement/Swap/Bundle、TargetSatelliteRanker 低成本排序权重、固定 Top-K 默认值、CompositeStrategy 权重；不指定配置文件时各调用方使用这些常量作为回退默认值；当前默认值与 `tuning.properties` 的同名生效参数保持一致；`EVAL_KEY_PERTURB_THRESHOLD=1` 与 `EVAL_KEY_PERTURB_STRENGTH=0.02` 是 2026-05-17 GA 质量优先默认口径的一部分；`COORD_FAST_REFINE_ADJACENT_SWAP_ENABLED` 控制邻接交换默认开启；额外补充插入候选配置、delta fast refine eligibility guard 配置和卫星侧 `B_j` 排序配置已删除 |

## 接口说明

### AlgorithmConstants
纯常量/配置工具类（`public final class`）。所有字段均为 `public static final`，并提供少量静态方法用于当前 6D 配置校验与枚举语义解析。

主要常量分组：
- 种群/迭代参数：`DEFAULT_POPULATION_Factor`, `DEFAULT_ITERATION_COEFFICIENT`, `DEFAULT_BOUND`
- 概率阈值：`PROBABILITY_HALF`, `PROBABILITY_5_PERCENT`, `EPSILON`
- G2/G3 update policy：`FULL`(0)、`TOP_SUBSET`(1)、`MIXED_SUBSET`(2)、`RANDOM_DECAY`(3)、`ABOVE_MEAN`(4)、`LOCAL_SEARCH`(5)、`WORST_REPAIR`(6)
- 算法索引：主动父算法为 `ALGORITHM_INDEX_GA`(0) ~ `ALGORITHM_INDEX_ALNS`(10)；ID 11-15 保留为实现库归档尾部
- 操作顺序类型：`OPERATION_ORDER_SEQUENTIAL`(0) ~ `OPERATION_ORDER_ADAPTIVE_CREDIT`(7)
- 混合级别：`HYB_LEVEL_POPULATION`(0) ~ `HYB_LEVEL_COMPONENT`(3)
- G5 survivor policy：`ELITIST_BEST_N`(0)、`TOURNAMENT`(1)、`PAIRWISE_GREEDY`(2)、`RANK_WEIGHTED`(3)；旧 `PERMUTATION` / `CHAMPION` / `SERIAL_NUMBER` / `RANK_BASED` 常量名仅作为兼容别名

### AlgorithmParameterValidator
工具类（`public final class`，私有构造器），全部为静态方法。

| 方法 | 说明 |
|------|------|
| `validatePopulation(List<double[]>)` | 校验种群非空且维度一致 |
| `validateSelectIndices(int[], int)` | 校验索引数组在合法范围内 |
| `validateFitness(double[], int)` | 校验适应度数组长度匹配种群大小 |
| `validateFitness(List<Double>, int)` | 同上（List 重载） |
| `validateConfig(Object)` | 校验配置对象非空 |
| `validateRandom(Random)` | 校验 Random 非空 |
| `validateGeneration(int)` | 校验代数非负 |
| `validateGeneration(int, int)` | 校验代数在 [0, maxGen) 范围 |
| `validateMinPopulationSize(int, int, String)` | 校验种群满足算法最小规模 |
| `validateRange(String, double, double, double)` | 校验 double 值在 [min, max] |
| `validateRange(String, int, int, int)` | 校验 int 值在 [min, max] |
| `validatePopulationBounds(List<double[]>, double, double)` | 校验所有个体在决策变量边界内，使用浮点容差避免边界舍入误判，并输出高精度越界值 |
| `validateBounds(double, double)` | 校验上界 > 下界 |
| `validateCommonParameters(...)` | 组合校验便捷方法（3 个重载） |
| `validateSigma(List<double[]>, int, int)` | 校验 SA 步长因子数组 |
| `validateSAParameters(...)` | SA 专用组合校验 |

### BoundaryHandler
公开类，含内部枚举 `BoundaryMode`。

枚举值：`CLIP`, `MIDPOINT`, `REFLECT`, `RANDOM`, `SPECULAR_REFLECTION`, `RANDOM_REBOUND`, `FOLD_BACK_REFLECTION`, `SHRINK`

| 方法 | 说明 |
|------|------|
| `clip(double, double, double)` | 裁剪到 [lower, upper] |
| `clipArray(double[], double, double)` | 原地裁剪数组 |
| `clipVelocity(double, double, double)` | PSO 速度裁剪 |
| `clipMidpoint(double, double, double, double)` | SHADE 风格中点修复 |
| `reflect(double, double, double)` | 迭代反射（最多 10 次） |
| `reflectWithVelocity(double, double, double, double)` | 带速度反转的反射 |
| `reflectWithVelocityInPlace(...)` | 分配无关的 PSO 反射 + 速度反转 |
| `foldBackReflect(double, double, double)` | 折叠式反射 |
| `foldBackReflectArray(double[], double, double)` | 原地折叠反射数组 |
| `randomReinitialize(double, double, double, Random)` | 越界时随机重初始化 |
| `repairDE(double, double, double, double, Random, BoundaryMode)` | DE-family 边界修复调度，默认 RANDOM 路径保持旧行为，可切 MIDPOINT/REFLECT/CLIP |
| `randomRepair(double, double, double, double, Random)` | 边界附近随机修复 |
| `randomRepairPopulation(List<double[]>, double, double, double, Random)` | 批量随机修复种群 |
| `shrinkAlongDirection(double[], double[], double, double, double)` | 沿方向比例收缩 |
| `shrinkAlongDirectionInPlace(double[], double[], double, double, double)` | 原地收缩 |
| `repairPositionInPlace(...)` | PSO 多模式修复调度器 |
| `isInBounds(double, double, double)` | 单值边界检查 |
| `isArrayInBounds(double[], double, double)` | 数组边界检查 |

### ConfigStringUtils
工具类（`public final class`，私有构造器）。

| 方法 | 说明 |
|------|------|
| `arrayToString(int[])` | int 数组 → 逗号分隔字符串 |
| `arrayToString(double[])` | double 数组 → 逗号分隔字符串 |
| `stringToIntArray(String)` | 逗号分隔字符串 → int 数组 |
| `stringToDoubleArray(String)` | 逗号分隔字符串 → double 数组 |

### FastGaussian
工具类（`public final class`，私有构造器）。

| 方法 | 说明 |
|------|------|
| `isEnabled()` | 读取 `autohyb.fastGaussian`；默认 false |
| `nextGaussian(Random)` | 使用 Box-Muller 生成标准正态样本，并按线程缓存备用样本；调用方只在 opt-in 分支使用 |

### HybridInitial
工具类（`public class`，私有构造器）。

| 方法 | 说明 |
|------|------|
| `hybridInitial(int nPar, int nOL, int nOO, int nSS, int nPop)` | 生成 nPop 个 6 维整数染色体，编码算子组合（完全随机），确保 G[0]≠G[1] |
| `hybridInitial(int nPar, int nOL, int nOO, int nSS, int nPop, boolean useSeedConfigs)` | 生成 nPop 个 6 维整数染色体，可选择用精英配置种子化前 3-4 个个体，确保 G[0]≠G[1] |
| `getEliteConfigurations(int nPar, int nOL, int nOO, int nSS)` (private) | 返回 4 个已知优秀 6D 混合配置，用于外层 MFEA 自动设计暖启动 |

染色体编码（**约束：G[0]≠G[1]，确保混合算法语义**）：

```text
G[0] — 父代算法 1                范围: [0, 10]  (主动 nPar=11)
G[1] — 父代算法 2                范围: [0, 10]，且必须 ≠ G[0]
G[2] — update ratio 1           范围: [0, 6]  (nOL=7)
G[3] — update ratio 2           范围: [0, 6]  (nOL=7)
G[4] — operation order          范围: [0, 7]  (nOO=8)
G[5] — survivor strategy        范围: [0, 3]  (nSS=4)
```

G5 survivor policy：

| code | policy | 语义 |
|------|--------|------|
| 0 | `ELITIST_BEST_N` | 父代与子代合并后选 fitness top-N |
| 1 | `TOURNAMENT` | 父代与子代合并后做锦标赛生存选择 |
| 2 | `PAIRWISE_GREEDY` | offspring[i] 与 parent[i] 一对一贪心比较 |
| 3 | `RANK_WEIGHTED` | 父代与子代合并后按 rank 权重随机选择 |

`PopulationManager` 的 partial-update fast path 现在也按 G5 在被更新子集内执行局部 survivor；旧常量名只用于兼容旧测试和旧配置引用。

插入策略不占独立维度，当前 6D 版本在 `main.EvaluationHyb` 与 `main.RunSingleHybridConfig` 中固定使用 `GREEDY`；DE 运行时也已收敛为单一固定缩放因子，不再暴露额外运行参数。

约束实现位置：
- 初始化：`HybridInitial.hybridInitial()`
- 精英配置：`HybridInitial.getEliteConfigurations()`
- 6D 变异：`operator.mutation.MutationHyb.mutationHyb()`
- 全局自动设计入口：`main.MainMFEAMOPHOA`

### RandomProvider
工具类（`public final class`，私有构造器）。

| 方法 | 说明 |
|------|------|
| `get()` | 获取全局共享 Random 实例（种子 42） |
| `getThreadLocal()` | 获取线程本地 Random（确定性种子） |
| `newWithSeed(long)` | 工厂方法，创建指定种子的 Random |
| `reset()` | 重置全局 Random 到默认种子 |
| `reset(long)` | 重置全局 Random 到指定种子 |
| `resetThreadCounter()` | 重置线程计数器 |
| `resetThreadLocal()` | 重置当前线程 Random |
| `resetThreadLocal(long)` | 重置当前线程 Random 到指定种子 |

### ResizePop
公开类，含内部类 `ResizeResult`。

`ResizeResult` 字段：`pop`, `popFit`, `pbestS`, `pbestF`, `archive`, `nPop`

| 方法 | 说明 |
|------|------|
| `resizePop(List<double[]>, List<Double>, List<double[]>, List<Double>, ListArchive, int, int, int, int)` | L-SHADE 线性种群缩减，移除最差个体，按 1.4x 比例裁剪存档 |

### TuningConfig
工具类（`public final class`，私有构造器）。

| 方法 | 说明 |
|------|------|
| `getInt(String key)` | 读取必需 int 参数，未配置时抛 IllegalStateException |
| `getInt(String key, int defaultValue)` | 读取 int 参数，读不到返回默认值 |
| `getLong(String key)` | 读取必需 long 参数，未配置时抛 IllegalStateException |
| `getLong(String key, long defaultValue)` | 读取 long 参数 |
| `getDouble(String key)` | 读取必需 double 参数，未配置时抛 IllegalStateException |
| `getDouble(String key, double defaultValue)` | 读取 double 参数 |
| `getBoolean(String key)` | 读取必需 boolean 参数，未配置时抛 IllegalStateException |
| `getBoolean(String key, boolean defaultValue)` | 读取 boolean 参数 |
| `getString(String key)` | 读取必需字符串参数，未配置时抛 IllegalStateException |
| `getString(String key, String defaultValue)` | 读取字符串参数，读不到返回默认值 |
| `reload()` | 重置加载状态，用于测试时切换配置文件 |

加载优先级：`.properties` 配置文件 > System Property > 默认值。配置文件路径通过 `System.getProperty("tuning.config.path")` 指定。

### TuningDefaults
纯常量类（`public final class`，私有构造器），无方法。所有字段均为 `public static final`。

主要常量分组：
- A. 运行控制：`ITERATION_COEFFICIENT`
- B. 重分配循环控制：`EVAL_MAX_REASSIGN_ITERATIONS`, `EVAL_KEY_PERTURB_THRESHOLD=1`, `EVAL_KEY_PERTURB_STRENGTH=0.02`
- C. 迁移策略：`COORD_REASSIGN_STAGNATION_THRESHOLD` 等
- D. 候选目标星排序：`COORD_REASSIGN_PRIORITY_TASK_TOP_K`
- E. k_sat / 星内排序 / 高价值任务 / Fast Refine / k_sat 反馈权重
- F. 热启动与预算：`COORD_LOCAL_REFINE_BUDGET_RATIO` 等
- G. Delta Fast Refine：`COORD_DELTA_FAST_REFINE_MAX_CANDIDATE_POSITIONS`、`COORD_DELTA_FAST_REFINE_WINDOW_PREFERENCE`、`COORD_FAST_REFINE_ADJACENT_SWAP_ENABLED` 等
- H. Replacement / Swap / Bundle：`COORD_REPLACEMENT_MAX_TRIALS_PER_SAT` 等
- I. TargetSatelliteRanker 权重：任务-卫星配对低成本排序、任务侧条件项、extractPairFeatures 内部组合权重，以及 ordinary Top-K / prioritized Top-K 的默认值；卫星侧 `B_j` 权重与子项已删除
- J. CompositeStrategy 分配权重：`ASSIGN_COMPOSITE_WINDOW_LENGTH_WEIGHT` 等

## 模块依赖关系

- `AlgorithmConstants` → 无外部依赖
- `AlgorithmParameterValidator` → `java.util.List`, `java.util.Random`
- `BoundaryHandler` → `java.util.List`, `java.util.Random`
- `ConfigStringUtils` → 无外部依赖
- `FastGaussian` → `java.util.Random`
- `HybridInitial` → `java.util.Random`, `src.common.RandomProvider`
- `RandomProvider` → `java.util.Random`, `java.util.concurrent.atomic.AtomicLong`, `src.common.AlgorithmConstants`
- `ResizePop` → `java.util.List`, `src.algorithm.shade.UpdateArchive`, `utils.FitnessUtils`
- `TuningConfig` → `java.io.FileInputStream`, `java.util.Properties`（纯 JDK，无外部模块依赖）
- `TuningDefaults` → 无外部依赖
