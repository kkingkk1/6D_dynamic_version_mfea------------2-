---
type: project
title: 计划 - 卫星调度混合元启发式项目
project: 6d-dynamic-version-mfea
status: active
updated: 2026-10-09
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

- [x] 将45条全速复测记录更新到论文560条数据、Table X/XI和计时说明，收益图保持原数值；隔离编译并验收PDF。见 [计划](Plan/2026-10-09-update-paper-fullspeed.md)。
- [x] 全速复测目前均值慢于 RK-HMA 的 9 个 Auto-Hybrid 场景，保留原五 seed 和预算，Normal、28 线程、逐 JVM 串行。见 [计划](Plan/2026-10-09-autohybrid-slower-fullspeed.md)。
- [x] 移植 Auto-Hybrid 快照重放/回滚和 GREEDY 秒数缓存；42 项相关测试、8 对实际运行签名及 57,600 次独立选择全部通过。见 [验收报告](Results/Reports/autohybrid-speed-merge-20261009.md)。
- [x] 按参考项目最新基线数据更新自动设计论文，扩展至十区域、六全局、七算法共 560 条；区域/全局图表分列，21 页 PDF 验收完成。见 [更新计划](Plan/2026-10-08-update-paper-current16.md) 和 [报告](Results/Reports/paper-current16-update-20261008.md)。
- [x] 补齐同一 MFEA 胜者在六全局的五 seed 结果；复用 20 条，新增十次，与十区域合成 80/80 条。见 [全局补测计划](Plan/2026-10-08-mfea-current-six-global.md) 和 [16 场景报告](Results/Reports/mfea-current-six-global-20261008.md)。
- [x] 补齐 MFEA 胜者 `[2,0,0,0,4,2]` 在当前十区域的五 seed 结果；复用 25 条历史记录，新增 25 次，50/50 条齐全。见 [补测计划](Plan/2026-10-08-mfea-current-ten-regional.md) 和 [报告](Results/Reports/mfea-current-ten-regional-20261008.md)。
- [x] 使用多场景 MFEA 在 11 个主动父算法的 6D 空间内完成自动设计搜索，记录最优配置、聚合适应度和搜索过程。
- [x] 用 `RunSingleHybridConfig` 复现自动设计得到的最优配置，并在 10 个场景、seed ID 10-14 上做 full-budget replay。
- [x] 建立自动设计结果表：场景、外部基线、8D Hybrid 对照、6D 自动设计均值 / 最优 / 最差、绝对提升、最优 6D 配置。
- [ ] 对收益提升明显的配置做机制分析：父算法组合、G2/G3 update policy、执行顺序和生存选择策略分别贡献什么。
- [x] 量化重分配级联与 delta fast refine 的贡献，重点检查邻接交换和插入候选位置。压缩结论见 [[Knowledge/Removed-Mechanisms|已移除机制]] 和 [[Knowledge/Source-Inventory|Source Inventory]]。
- [ ] 自动设计最优配置产出后，只对最终候选补做一次重分配 / delta fast refine 复核。
- [x] 测试自动设计配置在 500/5 到 10000/100 的 10 个任务-卫星体系下的可扩展性和跨场景稳定性。
- [x] 在 ID1-ID10、原生 `perRun=0..4` 下完成当前 1D Parent 与 Hybrid 的四配置 full-budget 配对运行、seed 验收和 Evidence 分析；每个 `(scene, perRun)` 使用同一实际 seed。旧非原生 seed 批次和 OA1-only parent 对照均不作为当前证据。
- [x] 完成五个外层 MFEA seed 的 Top-5 候选训练筛选，并将胜者 `[2,0,0,0,4,2]` 在 ID1-ID10、原生 `perRun=0..4` 下做全场景五 seed 复现；比较性结论仍待同批基线或候选对照。

## Plan 状态总表

