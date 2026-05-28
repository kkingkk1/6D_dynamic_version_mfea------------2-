---
type: meta
title: 来源清单 - 6D_dynamic_version_mfea
project: 6d-dynamic-version-mfea
updated: 2026-05-28T00:00:00+08:00
---

# 来源清单

来源仓库：`E:\OneDrive\project\paper_reproduction\AutoHyb\Code4mfea_mophoa_2\Code4mfea_mophoa_java_satellite_scheduling_test\6D_dynamic_version_mfea`。

## 规范 Markdown 来源

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `src\main\java\algorithm\AGENTS.md`
- `src\main\java\common\AGENTS.md`
- `src\main\java\core\AGENTS.md`
- `src\main\java\main\AGENTS.md`
- `src\main\java\model\AGENTS.md`
- `src\main\java\operator\AGENTS.md`
- `src\main\java\strategy\AGENTS.md`
- `src\main\java\utils\AGENTS.md`
- `vault\00-Hub.md`
- `vault\01-Plan.md`
- `vault\Knowledge\Architecture-Deep-Dive.md`
- `vault\Knowledge\Codebase-Overview.md`
- `vault\Knowledge\Removed-Mechanisms.md`
- `vault\Knowledge\Source-Inventory.md`

`.codepilot-uploads`、`.claude/logs`、`.serena/memories`、`target`、`outputs`、`result` 下的 Markdown 属于生成物或临时材料，不进入规范项目清单。

旧单算法调参 daily、plan、report 和脚本保留在本地 legacy artifacts 中，但不进入 fresh MFEA Git 历史。当前 tracked 文档只保留 MFEA 主线入口和可复用知识。

`src\main\java\main\test1.md` 已从源码树移除。该文件是临时优化笔记，不是模块文档或源码文件。

## 代码与配置快照

