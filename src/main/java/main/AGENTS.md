# main 模块摘要

## 模块职责

`main` 模块是 6D 纯语义动态版本的入口与全局协调层，负责数据加载、外层 Global MFEA 自动设计、单配置复现实验、单算法复现实验、6D 配置评估以及多卫星任务重分配协调。

## 成员清单

| 文件 | 类名 | 职责 |
|------|------|------|
| MainMFEAMOPHOA.java | `MainMFEAMOPHOA` | 外层 Global MFEA 自动设计入口；构造 6D 纯语义全局配置种群，调用 `EvaluationHyb` 并行评估候选混合配置，输出全局最优自动设计结果；逐代日志打印当前全局最优 `bestConfig`；支持 outer fitness cache 与 progressive racing opt-in，默认保持旧评估路径 |
| ParallelPolicy.java | `ParallelPolicy` | 并行层级策略；集中解析 `autohyb.parallel.level=run|satellite|vector|auto`，在外层评估活跃时阻止 `PlanUtils` 使用 common-pool 向量并行 |
| EvaluationHyb.java | `EvaluationHyb` | 6D 混合配置评估器；将单个全局配置解码为 HybCec 参数、运行时插入模式与单一 fixed DE scale，按多次独立运行评估配置质量，并向 `TaskAllocationCoordinator` 传递 run seed、配置与历史最优结果；MFEA fitness 直接使用优化后调度收益，不再用 baseline 兜底；run seed 统一使用 `stableSeed + runIndex + 8`，用于保持 6D baseline 与旧 8D `{...,GREEDY,flag}` 路径的 seed 兼容 |
| RunSingleHybridConfig.java | `RunSingleHybridConfig` | 单配置复现实验入口；加载数据、初始化任务分配、使用固定 6D 配置运行评估链路、输出调度结果；命令行只接收 6D 配置；DE 运行时统一为固定缩放因子；支持两种开关控制方式：1）直接在源码顶部修改 `DEFAULT_ENABLE_DELTA_FAST_REFINE` / `DEFAULT_ENABLE_LOCAL_REFINE_HOT_START_BUDGET` 两个布尔常量，便于 VSCode 直接运行时手动切换；2）通过前两个命令行参数显式覆盖，分别控制 delta fast refine 与局部重算热启动预算；源码顶部 `DEFAULT_RANDOM_SEED_ID` 用于切换单次复现实验的 1-based seed id，填 `1/2/3` 分别复现多次运行中的第 1/2/3 次 seed，未显式设置 `-Devaluation.runIndexBase` 时映射到 `evaluation.runIndexBase`；可通过 `-Dhybcec.insertionMode=<InsertionMode>` 对单配置消融运行覆盖插入策略，默认 `GREEDY`；默认开启 `-Dautohyb.deterministic=true` 复现实验模式，入口会重置 `RandomProvider` 全局随机源和线程计数；程序内部会将这些开关映射到协调器对应系统属性；默认 stdout 只打印当前混合配置、收益比例和总耗时；支持 `--record-baseline` / `--baseline-file` 将当前默认场景与配置的效用指标固化到基线文件，并仅在记录基线时打印基线对比；支持 `--quiet` 压制 warmup 状态日志，最终紧凑结果仍打印；`--log-interval=N` 继续控制显式开启的逐代曲线日志间隔 |
| RunSingleParentConfig.java | `RunSingleParentConfig` | 单算法复现实验入口；使用独立 3D 单算法配置 `{algorithmIndex, updateRatioCode, survivorStrategy}` 构建 OA1-only 运行；命令行不再复用混合组件语义，固定 `operationOrder=sequential` 与固定 DE 缩放因子，并通过运行时 `singleParentMode=true` 强制只启用 parent1；支持 `--run-index-base` 做 seed 分段诊断；支持 `--generation-log` 与 `--log-interval=N` 打印 HybCec 逐代最优适应度曲线；支持 `--convergence-file` 输出每个 run / 卫星的 HybCec best-fitness 曲线 |
| TargetSatelliteRanker.java | `TargetSatelliteRanker` | 目标星排序器；抽象候选目标星的任务侧与任务-卫星配对特征，只执行低成本排序，并按固定 Top-K 返回候选目标星；普通任务默认 Top-2，prioritized 任务默认 Top-4；卫星侧 `B_j` 通路已删除 |
| TargetSatelliteSelector.java | `TargetSatelliteSelector` | 包内私有候选目标星选择辅助类；从协调器状态构造 `TargetSatelliteRanker.RankRequest`，封装候选星上下文、任务侧优先级/约束紧度/未调度压力特征、任务-卫星窗口特征与 Top-K 结果转换 |
| TaskAllocationScoring.java | `TaskAllocationScoring` | 包内私有打分辅助类；集中维护未调度任务优先级、fast refine 修复评分、任务-卫星 effective score、时间窗冲突、约束紧度、未调度压力与归一化/截断等纯打分逻辑 |
| DeltaFastRefiner.java | `DeltaFastRefiner` | 包内私有 delta fast refine 辅助类；在分配变化时基于上一轮 `SatelliteState.bestPlan` 保留锚点序列，只对新增任务做有限候选插入、被移除任务原位置附近采样与邻接交换局部修补；启用条件只受 `taskcoord.deltaFastRefine.enabled` 控制；`coord.fastRefineAdjacentSwapEnabled` 可单独关闭邻接交换；额外补充插入候选通路已删除 |
| AssignmentDeltaEvaluator.java | `AssignmentDeltaEvaluator` | 包内私有 assignment delta 评估辅助类；集中处理试探移动、受影响卫星局部重算、大任务目标星优先惰性评估、增量方案合并、方案实体化、收益增量计算与受影响分配校验 |
| ReassignmentMoveServices.java | `ReassignmentMoveServices` | 包内私有高阶重分配动作依赖面；统一暴露目标星选择、反馈写回、全局任务键、卫星列表和 `evaluateTrialAssignment()`，避免各移动评估器直接持有协调器上下文或重复拼装增量方案/收益评估 |
| ReplacementMoveEvaluator.java | `ReplacementMoveEvaluator` | 包内私有替换移动辅助类；筛选一对一替换与批量移除可替换任务，构造替换试探分配，并通过增量评估收益与成功反馈 |
| SwapMoveEvaluator.java | `SwapMoveEvaluator` | 包内私有交换移动辅助类；筛选跨卫星可交换任务、接收星候选，构造 U->目标星 / X->接收星试探分配，并处理交换成功后的反馈 |
| BundleMoveEvaluator.java | `BundleMoveEvaluator` | 包内私有任务束移动辅助类；按共同候选星和时间窗口邻近度生成 2-3 任务束，构造联合迁移试探分配并评估收益 |
| ReassignmentMoveEvaluator.java | `ReassignmentMoveEvaluator` | 包内私有高阶重分配动作外观类；保留替换、交换、任务束的原调用面，将具体职责转发给 `ReplacementMoveEvaluator`、`SwapMoveEvaluator` 与 `BundleMoveEvaluator` |
| ReassignmentOrchestrator.java | `ReassignmentOrchestrator` | 包内私有重分配主循环辅助类；编排优先级迁移循环、标准迁移接受、替换/交换回退触发与任务束后处理，并通过上下文回调复用协调器的候选选择、试探评估和反馈状态 |
| TaskAllocationModels.java | `SatelliteState`, `SatelliteEvaluationResult`, `ReassignmentStats`, `ReassignmentWorkingState`, `PrioritizedTask`, `SatelliteCandidateSelection`, `SchedulingStats`, `TaskDelta`, `TrialMoveResult` | 包内私有数据结构集合；承载协调器内部状态快照、卫星并行评估结果、迁移统计、重分配候选工作状态、增量任务差异、候选选择结果与试探移动结果，不作为外部 API |
| TaskAllocationCoordinator.java | `TaskAllocationCoordinator`, `ConvergenceTrace` | 多卫星协调器；维护任务分配、全局任务键、任务-卫星 base score 与反馈 delta；编排跨卫星重分配的顶层触发、结果提交和刷新 best 后的完整校准；小规模任务默认立即校准，大规模中间校准只保留 interval/last 触发，末尾 final calibration 仍保留；记录正式卫星调度的 HybCec best-fitness 曲线供单父算法预算诊断使用；`autohyb.deterministic=true` 时仍使用卫星级并行评估，但每颗卫星只读取同一份 `SatelliteState` 快照，跑完后按 satellite id 固定顺序提交状态与收敛曲线，并按 satellite id 排序跨星模板 donor，避免线程完成顺序和 `ConcurrentHashMap` 遍历顺序影响复现实验；Phase 4 新增 sat state 池化、初始化 KNN 缓存、卫星池尺寸、自适应初始 ensemble 与校准 racing opt-in，默认均关闭或保持旧行为；候选目标星上下文构造下沉给 `TargetSatelliteSelector`，增量方案与试探移动评估下沉给 `AssignmentDeltaEvaluator`，重分配主循环下沉给 `ReassignmentOrchestrator`，替换/交换/任务束移动下沉给 `ReassignmentMoveEvaluator`，delta fast refine 下沉给 `DeltaFastRefiner`，排序仍由 `TargetSatelliteRanker` 完成 |