| Plan | 状态 | 测试 | 结果 |
|---|---|---|---|
| [全速复测结果更新论文](Plan/2026-10-09-update-paper-fullspeed.md) | done | 560条来源；112单元；21页PDF检查 | [报告](Results/Reports/paper-fullspeed-update-20261009.md)；九处耗时和正文已更新 |
| [Auto-Hybrid 慢场景全速复测](Plan/2026-10-09-autohybrid-slower-fullspeed.md) | done | 9 场景、45 seed 单元 | 全速复测完成；[验收报告](Results/Reports/autohybrid-slower-than-rkhma-fullspeed-20261009.md) |
| [十区域六全局论文更新](Plan/2026-10-08-update-paper-current16.md) | done | 来源哈希；112 单元独立复算；21 页 PDF 检查 | [报告](Results/Reports/paper-current16-update-20261008.md)；保留描述性比较边界 |
| [MFEA 六全局补测与16场景汇总](Plan/2026-10-08-mfea-current-six-global.md) | done | 首末 seed；30/80 条覆盖；源码输入哈希；后置五项测试 | 复用 20 条、新增十次；[80 条合并报告](Results/Reports/mfea-current-six-global-20261008.md) |
| [MFEA 当前十区域补测](Plan/2026-10-08-mfea-current-ten-regional.md) | done | 前后入口五项测试；首末 seed；50 条覆盖与哈希 | 复用 25 条、新增 25 次；[报告](Results/Reports/mfea-current-ten-regional-20261008.md) |
| MFEA 初始化 | running | compile | fresh Git root |
| [MFEA 激进搜索](Plan/2026-05-29-mfea-aggressive-search-plan.md) | planned | ID1/ID3/ID5 | nPopHyb=35, gMax=20, nRun=3, 60% maxFes |
| 多场景 MFEA full 搜索与 seed10-14 replay | done | ID1/ID3/ID5/ID7 search; ID1-ID10 replay | best `[2,9,0,0,0,2]`, aggregated fitness `2.928452`, replay avg gain +0.58 over 8D Hybrid |
| [四配置全场景五轮配对实验](Plan/2026-07-24-paired-config-all-scenes-perrun0-4.md) | done | ID1-ID10; seed42-46 | 200/200；混合配置对比仍有效，旧 OA1-only parent 对照只作历史证据 |
| [当前 1D Parent 与 Hybrid 全场景配对运行](Plan/2026-07-24-current-1d-parent-all-scenes-perrun0-4.md) | superseded | ID1-ID10；非原生 seed | 旧输出和报告已删除，不再作为 canonical 证据 |
| [原生 perRun 结果更新论文](Plan/2026-07-24-update-paper-with-current-410000-ablation.md) | done | ID1-ID10；原生 perRun0-4 | 200/200、零失败；Evidence、结果简报和论文 Fig. 6/9、Tab. IV–VI 已同步 |
| [Information Sciences 模板 PDF 构建](Plan/2026-07-25-information-sciences-pdf-build.md) | done | 官方 CAS 构建与视觉检查 | `cas-sc.cls` 2.4 成功编译为 25 页 A4 PDF；最终文件仅位于 `vault/Writing/paper_draft.pdf`，中间产物保留在 `outputs/` |
| MFEA 五 seed Top-5 筛选与全场景复现 | done | 5 outer seed；训练 100 次；ID1-ID10 50 次 | `[2,0,0,0,4,2]` 完成 50/50 原生 seed 复现；仅确认候选可复现，未作基线优越性结论 |

### Plan 详情

- fresh MFEA root 只跟踪代码、配置和主线知识文档；历史单算法调参计划、报告、脚本和原始日志保留在本地，但不进入新 Git 历史。
- 下一份 tracked plan 应直接服务 `MainMFEAMOPHOA` 搜索预算、场景矩阵和结果复现实验。

## 关键设计决策

- 6D 混合编码包含两个父算法、两个 update policy、执行顺序和生存选择策略。
- 固定配置 `{4,1,0,0,0,0}` 是对照基线，不是最终目标；主线目标是通过自动设计找到超过该基线的配置。
- 当前父算法搜索空间只包含 ID 0-10 的 11 个主动父算法；ID 11-15 为实现库归档尾部，不进入自动设计搜索。
- 根 `AGENTS.md` 只保留当前架构、默认语义、入口、数据流、模块依赖和回环规则；新 MFEA 实验表格、CI 和阶段流水账归档到 `vault/Results/Reports/`，本文件只同步会改变项目主线的压缩结论。
- 旧 OA1-only parent sanity check 和多维参数格结果只解释 6D 混合空间为何保留 update policy 与 survivor，不再作为当前单算法入口的性能结论。
- `RunSingleParentConfig` 当前只接收 1D `{algorithmIndex}`，由动态重分配层直接调用独立单算法循环，并使用一对一 greedy replacement；新路径需要单独重建收益和耗时基线。
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

