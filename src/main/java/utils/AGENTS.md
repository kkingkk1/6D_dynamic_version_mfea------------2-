# utils 模块摘要

## 模块职责

`utils` 包是卫星调度优化系统的基础设施层，供外层 Global MFEA 自动设计、单配置复现实验与多卫星重分配流程共同复用，提供数据加载、任务初始化分配、调度引擎、适应度评估与归档等核心工具类。

## 成员清单

| 类名 | 类型 | 职责 |
|------|------|------|
| `TimeUtils` | 工具类（静态方法） | 卫星姿态转换时间计算与可行性判断 |
| `PlanUtils` | 工具类（静态方法） | 核心调度引擎：染色体编解码、调度方案生成与评估；内部 `TaskIdMarker` 用 stamp 数组替代热路径任务 id `HashSet` |
| `DecodeWorkspace` | 可变工作区 | `PlanUtils.evaluateVector` / 序列直评路径的线程内排序、任务序列和调度状态复用缓冲，复用任务 id marker、GREEDY 插入结果 carrier 与直评专用 `ScheduledTask` 池，避免重复集合/结果包装/临时调度对象分配 |
| `AssignTaskOperator` | 实例类 | 任务-卫星分配算子，提供 9 种启发式/复合分配策略 |
| `Initialize` | 工具类（静态方法） | 任务到卫星的初始分配入口，为自动设计与单配置评估统一生成基线分配 |
| `DataLoader` | 工具类（静态方法） | 文件 I/O，解析任务列表、时间窗口、姿态记录 |
| `FitnessUtils` | 工具类（静态方法） | 适应度排序、极值查找、轮盘赌选择 |
| `ListUtils` | 工具类（静态方法） | MATLAB 风格数组/矩阵操作（初始化、深拷贝、掩码选择） |
| `CandidateArchive` | 实例类（线程安全） | 精英解档案库，维护有界有序候选解集合 |

## 接口说明

### TimeUtils
- `MIN_TRANSFORMATION_TIME_SECONDS` — 姿态转换可行性检查的最小时间下界，供热路径先做时间间隔剪枝
- `isEarlier(AttitudeRecord, AttitudeRecord) -> boolean` — 判断 t1 是否早于 t2
- `calculateTransformationTime(AttitudeRecord, AttitudeRecord) -> double` — 基于角度差的分段线性姿态转换时间
- `calculateTimeInterval(AttitudeRecord, AttitudeRecord) -> double` — 两记录间的时间间隔（秒）
- `checkTransformationTime(AttitudeRecord, AttitudeRecord) -> boolean` — 检查姿态转换是否可行
- `getTransformationAngle(AttitudeRecord, AttitudeRecord) -> double` — 滚转角+俯仰角差的曼哈顿距离