## 接口说明

### MainMFEAMOPHOA

```java
public static void main(String[] args)
```

### EvaluationHyb

```java
public static EvaluationResult evaluationHyb(
    int[] x, int d, int nPop, int maxFes, int nRun,
    List<Satellite> allSatellites, List<Task> allTasks,
    ExecutorService executor) throws Exception
```

`x` 必须传入 6D 配置。

Seed 约定：统一使用 `stableSeed + runIndex + 8`。其中 `{4,1,0,0,0,0}` 在 ID1 基准预算下复用旧 8D `{4,1,0,0,0,0,1,0}` 的 stable seed，保证 6D 折叠后仍命中旧 8D 单轮复现实验 seed。

评估约定：MFEA 搜索阶段只把优化后调度收益写入 run profit 和 best run，不再把初始化 assignment 的 baseline 方案作为兜底 fitness。

### RunSingleHybridConfig

```java
public static void main(String[] args)
```

补充约定：
- `--record-baseline`：将当前运行结果写入默认基线文件 `outputs/run-single-baseline.properties`
- `--baseline-file <path>`：覆盖默认基线路径
- `-Dhybcec.insertionMode=<InsertionMode>`：覆盖本次评估链路使用的插入策略；默认 `GREEDY`
- `DEFAULT_RANDOM_SEED_ID`：源码顶部 1-based 单次 seed id；默认 `1`，改成 `2/3/...` 可模拟多次运行中的第 2/3 次 seed；若 JVM 显式传入 `-Devaluation.runIndexBase=<long>`，则以 JVM 参数为准
- `-Dautohyb.deterministic=true|false`：控制单配置复现实验模式；默认 `true`，会重置 `RandomProvider`，多卫星快照评估仍并行执行，但读取固定状态快照并按 satellite id 固定顺序提交结果；设为 `false` 可恢复旧并行路径
- `--quiet`：隐藏 warmup 状态日志；最终混合配置、收益比例和耗时仍打印
- `--log-interval=N`：控制逐代日志间隔，默认 1，保持旧输出频率
- `-Dautohyb.generationLog=true|false`：控制 `TaskAllocationCoordinator` 内部 HybCec 是否打印 `[HybCecCurve]` 逐代曲线日志；默认 `false`
- `-Dautohyb.generationLog.enabled=true|false`：旧兼容别名，作用同 `autohyb.generationLog`
- `-Dautohyb.parallel.level=run|satellite|vector|auto`：选择并行层级；默认 `auto` 保持旧入口行为
- `-Dautohyb.parallel.satellitePoolSize=<int>`：显式配置卫星级 ForkJoinPool 大小；未设置时保持旧的 `max(2, availableProcessors)` 行为
- `-Dautohyb.outer.cache.enabled=true|false`：控制外层 6D 配置 fitness cache；默认 `false`
- `-Dautohyb.outer.racing.enabled=true|false`：控制外层 MFEA progressive racing；默认 `false`，只影响 `MainMFEAMOPHOA`
- `-Dautohyb.outer.nPopHyb=<int>` / `-Dautohyb.outer.gMax=<int>` / `-Dautohyb.outer.nRun=<int>` / `-Dautohyb.outer.maxFes=<int>`：外层短测预算覆盖；未设置时保持旧默认预算
- `-Dautohyb.satState.pool=true|false`：控制 `SatelliteState` 对象复用；默认 `false`
- `-Dautohyb.init.knnCache=true|false`：控制初始化与目标星排序共享任务-卫星窗口特征缓存；默认 `false`
- `-Dautohyb.coord.adaptiveEnsemble=true|false`：控制低负载卫星初始 ensemble racing；默认 `false`
- `-Dautohyb.coord.calibrationRacing=true|false`：控制刷新 best 后先做 cheap inherited-vector 校准筛查；默认 `false`
- `RunSingleHybridConfig` 默认 stdout 只打印 `Hybrid config`、`Optimized profit ratio` 和 `Elapsed` 三行
- 使用 `--record-baseline` 时，若基线文件存在且上下文（场景、任务规模、配置、`nRun`、`nPop`、`maxFes`）一致，会打印效用与耗时相对基线的增减，并写回当前基线
- 当前基线：`{4,1,0,0,0,0}`；ID1 基准预算 `nPop=270,maxFes=27000` 下使用 `runIndex+8` seed 序列；无参 `nRun=1` 默认命中旧 8D `{4,1,0,0,0,0,1,0}` 单轮复现实验 seed

