# model 模块摘要

## 模块职责

卫星成像任务调度的领域模型层。定义了 6D 自动设计、单配置评估、HybCec 单星优化与多卫星重分配流程共同复用的核心实体：姿态记录、时间窗口、任务、卫星、调度结果和调度方案。

## 成员清单

| 文件 | 类名 | 职责 |
|------|------|------|
| `AttitudeRecord.java` | `AttitudeRecord` | 姿态角度记录，表示某时刻的滚转角和俯仰角 |
| `TimeWindow.java` | `TimeWindow` | 时间窗口，定义卫星对任务的可观测时段及其姿态数据 |
| `Task.java` | `Task` | 成像任务实体，包含地理位置、优先级、成像时长和各卫星的时间窗口 |
| `Satellite.java` | `Satellite` | 卫星实体，持有时间窗口列表和已分配任务列表 |
| `SatelliteTaskPair.java` | `SatelliteTaskPair` | 不可变值对象，表示 (卫星ID, 任务ID) 配对 |
| `ScheduledTask.java` | `ScheduledTask` | 已调度任务，包装 Task 并附加调度上下文（卫星、时间窗口、姿态记录） |
| `SchedulingPlan.java` | `SchedulingPlan` | 调度方案对象，包含任务序列、调度结果和适应度值，作为 HybCec/重分配/后处理链路中的统一计划表示 |

## 依赖关系图

```
AttitudeRecord          ← 叶节点，无模块内依赖
SatelliteTaskPair       ← 叶节点，无模块内依赖

TimeWindow ──────────→ AttitudeRecord
Task ─────────────────→ TimeWindow
Satellite ────────────→ TimeWindow, Task
ScheduledTask ────────→ Task, TimeWindow, AttitudeRecord
SchedulingPlan ───────→ Task, ScheduledTask
```

## 接口说明

### AttitudeRecord
- `AttitudeRecord(int year, int month, int day, int hour, int minute, double second, double roll, double pitch)` — 从原始数据构造（仅 hour/minute/second 参与计算）
- `double getRollAngle()` — 获取滚转角
- `double getPitchAngle()` — 获取俯仰角
- `double getTotalSeconds()` — 获取当日秒数

### TimeWindow
- `TimeWindow(int satelliteId, int taskId, ...)` — 从 14 列原始数据构造
- `double getStartTime() / getEndTime() / getDuration()` — 时间属性
- `int getSatelliteId() / getTaskId()` — 关联 ID
- `List<AttitudeRecord> getAttitudeRecords()` — 获取姿态记录（不可变视图）
- `double getAttitudeRecordTimeSeconds(int index)` — 直接读取指定姿态记录的秒数，供插入热路径避免重复对象链读取
- `double[] getAttitudeRecordTimesUnsafe()` — 惰性构建并发布与记录顺序一致的只读秒数缓存；加载完成后支持并行只读，调用方不能修改数组。set/add/addAll/clear 记录时失效。窗口子类、记录子类或 null 记录返回 null，保留原对象访问语义；不支持并发修改记录列表
- `void addAttitudeRecord(AttitudeRecord)` — 添加姿态记录
- `boolean overlaps(TimeWindow)` — 判断时间窗口是否重叠
- `boolean contains(double time)` — 判断时间点是否在窗口内
- `boolean canAccommodate(double startTime, double duration)` — 判断能否容纳指定时长
- `boolean canAccommodateTask(int taskDuration)` — 判断姿态记录数是否足够

### Task
- `Task(int id, double lon, double lat, int priority, int duration)` — 构造函数
- `List<List<TimeWindow>> getTimeWindows()` — 获取所有卫星的时间窗口（不可变视图）
- `List<TimeWindow> getTimeWindowsForSatellite(int satelliteId)` — 获取指定卫星的时间窗口
- `int getTotalTimeWindowCount()` — 获取所有卫星时间窗口总数，供 ALNS ranked destroy 避免反复遍历窗口列表
- `void initializeTimeWindows(int numSatellites)` — 初始化时间窗口列表
- `void addTimeWindowsForSatellite(int satelliteId, List<TimeWindow>)` — 为指定卫星添加时间窗口
- `boolean hasTimeWindows()` — 是否存在时间窗口
- 标准 getter/setter: `id`, `longitude`, `latitude`, `priority`, `imagingDuration`

### Satellite
- `Satellite()` / `Satellite(int id)` — 构造函数
- `void addTask(Task) / removeTask(Task) / clearTasks()` — 任务管理
- `int getTaskCount() / boolean hasTasks()` — 任务查询
- `int getTimeWindowCount()` — 时间窗口数量
- 标准 getter/setter: `id`, `timeWindows`, `assignedTasks`

### SatelliteTaskPair
- `SatelliteTaskPair(int satelliteId, int taskId)` — 构造函数
- `int getSatelliteId() / int getTaskId()` — 获取 ID
- 不可变对象，支持 `equals` / `hashCode`

### ScheduledTask
- `ScheduledTask(Task task)` — 从 Task 构造
- `void resetSchedule(Task, TimeWindow, AttitudeRecord start, AttitudeRecord end)` — 重置为新的调度分配，供 workspace-owned 热路径对象复用
- `void setSchedule(TimeWindow, AttitudeRecord start, AttitudeRecord end)` — 设置调度分配
- `double getStartTime() / getEndTime() / getDuration()` — 调度时间
- `int getPriority() / int getTaskId()` — 委托给内部 Task
- `boolean isScheduled()` — 是否已调度
- 标准 getter/setter: `satelliteId`, `timeWindow`, `startRecord`, `endRecord`

### SchedulingPlan
- `SchedulingPlan(List<Task> taskSequence)` — 从任务序列构造
- `SchedulingPlan(SchedulingPlan other)` / `copy()` — 深拷贝
- `void setSchedule(List<ScheduledTask>)` / `setScheduleUnsafe(List<ScheduledTask>)` / `addScheduledTask(ScheduledTask)` — 设置调度结果；`setScheduleUnsafe` 仅用于调用方持有并承诺不再修改列表的热路径
- `int getTotalProfit()` — 计算总收益（优先级之和）；热路径使用 index loop，避免 stream spliterator 分配
- `Double getFitness() / void setFitness(Double)` — 适应度管理
- `boolean isFitnessCalculated() / void invalidateFitness()` — 适应度状态
- `List<Task> getTaskSequence()` / `List<ScheduledTask> getSchedule()` — 获取序列和调度（不可变视图）
