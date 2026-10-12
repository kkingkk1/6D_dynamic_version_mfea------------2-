---
status: done
updated: 2026-10-09
experiment_id: autohybrid-slower-than-rkhma-fullspeed-20261009
---

# Auto-Hybrid 慢于 RK-HMA 场景的全速复测

## 目标与范围

从当前十区域、六全局表中选择 Auto-Hybrid 五次算法耗时均值高于 RK-HMA 的场景。按当前加速实现复测所选场景，每场景五个 seed。

- 区域：500/5、2000/10、2000/20、3000/20、5000/50、6000/60、10000/100。
- 全局：3000/30、4000/40。
- 共 9 场景、45 次。其余 7 场景保留原结果。

## 执行合同

- 配置保持 `[2,0,0,0,4,2]`。每个场景保留已有五个实际 seed、perRun 0–4、nPop 和 maxFes。
- 当前源码、编译类、tuning、场景输入和原始数据表在实验现场记录哈希。自定义 seed 表仅位于本次 outputs，不改根 seed 表。
- Normal 优先级、全部 28 个逻辑处理器可用、28 个 HybCec 线程、单 JVM 串行；每个 seed 新建 JVM，无 warmup，-Xms512m/-Xmx4g。
- 使用 `RunSingleHybridConfig` 的算法计时；包含调度、重分配和校准，排除 JVM 启动、输入加载、初始分配及后续结果输出。
- 先完成 500/5 的 perRun 0、4，逐字段核对 RunSeed、预算与手动/批处理命令。两次计入正式结果，不重复运行。
- 输出现场为 `outputs/autohybrid-slower-than-rkhma-fullspeed-20261009/`。已有完成单元只回读，不重复启动；未完成现场先核对进程与日志。
- 单次 deadline 900 秒，整批 7200 秒。只处理本任务创建的子进程。

## 最小验收

- 45/45 次完成，每场景五个唯一实际 seed。逐次核对配置、预算、RunSeed、退出码、实际优先级和 CPU affinity。
- 与原结果核对收益；若变化，保留并报告，不把变化静默当作纯速度结果。
- 生成含新结果和保留结果的 80 条 canonical 表；原证据包保持。
- 串行完成实验后的相关测试。Evidence、Reports 和项目任务状态同步后标记完成。

## 解释边界

原 Auto-Hybrid 结果混合历史批次与 BelowNormal 并发补算。原 RK-HMA 也混合不同批次。旧均值用于筛选，不据此归因算法快慢；本次新 Auto-Hybrid 与现有 RK-HMA 的比较保持描述性。

## 结果入口

已完成验收与归档。采用最新结果库存；详见 [报告](../Results/Reports/autohybrid-slower-than-rkhma-fullspeed-20261009.md) 和 [证据](../Results/Evidence/autohybrid-slower-than-rkhma-fullspeed-20261009/evidence.md)。
