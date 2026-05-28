# algorithm 模块摘要

## 模块职责

元启发式优化算法库。提供卫星任务调度问题中使用的各类连续域优化算法实现，包括差分进化（DE）及其多种变体、粒子群优化（PSO）、人工蜂群（ABC）、蚁群优化（ACO）、遗传算法（GA）、估计分布算法（EDA）、模拟退火（SA）、自适应差分进化（SHADE）和自适应大邻域搜索（ALNS）。该模块本身不直接承担外层 MFEA 搜索，而是作为 6D 自动设计配置在 `core.HybCec` 中落地执行时的底层算法库。Phase D 搜索质量增强均为 opt-in 配置，默认关闭或中性，保护既有基线轨迹。

## 成员清单

| 文件 | 类名 | 职责 |
|------|------|------|
| `abc/ABC.java` | `ABC` | 人工蜂群算法，含雇佣蜂/观察蜂/侦察蜂三阶段，内部执行贪心选择 |
| `alns/ALNS.java` | `ALNS` | 自适应大邻域搜索，解码随机键任务序列后执行 destroy/repair 局部搜索、模拟退火接受和算子权重更新，再编码回连续染色体；候选构造避免 `Candidate` 包装、单独 `remaining` 列表、ranked destroy 装箱索引、重复分配 ranked scratch 数组和初始 decode 的 `SchedulingPlan` 中转 |
| `aco/ACOGaussGenerate.java` | `ACOGaussGenerate` | 连续域蚁群优化，基于精英个体的高斯混合采样生成新解；`sigma` 使用排序+前缀和精确计算均值绝对距离，并可复用 HybCec 已缓存的 fitness rank |
| `de/DEConfig.java` | `DEConfig` | DE 算法族共享配置，支持静态和自适应（逐代）缩放因子 F |
| `de/AdaptiveFSchedule.java` | `AdaptiveFSchedule` | F 值调度生成器，支持 Power/Piecewise/Cosine/Sigmoid/Stochastic 五种衰减模式 |
| `de/DERand1.java` | `DERand1` | DE/rand/1 变体：`v = x_r1 + F*(x_r2 - x_r3)` |
| `de/DERand2.java` | `DERand2` | DE/rand/2 变体：双差分向量，增强探索能力 |
| `de/DEBest1.java` | `DEBest1` | DE/best/1 变体：以最优个体为基向量，增强开发能力 |
| `de/DEBest2.java` | `DEBest2` | DE/best/2 变体：最优基向量 + 双差分向量 |
| `de/DECurrentToBest.java` | `DECurrentToBest` | DE/current-to-best/1 变体：个体向最优方向移动 + 随机扰动 |
| `de/DECurrentToRand.java` | `DECurrentToRand` | DE/current-to-rand/1 变体：个体向随机方向移动，无需适应度 |
| `de/DERandToBest.java` | `DERandToBest` | DE/rand-to-best/1 变体：随机基向量 + 最优引导 |
| `eda/EDAGaussSam.java` | `EDAGaussSam` | 估计分布算法，从精英个体构建高斯模型并采样 |
| `ga/GeneticAlgorithmNoSelect.java` | `GeneticAlgorithmNoSelect` | 遗传算法（无内部存活选择），含锦标赛选择、算术交叉、高斯变异 |
| `pso/PSO.java` | `PSO` | 粒子群优化，支持线性递减惯性权重和默认启用的 TVAC |
| `sa/SACont.java` | `SACont` | 连续域模拟退火，支持常数/几何/对数温度调度，内部执行 Metropolis 接受准则 |
| `shade/SHADELoopBrief.java` | `SHADELoopBrief` | SHADE 自适应差分进化，维护参数记忆（SF/CR/Freq），支持特征交叉 |
| `shade/UpdateArchive.java` | `UpdateArchive` | SHADE 外部存档管理，去重和容量控制 |
| `shade/UpdateProbSHADE.java` | `UpdateProbSHADE` | SHADE 参数记忆更新，基于加权 Lehmer 均值 |
| `workspace/Workspace.java` | `Workspace` | 算法工作区 marker 接口 |
| `workspace/DEWorkspace.java` | `DEWorkspace` | DE 变体复用 trial/mutant 缓冲和索引 scratch |
| `workspace/GAWorkspace.java` | `GAWorkspace` | GA offspring、适应度和抽样 scratch 复用缓冲 |
| `workspace/PSOWorkspace.java` | `PSOWorkspace` | PSO 新位置和速度复用缓冲 |
| `workspace/SAWorkspace.java` | `SAWorkspace` | SA 候选解、适应度和选中索引复用缓冲 |
| `workspace/SHADEWorkspace.java` | `SHADEWorkspace` | SHADE binomial 路径的 mutant/trial 复用缓冲，覆盖 full/partial update |
| `workspace/ACOWorkspace.java` | `ACOWorkspace` | ACO 权重、累计概率、精英引用、primitive fitness order、sigma、elite distribution 缓存和排序 scratch 复用缓冲 |
| `workspace/EDAWorkspace.java` | `EDAWorkspace` | EDA 均值、平方和、sigma 和精英索引复用缓冲 |
| `workspace/ABCWorkspace.java` | `ABCWorkspace` | ABC 三阶段候选和 scout 目标复用缓冲 |