### RunSingleParentConfig

```java
public static void main(String[] args)
```

补充约定：
- `configCsv` 固定为 3D：`algorithmIndex,updateRatioCode,survivorStrategy`
- 运行时固定 `operationOrder=sequential` 与固定 DE 缩放因子
- 运行链路通过 `singleParentMode=true` 强制只启用 OA1，因此不再把“单算法”伪装成双亲混合算法
- `--run-index-base N`：从指定 runIndex 开始跑 `nRun` 个连续 seed，用于定位波动来源
- `--generation-log`：打开 HybCec 逐代日志，输出 `[HybCecCurve]` 单星收敛曲线；`--log-interval=N` 控制采样间隔，用于单算法收敛曲线诊断
- 也可配合 `-Dautohyb.generationLog=true -Dautohyb.logInterval=N` 观察单算法在多卫星协调器内部的 HybCec 收敛曲线
- L-SHADE/SHADE 单算法调参可配合 `-Dhybcec.shade.archiveRateFast=<double>`、`-Dhybcec.shade.memorySize=<int>`、`-Dhybcec.shade.pbestRate=<double>`、`-Dhybcec.shade.learnPeriod=<int>`、`-Dhybcec.shade.crGaussianStd=<double>`、`-Dhybcec.shade.cauchyScale=<double>`，未设置时保持默认参数
- `--convergence-file <path>`：把正式调度阶段的每个 run / 卫星 / generation best-fitness 和已用 eval budget 曲线写成 CSV，用于估算短测预算

