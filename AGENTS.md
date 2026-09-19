# 6D pure-semantic dynamic version 全局地图

> 最后更新：2026-09-19

## 项目概述

**AutoHyb 卫星调度优化系统的 6 维纯语义动态版本**，用于多卫星成像任务调度优化。

## 当前工作地图

- 当前搜索空间为 6D 纯语义编码：`{parent1,parent2,update1,update2,operationOrder,survivor}`。
- `de.*`、`hybcec.insertionMode`、父算法内部参数和 speedup 开关都是运行时配置，不进入 6D 基因。
- 默认固定基线为 `{2,9,0,0,0,2}`；单配置复现实验从 `main.RunSingleHybridConfig.main()` 进入，默认开启 `autohyb.deterministic=true` 复现实验模式。
- G2/G3 是 update policy，G4 是 operation-order policy，G5 是 survivor policy。
- 单算法入口使用独立 1D `algorithmIndex`，由动态重分配层直接调用 `SingleAlgorithmOptimizer`；不复用 6D 混合基因或 HybCec OA1-only 模式。
- 当前默认和 MFEA 主线阶段结论见 `vault/01-Plan.md`；历史单算法调参计划、报告和原始日志保留在本地但不进入 fresh MFEA Git 历史。
- 防回退边界和恢复条件见 `vault/Knowledge/Removed-Mechanisms.md`。

本文件只维护 agent 工作所需的项目语义、入口、数据流、模块依赖和回环规则。不要把实验流水账、参数表格或统计细节写进本文件。

## 文档职责

- `AGENTS.md` 是本目录的唯一权威全局地图，维护项目语义、入口、数据流、模块依赖和回环检查规则。
- `CLAUDE.md` 只作为 Claude Code 入口文件，指向本文件并记录 Claude 专用差异。
- 不要在 `CLAUDE.md` 里复制全局地图。项目事实变化时更新本文件，再让 `CLAUDE.md` 保持轻量转发。

## AGENTS.md 分层粒度

- 默认只保留根目录 `AGENTS.md` 和主模块级 `AGENTS.md`。当前 Java 主模块为 `main/core/strategy/algorithm/operator/common/model/utils`。
- 不要给每个普通子目录都创建 `AGENTS.md`。只有子目录有长期稳定的独立职责、重复协作入口或特殊禁忌时，才新增局部 `AGENTS.md`。
- 模块级 `AGENTS.md` 只记录模块职责、关键类、public 入口、跨模块依赖和重要禁忌。
- 不把实验流水账、JFR 长记录、一次性性能对比、长参数表或临时计划写进模块级 `AGENTS.md`。
- 历史证据、可复核实验材料和详细结果放入 `vault/Knowledge/` 或 `vault/Results/Evidence/`；模块级 `AGENTS.md` 只保留一条短结论和链接。

## 计划文档工作流

