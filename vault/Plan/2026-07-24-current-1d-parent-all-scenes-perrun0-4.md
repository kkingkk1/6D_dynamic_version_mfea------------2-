---
status: completed
created: 2026-07-24
updated: 2026-07-24
experiment_id: paired-current-1d-parent-10scene-5perrun-20260724
---

# 当前 1D Parent 与 Hybrid 全场景配对运行

## 目标

在 ID1-ID10 的正式场景中，对 `perRun=0..4` 执行四套当前入口配置。

- `RunSingleHybridConfig`: `410000={4,1,0,0,0,0}` 与 `290002={2,9,0,0,0,2}`。
- `RunSingleParentConfig`: `4` 与 `1`。
- 同一 `(sceneId, perRun)` 的四次运行必须使用完全相同的实际 seed。

## 设计与约束

- 使用 `scripts/run_paired_configs_10scene_5perrun.ps1 -IncludeParents`，该脚本的当前 Parent 配置为 `parent-4` 和 `parent-1`。
- 历史 `paired-configs-10scene-5perrun-20260724` 的 Parent 为已退役 3D OA1-only 入口，不能复用。
- Maven 编译、运行时产物复制和 Java 实验严格串行。
- 使用独立的非 OneDrive `RuntimeClassesDir`，避免 IDE 进程覆盖项目 `target/classes`。
- 输出使用新目录；日志、合同、seed 参考和预期矩阵均保留在其中。

## 步骤

- [x] 确认当前入口、四套配置、十场景清单和 seed 传递路径。
- [x] 串行编译当前源码并创建隔离运行时类目录。
- [x] 运行 `-ValidateOnly`，验收 200 个预期 run 和四配置配对合同。
- [x] 启动可恢复 runner，并记录 PID、优先级、输出路径和资源快照。
- [x] 监控至 `progress.json` 完成或停止；异常时按日志精确恢复。
- [x] 审计 200 个 runKey、配对 seed、日志 artifact 和汇总 CSV。
- [x] 回写本计划和正式实验报告。

## 验证与停止条件

- 预检必须报告 200 个预期运行和 `parent-4,parent-1`。
- 每个日志的实际 seed 必须等于该 `sceneId + perRun` 的期望 seed。
- 连续三次失败、合同 source hash 漂移或既有 runner 写入同一目录时停止并诊断，不启动冲突任务。

## 状态

全部 200 条正式运行已完成：10 个场景各 20 条，每个配置各 50 条，`runKey` 唯一且完整，失败 attempt、缺失、额外、重复和配对 seed 不一致均为 0。runner 和 Java 子进程均已退出。

场景宏平均收益率为 `hybrid-290002=77.0542%`、`hybrid-410000=76.5742%`、`parent-4=75.5166%`、`parent-1=74.4338%`。两项预先定义场景级比较均为 6 胜、4 平、0 负；原始 Wilcoxon `p=0.03125`，两项 Holm 校正后均为 `p=0.0625`。因此候选方向一致但未通过校正后显著性门槛。完整报告见 [[Results/Reports/2026-07-24--current-1d-parent--r01--paired-summary|当前 1D Parent 配对总结]]。

## 错误记录

- 初次 `-ValidateOnly`：当前副本缺少默认 `outputs/mfea-multiscene-full-20260616/mfea_multiscene_full.command.txt`。该文件只提供 Java 与 classpath，不包含本次结果。预防动作：bootstrap 文件位于本次输出目录，且合同将记录解析结果和隔离 class hash。
