# core 模块摘要

## 模块职责

`core` 模块是 AutoHyb 混合进化算法框架的核心引擎层，负责 HybCec 主循环调度、种群管理、适应度评估、adaptive-credit 路由、混合级别掩码计算、状态维护与配置管理，并作为外层 Global MFEA 自动设计与内层单星优化之间的执行中枢。当前包含多个子包共 15 个 Java 文件，是连接 `algorithm`（算法实现）、`strategy`（策略模式）和 `common`（基础设施）的中枢。

## 成员清单

| 文件 | 类名 | 子包 | 职责 |
|------|------|------|------|
| FitnessEvaluator.java | `FitnessEvaluator` | (根) | 外置适应度评估接口，供 HybCec 与测试/替代评估器解耦 |
| HybCec.java | `HybCec`, `HybResult` | (根) | 主控制器，接收由 `main.EvaluationHyb` 解码后的 6D 纯语义 hybrid 配置，或由 `main.RunSingleParentConfig` 构造的 OA1-only 单算法运行配置，编排初始化→迭代→评估→结果返回的完整生命周期；`HybResult` 同步返回 best-fitness 曲线和对应 eval 计数 |
| HybridLevelCalculator.java | `HybridLevelCalculator` | calculator | 有状态的混合级别计算器，封装 G2/G3 update policy 掩码生成、个体子集选择与校验逻辑；随机子集选择使用当前 HybCec 运行持有的 `Random`，不再读取静态 thread-local 随机源 |
| AlgorithmIndex.java | `AlgorithmIndex` | config | 枚举，映射算法类型到 flagPar 数组索引；当前 6D 搜索只暴露 ID 0-10，ID 11-15 为实现库归档尾部 |
| ConfigValidatable.java | `ConfigValidatable`, `ValidationResult`, `ValidationResultBuilder` | config | 配置参数校验接口与流式构建器 |
| HybCecConfig.java | `HybCecConfig` | config | 配置序列化类，支持 Properties 文件读写；Phase D opt-in 参数带默认安全回退 |
| HybCecConfigManager.java | `HybCecConfigManager` | config | 集中式配置管理器，按激活标志初始化各算法配置 |
| HybCecExecutionException.java | `HybCecExecutionException` | exception | 自定义受检异常，用于执行期错误 |
| CreditManager.java | `CreditManager` | manager | adaptive-credit 路由管理器，按滑动窗口记录 OA 收益 / evalCost，输出 OA1 路由概率 |
| FitnessManager.java | `FitnessManager` | manager | 适应度评估与最优解更新，性能关键热路径 |
| PopulationManager.java | `PopulationManager` | manager | 种群选择、准备与更新的完整生命周期管理（模块最大文件） |
| PopulationResizer.java | `PopulationResizer` | manager | L-SHADE 线性种群缩减（LPSR）实现；archive 裁剪随机顺序使用当前 HybCec 运行持有的 `Random` |
| HybCecState.java | `HybCecState` | state | 中央状态容器，管理种群、适应度、迭代、算法专用参数和算法工作区等全部运行时状态 |
| StateKey.java | `StateKey` | state | 枚举，类型安全的状态键，替代魔法字符串 |
| StateUpdater.java | `StateUpdater` | state | 状态更新接口，定义策略执行后的状态回写协议 |

## 接口说明

### HybCec（主控制器）

实现 `StateUpdater` 接口。配套外置函数式接口 `FitnessEvaluator` 与结果类 `HybResult`。

`FitnessEvaluator` 函数式接口：
| 方法 | 说明 |
|------|------|
| `List<Double> evaluate(List<double[]> pop)` | 评估种群适应度 |

`HybResult` 静态内部类字段：`gbestSolution`, `gbestFit`, `initialGbestFit`, `bestFitRecord`, `evalRecord`, `gen`