## 单算法内部超参数

旧多维单父最优表已移出当前计划。原始报告保留在本地历史 artifacts；新 1D 独立优化器尚未重建跨算法基线。

### 内部超参数快照

- `GA`：`ga.probCrossover=0.9,ga.probMutation=0.15,ga.kTournament=2,ga.sigmaScale=0.2,ga.nElite=1,ga.maxMutationDimRatio=0.1,ga.adaptiveMutation=false`。
- `DE_RAND_1`、`DE_BEST_1`、`DE_CURRENT_TO_RAND_1`：`de.fSchedule=SIGMOID,de.fMax=0.10,de.fMin=0.01,de.crossoverRate=0.3,de.boundaryPolicy=RANDOM_REINIT`。
- `L_SHADE`：`pbestRate=0.4,memorySize=45,archiveRate=3.0,learnPeriod=20,crGaussianStd=0.1,cauchyScale=0.1`。
- `EDA`：`eda.kElite=0.12,eda.sigmaScale=1.00,eda.minSigmaRatio=0.002,eda.stagnationGenerations=0,eda.stagnationBoostRatio=1.0`。
- `PSO`：`pso.enableTVAC=true,pso.tvacC1=2.5->0.5,pso.tvacC2=0.5->2.5,pso.inertia=0.9->0.4,pso.boundaryMode=RANDOM_REBOUND,pso.boundaryRepairRatio=0.05,pso.vMaxLimit=80`。
- `ACO`：`aco.nSample=0.80,aco.intenseFactor=0.35,aco.deviateDistanceRatio=0.5,aco.minSigmaRatio=0.001`。
- `SA`：`freezeRate=0.99,temperature=0.5,temperatureSchedule=LOGARITHMIC,temperatureLogOffset=3.0,adaptiveSigma=false,hybcec.sa.genSAFast=5`。
- `ABC`：`abc.numNoImp=100,abc.phiScale=2.0,abc.phiOffset=1.0`。
- `ALNS`：`innerIterations=3,initialTemperatureRatio=0.032,coolingRate=0.99975,maxDestroyRatio=0.15,sigmaGlobal=30,sigmaLocal=20,sigmaBad=10,reactionFactor=0.5,weightUpdateInterval=3,maxInitialTemperature=100,enableRegret2Repair=false`。

## 阶段结论索引

- 2026-10-09 全速复测结果已进入论文Table X/XI及21页PDF；最新论文560条复现入口见 [报告](Results/Reports/paper-fullspeed-update-20261009.md)，收益图保持，耗时比较保留混合批次边界。