## 依赖关系图

```
外部依赖（所有算法共用）:
  src.common  → AlgorithmConstants, AlgorithmParameterValidator, BoundaryHandler
  src.core    → ConfigValidatable

DE 子模块内部依赖:
  AdaptiveFSchedule ──→ AlgorithmConstants, RandomProvider
  DEConfig ───────────→ AlgorithmConstants, ConfigValidatable
  DERand1 ────────────→ MutationDERand1, CrossoverDE
  DERand2 ────────────→ MutationDERand2, CrossoverDE
  DEBest1 ────────────→ MutationDEBest1, CrossoverDE, DEUtils
  DEBest2 ────────────→ MutationDEBest2, CrossoverDE, DEUtils
  DECurrentToBest ────→ MutationDECurrentToBest, CrossoverDE, DEUtils
  DECurrentToRand ────→ MutationDECurrentToRand, CrossoverDE
  DERandToBest ───────→ MutationDERandToBest, CrossoverDE, DEUtils

Workspace 子模块:
  DEWorkspace / PSOWorkspace / SAWorkspace / ACOWorkspace / EDAWorkspace / ABCWorkspace
  由 `core.state.HybCecState` 持有单例，策略通过 `ParentContext` 访问

SHADE 子模块内部依赖:
  UpdateArchive ──────→ FitnessUtils
  UpdateProbSHADE ────→ AlgorithmConstants
  SHADELoopBrief ─────→ UpdateArchive.ListArchive, EigenCrossover, BoundaryHandler

需要适应度评估器的算法（内部执行选择/接受）:
  ALNS ───→ model.Satellite, model.Task, PlanUtils
  ABC ────→ model.Satellite, model.Task, operator.insertion.InsertionMode, PlanUtils, FitnessUtils
  SACont ──→ model.Satellite, model.Task, operator.insertion.InsertionMode, PlanUtils

仅生成候选解的算法（外部执行选择）:
  DERand1, DERand2, DEBest1, DEBest2, DECurrentToBest, DECurrentToRand, DERandToBest
  ACOGaussGenerate, EDAGaussSam, GeneticAlgorithmNoSelect, PSO

SA 调参入口:
  SAConfig.defaultConfig() 可读取 JVM 参数 `sa.freezeRate`、`sa.temperature`、`sa.temperatureSchedule`、`sa.temperatureAlpha`、`sa.temperatureLogOffset`、`sa.adaptiveSigma` 和 `hybcec.sa.genSAFast`
  用于单父算法 SA (`8,...`) 快速参数网格；未设置时默认 `genSA=5`、`freezeRate=0.99`、`temperature=0.5`、`temperatureSchedule=LOGARITHMIC`、`temperatureLogOffset=3.0`、`adaptiveSigma=false`
```

## 接口说明

### ABC
- `run(pop, selectIndices, popFit, config, limit, satellite, allTasks, rand)` — 主入口，使用默认评估器
- `run(pop, selectIndices, popFit, config, limit, satellite, allTasks, evaluator, rand)` — 完整实现，含三阶段循环
- 内部类 `ABCConfig`: `numNoImp`(停滞阈值，默认 100), `upperBound`, `lowerBound`, `phiScale`(默认 2.0), `phiOffset`(默认 1.0)
- 内部类 `ABCIterationResult`: `pop`, `popFit`, `limit`
- 内部接口 `ObjectiveEvaluator`: `evaluate(List<double[]>)` — 函数式适应度评估器