- 构建文件：`pom.xml`，Java 21，Maven。
- 运行时配置：`tuning.properties`。
- Java 源文件数：`algorithm=28`，`common=11`，`core=15`，`main=19`，`model=7`，`operator=36`，`strategy=18`，`utils=9`。
- 当前混合染色体长度：`AlgorithmConstants.HYBRID_CONFIG_DIMENSION = 6`。
- 当前默认基线：`{4,1,0,0,0,0}`。
- 当前 G2/G3 搜索空间为 7 个 update policy；`hybcec.mixedTopRatio` 仅作为 `MIXED_SUBSET` 的运行时参数。
- 当前 G4 搜索空间为 8 个 operation-order policy；`ADAPTIVE_CREDIT` 是 AutoHyb 扩展项，periodic/process/diversity 类切换按 `itera` 评估预算计。
- 目标星排序已对齐 8D cheap-only fixed Top-K 语义：普通任务 Top-2，prioritized 任务 Top-4，卫星侧 `B_j` 通路已删除，最终 cheap rank 只保留任务-卫星配对特征和任务侧条件项。
- 动态重分配保留每轮迁移预算 guard：默认每轮最多接受 `min(ceil(未调度任务数 * 0.20), 12)` 个迁移；2026-05-15 的 ID1/ID3/ID5 消融显示取消该预算无稳定收益，ID5 均值下降 10.00、最优下降 30.00。
- 动态重分配已删除 tabu 机制：`tuning.properties` 不再包含 `eval.tabuTenure`，`TaskAllocationCoordinator` 不再维护 tabu 表或 blocked-history，目标星选择不再做回迁禁忌过滤。2026-05-15 的 no-tabu 消融显示 ID1 均值比原 `tabuTenure=2` 高 2.00，ID3/ID5 无差异。
- Delta fast refine 的新增任务数、单轮变化比例和累计变化比例 eligibility guard 均已移除。ID1/ID3/ID5 的 `nRun=3` A/B 未发现单轮变化比例 guard 影响收益、调度数或邻接交换统计；对新增任务数 `3` 与 `2147483647` 的 A/B 也未发现差异，删除后 ID1 固定基线仍为 `Avg profit=2738.67`、`Best profit=2741.00`。保留基础候选位置数、窗口偏好、repair score 权重和邻接交换相关配置；6D 额外的插入候选位置实现和配置键已删除。
- 重分配校准策略保持当前实现：小规模任务（`allTasks < 4000`）刷新 best 后立即用热启动 HybCec 做完整 assignment 校准；大规模任务才允许跳过中间校准，并用 final calibration 兜底。即时校准使用 `evaluateAssignmentSnapshot()`，已有 `SatelliteState` 时注入 inherited solution，`commitState=true` 的校准预算按 `coord.fullRefineBudgetRatio=0.5` 缩减并受 `coord.fullRefineMinGenerations=20` 下限保护。2026-05-16 的 ID1/ID3/ID5 消融显示，关闭小规模即时校准会使均值分别下降 22.34、30.67、38.00；在即时校准关闭前提下再关闭 final calibration 会继续下降 5.00、15.67、33.67。`4000-40-0-0-6` 的大规模消融显示 `profitGain > bestTotalProfit * 0.005` 触发条件没有观测到行为影响，开关前后均为 `Avg profit=13974.33`、`Best profit=13995.00`，该 bigGain 条件已删除。半程 full calibration reachability 检查显示，第 13 轮触发在当前默认流程下不可达，因为三个 run 分别在 iter=6、7、9 因 `consecutiveZeroProfitGain >= 2` 提前退出；真实测试中途 full 修正需提前触发点或临时放宽该 large-task early stop。当前证据支持保留小规模即时校准和 final calibration，大规模中间校准只保留 interval/last 触发。
- 当前配置 10 场景固定基线已在 2026-05-16 重建：这里的基线是当前代码、`tuning.properties` 和固定 6D 对照配置 `{4,1,0,0,0,0}` 的参考性能，不是自动设计搜索结果。每个场景一次 `nRun=3`，显式加载 `tuning.properties`。统计基线按场景汇总 run 1/2/3；整体单次最好按同一 `run_index` 汇总 10 场景总利润后选择。本次 run1/run2/run3 总利润分别为 `116241.03`、`116161.03`、`116418.03`，整体单次最好为 `run_index=3`。每场景最大值单独记录，不作为整体单次最好。完整历史报告和原始产物保留在本地 legacy artifacts。
- 速度优化综合计划已在 2026-05-17 完成 5 个 phase。新增主线能力包括 `evaluateVector` 直评、primitive fitness mirror、best/rank cache、primitive survivor metadata、fast path batch size、SA/ALNS/SHADE/FastGaussian opt-in、初始化 KNN cache、satellite state pool、并行层级策略、协调器 adaptive ensemble / calibration racing、warmup runs、scene cache、lazy config reload 和 outer progressive racing。新增性能控件默认关闭、unset 或等价旧行为。`RAND-1` 与 `DE-1` 已跳过，`OM-3` surrogate prefilter 延后。旧 speedup 报告保留在本地 legacy artifacts。
- `OM-3` surrogate prefilter 是外层 `MainMFEAMOPHOA` 搜索策略扩展，不影响固定配置入口 `RunSingleHybridConfig`。预期机制是用已评估的 6D 配置训练轻量质量预测器，优先完整评估预测较好的配置，并保留随机或不确定候选探索 quota。该项可能改变自动设计搜索轨迹，后续应作为独立 PR、默认关闭，并以真实 `EvaluationHyb` 复测结果作为最终证据。
- L-SHADE 缩群后 GA workspace 复用的 `popFit` size mismatch 已在 2026-05-17 修复。`GAWorkspace.fitnessBuffer` 现在按当前 `nPop` 精确重建，避免从较大 population 缩到较小 population 后把旧长度 fitness array 传入 `GeneticAlgorithmNoSelect.runInto(...)`。
- Speedup 后 ID1 11 个 OA1-only 单父算法 runtime 表已在 2026-05-17 重测：入口 `RunSingleParentConfig`，配置 `{algorithm,0,0}`，`nRun=3,nPop=270,maxFes=27000`，显式加载 `tuning.properties`。当前最快是 `DE_BEST_1`（wall `89.71s`），`DE_RAND_1` wall `95.92s` 且 AvgProfit 最高（`2739.00`），`L_SHADE` AvgProfit `2738.33`，`ALNS` 最慢（wall `423.81s`）。历史报告和原始产物保留在本地 legacy artifacts。
- ID1 单父 `{updatePolicy,survivor}` 参数格搜索已在 2026-05-18 汇总：入口 `RunSingleParentConfig`，10 个单父算法、7 个 update policy、4 个 survivor policy，共 280 个计划配置；有效配置 273 个，ACO 尾部 7 个配置截断。全局最好按 AvgProfit 为 `L_SHADE {9,3,0}` 与 `DE_RAND_1 {4,0,0}` 并列 `2740.33`，`L_SHADE {9,3,0}` 的 BestProfit 为 `2742.00`。历史报告和机器可读汇总保留在本地 legacy artifacts。
- ABC ID1 基准预算收敛曲线已在 2026-05-19 补测：入口 `RunSingleParentConfig` 新增 `--convergence-file`，配置 `{7,0,0}`，`nRun=3,nPop=270,maxFes=27000`，显式加载 `tuning.properties`。结果为 `AvgProfit=2690.33`、`BestProfit=2707.00`。该记录只作为历史调参预算证据；当前 ABC 内部默认见下方固定值。历史报告、原始曲线和汇总保留在本地 legacy artifacts。
- ACO `{3,3,0}` 内部超参数已固定为 `aco.nSample=0.80,aco.intenseFactor=0.35,aco.deviateDistanceRatio=0.5,aco.minSigmaRatio=0.001`。
- ABC `{7,1,1}` 内部超参数已固定为 `abc.numNoImp=100,abc.phiScale=2.0,abc.phiOffset=1.0`。ABC 短预算、完整预算和跨场景对照的详细参数表只作为本地 legacy artifacts 保留。
- GA 内部超参数已固定为 `ga.probCrossover=0.9,ga.probMutation=0.15,ga.kTournament=2,ga.sigmaScale=0.2,ga.nElite=1,ga.maxMutationDimRatio=0.1,ga.adaptiveMutation=false`。

