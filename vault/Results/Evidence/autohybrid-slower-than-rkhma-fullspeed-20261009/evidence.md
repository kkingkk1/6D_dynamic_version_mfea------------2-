# Auto-Hybrid 慢场景全速复测证据

## 问题与选择

按原十区域、六全局表的五seed算法耗时均值，选择 Auto-Hybrid 慢于 RK-HMA 的 9 个场景。本次只复测所选 45 个场景/seed 单元；其余 35 条保持原数据。

原始选择表为 `paper-current16-update-20261008/data.csv`，Auto-Hybrid 原记录来自 `mfea-current-six-global-20261008/data.csv`。选择前回读 manifest 的 SHA256，并核对两表 Auto-Hybrid 均值一致。完整16场景选择/复测对照见现场 time-comparison16.csv。

## 执行合同

配置 `[2,0,0,0,4,2]`。每个场景保留原实际五seed、perRun 0–4、nPop、maxFes。新自定义表由原行逐项生成；每次 nRun=1，首末槽满足 perRun+nRun<=20。

先手动完成 500/5 的 perRun 0、4，核对 RunSeed source/table/basename/perRun/seedId/实际seed，以及预算和命令。两次计入正式结果；批处理回读，未重复运行。所有结果逐次核对 custom 表中的实际 seed。

Normal 优先级、全部28个逻辑处理器可用、单JVM串行、28个HybCec线程；无warmup，每seed新建JVM。-Xms512m/-Xmx4g。冻结当前新加速classes和tuning，运行期间不执行Maven。每次读回 Windows PriorityClass=0x20，并核对 affinity 与系统可用掩码一致。

入口为 RunSingleHybridConfig。elapsedSeconds 来自精确 properties 的 elapsedMillis/1000，范围为 EvaluationHyb 完整调度评价，包含重分配和校准，排除 JVM 启动、读取、初始化分配及后续记录输出。processSeconds另存lifecycle，不混用。原始命令、资源、PID和退出码在 manifest/lifecycle 中。

## 结果

| 场景 | 原Auto/秒 | 新Auto/秒 | 现有RK-HMA/秒 |
|---|---:|---:|---:|
| 500-5-0-0-24 | 6.929 | 5.572 | 6.124 |
| 2000-10-0-0-12 | 68.087 | 16.149 | 19.456 |
| 2000-20-0-0-12 | 71.728 | 14.895 | 19.835 |
| 3000-20-0-0-8 | 193.645 | 32.950 | 38.926 |
| 5000-50-0-0-12 | 23.792 | 9.573 | 11.028 |
| 6000-60-0-0-6 | 30.861 | 10.688 | 14.661 |
| 10000-100-0-6-12 | 113.658 | 87.134 | 108.520 |
| 3000-30-1-12-20 | 12.906 | 4.048 | 4.862 |
| 4000-40-1-12-18 | 3.361 | 1.161 | 1.841 |

9 场景均为五seed均值。45/45 成功退出。新均值仍慢于现有 RK-HMA 的场景：无。

45 次收益与原记录在 1e-8 容差内一致。

## 验证与限制

- 45个新单元与35个保留单元构成80条唯一记录，16场景各五seed。配置、实际seed和预算逐项保持。
- 前置57项测试通过，实际运行后再串行执行同组57项测试通过。启动前修正了一处入口测试的过时默认值期望；生产算法配置未改动。
- 源码、冻结类、输入、tuning、seed表和原始数据哈希保持；逐次日志、精确properties和lifecycle保留。异常或负向结果未剔除。
- 原Auto记录混合历史与BelowNormal并发批次。资源条件和加速实现均变化，旧/新耗时差不能单独归因两项代码优化。
- RK-HMA原值来自多个批次，实际seed可能不同。这里只做现有均值的描述性比较，不作配对显著性或全场景公平速度结论。严格同合同改前/改后加速证据另见 [前次验收](../autohybrid-speed-merge-20261009/evidence.md)。
- 新全速只覆盖9场景。其余7场景35条仍保持原运行条件；最新80条表不能整体称为同批全速数据。
- 当前入口没有导出完整调度签名，本轮以元数据、收益回读和相关测试验收，不宣称逐任务独立验算。

## 文件与决策

- [data.csv](data.csv)：最新80条Auto-Hybrid canonical库存，45条新全速记录带 origin=fullspeed-new-20261009。
- [manifest.json](manifest.json)：选择、合同、逐次命令、seed、原输入和产物SHA256。
- 原始现场 `outputs/autohybrid-slower-than-rkhma-fullspeed-20261009/`：fullspeed45.csv、time-comparison16.csv、冻结classes、tuning、seed表、日志、properties、PID、进度和测试报告。

采用最新80条表作为后续结果更新入口。原证据包保留。论文旧表尚未在本轮重建。