### ALNS
- `run(population, selectedIndices, populationFitness, config, satellite, allTasks, random, evaluator)` — 对选中个体执行单星任务序列 ALNS 局部搜索
- `runWithResult(...)` — 返回 `ALNSResult`，包含新染色体、对应已评估 fitness 和 ALNS 内部真实 evaluator 调用次数
- 内部类 `ALNSResult`: `updatedPopulation`, `evaluatedFitness`, `evaluationCount`；供 `ALNSStrategy` 消除重复外层评价，并只按真实评价数追加 eval budget
- 内部类 `ALNSConfig`: `innerIterations`, `weightUpdateInterval`, `minDestroyCount`, `maxDestroyRatio`, `sigmaGlobal/sigmaLocal/sigmaBad`, `reactionFactor`, `initialTemperatureRatio`(当前默认 0.032), `coolingRate`, `insertionMode`, `enableRegret2Repair`(默认 false), `destroyWeights`, `repairWeights`；`hybcec.alns.innerIterationsRatio` 可 opt-in 下调默认 innerIterations，缺省 1.0 等价旧预算
- Destroy 算子：随机移除、低优先级移除、多窗口任务移除
- Repair 算子：高优先级插入、少窗口优先插入、随机插入；`enableRegret2Repair=true` 时追加 regret-2 插入
- 算子初始权重：`destroyWeights` 对应 `[RANDOM, LOW_PRIORITY, MANY_WINDOWS]`，`repairWeights` 对应 `[HIGH_PRIORITY, FEW_WINDOWS, RANDOM]`，启用 regret-2 时 repair 权重长度为 4；未设置时保持等权初始化
- 候选构造热路径：destroy 使用位置布尔标记；`LOW_PRIORITY` / `MANY_WINDOWS` ranked destroy 使用复用的 primitive `int[]` 洗牌、预计算 rank key 和稳定归并排序，避免 `ArrayList<Integer>` / `Integer` 装箱并保留 tie 顺序
- 编码/解码热路径：ALNS 为固定 `referenceTasks` 构建一次 dense task-id -> gene-index 查表；best sequence 编码和 regret 补全序列复用该查表，初始随机键 decode 复用 `SequenceScratch` 的 primitive order/scratch 数组并直接生成任务序列，避免每个个体重复构造 `HashMap<Integer,Integer>` / `HashSet<Integer>` 和 `SchedulingPlan` 中转
- 旧 `run(...)` 仍输出 `double[]` 随机键染色体；`strategy.ALNSStrategy` 使用 `runWithResult(...)` 适配到 HybCec 父算法接口

### ACOGaussGenerate
- `run(pop, selectIndices, popFit, config, customRand)` — 精英选择 + 高斯采样生成新种群
- `runUnsafe(pop, selectIndices, popFit, config, customRand, workspace)` — HybCec 热路径入口，跳过重复全量参数/边界校验；`ACOWorkspace` 缓存权重、累计概率、精英引用、primitive fitness order、elite distribution 和 `sigma` 排序 scratch
- `runUnsafe(..., workspace, fitnessRankDesc)` — rank-aware 热路径入口；当 HybCec 已缓存 fitness 降序 rank 时，ACO 直接复用该 rank，避免重复排序
- 内部类 `ACOConfig`: `nSample`(精英比例，默认 0.8), `intenseFactor`(默认 0.35), `deviateDistanceRatio`(默认 0.5), `upperBound`, `lowerBound`, `minSigmaRatio`(默认 0.001), `legacySigma`(默认 false)
- `sigma` 仍等价于每个精英到其他精英的平均绝对距离；实现从暴力 `O(nElite^2 * D)` 改为按维度排序+前缀和 `O(D * nElite log nElite)`；fast 排序使用 median-of-three pivot 和小分区 insertion sort cutoff
- elite fitness 排序使用 primitive `int[]` order，替代 `FitnessUtils.IndexFitnessPair` list；排序规则与旧 stable 工具对齐为 fitness 降序、index 升序
- partial-update 中如果 elite 索引、elite 个体引用、维度和 ACO sigma 参数都未变化，复用上次 elite distribution/sigma；若 survivor 替换 cached elite，`PopulationManager` 会失效该缓存
- batch roulette selection 已实测为负收益并撤回；当前仍在每个 child 生成前抽 roulette，以保持原 RNG 消耗顺序
- `aco.legacySigma=true` 通过 `HybCecConfigManager` 读入 `ACOConfig`，可临时切回旧 pairwise 累加顺序；该开关用于复现实验和速度/轨迹对照，不进入 6D 搜索基因

### DEConfig
- `defaultConfig()` — 静态 F=0.01, CR=0.3
- `defaultForGenerations(maxG)` — 线性衰减 F (1.0→0.5)
- `sigmoidAdaptiveForGenerations(maxG)` — Sigmoid 衰减 F
- `withTwoF(F1, F2, CR, upper, lower)` — 双 F 值工厂方法
- `getF1(gen)` / `getF2(gen)` — 获取第 gen 代的 F 值
- `boundaryPolicy` — DE 边界策略，默认 `RANDOM_REINIT` 保持旧路径；`CLIP_MIDPOINT` 和 `REFLECT` 已贯穿 7 个 DE mutation 热路径，可用于 opt-in 消融
- `HybCecConfigManager` 可读取 `de.fSchedule`、`de.differentialWeight1/2`、`de.fStatic`、`de.fMax`、`de.fMin`、`de.sigmoidP0`、`de.sigmoidK`、`de.crossoverRate` 和 `de.boundaryPolicy`；未设置时保持当前 sigmoid F `0.1 -> 0.01`、`CR=0.3`、`RANDOM_REINIT`