- 不生成 `vault/Daily/` 或按日期堆积的工作日志。实验现场放在 `outputs/<experiment-id>/`；可复核结论放入 `vault/Results/Evidence/` 和 `vault/Results/Reports/`；项目级决策更新到 `vault/01-Plan.md`，机制与删除边界更新到 `vault/Knowledge/`。
- `vault/01-Plan.md` 只放项目级目标、当前任务、关键决策和阶段结论；阶段结论压成 1-2 行，并链接到人读报告或证据包。
- `vault/Results/Evidence/<experiment-id>/` 是 agent、审计和复分析入口。默认只建 `evidence.md`、`data.csv` 和 `manifest.json`；有图才建 `figures/`。`evidence.md` 记录问题、方法、完整结论、统计边界和文件说明；`data.csv` 是本次分析实际使用的 canonical 结果表；`manifest.json` 记录 Git HEAD、参数、seed、命令、来源路径和 SHA256。
- 不预建 `source/`、`derived/`、`stats-appendix.md` 或图表目录。只有数据确有多表、或论文/审稿需要完整统计附录时，才增加对应文件。
- `vault/Results/Reports/` 是给人读的简练报告。只写研究问题、3-5 条发现、限制、决策和下一步，并链接同名 `Evidence` 包；不重复长统计合同、逐次运行审计、命令和 artifact 清单。
- `vault/Plan/` 放新的 MFEA 测试方案、搜索方案、分支实验计划，以及计划模式、CCG、Claude 计划模式生成的 plan 文档。
- `outputs/<experiment-id>/` 是本地运行现场，保存日志、命令、stdout/stderr、JFR、PID、进度和恢复文件，继续忽略提交。分析所需的 canonical 结果表默认复制为 `Evidence/data.csv`；表过大时不复制，在 `manifest.json` 记录其 `outputs/` 路径和 SHA256。
- `vault/00-Hub.md` 只在方向性里程碑、项目索引或顶层入口变化时同步。
- 消融完成后，按 `outputs → Evidence → Reports → vault/01-Plan.md` 生成和链接产物。若结果改变项目主线，再把压缩结论同步到 `vault/01-Plan.md` 的“关键设计决策”或“阶段结论索引”。
- 已删除、废弃或防回退机制统一写入 `vault/Knowledge/Removed-Mechanisms.md`，包含删除对象、当前行为、证据入口和恢复条件；`vault/01-Plan.md` 只保留项目级影响和该文档链接，不展开删除细节。
- `vault/Plan/` 中任一计划完成、废弃、阻塞或转 deferred 时，必须在同一轮同步相关文档：
  1. 更新该 plan 文件的 `status`、结果和决策；
  2. 更新 `vault/01-Plan.md` 的 Plan 状态总表、当前任务勾选和必要的阶段结论入口；
  3. 若有实验结果，确认对应 `vault/Results/Evidence/` 已有轻量证据包，并在 `vault/Results/Reports/` 有链接该证据包的人读报告；
  4. 若改变稳定机制、默认参数、删除边界或恢复条件，同步 `vault/Knowledge/` 相关 canonical note；
  5. 只有方向性里程碑、顶层入口或项目索引变化时才同步 `vault/00-Hub.md`。
- 不要只在聊天里宣布 plan 完成；完成状态必须落到可检索文档里。

## 论文写作回环

- 修改 `vault/Writing/` 下论文草稿、实验段落、图表说明或学术回复后，默认调用 `writing-anti-ai` skill 对本轮新增或重写段落做轻量去 AI 味处理。
- 平时只处理本轮改动段落，不重写全稿，避免制造无关 diff 和语义漂移。
- 一节或一章内容稳定后，再对该节或该章做一次统一的段落连贯性去 AI 味检查。
- 去 AI 味不得改变实验事实、数值、引用、算法名、变量名、表号、图号和证据边界。
- 公式密集、表格密集、纯参数说明段只做最小措辞调整，优先保持可核查性。

## 论文 PDF 构建产物

- 从项目中的 PDF 导出批注时，默认生成独立 UTF-8 Markdown 文件，命名为 `<PDF basename>_annotations.md`，并放在源 PDF 同目录；`outputs/` 只用于提取过程中的临时文件或验证产物，除非用户明确指定其他位置。
- 从 `vault/Writing/*.md` 构建论文 PDF 时，最终 PDF 仅保存在对应 Markdown 同目录，命名为 `<basename>.pdf`。
- `.tex`、`.aux`、`.bbl`、`.blg`、`.log`、`.out`、`.toc`、`.synctex.gz`、转换文件、页面渲染图、字体与检查报告等中间产物必须放在独立的 `outputs/<build-id>/`，不得写入 `vault/Writing/`。
- 先在 `outputs/<build-id>/` 的隔离工作区完成编译、日志和视觉检查；通过后才复制最终 PDF 到 `vault/Writing/`。

## 长跑续跑安全

- 长跑续跑遵循用户级“长跑任务续跑安全”规则；本项目重点检查 `java.exe`、候选参数、worktree 路径和 `.log` 文件。
- 多 seed 或跨配置配对长跑启动前，必须先完成 seed preflight：Hybrid 用一个场景核对首轮和末轮的实际 `[RunSeed] source/table/scene/perRun/seedId/seed`、场景 basename 到固定表行的映射以及 `perRunStart+nRun<=20`，并确认同轮各配置使用相同 seed；Parent 入口另行核对 `evaluation.runIndexBase/runSeedBase` 合同。至少将一次手动启动结果与批处理命令记录对照；任一 seed 不一致时禁止启动完整批次。