| 方法 | 说明 |
|------|------|
| `run()` | 主循环：初始化→迭代→适应度更新→返回 HybResult |
| `printGenerationLog(int, int, double, long)` | 打印逐代曲线日志，输出代数、eval/maxFes、当前种群规模、当前最优适应度、单代耗时与 eval 进度 |
| `setEnableGenerationLog(boolean)` | 设置是否打印逐代日志 |
| `setGenerationLogInterval(int)` | 设置逐代日志打印间隔；默认 1 保持旧输出频率 |
| `setEnableInitialPopLog(boolean)` | 设置是否打印初始种群诊断日志（适应度统计、种子个体 vs 随机个体对比） |
| `executeCombinedMode()` | 组合模式：准备双种群→顺序执行→合并幸存者 |
| `getCurrentInsertionMode()` | 根据当前迭代进度选择早期/后期插入策略 |
| `getParentAlgorithm(int)` | 工厂方法，根据索引返回对应的 ParentStrategy |
| `createParentContext(...)` | 构建含算法专用子上下文的 ParentContext |
| `updateEnableParents()` | 8 种 operation-order policy（serial、periodic、stage、best-no-improvement、process-no-improvement、diversity、parallel、adaptive-credit）；若运行时 `singleParentMode=true`，则短路为 OA1-only |
| `initializeRun()` | 评估初始种群，设置 pbest/gbest，创建管理器 |
| `reSetParameters(int D, int newNPop)` | 种群规模变化时重置所有数据结构 |

### HybridLevelCalculator（有状态掩码计算器）

构造器接收当前 HybCec 运行持有的 `Random`。`MIXED_SUBSET`、`RANDOM_DECAY` 和并行补集回退都使用该随机源，保证同一 seed 下可复现。

| 方法 | 说明 |
|------|------|
| `determineHybridLevel1()` | 计算 OA1 掩码，返回选中个体数 |
| `determineHybridLevel2()` | 计算 OA2 掩码（串行模式），含补集回退逻辑 |
| `determineHybridLevel2ForParallel()` | 计算 OA2 掩码（并行模式），含补集回退逻辑（A6 修复） |
| `computeDerivedMasksInPlace()` | 单遍计算 indMask、resUnitMask 和计数 |
| `validateUnitMask()` | 确保至少一个单元被选中 |

G2/G3 update policy：

| code | 语义 |
|------|------|
| 0 | `FULL`：全体更新 |
| 1 | `TOP_SUBSET`：固定比例 top-fitness 子集，默认比例 0.5 |
| 2 | `MIXED_SUBSET`：固定比例 top-fitness + random 混合子集，默认总比例 0.5 |
| 3 | `RANDOM_DECAY`：随机子集，内部比例从 0.5 递减到 0.1 |
| 4 | `ABOVE_MEAN`：选择适应度高于均值的个体 |
| 5 | `LOCAL_SEARCH`：只更新历史最优个体 |
| 6 | `WORST_REPAIR`：只更新当前适应度最差个体 |

运行时属性：

