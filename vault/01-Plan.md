---
type: project
title: 计划 - 卫星调度混合元启发式项目
project: 6d-dynamic-version-mfea
status: active
updated: 2026-05-28
---

# 计划

## 研究问题

如何在 11 个主动父算法构成的 6D 配置空间中自动设计混合元启发式组合，并结合跨卫星动态任务重分配，使自动设计配置获得超过固定基线 `{4,1,0,0,0,0}` 的调度收益？

## 当前目标

- 运行 `MainMFEAMOPHOA` 搜索 6D 混合配置，产出相对固定基线 `{4,1,0,0,0,0}` 有收益提升的自动设计配置。
- 用 `RunSingleHybridConfig` 复现实验自动设计得到的候选配置，并与固定基线在相同场景、预算和 `tuning.properties` 下对比。
- 分析自动设计收益来自父算法组合、G2/G3 update policy、执行顺序、生存选择策略，还是来自重分配级联与 delta fast refine 的交互。
- 在多卫星场景上验证自动设计配置的可迁移性，规模可扩展到 10000 个任务 / 100 颗卫星。

## 当前任务

- [ ] 使用 `MainMFEAMOPHOA` 在 11 个主动父算法的 6D 空间内做自动设计搜索，记录最优配置、平均收益、最佳收益和搜索过程。
- [ ] 用 `RunSingleHybridConfig` 复现自动设计得到的最优配置，并与固定基线 `{4,1,0,0,0,0}` 做同预算对比。
- [ ] 建立自动设计结果表：场景、基线收益、自动设计收益、绝对提升、相对提升、最优 6D 配置。
- [ ] 对收益提升明显的配置做机制分析：父算法组合、G2/G3 update policy、执行顺序和生存选择策略分别贡献什么。
- [x] 量化重分配级联与 delta fast refine 的贡献，重点检查邻接交换和插入候选位置。压缩结论见 [[Knowledge/Removed-Mechanisms|已移除机制]] 和 [[Knowledge/Source-Inventory|Source Inventory]]。
- [ ] 自动设计最优配置产出后，只对最终候选补做一次重分配 / delta fast refine 复核。
- [ ] 测试自动设计配置在不同任务数和卫星数下的可扩展性和跨场景稳定性。
- [ ] 后续 MFEA 搜索方案写入 `vault/Plan/`，完整 MFEA 实验结果写入 `vault/Results/Reports/`，本文件只同步会改变项目主线的压缩结论。

## Plan 状态总表

| Plan | 状态 | 测试 | 结果 |
|---|---|---|---|
| MFEA 初始化 | running | compile | fresh Git root |

### Plan 详情

- fresh MFEA root 只跟踪代码、配置和主线知识文档；历史单算法调参计划、报告、脚本和原始日志保留在本地，但不进入新 Git 历史。
- 下一份 tracked plan 应直接服务 `MainMFEAMOPHOA` 搜索预算、场景矩阵和结果复现实验。

## 关键设计决策

