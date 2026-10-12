---
status: complete
updated: 2026-10-08
---

# MFEA 胜者补齐当前十区域

## 目标与范围

使用已采用的 `[2,0,0,0,4,2]`，补齐当前十个区域场景的每场景五 seed 结果。排除旧 `1000-20-0-0-12`，包含新 `2000-20-0-0-12`。用户确认已有结果不重复计算。

## 执行计划

1. 按真实场景 basename 核对旧证据、原始完成记录、实际 seed 与配置。
2. 复用 500/5、1000/10、4000/40、8000/80、10000/100 的 25 条历史记录。
3. 补测 2000/10、2000/20、3000/20、5000/50、6000/60，各五次，共 25 次。
4. 首末 seed 实跑完成后回读 `[RunSeed]` 全字段，计入正式结果，不重复预检运行。
5. 归档 Evidence、简报和项目计划，核对 50 条唯一结果及输入/源码哈希。

## 合同

- 入口 `main.RunSingleHybridConfig`，factor 2.5、coefficient 100，确定性模式、GREEDY；无 warmup。
- 原有场景保持 `native200042` 实际 seed。原表缺少五个新增 basename，本轮使用 `outputs/mfea-current-ten-regional-20261008/seed-table.properties`，新增行沿用原表 500/5 的五个不同实际 seed。20 槽 schema 中 5–19 为别名，正式只运行 0–4。
- 不修改根 seed 表、Java 算法或默认配置。复用结果保留旧代码和旧计时来源；不宣称全部是同批、同源码或配对比较。
- Maven 编译/入口测试先完成，随后冻结运行 class 文件；不与实验并行构建。
- 本轮 Java 使用 BelowNormal、最多四个独立 JVM，每个 `-Xmx4g`；单次 deadline 900 秒，整批 3600 秒；不自动重试已启动任务。
- 本轮脚本及原始进程、stdout/stderr、精确 properties 保存到 `outputs/mfea-current-ten-regional-20261008/`。

## 验收与结果

25 次新增和 25 条历史复用均完成，当前十区域 50/50 条结果齐全。25 个不同 JVM 均正常退出，五场景各五个不同实际 seed，输入/源码/冻结类文件哈希保持；前后各五项现有入口测试通过。首条正常结果的日志解码核查失败已修正并回读，该 JVM 没有重复启动。

新增五场景均值依次为 34.9217%、59.8581%、28.1153%、81.1941%、66.8411%。采用本轮作为当前十区域结果库存，保留历史与新增来源，不修改算法或默认配置。

结果见 [证据包](../Results/Evidence/mfea-current-ten-regional-20261008/evidence.md) 和 [报告](../Results/Reports/mfea-current-ten-regional-20261008.md)。