| 属性 | 默认值 | 可选值 | 作用 |
|------|--------|--------|------|
| `hybcec.mixedTopRatio` | `0.8` | `[0.0, 1.0]` | 仅在 `MIXED_SUBSET` 下生效，控制高适应度个体子集占比，其余个体随机补足 |
| `hybcec.fastPathBatchSize` | `auto` | `auto` 或正整数 | OA1 batched fast path 批大小；`auto` 保持 legacy 初始批大小并按早期测量保守放大 |
| `ga.probCrossover` | `0.9` | `[0.0, 1.0]` | GA 交叉概率；默认保持 `GeneticAlgorithmNoSelect.GAConfig.defaultConfig()` |
| `ga.probMutation` | `0.15` | `[0.0, 1.0]` | GA mutation 概率 |
| `ga.kTournament` | `2` | 正整数 | GA tournament parent selection 大小 |
| `ga.sigmaScale` | `0.2` | `>=0` | GA Gaussian mutation 强度 |
| `ga.nElite` | `1` | `>=0` | GA 保留精英个体数；2026-05-17 ID1 调参后默认启用 1 个 elite |
| `ga.maxMutationDimRatio` | `0.1` | `[0.0, 1.0]` | GA 单次 mutation 最多扰动维度比例；默认限制为 10% 以减少排序扰动 |
| `ga.adaptiveMutation` | `false` | `true/false` | GA 后半程 mutation 概率、强度和扰动维度线性衰减开关；2026-05-18 ID1 A/B 未提升默认 |
| `ga.probMutationLate` | 同 `ga.probMutation` | `[0.0, 1.0]` | adaptive 开启后期 mutation 概率 |
| `ga.sigmaScaleLate` | 同 `ga.sigmaScale` | `>=0` | adaptive 开启后期 Gaussian mutation 强度 |
| `ga.maxMutationDimRatioLate` | 同 `ga.maxMutationDimRatio` | `[0.0, 1.0]` | adaptive 开启后期单次 mutation 扰动维度比例 |
| `ga.mutationDecayStartRatio` | `0.5` | `[0.0, 1.0]` | adaptive mutation 开始衰减的代数进度比例 |
| `eda.kElite` | `0.12` | `[0.0, 1.0]` | EDA elite 采样比例 |
| `eda.sigmaScale` | `1.0` | `>0` | EDA Gaussian 采样方差缩放 |
| `eda.minSigmaRatio` | `0.002` | `[0.0, 1.0]` | EDA 最小方差比例，防止过早收缩 |
| `eda.stagnationBoostRatio` | `1.0` | `>0` | 停滞后最小方差放大倍率；默认保持旧行为 |
| `eda.stagnationGenerations` | `0` | `>=0` | 触发停滞方差放大的代数阈值；0 表示关闭 |
| `aco.nSample` / `aco.intenseFactor` / `aco.deviateDistanceRatio` / `aco.minSigmaRatio` | `0.8` / `0.35` / `0.5` / `0.001` | `[0.0, 1.0]` / 正数 / 正数 / `[0.0, 1.0]` | ACO 精英采样比例、采样强度、偏离距离比例和最小 sigma 比例 |
| `sa.freezeRate` / `sa.temperature` / `sa.temperatureSchedule` / `sa.temperatureLogOffset` | `0.99` / `0.5` / `LOGARITHMIC` / `3.0` | 正数 / 正数 / `CONSTANT,GEOMETRIC,LOGARITHMIC` / `>1.0` | SA 冷却率、初温、退火路径和对数退火偏移；`LOGARITHMIC` 下使用 `T0 * ln(offset) / ln(gen + offset)` |
| `hybcec.shade.archiveRateFast` | `3.0` | `>=0` | SHADE/L-SHADE 外部 archive 容量倍率 |
| `hybcec.shade.memorySize` | `45` | 正整数 | SHADE/L-SHADE SF/CR/Freq 参数记忆长度 |
| `hybcec.shade.pbestRate` | `0.4` | `[0.0, 1.0]` | SHADE/L-SHADE current-to-pbest 的 pbest 候选比例 |
| `hybcec.shade.learnPeriod` | `20` | 正整数 | SHADE/L-SHADE 策略学习期长度 |
| `hybcec.shade.crGaussianStd` | `0.1` | `>=0` | CR 正态采样标准差 |
| `hybcec.shade.cauchyScale` | `0.1` | `>0` | SF/Freq Cauchy 采样尺度 |
| `pso.cognitiveCoefficient` | `2.0,0.5` | `c1,c2` | PSO 个体/全局学习因子；单父 PSO 调参时通过配置文件或 System Property 覆盖 |
| `pso.inertiaWeight` | 未设置 | 单值或长度等于 PSO maxG 的数组 | PSO 惯性权重；单值会扩展为全程常数，未设置时使用 `pso.inertiaStart -> pso.inertiaEnd` 线性表 |
| `pso.inertiaStart` | `0.9` | double | 未显式设置 `pso.inertiaWeight` 时的 PSO 初始惯性权重 |
| `pso.inertiaEnd` | `0.4` | double | 未显式设置 `pso.inertiaWeight` 时的 PSO 末端惯性权重，默认保持旧 `0.9 -> 0.4` 语义 |
| `pso.vMaxLimit` | `80.0` | double | PSO 绝对最大速度；当 `pso.vMaxRatio` 未设置时生效 |
| `pso.vMinLimit` | `-pso.vMaxLimit` | double | PSO 绝对最小速度 |
| `pso.boundaryMode` | `RANDOM_REBOUND` | `BoundaryMode` 枚举 | PSO 位置越界修复策略；旧行为可显式设为 `SPECULAR_REFLECTION` |
| `pso.boundaryRepairRatio` | `0.05` | `[0.0, 1.0]` | `RANDOM_REBOUND` 等边界修复策略使用的回弹比例 |
| `pso.enableTVAC` | `true` | `true/false` | 开启 PSO time-varying acceleration coefficients；2026-05-19 ID1 100% 预算复核后升为默认，旧行为可显式设为 `false` |
| `pso.tvacC1Start` | `2.5` | `>=0` | TVAC 开始代的 cognitive coefficient |
| `pso.tvacC1End` | `0.5` | `>=0` | TVAC 末代的 cognitive coefficient |
| `pso.tvacC2Start` | `0.5` | `>=0` | TVAC 开始代的 social coefficient |
| `pso.tvacC2End` | `2.5` | `>=0` | TVAC 末代的 social coefficient |
| `pso.vMaxRatio` | `NaN` | `>0` 或未设置 | 按搜索区间比例限制速度；未设置时保持绝对速度上限 |
| `pso.topology` | `GLOBAL_BEST` | `GLOBAL_BEST` | `RING` 仍为 scaffold-only，会在运行时拒绝 |
| `abc.numNoImp` / `abc.phiScale` / `abc.phiOffset` | `100` / `2.0` / `1.0` | 正整数 / 正数 / 实数 | ABC 停滞 scout 阈值与 phi 扰动范围参数，运行时由 `HybCecConfigManager` 通过 `TuningConfig` 读取 |