- 2026-10-09 Auto-Hybrid 慢场景45次全速复测完成，最新80条结果保留35条历史记录；后续结果更新使用 [本次报告](Results/Reports/autohybrid-slower-than-rkhma-fullspeed-20261009.md) 所链接的canonical表。
- 2026-10-09 两项等价加速进入 Auto-Hybrid 默认路径；本次 500/5、1000/10 小样本耗时下降 23.92%/28.78%，8 对调度签名相同。结果不外推全场景，见 [报告](Results/Reports/autohybrid-speed-merge-20261009.md)。
- 2026-10-08 论文更新至十区域、六全局；Auto-Hybrid/RK-HMA 区域宏均值 57.12%/56.19%，全局 97.00%/97.01%。来源 seed、运行批次和预算不一致，结论保持描述性；见 [报告](Results/Reports/paper-current16-update-20261008.md)。
- 组件库边界已收口：`InsertionMode` 不进入 6D；G5 保留 4 类 survivor policy；11 个主动父算法进入自动设计搜索空间。
- 单算法和整体框架加速计划已收口；新增性能开关保持 opt-in 或等价旧行为。`OM-3` surrogate prefilter deferred，若恢复需独立立项并用真实评估复测。
- 6D 与 8D 的 `feedback/effective score` 标量语义一致；相关机制收口见 [[Knowledge/Removed-Mechanisms|已移除机制]]。
- Delta fast refine 邻接交换能产生局部正收益，但不会等量传导到最终全局均值；当前更适合作为可开关修补算子，而不是无条件主收益来源。
- 重分配校准策略保留小规模即时校准和 final calibration；大规模中间校准只保留 interval/last 触发。
- 2026-05-16 已重建当前配置 10 场景固定基线；整体单次最好为 `run_index=3`。完整历史报告保留在本地 legacy artifacts。
- 重分配每轮迁移预算应保留；取消预算没有稳定收益，ID5 明显变差且更慢。
- 每类重分配移动中，Standard 是主要贡献来源，Replace 是稳定补充，Swap 更偏小规模，Bundle 是低频高价值修复。
- 旧 OA1-only runtime 与参数格结果只作为 MFEA 组件选择的历史证据，不外推到当前 1D 独立优化器。
- GA、DE、L-SHADE、EDA、PSO、ACO、SA、ABC、ALNS 的内部默认已收口为本文件“内部超参数快照”；后续不再沿单算法调参主线展开。
- 2026-06-17 多场景 MFEA full 搜索选出 `[2,9,0,0,0,2]`，即 EDA + L-SHADE、FULL/FULL、SERIAL、PAIRWISE_GREEDY；设计阶段最佳聚合适应度为 `2.928452`。
- 该配置在 seed ID 10-14 的 10 场景 full-budget replay 中，相比最新 8D Hybrid 平均收益全场景提升 `+0.58` 个百分点，6 个非饱和场景提升 `+0.97` 个百分点；最佳单种子为 seed ID 13，总和 `770.95`，均值 `77.09`。
- 2026-07-24 的 seed42-46 四配置配对实验再次验证 `[2,9,0,0,0,2]`：相对 `{4,1,0,0,0,0}` 为 6 胜、4 平、0 负，场景宏平均提高 `0.4458` 个百分点。完整数据见 [[Results/Reports/2026-07-24-paired-config-all-scenes-perrun0-4|四配置全场景五轮配对实验报告]]。
- 2026-07-25 原生 `perRun=0..4` 四配置实验重建了当前 1D Parent 消融证据：`410000` 比 Parent 4 高 `1.0526` pp、比 Parent 1 高 `2.1078` pp，均为 6 胜、4 平、0 负；`410000` 比 `290002` 低 `0.4272` pp，为 0 胜、4 平、6 负。三个 exact Wilcoxon raw `p=0.03125`，Holm 校正后均为 `p=0.09375`，只支持方向一致和实际效应，不支持校正后显著性措辞。结果已同步到论文 Fig. 6/9、Tab. IV–VI、摘要和结论；详见 [[Results/Reports/paired-native-perrun0-4-10scene-20260724-r01|Native Paired Ablation 总结]]。
- 2026-08-17 五个 outer seed 的 Top-5 训练筛选后，`[2,0,0,0,4,2]` 在 ID1-ID10、原生 seed ID `10..14` 下完成 50/50 复现，十场景宏平均 `77.0034%`。训练第一、二名仅差 `0.0375 pp`，且最终无同批基线，因此该结果只确认候选可复现，不升级为默认或基线优越性结论；详见 [[Results/Reports/mfea-top5-train-final-all10-20260817|MFEA Top-5 训练筛选与全场景复现]]。
- 2026-10-08 同配置补齐当前十区域（排除旧 1000/20、包含新 2000/20），复用 25 条、新增 25 次，50/50 条完成；宏平均 57.1246%，历史与新增来源分列。见 [报告](Results/Reports/mfea-current-ten-regional-20261008.md)。
- 2026-10-08 同配置补齐六全局，复用 20 条、新增十次；新 3000/30、4000/40 均值 94.9940%、96.0717%。十区域加六全局共 80/80 条，见 [合并报告](Results/Reports/mfea-current-six-global-20261008.md)。
