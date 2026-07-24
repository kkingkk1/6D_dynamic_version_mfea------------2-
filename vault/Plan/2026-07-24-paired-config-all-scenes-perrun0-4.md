---
status: completed
created: 2026-07-24
updated: 2026-07-24
---

# 全场景配对配置五轮实验计划

> 历史口径：本文中的 Parent 配置来自已退役的 3D OA1-only 入口。当前 `RunSingleParentConfig` 只接收 1D `algorithmIndex`，本文 Parent 结果不得作为新入口基线。

## 目标

在相同场景和完全一致的随机数种子下，对每个 `perRun = 0..4` 运行以下四种配置：

- `RunSingleHybridConfig`：`{4,1,0,0,0,0}`、`{2,9,0,0,0,2}`
- `RunSingleParentConfig`：`{4,0,0}`、`{1,0,0}`

覆盖项目定义的全部正式场景，保留可恢复日志，并验证所有预期运行均完成。

## Design Brief

目标：复用已有批量实验脚本完成四配置、全场景、五个配对 seed 的正式运行。

已知事实：

- 用户要求先核查 `scripts/` 是否已有可复用脚本。
- `perRun` 必须从 `+0` 到 `+4`，共五轮。
- 四种配置在同一场景、同一 `perRun` 下必须获得完全相同的随机数种子。
- Maven 编译或测试不能与 Java 实验脚本并行运行。

假设：

- “所有场景”以现有 canonical 批量脚本或场景 manifest 为准；启动前枚举并固化实际清单。
- 优先复用脚本已有断点续跑和完整性检查；若现有脚本不满足 seed 配对条件，只做最小修补。

待核查：

- 脚本是否已包含四个目标配置、全部场景和 `perRun 0..4`。
- 两个 Java 入口如何把 base seed 与 `perRun` 转换为实际 seed。
- 是否存在同一任务的在途进程、可复用结果或未完成输出。

约束：

- 用户已明确要求全速测试。Java 与 runner 使用 `Normal` 优先级，允许使用全部 28 个逻辑处理器，并记录优先级、处理器数和 CPU 快照。
- 运行前记录工作目录、Git 状态、HEAD、场景清单、参数、输出目录和进程命令行。
- 不并行启动写入同一输出目录的第二个 runner。

验证：

- 静态检查脚本参数与 Java seed 计算路径。
- 启动前串行运行最小编译或脚本预检。
- 运行后按 `(entrypoint, config, scene, perRun, effectiveSeed)` 建立期望矩阵并逐项核对日志或结果文件。

## 步骤

- [x] 枚举 `scripts/`，定位可复用 runner、场景清单和结果校验器。
- [x] 审计两个入口及调用链的 seed 计算，证明四配置 seed 完全配对。
- [x] 核查现有 Java/runner 进程、输出目录和可复用结果，避免重复写入。
- [x] 最小修改 seed 路径和脚本，并执行脚本级预检与串行 Maven 验证。
- [x] 以 `Normal` 启动可恢复全速长跑，记录 PID、命令行、日志、CPU 快照和输出路径。
- [x] 监控运行并处理可恢复失败，不启动冲突 runner。
- [x] 对全部场景、四配置和五个 `perRun` 做完整性与 seed 配对验收。
- [x] 回写本计划状态、结果入口和必要的项目级阶段结论。

## 风险与停止条件

- seed 公式不一致：停止启动，先修正或选择可保证配对的调用方式。
- 已有相同 runner 正在写同一输出：不重复启动，转为监控或恢复。
- 场景清单、预算或运行参数存在多个 canonical 来源：以入口代码、现有正式 runner 和 `vault/01-Plan.md` 交叉核查；冲突会改变实验含义时暂停说明。
- 用户已要求全速测试：保持 `Normal` 并允许全部处理器；CPU 高占用属于预期，不把限速结果当作本次性能数据。

## 计划自审

- 清晰度：9/10
- 完整性：9/10
- 可行性：8/10
- 风险评估：9/10
- 需求匹配：10/10
- 加权总分：8.9/10，通过。

## 状态

已确认 `run_best_config_10scene_5seed.ps1` 与 `start_best_config_10scene_5seed.ps1` 可复用场景矩阵、CSV、日志和后台启动结构；其 ID1-ID10 与当前 10 个场景目录一致。旧 runner 仅支持一个 Hybrid 配置，不能直接满足四配置配对实验。