三层架构：
- **外层全局 MFEA 自动设计层**：搜索 6 维混合算法配置染色体，自动设计父算法组合、update policy、执行顺序和生存策略
- **内层 HybCec**：对单颗卫星的任务序列进行连续编码优化
- **动态重分配层 TaskAllocationCoordinator**：多卫星场景下跨卫星任务重分配与迭代再调度

## 根目录结构

```text
6D_dynamic_version_mfea/
├── pom.xml / tuning.properties
├── vault/
│   ├── Plan/          ← MFEA 搜索计划和测试方案
│   ├── Results/       ← Evidence（agent/审计）与 Reports（人读）
│   ├── Knowledge/     ← 架构、来源清单和防回退知识
│   └── Writing/       ← 论文草稿和写作材料
├── src/main/java/
│   ├── main/          ← 入口与全局协调层（详见本文件「关键入口」）
│   ├── core/          ← 混合优化核心引擎（详见 core/AGENTS.md）
│   ├── strategy/      ← 策略模式适配层（详见 strategy/AGENTS.md）
│   ├── algorithm/     ← 元启发式算法库（详见 algorithm/AGENTS.md）
│   ├── operator/      ← 算子层（详见 operator/AGENTS.md）
│   ├── common/        ← 共享基础设施（详见 common/AGENTS.md）
│   ├── model/         ← 领域模型（详见 model/AGENTS.md）
│   └── utils/         ← 工具层（详见 utils/AGENTS.md）
├── scripts/           ← 批量实验、结果解析和论文图表复现脚本
└── src/test/java/     ← 测试
```

## 模块依赖

```text
main → core / strategy / algorithm → operator → common → model/utils
```

- `main → core / strategy / algorithm / utils / model / common / operator.assignment`
- `utils → model / operator.insertion / operator.assignment`
- `model` 为底层领域对象，不依赖上层模块
- 禁止循环依赖

## 核心数据流