- 6D 混合编码包含两个父算法、两个 update policy、执行顺序和生存选择策略。
- 固定配置 `{4,1,0,0,0,0}` 是对照基线，不是最终目标；主线目标是通过自动设计找到超过该基线的配置。
- 当前父算法搜索空间只包含 ID 0-10 的 11 个主动父算法；ID 11-15 为实现库归档尾部，不进入自动设计搜索。
- 根 `AGENTS.md` 只保留当前架构、默认语义、入口、数据流、模块依赖和回环规则；新 MFEA 实验表格、CI 和阶段流水账归档到 `vault/Results/Reports/`，本文件只同步会改变项目主线的压缩结论。
- ID1 的 OA1-only parent sanity check 已验证 11 个主动父算法都能通过 `RunSingleParentConfig` 跑完；收益和耗时差异明显，自动设计结果需要同时报告 profit 和 wall time。
- 2026-05-18 的 ID1 单父 `{updatePolicy,survivor}` 参数格搜索显示，各算法最佳策略不同。全局最好按 AvgProfit 为 `L_SHADE {9,3,0}` 与 `DE_RAND_1 {4,0,0}` 并列 `2740.33`；这支持保留算法组件、更新范围和 survivor 三类语义。
- `InsertionMode` 保持运行时消融开关，不升级为 6D 搜索基因。ID1 消融显示 `GREEDY` 仍是收益最好且耗时最低的默认值。
- G2/G3 已收敛为 7 个 update policy：`FULL`、`TOP_SUBSET`、`MIXED_SUBSET`、`RANDOM_DECAY`、`ABOVE_MEAN`、`LOCAL_SEARCH`、`WORST_REPAIR`。
- G4 已扩为 8 个 operation-order policy：`SERIAL`、`PERIODIC_SWITCH`、`STAGE_SWITCH`、`BEST_NO_IMPROVEMENT_SWITCH`、`PROCESS_NO_IMPROVEMENT_SWITCH`、`DIVERSITY_SWITCH`、`PARALLEL`、`ADAPTIVE_CREDIT`。
- G5 保持 4 个 survivor policy：`ELITIST_BEST_N`、`TOURNAMENT`、`PAIRWISE_GREEDY`、`RANK_WEIGHTED`。固定对照基线仍保留 `{4,1,0,0,0,0}`。
- `TargetSatelliteRanker` 只使用低成本排序，并按固定 Top-K 返回候选目标星；普通任务默认 Top-2，prioritized 任务默认 Top-4。
- 重分配每轮迁移预算保留为工程 guard：默认每轮最多接受 `min(ceil(未调度任务数 * 0.20), 12)` 个迁移，至少 1 个。
- 已移除机制、删除理由和恢复条件统一维护在 [[Knowledge/Removed-Mechanisms|已移除机制]]。
- 重分配校准策略保持简化后主线：小规模任务刷新 best 后立即用热启动 HybCec 做完整 assignment 校准；大规模任务才允许跳过中间校准，并在末尾 final calibration 兜底。
- Phase D 搜索质量增强作为 opt-in 配置接入，默认 `{4,1,0,0,0,0}` 路径保持旧行为或中性参数；当前算法默认快照见下节。
- `OM-3` surrogate prefilter 只服务 `MainMFEAMOPHOA` 外层自动设计搜索；它会改变搜索轨迹，后续必须默认关闭、保留探索 quota，并用真实评估复测最终 best config。

## 待回答问题

- 自动设计配置相对固定基线的收益提升是否能在 ID1/ID3/ID5 和更大规模场景中重复出现？
- 自动设计搜索需要多大的外层种群、代数和内层评估预算，才能稳定超过固定基线？
- 性能对 6D 配置向量中每一维有多敏感？

## 当前阶段结论快照

- 6D 搜索空间保持 `{parent1,parent2,update1,update2,operationOrder,survivor}`；`de.*`、`hybcec.insertionMode`、父算法内部参数和 speedup 开关只作为运行时配置。
- 单算法内部超参数每个算法只保留一套代码默认。当前固定为 GA `0.9/0.15/k2/sigma0.2/elite1/mutationDim0.1/adaptive=false`，DE 系 `SIGMOID F=0.10->0.01,CR=0.3,RANDOM_REINIT`，L-SHADE `pbestRate=0.4,memorySize=45,archiveRate=3.0,learnPeriod=20,crStd=0.1,cauchy=0.1`，EDA `kElite=0.12,sigmaScale=1.00,minSigmaRatio=0.002,stagnation=off`，PSO `TVAC + RANDOM_REBOUND r=0.05 + vMaxLimit=80`，ACO `0.80/0.35/0.5/0.001`，SA `freezeRate=0.99,temperature=0.5,LOGARITHMIC offset=3.0`，ABC `numNoImp=100,phiScale=2.0,phiOffset=1.0`，ALNS A37 `initialTemperatureRatio=0.032,coolingRate=0.99975`。
- Phase D 和 speedup 新增性能 / 调参开关默认关闭、unset 或等价旧行为；改变搜索轨迹的开关必须用真实评估复测最终配置。

## 单算法最优配置与内部超参数

### 单父最优配置总表

| 算法 | 配置 | 平均收益 | 最优收益 |
|---|---|---:|---:|
| GA | `0,0,0` | `2735.67` | `2743.00` |
| PSO | `1,2,0` | `2729.33` | `2732.00` |
| EDA | `2,2,2` | `2738.00` | `2740.00` |
| ACO | `3,3,0` | `2693.33` | `2698.00` |
| DE_RAND_1 | `4,0,0` | `2740.33` | `2741.00` |
| DE_BEST_1 | `5,4,2` | `2739.00` | `2741.00` |
| DE_CURRENT_TO_RAND_1 | `6,5,0` | `2737.67` | `2740.00` |
| ABC | `7,1,1` | `2694.67` | `2699.00` |
| SA | `8,1,1` | `2724.33` | `2727.00` |
| L_SHADE | `9,3,0` | `2740.33` | `2742.00` |
| ALNS | `10,1,0` | `2737.00` | `2740.00` |