- EDA `{2,2,2}` 内部超参数已固定为 `eda.kElite=0.12,eda.sigmaScale=1.00,eda.minSigmaRatio=0.002,eda.stagnationGenerations=0,eda.stagnationBoostRatio=1.0`。
- SA `{8,1,1}` 内部超参数已固定为 `freezeRate=0.99,temperature=0.5,temperatureSchedule=LOGARITHMIC,temperatureLogOffset=3.0,sa.adaptiveSigma=false,hybcec.sa.genSAFast=5`。

## core 引擎文件

- `src\main\java\core\FitnessEvaluator.java`
- `src\main\java\core\HybCec.java`
- `src\main\java\core\calculator\HybridLevelCalculator.java`
- `src\main\java\core\config\AlgorithmIndex.java`
- `src\main\java\core\config\ConfigValidatable.java`
- `src\main\java\core\config\HybCecConfig.java`
- `src\main\java\core\config\HybCecConfigManager.java`
- `src\main\java\core\exception\HybCecExecutionException.java`
- `src\main\java\core\manager\CreditManager.java`
- `src\main\java\core\manager\FitnessManager.java`
- `src\main\java\core\manager\PopulationManager.java`
- `src\main\java\core\manager\PopulationResizer.java`
- `src\main\java\core\state\HybCecState.java`
- `src\main\java\core\state\StateKey.java`
- `src\main\java\core\state\StateUpdater.java`

## 结果与报告文件

新 MFEA 实验结果应从 fresh root 之后重新写入 `vault\Results\Reports\`。旧单算法调参报告和原始日志保留在本地 legacy artifacts，不进入新 Git 历史。