G4 operation-order policy：

| code | 语义 |
|------|------|
| 0 | `SERIAL`：每代 OA1 后 OA2 串行执行 |
| 1 | `PERIODIC_SWITCH`：按 `itera` 周期在 OA1/OA2 间切换 |
| 2 | `STAGE_SWITCH`：前半预算用 OA1，后半预算用 OA2 |
| 3 | `BEST_NO_IMPROVEMENT_SWITCH`：历史最优 `gbest` 连续无提升后切到 OA2 |
| 4 | `PROCESS_NO_IMPROVEMENT_SWITCH`：当前搜索过程按 `itera` 连续无进展后切到 OA2，进展由 `gbest` 或种群平均适应度提升判定 |
| 5 | `DIVERSITY_SWITCH`：连续种群向量 normalized std 低于阈值时切到 OA2 |
| 6 | `PARALLEL`：分别准备 OA1/OA2 候选并合并 survivor |
| 7 | `ADAPTIVE_CREDIT`：按 CreditManager 的单位评估收益路由 OA1/OA2 |

G5 survivor policy：

| code | 语义 |
|------|------|
| 0 | `ELITIST_BEST_N`：父代与子代合并后选 fitness top-N |
| 1 | `TOURNAMENT`：父代与子代合并后做锦标赛生存选择 |
| 2 | `PAIRWISE_GREEDY`：offspring[i] 与 parent[i] 一对一贪心比较 |
| 3 | `RANK_WEIGHTED`：父代与子代合并后按 rank 权重随机选择 |

`PopulationManager.processParentUpdateFastPath()` 对 partial-update 子集也执行 G5 局部 survivor，不再无条件绕过 survivor 策略；survivor 选回同一 parent 引用且 fitness 未变时跳过无效写回。ACO 生成的 candidate 是新数组，partial-update 收集阶段可直接转移引用，其他父算法仍复制隔离。OA1 batched fast path 中 `PAIRWISE_GREEDY` 保留多候选取最优再替换的局部搜索语义。ACO partial-update 如果 survivor 替换 cached elite 个体，会失效 `ACOWorkspace` 的 elite distribution/sigma 缓存。

### AlgorithmIndex（算法索引枚举）

当前 6D 搜索主动父算法：`GA`(0), `PSO`(1), `EDA`(2), `ACO`(3), `DE_RAND_1`(4), `DE_BEST_1`(5), `DE_CURRENT_TO_RAND_1`(6), `ABC`(7), `SA`(8), `L_SHADE`(9), `ALNS`(10)。

实现库归档尾部：`DE_RAND_2`(11), `DE_BEST_2`(12), `DE_CURRENT_TO_BEST_1`(13), `DE_RAND_TO_BEST_1`(14), `SHADE`(15)。这些 ID 保留实现和兼容索引，但不进入当前 `HYBCEC_ACTIVE_PARENT_ALGORITHM_COUNT = 11` 的混合搜索空间。