数据来自历史单父参数格搜索和 GA 参数影响实验；原始报告保留在本地 legacy artifacts，不进入 fresh MFEA Git 历史。

### 内部超参数快照

- `GA {0,0,0}`：`ga.probCrossover=0.9,ga.probMutation=0.15,ga.kTournament=2,ga.sigmaScale=0.2,ga.nElite=1,ga.maxMutationDimRatio=0.1,ga.adaptiveMutation=false`。
- `DE_RAND_1 {4,0,0}`、`DE_BEST_1 {5,4,2}`、`DE_CURRENT_TO_RAND_1 {6,5,0}`：`de.fSchedule=SIGMOID,de.fMax=0.10,de.fMin=0.01,de.crossoverRate=0.3,de.boundaryPolicy=RANDOM_REINIT`。
- `L_SHADE {9,3,0}`：`pbestRate=0.4,memorySize=45,archiveRate=3.0,learnPeriod=20,crGaussianStd=0.1,cauchyScale=0.1`。
- `EDA {2,2,2}`：`eda.kElite=0.12,eda.sigmaScale=1.00,eda.minSigmaRatio=0.002,eda.stagnationGenerations=0,eda.stagnationBoostRatio=1.0`。
- `PSO {1,2,0}`：`pso.enableTVAC=true,pso.tvacC1=2.5->0.5,pso.tvacC2=0.5->2.5,pso.inertia=0.9->0.4,pso.boundaryMode=RANDOM_REBOUND,pso.boundaryRepairRatio=0.05,pso.vMaxLimit=80`。
- `ACO {3,3,0}`：`aco.nSample=0.80,aco.intenseFactor=0.35,aco.deviateDistanceRatio=0.5,aco.minSigmaRatio=0.001`。
- `SA {8,1,1}`：`freezeRate=0.99,temperature=0.5,temperatureSchedule=LOGARITHMIC,temperatureLogOffset=3.0,adaptiveSigma=false,hybcec.sa.genSAFast=5`。
- `ABC {7,1,1}`：`abc.numNoImp=100,abc.phiScale=2.0,abc.phiOffset=1.0`。
- `ALNS {10,1,0}`：`innerIterations=3,initialTemperatureRatio=0.032,coolingRate=0.99975,maxDestroyRatio=0.15,sigmaGlobal=30,sigmaLocal=20,sigmaBad=10,reactionFactor=0.5,weightUpdateInterval=3,maxInitialTemperature=100,enableRegret2Repair=false`。

## 阶段结论索引

- 组件库边界已收口：`InsertionMode` 不进入 6D；G5 保留 4 类 survivor policy；11 个主动父算法进入自动设计搜索空间。
- 单算法和整体框架加速计划已收口；新增性能开关保持 opt-in 或等价旧行为。`OM-3` surrogate prefilter deferred，若恢复需独立立项并用真实评估复测。
- 6D 与 8D 的 `feedback/effective score` 标量语义一致；相关机制收口见 [[Knowledge/Removed-Mechanisms|已移除机制]]。
- Delta fast refine 邻接交换能产生局部正收益，但不会等量传导到最终全局均值；当前更适合作为可开关修补算子，而不是无条件主收益来源。
- 重分配校准策略保留小规模即时校准和 final calibration；大规模中间校准只保留 interval/last 触发。
- 2026-05-16 已重建当前配置 10 场景固定基线；整体单次最好为 `run_index=3`。完整历史报告保留在本地 legacy artifacts。
- 重分配每轮迁移预算应保留；取消预算没有稳定收益，ID5 明显变差且更慢。
- 每类重分配移动中，Standard 是主要贡献来源，Replace 是稳定补充，Swap 更偏小规模，Bundle 是低频高价值修复。
- Speedup 后 ID1 单父 runtime 表显示，`DE_BEST_1` 最快，`DE_RAND_1` AvgProfit 最高；该结果只作为 MFEA 父算法代价参考。
- ID1 单父 `{updatePolicy,survivor}` 参数格搜索显示，`L_SHADE {9,3,0}` 与 `DE_RAND_1 {4,0,0}` 按 AvgProfit 并列第一；该结果支持保留 update policy 和 survivor 语义。
- GA、DE、L-SHADE、EDA、PSO、ACO、SA、ABC、ALNS 的内部默认已收口为本文件“内部超参数快照”；后续不再沿单算法调参主线展开。