### PlanUtils
- `decode(double[], List<Task>) -> SchedulingPlan` — 连续染色体向量按值降序解码为调度方案（值越大越靠前）
- `evaluateVector(double[], List<Task>, Satellite, InsertionMode, DecodeWorkspace) -> double` — 连续染色体直评路径，复用工作区完成同序解码并跳过 `SchedulingPlan` 构造
- `evaluateTaskSequence(List<Task>, Satellite, InsertionMode, DecodeWorkspace) -> double` — 任务序列直评路径，保留重复任务防护并复用 `DecodeWorkspace`
- `evaluateUniqueTaskSequence(List<Task>, Satellite, InsertionMode, DecodeWorkspace) -> double` — 唯一任务序列直评路径，跳过重复任务集合检查，供 ALNS 候选序列热路径使用
- `encodePopulation(List<SchedulingPlan>, List<Task>) -> List<double[]>` — 种群编码为与降序解码一致的染色体向量
- `encodePlan(SchedulingPlan, List<Task>) -> double[]` — 将单个调度方案编码为与降序解码一致的染色体向量
- `findBestInPopulation(List<SchedulingPlan>, Satellite, List<Task>) -> SchedulingPlan` — 查找种群最优方案
- `checkRepeatedTasks(SchedulingPlan) -> boolean` — 验证无重复任务
- `checkTransitionTimeConstraints(SchedulingPlan) -> boolean` — 验证转换时间约束
- `sortTaskSequenceByEarliestStart(List<Task>, int) -> void` — 按最早开始时间排序
- `generateSchedule(SchedulingPlan, Satellite, InsertionMode) -> List<ScheduledTask>` — 核心调度：使用指定插入策略生成调度方案
- `generateSchedule(SchedulingPlan, Satellite, InsertionMode, boolean) -> List<ScheduledTask>` — 核心调度：允许在 `GREEDY` 模式下按需对选定任务启用窗口排序式插入
- `generateSchedule(SchedulingPlan, Satellite, InsertionMode, boolean, Set<Integer>) -> List<ScheduledTask>` — 核心调度：允许对指定任务集合在 `GREEDY` 模式下启用”先按 `windowScore` 排序、再逐窗尝试”的窗口偏好路径；窗口偏好统计默认关闭，可用 `-Dplanutils.windowPreferenceStats=true` 打开
- `resetWindowPreferenceSummary() -> void` — 清空当前线程窗口偏好统计汇总
- `getWindowPreferenceSummarySnapshot() -> WindowPreferenceSummary` — 获取当前线程窗口偏好统计快照（调用次数、候选窗口均值、第一名命中率、回退率、平均命中名次等）
- `isWindowPreferenceStatsEnabled() -> boolean` — 返回当前 JVM 是否启用窗口偏好统计采集
- `evaluatePlan(SchedulingPlan, Satellite, InsertionMode) -> double` — 评估方案适应度
- `buildPlanByLimitedInsertion(List<Task>, List<Task>, Satellite, InsertionMode, int) -> SchedulingPlan` — 基于旧序列对少量新增任务做有限候选插入，用于 delta fast refine 快速局部修补；默认候选位置为边界/中点/均匀采样
- `buildPlanByLimitedInsertion(List<Task>, List<Task>, Satellite, InsertionMode, int, boolean) -> SchedulingPlan` — 在 limited insertion 中按需启用 `GREEDY` 的窗口排序式插入，对所有新增任务走窗口偏好路径；默认仍使用原候选位置
- `buildPlanByLimitedInsertion(List<Task>, List<Task>, Satellite, InsertionMode, int, boolean, List<Integer>) -> SchedulingPlan` — 带锚点位置的有限候选插入，replacement move 场景下在被移除任务原位置附近做密集采样
- `evaluatePop(List<double[]>, Satellite, InsertionMode) -> List<Double>` — 基于卫星当前 assignedTasks 的自适应并行/串行种群评估
- `evaluatePop(List<double[]>, Satellite, List<Task>, InsertionMode) -> List<Double>` — 使用显式 referenceTasks 作为染色体解码参考的自适应并行/串行种群评估
- `applyEliteEvaluation(List<double[]>, List<Double>, Satellite, double) -> void` — 精英解重评估
- `calculateProfit(List<ScheduledTask>) -> int` — 计算调度收益
- `generateScheduleWithSnapshots(List<Task>, Satellite, InsertionMode, Set<Integer>) -> ScheduleSnapshotResult` — 带快照记录的完整调度生成，在指定位置记录前缀状态快照供增量评估复用
- `generateScheduleWithSnapshotRange(List<Task>, Satellite, InsertionMode, int, int) -> ScheduleSnapshotResult` — 记录闭区间内的前缀快照，供连续邻接交换复用；与 Set 入口使用相同解码顺序
- `generateScheduleFromSnapshot(List<Task>, Satellite, InsertionMode, List<ScheduledTask>, int[], int) -> List<ScheduledTask>` — 从快照位置开始的增量调度生成，只处理 startIndex 及之后的任务；已调度 id 快照使用 `int[]`，重建时进入 marker
- `generateScheduleFromSnapshot(List<Task>, Satellite, InsertionMode, List<ScheduledTask>, int[], int, TaskIdMarker) -> List<ScheduledTask>` — 同上，但允许调用方传入 marker scratch，供 delta fast refine 邻接交换循环避免重复 marker 扩容
- `generateScheduleFromSnapshotInPlace(List<Task>, Satellite, InsertionMode, List<ScheduledTask>, int[], int, int, SnapshotReplayScratch) -> List<ScheduledTask>` — 在调用方独占的前缀列表中重放 `[startIndex,endIndex)`，只插入新调度任务，保留已有元素
- `continueScheduleFromSnapshotInPlace(List<Task>, Satellite, InsertionMode, List<ScheduledTask>, int, SnapshotReplayScratch) -> List<ScheduledTask>` — 保留已准备的任务 id marker 和回滚记录，继续重放后缀
- 内部类: `SnapshotReplayScratch` — refiner 独占的 marker、插入结果 carrier 与逆序回滚记录；调用方必须在 finally 中调用 `rollback(List<ScheduledTask>)`，接受的调度必须先复制，不能跨并发调用共享
- 内部类: `TaskIdMarker` — stamp 数组式任务 id marker，用于热路径去重，避免 `HashSet<Integer>` 装箱与 node 分配
- 内部类: `ScheduleSnapshotResult` — 带快照记录的调度生成结果（finalSchedule + scheduleSnapshots + scheduledIdSnapshots，其中 scheduledIdSnapshots 为 `int[]`）