```text
ScenePathResolver（`autohyb.sceneRoot` → `AUTOHYB_SCENE_ROOT` → 当前/相邻 `Scene`）
  → DataLoader → Initialize（任务-卫星分配）
  → 自动设计路径：MainMFEAMOPHOA（外层 MFEA，int[nPop][6]）
    → HybridInitial（优先读取 EliteConfigArchive 实例归档，缺失/损坏时回退到默认 4 组精英种子）
 → EvaluationHyb（只接收当前 6D 配置，默认 `GREEDY` 插入策略与 `de.fSchedule=SIGMOID,de.fMax=0.10,de.fMin=0.01,de.crossoverRate=0.3,de.boundaryPolicy=RANDOM_REINIT`；可通过 `-Dhybcec.insertionMode=...` 和 `de.*` 覆盖运行时插入 / DE 参数；Hybrid seed 按 `sceneDir` basename 读取根目录 seed 表，默认 source `native290002` → `scene-seeds-native290002.properties`，可用 `-Devaluation.seedTable.source=native270342|native200042|native410000` 切换到对应内置表，也可用 `-Devaluation.seedTable.path=...` 指定完整表；`native200042` 的前五个表项固定映射原始 native290002 seed ID `13,17,21,24,25`；`perRun=0..19` 对应 seed ID `10..29`，与配置、预算及 `evaluation.runIndexBase/runSeedBase` 无关，`evaluation.perRunStart` 选择表索引；当前 MFEA 选定的四个 `-train` basename 已有显式 `native290002` 行；`RunSingleHybridConfig` 直跑默认开启 `evaluation.runSeedLog`，输出 source、表文件名、场景、`perRun`、seed ID 和实际 seed，可用 `-Devaluation.runSeedLog=false` 关闭；MFEA fitness 直接使用优化后调度收益，不再用 baseline 兜底；`PlanUtils` 里可对选定任务开启窗口偏好路径；`ParallelPolicy` 在外层评估活跃时禁用 `PlanUtils` 的 common-pool 向量并行）
      → TaskAllocationCoordinator.scheduleWithReassignment()（刷新 best 后，小规模任务立即完整校准；大规模中间校准按 `CALIBRATION_INTERVAL` 与最后一轮触发；末尾 final calibration 保留；`autohyb.deterministic=true` 时多卫星快照仍并行评估，但读取固定 `SatelliteState` 快照并按 satellite id 固定顺序提交结果）
        → reassignUnscheduledTasks()（由 ReassignmentOrchestrator 编排优先级迁移循环与任务束后处理；由 AssignmentDeltaEvaluator 处理试探移动和增量评估；由 ReassignmentMoveEvaluator 外观类转发替换、交换、任务束移动到对应子评估器；delta fast refine 的 limited insertion 默认对齐 8D，使用基础候选位置，以及 replacement/swap 原任务位置附近的锚点候选）
        → buildPopulationWithInheritance()（重分配阶段可注入跨卫星共享任务排序模板）
        → HybCec.run()（内层混合算法，double[nPop][D]；operationOrder 控制执行顺序；survivor 在全量更新和 partial-update fast path 中分别控制全局/局部生存选择；DE 运行时使用 `HybCecConfigManager` 生成 `DEConfig`，默认 sigmoid F 路径，可 opt-in 覆盖为 static / linear / explicit F 序列）
          → HybridLevelCalculator（G2/G3 update policy 掩码；`FULL` 做全体更新，其余 policy 做个体子集更新；`TOP_SUBSET` / `MIXED_SUBSET` 使用固定 `0.5` 子集比例，`RANDOM_DECAY` 使用递减随机子集，`hybcec.mixedTopRatio` 控制 `MIXED_SUBSET` 的高适应度个体子集占比，默认 0.8；随机子集使用当前 HybCec run-owned `Random`）
          → CreditManager（按滑动窗口记录 OA 收益 / evalCost，并由 G4=`ADAPTIVE_CREDIT` 路由读取概率）
          → runParentAlgorithm()
          → PlanUtils.decode() → evaluatePlan()
      → 收集未调度任务 → 停滞时重分配 → 返回历史最优
    → EliteConfigArchive.saveBestConfig()（按 dataDir + numTasks + numSatellites + populationFactor + maxFes + insertionMode 的实例签名回写最优 6D 配置）
  → 单配置复现实验路径：RunSingleHybridConfig（直接评估固定 6D 配置；命令行只接收 6D 配置，DE 参数从 `tuning.properties` 或 JVM `de.*` 属性读取；默认 `autohyb.deterministic=true`，可设为 `false` 恢复并行快跑；Hybrid seed 默认使用 `native290002`，直跑可编辑 `MANUAL_SEED_TABLE_SOURCE` 切换，显式 `-Devaluation.seedTable.source=native270342|native200042|native410000` 优先；批量配对实验通过同一场景的 `evaluation.perRunStart` 让不同配置共享完全相同的 fixed-table seed）
    → EvaluationHyb → TaskAllocationCoordinator.scheduleWithReassignment()
    → 可选 EliteConfigArchive.saveCandidateConfig()（仅在显式开启 --record-elite-archive 时，将固定配置追加到同实例域热启动归档）
  → 单算法复现实验路径：RunSingleParentConfig（只接收 1D `{algorithmIndex}`；DE 参数从 `de.*` 读取；动态重分配层直接调用 `SingleAlgorithmOptimizer.optimize()`，每轮由单个 parent strategy 生成候选并做逐候选 greedy replacement；保留独立的 `evaluation.runIndexBase/runSeedBase` seed 合约；可选 `--convergence-file` 输出正式卫星调度阶段的 per-run / per-satellite 单算法 best-fitness 曲线）
```

## 关键入口

| 场景 | 入口 |
|------|------|
| 自动设计主入口（完整 6D 动态全局优化） | `main.MainMFEAMOPHOA.main()` |
| 单配置复现实验入口 | `main.RunSingleHybridConfig.main()` |
| 单算法复现实验入口 | `main.RunSingleParentConfig.main()` |
| 评估单个 6D 配置 | `main.EvaluationHyb.evaluationHyb()` |
| 多卫星协调调度 | `main.TaskAllocationCoordinator.scheduleWithReassignment()` |
| 单卫星 HybCec | `core.HybCec.run()` |

