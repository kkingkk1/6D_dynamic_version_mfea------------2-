# 6D pure-semantic dynamic version 全局地图

> 最后更新：2026-06-16

## 项目概述

**AutoHyb 卫星调度优化系统的 6 维纯语义动态版本**，用于多卫星成像任务调度优化。

## 当前工作地图

- 当前搜索空间为 6D 纯语义编码：`{parent1,parent2,update1,update2,operationOrder,survivor}`。
- `de.*`、`hybcec.insertionMode`、父算法内部参数和 speedup 开关都是运行时配置，不进入 6D 基因。
- 默认固定基线为 `{4,1,0,0,0,0}`；单配置复现实验从 `main.RunSingleHybridConfig.main()` 进入。
- G2/G3 是 update policy，G4 是 operation-order policy，G5 是 survivor policy。
- `singleParentMode` 仅用于 OA1-only 单算法实验，不进入混合算法组件库语义。
- 当前默认和 MFEA 主线阶段结论见 `vault/01-Plan.md`；历史单算法调参计划、报告和原始日志保留在本地但不进入 fresh MFEA Git 历史。
- 防回退边界和恢复条件见 `vault/Knowledge/Removed-Mechanisms.md`。

本文件只维护 agent 工作所需的项目语义、入口、数据流、模块依赖和回环规则。不要把实验流水账、参数表格或统计细节写进本文件。

## 文档职责

- `AGENTS.md` 是本目录的唯一权威全局地图，维护项目语义、入口、数据流、模块依赖和回环检查规则。
- `CLAUDE.md` 只作为 Claude Code 入口文件，指向本文件并记录 Claude 专用差异。
- 不要在 `CLAUDE.md` 里复制全局地图。项目事实变化时更新本文件，再让 `CLAUDE.md` 保持轻量转发。

## 计划文档工作流

- `vault/01-Plan.md` 只放项目级目标、当前任务、关键决策和阶段结论；阶段结论压成 1-2 行，并链接到详细报告或原始产物。
- `vault/Results/Reports/` 放完整实验表格、参数统计、性能对比和结论解释。
- `vault/Plan/` 放新的 MFEA 测试方案、搜索方案、分支实验计划，以及计划模式、CCG、Claude 计划模式生成的 plan 文档。
- `outputs/` 放原始日志、CSV、stdout、JFR 和中间结果。
- `vault/00-Hub.md` 只在方向性里程碑、项目索引或顶层入口变化时同步。
- 消融完成后，把完整结果写入对应 report；如果结果改变项目主线，再把压缩结论同步到 `vault/01-Plan.md` 的“关键设计决策”或“阶段结论索引”。
- 已删除、废弃或防回退机制统一写入 `vault/Knowledge/Removed-Mechanisms.md`，包含删除对象、当前行为、证据入口和恢复条件；`vault/01-Plan.md` 只保留项目级影响和该文档链接，不展开删除细节。
- `vault/Plan/` 中任一计划完成、废弃、阻塞或转 deferred 时，必须在同一轮同步相关文档：
  1. 更新该 plan 文件的 `status`、结果和决策；
  2. 更新 `vault/01-Plan.md` 的 Plan 状态总表、当前任务勾选和必要的阶段结论入口；
  3. 若有实验结果，确认对应 `vault/Results/Reports/` 已有完整报告；
  4. 若改变稳定机制、默认参数、删除边界或恢复条件，同步 `vault/Knowledge/` 相关 canonical note；
  5. 只有方向性里程碑、顶层入口或项目索引变化时才同步 `vault/00-Hub.md`。
- 不要只在聊天里宣布 plan 完成；完成状态必须落到可检索文档里。

## 长跑续跑安全