| 方法 | 说明 |
|------|------|
| `getIndex()` | 获取 flagPar 数组索引 |
| `getName()` | 获取算法名称 |
| `isDEVariant()` | 是否为 DE 变体 |
| `isSHADEVariant()` | 是否为 SHADE 变体 |
| `fromIndex(int)` | 静态工厂，索引→枚举值 |
| `getRequiredFlagParLength()` | 获取 flagPar 数组所需最小长度 |

### ConfigValidatable（配置校验接口）

接口，提供默认 `validate()` 方法。含内部类 `ValidationResult` 和 `ValidationResultBuilder`。

`ValidationResultBuilder` 流式 API：
| 方法 | 说明 |
|------|------|
| `checkRange(String, double, double, double)` | 校验值在 [min, max] 范围 |
| `checkPositive(String, double)` | 校验正数 |
| `checkNonNegative(String, double)` | 校验非负数 |
| `checkPositiveInt(String, int)` | 校验正整数 |
| `checkNotNull(String, Object)` | 校验非空 |
| `checkSize(String, Collection, int)` | 校验集合大小 |
| `build()` | 构建 ValidationResult |

### HybCecConfig（配置序列化）

| 方法 | 说明 |
|------|------|
| `HybCecConfig(HybCec)` | 从运行实例提取配置 |
| `saveToPropertiesFile(String)` | 保存到 Properties 文件 |
| `loadFromPropertiesFile(String)` | 从 Properties 文件加载 |
| `validate()` | 校验基本参数和各算法配置 |

### HybCecConfigManager（配置管理器）

| 方法 | 说明 |
|------|------|
| `initialize(int[], int, int)` | 根据 flagPar 激活标志初始化各算法配置 |
| `adjustDEConfig(int)` | maxG 变化时重建 DE 配置 |
| `adjustSHADEConfig(int)` | 种群变化时调整 SHADE 配置 |
| `validateConfiguration(int)` | 校验指定算法配置是否已初始化 |

### HybCecExecutionException（执行异常）

受检异常（`extends Exception`），构造器：`(String)`, `(String, Throwable)`, `(Throwable)`。

### CreditManager（adaptive-credit 路由管理器）

| 方法 | 说明 |
|------|------|
| `recordGeneration(double, int, double, int)` | 记录本代 OA1/OA2 收益与评估成本 |
| `getParent1Credit()` / `getParent2Credit()` | 返回滑动窗口内的单位评估收益 |
| `getParent1Ratio()` | 返回 OA1 路由概率，供 `G4=ADAPTIVE_CREDIT` 读取 |
| `seedRatioForTest(double)` | 测试专用，设置初始路由概率 |

当 `G4=ADAPTIVE_CREDIT` 时，HybCec 直接记录并更新 CreditManager；该路由不再受独立 adaptive gene 控制。

### FitnessManager（适应度管理器）

| 方法 | 说明 |
|------|------|
| `updateBestSolutions()` | 单遍更新 pbest 和 gbest |
| `afterIterationUpdate(boolean)` | 迭代后处理：记录适应度、改进标志、离散度计算 |
| `afterIterationUpdate()` | 向后兼容重载（不计算离散度） |

### PopulationManager（种群管理器）

模块最大文件。含内部接口 `NewPopulationGetter`、`PopulationSetter` 和辅助类 `IndividualWrapper`、`PbestRebuildResult`。

| 方法 | 说明 |
|------|------|
| `preparePopSelect()` / `preparePopSelect1()` / `preparePopSelect2()` | 深拷贝种群并计算选择索引 |
| `processParentUpdate()` / `processParent1Update()` / `processParent2Update()` | 完整 7 步更新周期 |
| `processParentUpdateFastPath()` / `processParent1UpdateFastPath()` / `processParent2UpdateFastPath()` | O(cnt) 快速路径 |
| `processParent1UpdateFastPathBatched()` | 批量 (μ+λ) 候选生成 |
| `processParallelUpdate()` / `processParallel1()` / `processParallel2()` | 并行模式更新 |
| `combineSurvivorsParallel()` | 合并 OA1/OA2 结果 |

### PopulationResizer（种群缩减器）