### TargetSatelliteRanker

```java
public List<Integer> rank(RankRequest request)
```

内部类：
- `RankRequest` — 排序请求；封装候选目标星上下文、任务侧归一化特征与 high-value 标记
- `SatelliteCandidateContext` — 单个候选目标星上下文；封装该任务在目标星上的窗口数量、窗口总长度、最早开始时间、`k_sat(i,s)`、分配任务数、已调度任务数与目标星历史成功率
- `RankedCandidate` — 排序内部候选目标星快照；保存低成本分数、排名与特征，不作为外部返回对象

### TargetSatelliteSelector / TaskAllocationScoring / DeltaFastRefiner / AssignmentDeltaEvaluator / ReassignmentOrchestrator / ReassignmentMoveEvaluator / TaskAllocationModels

这些类为 `main` 包内辅助类，不提供 public 外部接口：
- `TargetSatelliteSelector`：从 `TaskAllocationCoordinator` 的上下文接口读取任务-卫星键等状态，构造 `RankRequest` 并把排序器返回的固定 Top-K 卫星 ID 包装为 `SatelliteCandidateSelection`
- `TaskAllocationScoring`：集中计算 prioritized unscheduled task score、fast refine repair score、任务-卫星 effective score、窗口冲突分数、tightness/unscheduled-pressure 与 `[0,1]` 归一化/截断
- `DeltaFastRefiner`：集中处理 delta fast refine 的任务差异识别、基于锚点计划的有限候选插入、被移除任务原位置附近采样与邻接交换局部修补；启用条件只受 `taskcoord.deltaFastRefine.enabled` 控制；维护邻接交换调用、尝试、接受、收益和耗时统计；额外补充插入候选通路已删除
- `AssignmentDeltaEvaluator`：集中处理 assignment delta 的试探移动构造、受影响卫星局部重算、大任务目标星优先惰性评估、增量方案合并、方案实体化、收益增量计算与受影响分配校验
- `ReassignmentOrchestrator`：集中编排 `reassignUnscheduledTasks` 的优先级迁移循环、标准迁移接受、替换/交换回退触发与任务束后处理；通过上下文调用协调器状态更新，避免直接持有全局可变结构
- `ReassignmentMoveServices`：收束替换、交换、任务束移动共用依赖；通过 `evaluateTrialAssignment()` 统一生成 `TrialMoveResult`，对外隐藏 `ReassignmentMoveEvaluator.Context` 与 `AssignmentDeltaEvaluator` 的组合细节
- `ReassignmentMoveEvaluator`：作为外观类保留 `ReassignmentOrchestrator` 使用的原方法名；具体替换、交换、任务束逻辑分别下沉给 `ReplacementMoveEvaluator`、`SwapMoveEvaluator` 与 `BundleMoveEvaluator`
- `ReplacementMoveEvaluator`：集中处理替换移动的可替换任务识别、一对一替换、批量移除替换和被挤出任务回传
- `SwapMoveEvaluator`：集中处理交换移动的交换候选识别、接收星排序、2-3 星联动增量评估和成功反馈写回
- `BundleMoveEvaluator`：集中处理任务束候选构建、共同目标星交集筛选、任务束试探分配和增量收益评估
- `TaskAllocationModels`：保存迁移流程内部数据结构，包括已接受状态、卫星并行评估结果、候选工作状态、增量差异与试探移动结果，避免 `TaskAllocationCoordinator` 内部类继续膨胀