- 长跑续跑遵循用户级“长跑任务续跑安全”规则；本项目重点检查 `java.exe`、候选参数、worktree 路径和 `.log` 文件。

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
│   ├── Results/       ← 完整实验报告和结果表
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
└── src/test/java/     ← 测试
```

## 模块依赖

```text
main → core → strategy → algorithm → operator → common → model/utils
```

- `main → core / utils / model / common / operator.assignment`
- `utils → model / operator.insertion / operator.assignment`
- `model` 为底层领域对象，不依赖上层模块
- 禁止循环依赖

## 核心数据流

```text
DataLoader → Initialize（任务-卫星分配）
  → 自动设计路径：MainMFEAMOPHOA（外层 MFEA，int[nPop][6]）
    → HybridInitial（优先读取 EliteConfigArchive 实例归档，缺失/损坏时回退到默认 4 组精英种子）
 → EvaluationHyb（只接收当前 6D 配置，默认 `GREEDY` 插入策略与 `de.fSchedule=SIGMOID,de.fMax=0.10,de.fMin=0.01,de.crossoverRate=0.3,de.boundaryPolicy=RANDOM_REINIT`；可通过 `-Dhybcec.insertionMode=...` 和 `de.*` 覆盖运行时插入 / DE 参数，`PlanUtils` 里可对选定任务开启窗口偏好路径；`ParallelPolicy` 在外层评估活跃时禁用 `PlanUtils` 的 common-pool 向量并行）
      → TaskAllocationCoordinator.scheduleWithReassignment()（刷新 best 后，小规模任务立即完整校准；大规模中间校准按 `CALIBRATION_INTERVAL` 与最后一轮触发；末尾 final calibration 保留）
        → reassignUnscheduledTasks()（由 ReassignmentOrchestrator 编排优先级迁移循环与任务束后处理；由 AssignmentDeltaEvaluator 处理试探移动和增量评估；由 ReassignmentMoveEvaluator 外观类转发替换、交换、任务束移动到对应子评估器；delta fast refine 的 limited insertion 默认对齐 8D，使用基础候选位置，以及 replacement/swap 原任务位置附近的锚点候选）
        → buildPopulationWithInheritance()（重分配阶段可注入跨卫星共享任务排序模板）
        → HybCec.run()（内层混合算法，double[nPop][D]；operationOrder 控制执行顺序；survivor 在全量更新和 partial-update fast path 中分别控制全局/局部生存选择；DE 运行时使用 `HybCecConfigManager` 生成 `DEConfig`，默认 sigmoid F 路径，可 opt-in 覆盖为 static / linear / explicit F 序列）
          → HybridLevelCalculator（G2/G3 update policy 掩码；`FULL` 做全体更新，其余 policy 做个体子集更新；`TOP_SUBSET` / `MIXED_SUBSET` 使用固定 `0.5` 子集比例，`RANDOM_DECAY` 使用递减随机子集，`hybcec.mixedTopRatio` 控制 `MIXED_SUBSET` 的高适应度个体子集占比，默认 0.8）
          → CreditManager（按滑动窗口记录 OA 收益 / evalCost，并由 G4=`ADAPTIVE_CREDIT` 路由读取概率）
          → runParentAlgorithm()
          → PlanUtils.decode() → evaluatePlan()
      → 收集未调度任务 → 停滞时重分配 → 返回历史最优
    → EliteConfigArchive.saveBestConfig()（按 dataDir + numTasks + numSatellites + populationFactor + maxFes + insertionMode 的实例签名回写最优 6D 配置）
  → 单配置复现实验路径：RunSingleHybridConfig（直接评估固定 6D 配置；命令行只接收 6D 配置，DE 参数从 `tuning.properties` 或 JVM `de.*` 属性读取）
    → EvaluationHyb → TaskAllocationCoordinator.scheduleWithReassignment()
    → 可选 EliteConfigArchive.saveCandidateConfig()（仅在显式开启 --record-elite-archive 时，将固定配置追加到同实例域热启动归档）
  → 单算法复现实验路径：RunSingleParentConfig（直接评估独立 3D 单算法配置 `{P0 algorithm, P1 updateRatio, P2 survivor}`；运行时固定 `operationOrder=sequential`，DE 参数从 `de.*` 读取，并通过 `singleParentMode=true` 强制仅启用 OA1；可选 `--convergence-file` 输出正式卫星调度阶段的 per-run / per-satellite HybCec best-fitness 曲线）
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

### 检查项 2：模块文档成员清单

被修改文件所在模块的 `AGENTS.md` 成员清单必须反映当前实际状态。

检查步骤：
1. 确定被修改文件所属模块
2. 读取该模块的 `AGENTS.md`
3. 检查成员清单表格：新增类→添加、删除类→移除、变更→更新
4. 检查接口说明：新增/删除/修改 public 方法 → 更新
5. 检查依赖关系：新增/删除模块间依赖 → 更新

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
2. 如果本次任务涉及文件新增/删除/移动：更新对应模块 `AGENTS.md` 的成员清单
3. 如果本次任务涉及模块间依赖变化：更新「模块依赖」
4. 执行上述「代码变更后强制回环检查」的全部 4 项
5. 回环检查只有在发现变化的时候才回复相应信息；像"无新增""未修改""无需同步""跳过"等无变化说明不要打印

## 规则：Maven 与实验脚本串行

- 不要在同一个 worktree 内并行运行 Maven 测试/编译与 Java 实验脚本。
- 两者共享 `target/classes`；并行执行可能导致 `NoClassDefFoundError` 或 stale classpath。
- 正确顺序是先跑 compile/test，再跑长实验脚本，最后重新跑 compile/test。
