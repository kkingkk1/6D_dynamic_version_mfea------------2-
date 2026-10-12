---
type: experiment-evidence
experiment_id: mfea-native200042-final-all10-20260831
status: complete
primary_metric: profitRatio
primary_unit: scene-level five-run mean
---

# native200042 全场景复现 Evidence

## 研究问题

采用统一的 `native200042` 固定 seed 表后，保留配置 `[2,0,0,0,4,2]` 能否在 ID1--ID10 上完成五次 full-budget replay，并得到可复核的场景均值？

## 实验协议

- 入口：`main.RunSingleHybridConfig`。
- 配置：`[2,0,0,0,4,2]`。
- 模式：`autohyb.deterministic=true`，Java 进程优先级为 `Normal`。
- seed：`native200042`，`perRun=0..4`，逻辑 seed ID 为 `10..14`。
- seed 映射：`native200042` 的五个 seed 槽对应 `native290002` 的 source seed ID `13,17,21,24,25`；该映射由 seed 表逐场景核对。
- ID2--ID10 的 45 次运行来自 2026-08-18 批次；ID1 的 5 次运行于 2026-08-31 补齐。两批使用相同配置、seed 表和 full-budget 入口。

## 完整性与结论

- ID1--ID10 共 50 个计划运行，完成 `50/50`。
- ID1 的均值为 `99.6002%`，标准差为 `0.0257` 个百分点。
- 十场景宏平均为 `77.0369%`；regional 子集均值为 `63.2402%`，global 子集均值为 `97.7320%`。
- 逐场景统计、区间和耗时见 `stats-appendix.md`。
- 该证据只确认选定配置在统一 seed 口径下完成复现。由于没有同批基线，不支持显著性、效应量或自动设计因果效果结论。

## 来源与文件

- [data.csv](data.csv)：50 条按场景和 seed 规范化的结果记录。
- [stats-appendix.md](stats-appendix.md)：场景内描述统计与运行时间。
- [manifest.json](manifest.json)：实验来源、源码状态、seed 合同、完整性和 SHA256。
- ID1 原始输出：`outputs/native200042-config-2-0-0-0-4-2-ID1-sourceIDs13-17-21-24-25-20260831/`。
- ID2--ID10 原始输出：`outputs/native200042-config-2-0-0-0-4-2-ID2-10-sourceIDs13-17-21-24-25-20260818/`。