### TaskAllocationCoordinator

```java
// 构造器
public TaskAllocationCoordinator(
    List<Task> allTasks, List<Satellite> satellites,
    AssignmentStrategy reassignmentStrategy,
    int maxReassignIterations, int keyPerturbThreshold,
    double keyPerturbStrength)

// 核心调度方法
public Map<Integer, SchedulingPlan> scheduleWithReassignment(
    HybCecConfig hybCecConfig, List<Satellite> satellites,
    Map<Integer, Integer> initialAssignment) throws Exception
public List<ConvergenceTrace> getConvergenceTracesSnapshot()

// 快照查询
public Map<Integer, Integer> getTaskAssignmentSnapshot()
public Map<Integer, Integer> getBestTaskAssignmentSnapshot()
public List<String> getStrategyHistorySnapshot()
public List<Integer> getUnscheduledTaskCountHistorySnapshot()
public List<Integer> getMigrationCountHistorySnapshot()
public List<Double> getTotalProfitHistorySnapshot()

```

内部类：
- `HybCecConfig` — HybCec 运行配置（父算法索引、操作级别、执行顺序、生存选择策略、运行时 `singleParentMode`、插入模式、种子等）

## 动态调度特性

### 全局任务键与任务-卫星偏好键

`TaskAllocationCoordinator` 现维护两层键：
- `k_task(i)`：任务优先级键，初始化时融合任务收益、候选卫星数、总窗口数与小随机扰动；用于未调度任务排序、星内排序、启发式基线、失败反馈修正与 fast refine 修复
- `k_sat(i,s)`：任务-卫星偏好键，对外读取值为 `clip01(baseScore(i,s) + feedbackDelta(i,s))`。`baseScore` 按任务在候选卫星上的窗口数量、总窗口长度、最早可观测时刻与小随机扰动生成；`feedbackDelta` 初始为 0，在重分配试探中对 accepted move 的成功目标星做正反馈，对“本轮最接近成功的最佳失败目标星”做负反馈。该 effective score 用于候选目标星排序、星内排序与 fast refine repair 的本星新增任务优先级。

