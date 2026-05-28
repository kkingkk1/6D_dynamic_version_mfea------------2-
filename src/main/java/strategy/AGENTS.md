# strategy 模块摘要

## 概述

`strategy` 模块实现了 **策略模式 (Strategy Pattern)**，将不同的元启发式优化算法封装在统一接口 `ParentStrategy` 之后，供混合进化算法框架调用。外层 6D MFEA 自动设计只负责搜索“选哪两个父算法、操作级别和顺序”等配置；真正的父算法执行由本模块在 `core.HybCec` 中通过 `apply(ParentContext, StrategyInput)` 落地。

## 成员清单

| 文件 | 类型 | 职责 |
|------|------|------|
| `ParentStrategy.java` | 接口 | 核心策略抽象，定义 `apply()` 与可携带已评估 fitness 的 `applyWithResult()` 入口 |
| `ParentUpdateResult.java` | 值对象 | 父算法输出包装，携带新种群和可选的已评估适应度 |
| `ParentContext.java` | 类 (不可变, Builder) | 执行上下文对象，封装共享状态、算法工作区访问器和算法专属子上下文 |
| `StrategyInput.java` | 类 (不可变, Builder) | 数据传输对象，携带种群、适应度等输入参数 |
| `DERand1Strategy.java` | 策略实现 | DE/rand/1 差分进化 |
| `DERand2Strategy.java` | 策略实现 | DE/rand/2 差分进化 |
| `DEBest1Strategy.java` | 策略实现 | DE/best/1 差分进化 |
| `DEBest2Strategy.java` | 策略实现 | DE/best/2 差分进化 |
| `DECurrentToBestStrategy.java` | 策略实现 | DE/current-to-best 差分进化 |
| `DERandToBestStrategy.java` | 策略实现 | DE/rand-to-best 差分进化 |
| `DECurrentToRandStrategy.java` | 策略实现 | DE/current-to-rand/1 差分进化 |
| `GAStrategy.java` | 策略实现 | 遗传算法 (GA) |
| `EDAStrategy.java` | 策略实现 | 分布估计算法 (EDA) |
| `ACOStrategy.java` | 策略实现 | 蚁群优化 (ACO)，向算法层传递 cached fitness rank |
| `PSOStrategy.java` | 策略实现 | 粒子群优化 (PSO) |
| `ABCStrategy.java` | 策略实现 | 人工蜂群 (ABC, 有副作用: 更新 limit 和迭代计数) |
| `SAStrategy.java` | 策略实现 | 模拟退火 (SA, 有副作用: 更新 sigma 和迭代计数) |
| `SHADEStrategy.java` | 策略实现 | 自适应差分进化 SHADE (有副作用: 更新 SHADE 记忆) |
| `ALNSStrategy.java` | 策略实现 | 自适应大邻域搜索 (ALNS, 内部执行 destroy/repair 局部搜索并按真实评价次数追加预算计数) |

## 接口说明

### ParentStrategy (核心接口)

```java
public interface ParentStrategy {
    List<double[]> apply(ParentContext context, StrategyInput input) throws Exception;
    default ParentUpdateResult applyWithResult(ParentContext context, StrategyInput input) throws Exception;
}
```

所有 15 个具体策略均实现此接口。默认 `applyWithResult()` 只包装 `apply()` 结果，不附带 fitness。ALNS 覆盖该入口，把局部搜索内部已经真实评估过的候选 fitness 传给 `PopulationManager`，用于消除重复外层评价。

### ParentUpdateResult

- `unevaluated(updatedPopulation)` — 普通父算法路径，只返回新染色体，外层继续真实评价。
- `evaluated(updatedPopulation, evaluatedFitness)` — 局部搜索父算法路径，要求两者长度一致；只有组件 mask 覆盖全维时，`PopulationManager` 才复用 fitness。
- 缓存 fitness 复用不增加 eval 计数；ALNS 内部真实 evaluator 调用由 `ALNSResult.evaluationCount()` 单独计入。

### ParentContext (执行上下文)

通用字段:
- `D` — 问题维度
- `satellite` / `allTasks` — 卫星调度评估所需的领域对象
- `rand` — 随机数生成器
- `genSupplier` / `getGen()` — 当前代数
- `itera` / `maxItera` — 迭代计数与上限
- `count` — 待更新个体数
- `stateUpdater` — 状态回调接口 (更新 HybCec 共享状态)
- `getSingleEvaluator()` — 可选单染色体直评函数，供 ALNS 等局部搜索热路径避免单元素种群包装
- `getSequenceEvaluator()` — 可选任务序列直评函数，供 ALNS 内部候选避免 `encode -> decode` 往返
- `getDEWorkspace()` / `getPSOWorkspace()` / `getSAWorkspace()` / `getACOWorkspace()` / `getEDAWorkspace()` / `getABCWorkspace()` — 访问 `HybCecState` 持有的复用工作区
- `getAlnsDestroyOperators(config)` / `getAlnsRepairOperators(config)` — 按当前 ALNSConfig 获取同一运行内复用的 destroy/repair operator state
- `getCountNoImprove()` — 读取当前全局最优停滞计数，供 opt-in 停滞感知策略使用