含内部类 `ResizeResult`（字段：`needsParameterReset`, `newNPop`, `resizeResult`）。

构造器接收当前 HybCec 运行持有的 `Random`，并传给 `ResizePop.resizePop()`。L-SHADE/SHADE archive 超容量裁剪因此随 run seed 复现。

| 方法 | 说明 |
|------|------|
| `resizePopulation(int)` | L-SHADE LPSR 种群缩减，返回 ResizeResult |

### HybCecState（中央状态容器）

实现 `Serializable`。管理全部运行时状态，含 `Builder` 流式构建器。

状态分组：
- 种群与适应度：`pop`, `popFit`, `popFitArray`, `nPop`, `pbestSolution`, `pbestFit`, `gbestSolution`, `gbestFit`, `initialGbestFit`
- 迭代与记录：`itera`, `gen`, `flagImprove`, `countNoImprove`, `flagDispersity`, `totalUpdatedInd`, `bestFitRecord`
- 主循环参数：`enableParents`, `oOReal`, `hybLevel`, `oLReal`, `flagPar`
- 算法专用：`v`(PSO), `limitABC`, `sigma`(SA), SHADE 系列参数
- 算法工作区：DE/GA/PSO/SA/SHADE/ACO/EDA/ABC 复用缓冲，以及 ALNS 算子权重状态
- 循环临时变量：`indMask1/2`, `unitMask1/2`, `resUnitMask1/2`, `X1/X2`, `selectIndices1/2`, `popFit1/2`, `newPopUpdated1/2`

| 方法 | 说明 |
|------|------|
| `validate()` | 校验状态一致性 |
| `snapshot()` | 创建状态快照 |
| `reset()` | 重置状态 |
| `updateCacheFlags()` | 更新缓存标志 |
| `getCachedBestIndex()` / `getCachedFitnessRankDesc()` | 返回当前适应度缓存的最优索引和降序 rank；适应度变更后失效重算 |

### StateKey（状态键枚举）

枚举值：`ABC_LIMIT`, `SA_SIGMA`, `SHADE_GG`, `SHADE_SF`, `SHADE_CR`, `SHADE_FREQ`, `FLAG1_SHADE`, `FLAG2_SHADE`

| 方法 | 说明 |
|------|------|
| `getKey()` | 获取键字符串 |
| `fromString(String)` | 字符串→枚举值 |

### StateUpdater（状态更新接口）

| 方法 | 说明 |
|------|------|
| `updateState(StateKey, List<T>, List<Boolean>)` | 泛型部分/全量状态更新 |
| `updateStates(Map<String, Object>)` | 批量状态更新 |
| `incrementIteration(int)` | 递增迭代计数 |
| `updateABCLimit()` | 默认方法：更新 ABC 限制计数器 |
| `updateSASigma()` | 默认方法：更新 SA 步长因子 |
| `updateSHADEState()` | 默认方法：更新 SHADE 状态 |

## 模块依赖关系

### 模块内部依赖
- `HybCec` → `HybCecState`, `HybCecConfigManager`, `CreditManager`, `PopulationResizer`, `FitnessManager`, `HybridLevelCalculator`, `PopulationManager`, `HybCecExecutionException`, `StateUpdater`
- `HybridLevelCalculator` → `HybCecState`, `java.util.Random`
- `PopulationManager` → `HybCecState`, `HybCecConfigManager`, `PopulationResizer`, `HybridLevelCalculator`
- `FitnessManager` → `HybCecState`
- `CreditManager` → `java.util.ArrayDeque`
- `PopulationResizer` → `HybCecState`, `HybCecConfigManager`, `java.util.Random`
- `HybCecConfig` → `HybCec`, `ConfigValidatable`
- `HybCecConfigManager` → `AlgorithmIndex`
- `StateUpdater` → `StateKey`

### 外部依赖
- `src.common`: `AlgorithmConstants`, `RandomProvider`, `ResizePop`, `ConfigStringUtils`
- `src.algorithm`: PSO/GA/EDA/ACO/DE/ABC/SA/SHADE 各算法配置类
- `src.strategy`: 全部 `ParentStrategy` 实现
- `utils`: `ListUtils`, `FitnessUtils`, `PlanUtils`
- `model`: `Satellite`, `Task`