正在审计统一 seed 路径。当前代码证据显示 Hybrid 和 Parent 都把配置值纳入 `stableSeed`，相同 `perRun` 偏移不能单独证明四配置获得相同实际 seed。

已新增 opt-in `evaluation.runSeedBase`。runner 固定 base 为 `42`，因此 `perRun 0..4` 的实际 seed 为 `42..46`；Hybrid 通过 `[RunSeed]`、Parent 通过 `[Run]` 日志逐项校验实际 seed。

已新增 `run_paired_configs_10scene_5perrun.ps1` 与后台 starter。`-ValidateOnly` 预检得到 200 行、10 场景、50 个配对组、0 个错误配对组；每组只含四个目标配置且 seed 唯一一致。正式输出目录为 `outputs/paired-configs-10scene-5perrun-20260724`。

串行验证结果：新增两个 seed 配对测试通过，`mvn -q -DskipTests compile` 通过；四配置 ID1 低预算 smoke 在 `perRun=4` 均输出实际 seed `46` 并正常退出。正式运行保持 `Normal` 优先级，使用全部 28 个逻辑处理器。

首个 runner 因 CRLF 行尾解析缺陷把三条 `exitCode=0` 的成功日志误标为 `parse`，保护规则在连续三条后停止，未误写成功结果。正则已改为允许 `\r?$`，合同改为 JSON 语义比较；三条结果已从原日志校验 seed、ratio 和 elapsed 后恢复，未重跑。

运行到 `185/200` 时，OneDrive 冲突副本触发 VS Code JDT 增量编译，并用 unresolved-compilation 错误桩覆盖 `target/classes`。冲突源码已保留到 `outputs/paired-configs-10scene-5perrun-20260724/quarantined-source-conflicts/`。后续在非 OneDrive detached worktree 中按实验合同逐项复原 source hash、runner hash 和 Git HEAD，只补跑 15 个缺失项。

最终状态：200/200 完成；200 个唯一 `runKey`；10 个场景各 20 行；50 个四配置配对组；实际 seed 全部匹配 `42..46`；缺失、重复、字段错配和 artifact 缺失均为 0。完整报告见 [[Results/Reports/2026-07-24-paired-config-all-scenes-perrun0-4|四配置全场景五轮配对实验报告]]。

结果显示 `hybrid-290002` 相对 `hybrid-410000` 为 6 胜、4 平、0 负，场景宏平均收益率提高 `0.4458` 个百分点；`parent-400` 相对 `parent-100` 为 6 胜、4 平、0 负，宏平均提高 `1.7256` 个百分点。

## 错误记录

- `mvn -q "-Dtest=main.RunSingleHybridConfigTest,main.RunSingleParentConfigTest" test`：24 项中 1 项既有默认配置断言失败。测试期望 `{9,2,0,0,0,0}`，源码实际为 `{4,1,0,0,0,0}`；与本轮统一 seed 改动无关。预防动作：本轮不依赖入口默认配置，runner 显式传入四个目标配置；另行运行新增 seed 配对测试并在最终全量验证中如实保留该漂移证据。
- `mvn -q test`：112 项中同一既有默认配置断言失败，其余 111 项通过；未发现第二个失败。正式 runner 显式传入配置，不走该默认值。
- 首次正式 runner：Java 三项均 `exitCode=0`，但 PowerShell multiline regex 未允许 CRLF 的 `\r`，导致 `seed/ratio/elapsed` 匹配失败并触发三连失败停止。预防动作：所有行尾模式使用 `\r?$`；以既有三份日志做回归解析，均得到 1 个 seed、1 个 ratio、1 个 elapsed；合同改为 JSON 语义比较，避免换行格式造成假冲突。
- 运行到 `185/200` 后，`RunSingle*Config-DESKTOP-UKPM2VE.java` 与 `EvaluationHyb-DESKTOP-UKPM2VE.java` 被 JDT 视为源码，错误桩覆盖正式 class。预防动作：长跑使用非 OneDrive detached worktree 和独立 `target/classes`；启动前核对合同 source hash、Git HEAD 与 scene manifest；原输出目录通过 junction 原地续写。