### GREEDY / limited insertion 补充

- `generateSchedule(..., true, Set<Integer>)` 会对指定任务启用 `GREEDY` 的窗口偏好路径；普通 `generateSchedule` 默认不启用。
- `buildPlanByLimitedInsertion` 在 delta fast refine 和锚点修补里复用同一路径；当前通过 `coord.deltaFastRefineWindowPreference=true` 为新增任务启用窗口偏好，额外补充插入候选通路已删除。
- 普通 GREEDY 调度生成路径复用 `GreedyInsertion.ReusableInsertionResult`，避免每次成功插入都创建 `InsertionResult` 包装；公开 schedule 仍返回独立 `ScheduledTask` 元素，不做池化复用；`DecodeWorkspace` 直评路径可复用 workspace-owned 临时 `ScheduledTask`；候选起点会用 `TimeUtils.MIN_TRANSFORMATION_TIME_SECONDS` 先跳过不可能满足姿态转换最小时间的相邻任务间隔。
- `MAX_REMAINING_CAPACITY` 更像窗口级选择器，不是窗口内起点优化；如果继续优化 `GREEDY`，先改窗口内扫描剪枝。

### AssignTaskOperator
- 构造器: `AssignTaskOperator(List<Task>, List<Satellite>, List<Integer>)`
- `assignRandomly() -> List<List<Integer>>` — 随机分配
- `assignBasedTaskNums() -> List<List<Integer>>` — 按任务数量均衡分配
- `assignBasedWindowNums() -> List<List<Integer>>` — 按时间窗口数量分配
- `assignBasedMinRollAngle() -> List<List<Integer>>` — 按最小姿态调整分配
- `assignBasedEarliestTime() -> List<List<Integer>>` — 按最早可用窗口分配
- `assignBasedLongestWindow() -> List<List<Integer>>` — 按最长窗口时长分配
- `assignBasedMinPriority() -> List<List<Integer>>` — 按最低平均优先级分配
- `assignComposite() -> List<List<Integer>>` — 多维度加权 + 冲突感知分配
- `assignCompositeWithCapacity() -> List<List<Integer>>` — 复合分配 + 补漏 + 适应度交换：Phase 1 使用 CompositeStrategy（同策略 7）全量分配，Phase 2 扫描 0 任务卫星从过载卫星偷取最高优先级可行任务，Phase 3 对贪心解码后未调度的任务按优先级降序尝试迁移到备选可行卫星（延迟源星评估，仅接受净适应度增益为正的迁移）
- `assignTaskToSatellites(List<List<Integer>>, List<Task>, List<Satellite>) -> void` — 静态方法，应用分配结果

### Initialize
- `initialize(List<Task>, List<Satellite>) -> List<List<Integer>>` — 仅执行被选中的单一策略生成初始分配；当 `USE_RANDOM_STRATEGY=false` 时只执行 `DEFAULT_STRATEGY_INDEX` 对应策略（当前默认 8 = CompositeWithCapacity）
- `initializeWithStrategy(List<Task>, List<Satellite>, int) -> List<List<Integer>>` — 按指定策略索引（0-8）执行单一分配策略