仍留在初始卫星上的任务优先继承初始 `assignedTasks` 顺序。

### 初始完整评估小集成

初始完整评估（`commitState=true` 且无继承状态）时，对每颗卫星运行 `INITIAL_ENSEMBLE_SIZE`（默认 2）次独立 HybCec，每次使用不同种子（`config.seed + satellite.getId() + ensembleIdx * ENSEMBLE_SEED_OFFSET`），取适应度最高的方案作为该卫星的初始状态。目的是降低单次 HybCec 随机波动对后续迁移路径的影响。有继承状态或增量评估时不触发小集成，保持原有单次运行行为。

### 单卫星初始化结构

每颗卫星的 HybCec 初始化种群按以下优先级构造：
1. 真实基线精英个体：基于初始化阶段真实基线顺序编码得到的精英染色体；对仍留在初始卫星的任务优先继承初始 `assignedTasks` 顺序，再对迁入任务应用稳定顺序补尾
2. 启发式基线个体：由 `k_task(i)` 主导构造的确定性参考个体
3. `inherited solution`：上一轮该卫星最优向量按 `taskId` 投影到当前任务集；新任务使用启发式基线值补齐
4. `random`：其余随机个体，用于保持探索多样性

若上一轮最优向量与其任务快照不自一致，或旧/新任务列表存在重复 `taskId`，则直接快速失败并抛错，不执行随机回退。

### 任务重分配循环