算法专属子上下文 (静态内部类):
- `ABCContext` — `limitABC`, `ABCConfig`, 可选 `evaluator`
- `SAContext` — `sigma`, `SAConfig`, 可选 `evaluator`
- `SHADEContext` — `SHADEConfig`, `shadeGG`, `nPop`, 四组适应度列表
- `PSOContext` — `velocity`, `PSOConfig`

访问方式: `getXxxContext()` 返回 `Optional`，`requireXxxContext()` 不存在时抛异常。

### StrategyInput (输入数据)

必填字段:
- `population` — 完整种群 `List<double[]>`
- `selectedIndices` — 被选中个体的索引 `int[]`

可选字段:
- `populationFitness` — 适应度值 `List<Double>`
- `fitnessRankDesc` — 可选降序 rank 缓存，供 ACO/SHADE/L-SHADE 避免重复适应度排序
- `pbestSolution` — 个体最优 (PSO) `List<double[]>`
- `gbestSolution` — 全局最优 (PSO) `double[]`
- `indToBeUpdated` — 更新掩码 (PSO/SA) `List<Boolean>`

## 策略分类

### 配置注入型 (构造器传入 Config)
DERand1, DERand2, DEBest1, DEBest2, DECurrentToBest, DERandToBest, DECurrentToRand, GA, EDA, ACO, PSO

### 上下文驱动型 (无参构造器，运行时从 ParentContext 获取配置)
ABC, SA, SHADE

### 有副作用的策略 (通过 StateUpdater 回调修改共享状态)
ABC, SA, SHADE, ALNS

### 纯函数策略 (仅返回新种群，无副作用)
DERand1, DERand2, DEBest1, DEBest2, DECurrentToBest, DERandToBest, DECurrentToRand, GA, EDA, ACO, PSO

DE、PSO 与 ACO 策略在 HybCec 热路径调用算法层 `*Unsafe` / `runUnsafe` 入口。ACO 会把 `StrategyInput.fitnessRankDesc` 传给算法层，复用当前种群 rank。公开 safe API 保留参数校验，供测试和外部调用使用；HybCec 在初始化与种群 resize 边界做一次性 PSO 状态校验。

## 父算法索引映射

当前 6D 搜索只暴露 ID 0 到 10 的主动父算法。ID 11 到 15 是实现库归档尾部，不进入当前混合配置搜索空间。

| 索引 | 状态 | 算法 | 策略类 | 实现类 |
|------|------|------|--------|--------|
| 0 | 主动 | GA | `GAStrategy` | `GeneticAlgorithmNoSelect` |
| 1 | 主动 | PSO | `PSOStrategy` | `PSO` |
| 2 | 主动 | EDA | `EDAStrategy` | `EDAGaussSam` |
| 3 | 主动 | ACO | `ACOStrategy` | `ACOGaussGenerate` |
| 4 | 主动 | DE/rand/1 | `DERand1Strategy` | `DERand1` |
| 5 | 主动 | DE/best/1 | `DEBest1Strategy` | `DEBest1` |
| 6 | 主动 | DE/current-to-rand/1 | `DECurrentToRandStrategy` | `DECurrentToRand` |
| 7 | 主动 | ABC | `ABCStrategy` | `ABC` |
| 8 | 主动 | SA | `SAStrategy` | `SACont` |
| 9 | 主动 | L-SHADE | `SHADEStrategy` | `SHADELoopBrief` + `ResizePop` |
| 10 | 主动 | ALNS | `ALNSStrategy` | `ALNS` |
| 11 | 归档尾部 | DE/rand/2 | `DERand2Strategy` | `DERand2` |
| 12 | 归档尾部 | DE/best/2 | `DEBest2Strategy` | `DEBest2` |
| 13 | 归档尾部 | DE/current-to-best/1 | `DECurrentToBestStrategy` | `DECurrentToBest` |
| 14 | 归档尾部 | DE/rand-to-best/1 | `DERandToBestStrategy` | `DERandToBest` |
| 15 | 归档尾部 | SHADE | `SHADEStrategy` | `SHADELoopBrief` |

## 外部依赖

- `src.algorithm.de.*` — DE 系列算法实现 (DERand1, DERand2, DEBest1, DEBest2, DECurrentToBest, DERandToBest, DECurrentToRand, DEConfig)
- `src.algorithm.ga.GeneticAlgorithmNoSelect` / `src.algorithm.workspace.GAWorkspace` — GA 算法实现与复用缓冲
- `src.algorithm.eda.EDAGaussSam` — EDA 算法实现
- `src.algorithm.aco.ACOGaussGenerate` — ACO 算法实现
- `src.algorithm.pso.PSO` — PSO 算法实现
- `src.algorithm.abc.ABC` — ABC 算法实现
- `src.algorithm.alns.ALNS` — ALNS 算法实现
- `src.algorithm.sa.SACont` — SA 算法实现
- `src.algorithm.shade.SHADELoopBrief` / `src.algorithm.workspace.SHADEWorkspace` — SHADE 算法实现与 full-update 复用缓冲
- `src.core.state.StateUpdater` — 状态更新回调接口
- `model.Satellite` / `model.Task` — 卫星调度领域模型
- `operator.insertion.InsertionMode` — ABC fallback 评估的默认插入模式
- `utils.ListUtils` — 列表工具 (PSOStrategy 使用)