### DataLoader
- 内部类: `DataSet` — 包含 tasks 和 satellites 的数据容器
- `loadTasks(String) -> List<Task>` — 从 tasklist.txt 加载任务
- `loadTimeWindows(String, List<Task>, int) -> List<Satellite>` — 加载时间窗口数据
- `loadAttitudeRecords(String, List<Satellite>) -> void` — 加载姿态记录数据
- `loadAllData(String, int, int) -> DataSet` — 一次性加载全部数据

### FitnessUtils
- 内部类: `IndexFitnessPair` — 索引-适应度值对
- `sortIndexFitnessDesc(List<Double>) -> List<IndexFitnessPair>` — 降序排序（保留原始索引）
- `sortIndexFitnessAsc(List<Double>) -> List<IndexFitnessPair>` — 升序排序
- `getTopK(List<Double>, int) -> List<IndexFitnessPair>` — 返回 Top-K
- `getMaxIndex(List<Double>) -> int` — 最大值索引
- `getMinIndex(List<Double>) -> int` — 最小值索引
- `binarySearchRoulette(List<Double>, double) -> int` — 轮盘赌二分查找

### ListUtils
- `zeros2DList(int, int) -> List<double[]>` — 创建零填充二维列表
- `zeros1DList(int) -> List<Double>` — 创建零填充一维列表
- `fill2DList(int, int, double) -> List<double[]>` — 指定值填充二维列表
- `fill1DListDouble(int, double) -> List<Double>` — 指定值填充一维列表
- `fill1DListBoolean(int, boolean) -> List<Boolean>` — 布尔值填充一维列表
- `falseMatrix(int, int) -> List<boolean[]>` — 全 false 布尔矩阵
- `initializeRandomPopulation(int, int, double, double, Random) -> List<double[]>` — 随机种群初始化
- `deepCopy2D(List<double[]>) -> List<double[]>` — 二维深拷贝
- `deepCopy2DBool(List<boolean[]>) -> List<boolean[]>` — 布尔二维深拷贝
- `selectRows / selectRowsView / selectElements` — 布尔掩码行列选择
- `assignRows / assignElements` — 掩码赋值
- `combineByMask(...)` — 按掩码合并两矩阵
- `resize2DList / resize1DList` — 列表缩放
- `anyTruePerRow / countTrue / hasAnyTrue` — 布尔聚合
- `negate(List<boolean[]>) -> List<boolean[]>` — 逻辑取反

### CandidateArchive
- 内部类: `ArchiveStatistics` — 接受率/重复率/替换率统计
- 构造器: `CandidateArchive(int)` / `CandidateArchive(int, double, boolean)`
- `addCandidate(double[], double) -> void` — 添加单个候选解（二分插入，重复检测）
- `addCandidates(List<double[]>, List<Double>) -> void` — 批量添加（归并排序）
- `getOptimalSequence(Satellite, List<Task>) -> SchedulingPlan` — 提取最优调度方案
- `size() / isEmpty() / clear() / getMaxSize() / getBestFitness()` — 基本查询
- `getTopSolutions(int) -> List<double[]>` — 返回 top-k 解的深拷贝
- `getBestReEvaluatedFitness(Satellite, List<Task>) -> double` — 双模式重评估最优适应度
- `getStatistics() / resetStatistics()` — 统计信息

## 依赖关系

```
DataLoader ──> model.* (Task, Satellite, TimeWindow, AttitudeRecord)
TimeUtils ──> model.AttitudeRecord
PlanUtils ──> model.* + src.operator.insertion.* + src.common.TuningConfig/TuningDefaults + TimeUtils (隐式)
DecodeWorkspace ──> model.AttitudeRecord/model.Task/model.TimeWindow/model.ScheduledTask + operator.insertion.GreedyInsertion
AssignTaskOperator ──> model.* + src.operator.assignment.* + src.operator.insertion.InsertionMode + PlanUtils + src.common.RandomProvider
Initialize ──> model.* + AssignTaskOperator + src.common.RandomProvider；被 `main.MainMFEAMOPHOA` 与 `main.RunSingleHybridConfig` 共同调用
FitnessUtils ──> (无外部依赖)
ListUtils ──> (无外部依赖)
CandidateArchive ──> model.* + PlanUtils (隐式)
```