### AdaptiveFSchedule
- `build(buckets, mode, alpha, fMax, fMin, ..., rand)` — 生成 F 值数组，支持 5 种衰减模式

### DE 变体统一接口
- `DERand1.run(pop, selectIndices, config, gen, rand)` — 最小种群: 4
- `DERand1.runUnsafe(...)` / `DERand1.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DERand2.run(pop, selectIndices, config, gen, rand)` — 最小种群: 6，使用 F1+F2
- `DERand2.runUnsafe(...)` / `DERand2.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DEBest1.run(pop, selectIndices, fitness, config, gen, rand)` — 最小种群: 3
- `DEBest1.runWithBest(pop, selectIndices, bestIndex, config, gen, rand)` — 预计算最优索引
- `DEBest1.runWithBestUnsafe(...)` / `DEBest1.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DEBest2.run(pop, selectIndices, fitness, config, gen, rand)` — 最小种群: 5，使用 F1+F2
- `DEBest2.runWithBest(pop, selectIndices, bestIndex, config, gen, rand)` — 预计算最优索引
- `DEBest2.runInto(..., DEWorkspace)` — 复用 mutant/trial 缓冲
- `DEBest2.runWithBestUnsafe(...)` / `DEBest2.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DECurrentToBest.run(pop, selectIndices, fitness, config, gen, rand)` — 最小种群: 3
- `DECurrentToBest.runWithBest(pop, selectIndices, bestIndex, config, gen, rand)` — 预计算最优索引
- `DECurrentToBest.runWithBestUnsafe(...)` / `DECurrentToBest.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DECurrentToRand.run(pop, selectIndices, config, gen, rand)` — 最小种群: 4，使用 F1+F2
- `DECurrentToRand.runInto(..., DEWorkspace)` — 复用 mutant/trial 缓冲
- `DECurrentToRand.runUnsafe(...)` / `DECurrentToRand.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验
- `DERandToBest.run(pop, selectIndices, fitness, config, gen, rand)` — 最小种群: 4
- `DERandToBest.run(pop, selectIndices, bestIndex, config, gen, rand)` — 预计算最优索引
- `DERand2.runInto(..., DEWorkspace)` / `DERandToBest.runInto(..., DEWorkspace)` — 复用 mutant/trial 缓冲
- `DERandToBest.runUnsafe(...)` / `DERandToBest.runIntoUnsafe(..., DEWorkspace)` — HybCec 热路径入口，跳过重复参数校验

### EDAGaussSam
- `run(pop, popFit, selectIndices, config, rand)` — 精英选择 → 模型估计 → 高斯采样 → 边界修复
- `run(pop, popFit, selectIndices, config, rand, stagnationCount)` — opt-in 停滞感知 minSigma boost 入口
- 内部类 `EDAConfig`: `kElite`(默认 0.12), `sigmaScale`(默认 1.0), `upperBound`, `lowerBound`, `minSigmaRatio`(默认 0.002), `stagnationBoostRatio`(默认 1.0), `stagnationGenerations`(默认 0)

### GeneticAlgorithmNoSelect
- `run(pop, selectIndices, popFit, config, gen, rand)` — 精英保留 + 锦标赛交叉 + 高斯变异
- `runInto(..., GAWorkspace)` — 复用 offspring、fitness 和抽样缓冲；不原地覆盖 `pop`；`GAWorkspace.fitnessBuffer` 按当前 `nPop` 精确重建，避免 L-SHADE 缩群后沿用旧长度适应度数组
- 内部类 `GAConfig`: `probCrossover`, `probMutation`, `kTournament`, `sigmaScale`, `upperBounds`, `lowerBounds`, `nElite`(默认 1), `elitismScope`(默认 GLOBAL), `maxMutationDimRatio`(默认 0.1), `adaptiveMutation`(默认 false), `probMutationLate`, `sigmaScaleLate`, `maxMutationDimRatioLate`, `mutationDecayStartRatio`
- 2026-05-17 ID1 调参后，GA 默认保留 1 个精英个体，并将单次 mutation 扰动维度上限收紧到 10%。`tuning.properties` 可用 `ga.nElite` 和 `ga.maxMutationDimRatio` 覆盖。
- 2026-05-18 增加 GA adaptive mutation opt-in：开启后从 `ga.mutationDecayStartRatio` 对应代数进度开始，把 `probMutation/sigmaScale/maxMutationDimRatio` 线性衰减到 late 值。ID1 A/B 中 `0.1/0.2/0.15 -> 0.05/0.1/0.10` 未提升默认，当前保持关闭。

### PSO
- `run(pop, pbestSolution, gbestSolution, v, selectIndices, config, gen, random)` — 速度+位置更新
- `runUnsafe(..., PSOWorkspace, velocityOut)` — HybCec 热路径入口，假定初始化/resize 边界已校验 PSO 状态
- `run(..., PSOWorkspace)` — 复用新位置缓冲；速度可继续走工作区缓冲，也可直接写入外部速度矩阵，仍不原地覆盖 `pop`
- `initVelocity(nPop, D, config, random)` — 初始化速度矩阵
- `validateStateDimensionsForHybCec(pbestSolution, gbestSolution, v, dimension)` — HybCec 初始化与种群 resize 边界使用的一次性状态校验
- 内部类 `PSOConfig`: `cognitiveCoefficient`(c1,c2), `inertiaWeight`(逐代), `vMaxLimit`, `vMinLimit`, `boundaryMode`(默认 `RANDOM_REBOUND`，旧行为可设为 `SPECULAR_REFLECTION`), `boundaryRepairRatio`(默认 `0.05`), `enableTVAC`(默认 true，可用 `pso.enableTVAC=false` 回退), `tvacC1Start/tvacC1End/tvacC2Start/tvacC2End`(默认 `2.5->0.5` 与 `0.5->2.5`), `vMaxRatio`(默认 NaN), `topology`(默认 GLOBAL_BEST；RING 会显式拒绝，直到 local-best 状态接入)
- 内部类 `PsoResult`: `popSelect`(新位置)

### SACont
- `run(pop, popFit, sigma, selectIndices, config, satellite, allTasks, random, evaluator)` — 多轮 SA 循环
- `run(..., SAWorkspace)` — 复用候选解、当前解、最优解、sigma 和适应度缓冲；不原地覆盖 `pop`
- 内部类 `SAConfig`: `genSA`(迭代数，默认 5), `freezeRate`(冷却率，默认 0.99), `temperature`(默认 0.5), `temperatureSchedule`(默认 LOGARITHMIC，可选 CONSTANT/GEOMETRIC/LOGARITHMIC), `temperatureLogOffset`(对数退火偏移，默认 3.0), `adaptiveSigma`(默认 false)；`SAConfig.defaultConfig()` 可由 JVM 参数 `sa.freezeRate`、`sa.temperature`、`sa.temperatureSchedule`、`sa.temperatureAlpha`、`sa.temperatureLogOffset`、`sa.adaptiveSigma` 和 `hybcec.sa.genSAFast` 覆盖
- 内部类 `SAResult`: `sBest`(最优解), `fBest`(最优适应度), `sigma`(步长)

### SHADELoopBrief
- `run(popOld, fitness, selectedIndices, shadeGG, nfes, maxNfes, config, ...)` — SHADE 主循环
- `runInto(..., SHADEWorkspace)` — binomial crossover 时复用 mutant/trial 缓冲，覆盖 full/partial update；eigen 路径保持原实现
- 内部类 `SHADEConfig`: `memorySF/CR/Freq`, `archive`, `memorySize`, `probEigenCrossover`, `pbestRate`, `archiveRate`；`hybcec.shade.archiveRateFast`、`hybcec.shade.memorySize`、`hybcec.shade.pbestRate`、`hybcec.shade.learnPeriod`、`hybcec.shade.crGaussianStd`、`hybcec.shade.cauchyScale` 可 opt-in 覆盖默认值，缺省保持旧参数；HybCec 可传入 `cachedFitnessRankDesc` 复用 rank
- 内部类 `SHADEResult`: `newPop`, `shadeGG`, `shadeSF`, `shadeCR`, `shadeFreq`, `flag1Shade`, `flag2Shade`

### UpdateArchive
- `updateArchive(archive, newPop, newFunValues)` — 添加个体到存档，去重 + 容量控制
- 内部类 `ListArchive`: `NP`(容量), `pop`, `fitness`

### UpdateProbSHADE
- `updateProbSHADE(pop, popFit, selectIndices, newPopFit, shadeSF, shadeCR, shadeFreq, archive, ..., memorySf, memoryCr, memoryFreq, ...)` — 基于成功历史更新参数记忆
