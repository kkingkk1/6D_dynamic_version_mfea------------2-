---
status: completed
created: 2026-07-24
updated: 2026-07-24
experiment_id: paired-configs-10scene-5perrun-20260724
---

# 四配置全场景五轮配对实验报告

> 历史口径：本文中的 Parent 两组结果由已退役的 3D OA1-only 入口产生。当前 1D `RunSingleParentConfig` 改走 `SingleAlgorithmOptimizer`，只能继续使用本文 Hybrid 对比结论；Parent 数值不可直接复用。

## 结论

200 次正式运行全部完成并通过完整性审计。自动设计 Hybrid 配置 `{2,9,0,0,0,2}` 在 10 个场景中相对固定 Hybrid 配置 `{4,1,0,0,0,0}` 获得 6 胜、4 平、0 负，场景宏平均收益率提高 `0.4458` 个百分点。在 6 个非平局场景上，平均提高 `0.7430` 个百分点。

四个配置中，`hybrid-290002` 的场景宏平均收益率最高，为 `77.0184%`。其单次平均耗时为 `22.36 s`，低于 `hybrid-410000` 的 `24.81 s`。

## 实验合同

- 场景：ID1-ID10，共 10 个正式场景。
- `perRun`：`0..4`。
- 实际 seed：`42..46`。
- Hybrid：`410000 = {4,1,0,0,0,0}`；`290002 = {2,9,0,0,0,2}`。
- Parent：`400 = {4,0,0}`；`100 = {1,0,0}`。
- 配对规则：同一 `(sceneId, perRun)` 的四配置使用完全相同的实际 seed。
- 运行模式：`autohyb.deterministic=true`。
- 资源：`Normal` 优先级，28 个逻辑处理器，不限速。
- Git HEAD：`fb60a14cd411a47882ebfd2c5f76d28a1c9560ea`。

## 完整性验收

- `run-details.csv`：200 行、200 个唯一 `runKey`。
- 每个场景：20 行，共 10 个场景。
- 配对组：50 组；每组恰好 4 个目标配置。
- `perRun` 集合：`0,1,2,3,4`。
- seed 集合：`42,43,44,45,46`。
- 日志实际 seed 与期望 seed：200/200 一致。
- 缺失、额外、重复、字段错配、artifact 缺失：均为 0。
- runner 与本实验 Java 进程：完成后均已退出。

## Hybrid 结果

数值为五个配对 seed 的平均收益率。差值为 `290002 - 410000`，单位为百分点。

| 场景 | `410000` | `290002` | 差值 |
|---|---:|---:|---:|
| ID1 | 99.482 | 99.556 | +0.074 |
| ID2 | 99.890 | 99.890 | 0.000 |
| ID3 | 47.508 | 47.924 | +0.416 |
| ID4 | 92.590 | 92.590 | 0.000 |
| ID5 | 78.396 | 79.046 | +0.650 |
| ID6 | 98.440 | 98.440 | 0.000 |
| ID7 | 64.036 | 66.974 | +2.938 |
| ID8 | 100.000 | 100.000 | 0.000 |
| ID9 | 51.298 | 51.452 | +0.154 |
| ID10 | 34.086 | 34.312 | +0.226 |

`290002` 的主要增益来自 ID7；ID1、ID3、ID5、ID9 和 ID10 也保持正增益。4 个平局场景都接近或达到当前收益上限，不能据此区分配置。

## Parent 结果

数值为五个配对 seed 的平均收益率。

| 场景 | `400` | `100` | `400 - 100` |
|---|---:|---:|---:|
| ID1 | 99.548 | 98.518 | +1.030 |
| ID2 | 99.890 | 99.890 | 0.000 |
| ID3 | 48.132 | 45.238 | +2.894 |
| ID4 | 92.590 | 92.590 | 0.000 |
| ID5 | 79.312 | 77.204 | +2.108 |
| ID6 | 98.440 | 98.440 | 0.000 |
| ID7 | 61.976 | 59.058 | +2.918 |
| ID8 | 100.000 | 100.000 | 0.000 |
| ID9 | 50.482 | 45.462 | +5.020 |
| ID10 | 33.448 | 30.162 | +3.286 |

`parent-400` 相对 `parent-100` 为 6 胜、4 平、0 负，场景宏平均收益率高 `1.7256` 个百分点。

## 汇总

| 配置 | 场景宏平均收益率 | 50 次总耗时 | 单次平均耗时 |
|---|---:|---:|---:|
| `hybrid-290002` | 77.0184 | 1118.14 s | 22.36 s |
| `hybrid-410000` | 76.5726 | 1240.33 s | 24.81 s |
| `parent-400` | 76.3818 | 982.27 s | 19.65 s |
| `parent-100` | 74.6562 | 981.98 s | 19.64 s |

宏平均按 10 个场景等权计算。总耗时为各配置 50 次运行的 `elapsedSeconds` 之和，不包含 runner 预检、故障诊断和 Maven 验证时间。

## 运行故障与恢复

首次 runner 的 multiline regex 未接受 CRLF 行尾，三条 `exitCode=0` 日志被误标为 `parse`。三条结果已从原日志校验 seed、收益率和耗时后恢复，没有重跑；runner 正则随后改为允许 `\r?$`。

运行到 `185/200` 时，OneDrive 冲突副本触发 VS Code JDT 增量编译，并用 unresolved-compilation 错误桩覆盖 `target/classes`。该事件产生 3 条 `exit-1` 历史 attempt。恢复时保留并隔离冲突源码，建立非 OneDrive detached worktree，逐项验证三份 main 源码、`pom.xml`、`tuning.properties`、runner hash 和合同 Git HEAD 后，从缺失项继续。3 个失败 runKey 均在隔离运行时成功补齐。

`run-status.csv` 保留 3 条 `parse` 和 3 条 `exit-1` 历史记录，便于审计。最终 200 个 `runKey` 都有且只有一条 canonical 结果。

## 构建与测试

- `mvn -q -DskipTests clean compile`：通过。
- 两项显式 seed 配对测试：通过。
- `mvn -q test`：112 项中 111 通过。
- 唯一失败：`RunSingleHybridConfigTest.defaultConfigUsesCurrentAutoDesignedVector` 期望默认 `{9,2,0,0,0,0}`，合同源码默认 `{4,1,0,0,0,0}`。正式 runner 显式传入四个目标配置，不读取该默认值。

## Artifact

- 原始目录：`outputs/paired-configs-10scene-5perrun-20260724/`
- 完整结果：`run-details.csv`
- 场景与配置汇总：`summary.csv`
- 期望矩阵：`expected-runs.csv`
- attempt 审计：`run-status.csv`
- 实验合同：`experiment-contract.json`
- 场景 manifest：`scene-manifest.csv`
- 原始 stdout/stderr：`logs/`
- 精确命令：`commands/`
- 冲突源码保留区：`quarantined-source-conflicts/`
- 隔离运行时：`C:\Users\a_wei\Documents\Codex\2026-07-24\autohyb-paired-runtime-019f8fe1`