多卫星模式下迭代执行：
1. 按当前 assignment 对每颗卫星单独运行 HybCec
2. 收集**全部任务口径**的未调度任务并记录失败计数；当前未出现在任一卫星 schedule 中的任务（包括初始未分配任务、以及上一轮已调度但本轮因重分配回退为未调度的任务）都会进入候选集
3. 收益有改进 → 继续当前分配；若分配与当前已缓存方案对应快照一致，则直接复用已有完整评估结果，不重复全量评估；刷新 best 后，小规模任务立即完整校准，大规模中间校准只保留 `CALIBRATION_INTERVAL` 与最后一轮触发，已删除 `profitGain > bestTotalProfit * 0.005` 触发条件
4. 连续无改进轮数 >= REASSIGN_STAGNATION_THRESHOLD（默认=1）→ 对未调度任务尝试迁移；对原本未分配任务允许直接尝试分配到任一卫星；阈值为 1 意味着几乎每轮都会触发重分配（除第 0 轮和收益刚改进的下一轮）
5. `ReassignmentOrchestrator` 负责逐个处理高优先级未调度任务：先选候选目标星，再通过 `AssignmentDeltaEvaluator` 的统一试探移动入口推导 `trialAssignment` / `affectedSatelliteIds`，并经由统一的增量方案构造入口只局部重算受影响卫星（源卫星 + 目标卫星），其余卫星复用上一轮方案；若该受影响卫星存在上一轮继承状态，则优先走基于旧 `bestPlan` 的 fast refine：保留锚点计划中仍留在本星的旧序列，仅对本轮新增任务做有限候选插入，插入后对序列做邻接交换优化以修复局部冲突，并复用 `PlanUtils.evaluatePlan()` 统一重建收益；fast refine 不适用时，回退到带下限保护热启动预算的 HybCec 局部重算
6. 当标准迁移对高价值未调度任务无法找到正收益目标时，`ReassignmentOrchestrator` 触发 `ReassignmentMoveEvaluator` 外观类，再由 `ReplacementMoveEvaluator` 尝试替换移动（时间窗口感知版本）：先做一对一替换（最多 REPLACEMENT_MAX_TRIALS_PER_SAT 个候选），若无正收益再尝试贪心递增批量移除（按时间重叠度降序排列可替换任务，逐个追加移除评估，上限 MAX_BATCH_REMOVAL=3），仅在净收益为正时接受替换；fast refine 插入采用锚点增强（被移除任务原位置 ±2 邻域密集采样）
7. 当替换移动也失败时，`ReassignmentOrchestrator` 继续触发 `ReassignmentMoveEvaluator` 外观类，再由 `SwapMoveEvaluator` 尝试跨卫星交换：在目标星已调度任务中筛选与未调度任务候选窗口有时间重叠且在其他卫星上有候选窗口的任务 X（按优先级升序，每颗目标星最多 SWAP_MAX_CANDIDATES_PER_SAT 个候选），对 X 的每个接收星（按窗口数降序，最多 SWAP_MAX_RECEIVER_SATS 个）构造试探分配（U→目标星，X→接收星），通过增量方案评估 2-3 星联动收益，仅在总收益为正时接受交换
8. 逐个任务的标准迁移、替换、交换全部完成后，`ReassignmentOrchestrator` 收集仍未调度任务，并调用 `ReassignmentMoveEvaluator` 外观类，再由 `BundleMoveEvaluator` 尝试任务束移动（多任务联合迁移）：按时间窗口邻近度（同一候选卫星上窗口起始时间差 <= 120 秒）聚类生成 2-3 个任务束，对每个任务束取共同候选目标星交集，一次性评估整组任务插入的增量收益，仅在收益为正时接受；每轮最多尝试 BUNDLE_MAX_ATTEMPTS_PER_ROUND=5 个任务束
9. 增量方案验证要求固定预算下收益一致，并保持目标选择一致性；当存在多个候选目标卫星时，增量评估与完整评估必须选出相同的最佳目标；当多个候选目标收益并列时，增量评估与完整评估必须落到相同的并列裁决结果；当 basePlans 来自上一轮增量复用时，上述并列裁决仍必须保持一致

### 单卫星/多卫星双模式

- `satellites.size() == 1` → `scheduleSingleSatelliteMode()`
- `satellites.size() > 1` → `scheduleMultiSatelliteMode()`

## 外部依赖

- `core.HybCec` — 混合优化引擎
- `common.AlgorithmConstants / HybridInitial / RandomProvider` — 常量、初始化、随机数
- `operator.assignment.*` — 任务分配策略
- `operator.insertion.InsertionMode` — 插入策略枚举
- `utils.DataLoader / Initialize / AssignTaskOperator / PlanUtils / ListUtils` — 数据加载与调度工具
- `model.*` — 领域模型

进行速度和适应度优化时候，要看优化过程里面的运行速度优化.md和适应度优化.md作为历史参考