## 文档索引

| 模块 | 文档路径 |
|------|----------|
| main | `src/main/java/main/AGENTS.md` |
| algorithm | `src/main/java/algorithm/AGENTS.md` |
| common | `src/main/java/common/AGENTS.md` |
| core | `src/main/java/core/AGENTS.md` |
| model | `src/main/java/model/AGENTS.md` |
| operator | `src/main/java/operator/AGENTS.md` |
| strategy | `src/main/java/strategy/AGENTS.md` |
| utils | `src/main/java/utils/AGENTS.md` |

---

## 规则：代码变更后强制回环检查

每次代码变更完成后，必须执行以下回环检查清单。任何一项不通过则必须立即修复后再标记任务完成。

### 检查项 1：文件头依赖声明

每个 Java 文件头部的 `依赖` 注释块必须与实际 import 保持一致。

检查步骤：
1. 读取被修改文件的 `import` 语句列表
2. 对比文件头 `依赖:` 注释块中列出的依赖项
3. 如有新增 import → 在依赖注释中补充对应条目
4. 如有删除 import → 从依赖注释中移除对应条目
5. 如文件无依赖注释块 → 跳过（不强制添加）

### 检查项 2：模块文档地图

被修改文件所在模块的 `AGENTS.md` 必须反映会影响后续 agent 判断的模块地图变化。

检查步骤：
1. 确定被修改文件所属模块
2. 读取该模块的 `AGENTS.md`
3. 新增/删除/重命名关键入口类、public 类、跨模块协作类或改变模块职责的 helper → 更新成员清单
4. 新增/删除/修改 public 方法、运行时开关或模块外可见合约 → 更新接口说明
5. 新增/删除模块间依赖、数据流或调用方向 → 更新依赖关系
6. 纯实现细节、私有 helper 内部重构、局部性能试验不强制写入模块 `AGENTS.md`

### 检查项 3：全局地图一致性

如果变更涉及以下情况，必须同步更新本文件：
- 新增/删除/重命名模块或子包
- 模块间依赖关系变化
- 数据流变化

### 检查项 4：跨模块影响

如果修改了某个类的 public 接口（方法签名、返回类型、参数），必须：
1. 搜索所有调用方，确认调用方代码仍然兼容
2. 如有不兼容 → 同步修改调用方
3. 调用方所在模块的 `AGENTS.md` 也需要回环检查

---

## 规则：任务结束自动更新全局地图

每个编码任务结束时，必须执行以下更新流程：

1. 更新本文件顶部的「最后更新」日期
2. 如果本次任务涉及文件新增/删除/移动且影响模块地图：更新对应模块 `AGENTS.md` 的成员清单
3. 如果本次任务涉及模块间依赖变化：更新「模块依赖」
4. 执行上述「代码变更后强制回环检查」的全部 4 项
5. 回环检查只有在发现变化的时候才回复相应信息；像"无新增""未修改""无需同步""跳过"等无变化说明不要打印

## 规则：Maven 与实验脚本串行

- 不要在同一个 worktree 内并行运行 Maven 测试/编译与 Java 实验脚本。
- 两者共享 `target/classes`；并行执行可能导致 `NoClassDefFoundError` 或 stale classpath。
- 正确顺序是先跑 compile/test，再跑长实验脚本，最后重新跑 compile/test。

## Java 本机运行资源

- Codex 在本机启动或管理 Java 程序时，默认将目标 Java 进程优先级设为 `BelowNormal`，优先保证 Windows、Codex 和其他交互应用流畅。
- 修改优先级前确认目标进程、主类和当前任务，避免修改无关 Java 进程。
- 对 CPU 密集型并行 Java 任务，如果设置 `BelowNormal` 后仍造成卡顿，或整机 CPU 长时间超过 90%，再限制任务并发，至少保留 4–6 个逻辑处理器。
- 用户明确要求测试算法速度、基准测试或满速运行时，使用 `Normal` 优先级并允许使用全部可用处理器。
- 测试算法速度时记录线程数、优先级、CPU 占用和关键运行参数，避免把限速结果当作满速性能。
