# 全速复测结果更新论文的证据

## 问题与方法

将已验收的 Auto-Hybrid 全速结果用于当前十区域、六全局论文。输入为上一轮论文的 560 条 canonical 记录和本次复测的最新 80 条 Auto-Hybrid 记录。两份数据及 manifest 的来源哈希均已核对。原证据包保持。

按 `(scene, perRun)` 替换 45 条新全速 Auto-Hybrid 记录的算法耗时、进程耗时、计时说明与来源。35 条未复测 Auto-Hybrid 和 480 条基线逐字段保持。所有 560 条收益、实际 seed、预算均保持。新表完整覆盖 16×7×5 个唯一单元。

新算法耗时来自 RunSingleHybridConfig 的精确 properties，采用 elapsedMillis/1000。进程耗时来自逐次 PID 记录，另存 processSeconds，不用于替代完整 solverSeconds。新计时包括完整调度评价、重分配与校准，排除 JVM 启动、输入加载、初始分配和后续输出。

## 结果

Table X/XI 中九个 Auto-Hybrid 场景耗时均值更新如下。显示值采用 Decimal ROUND_HALF_UP 两位小数。

| 场景 | Auto-Hybrid 秒 | 现有 RK-HMA 秒 |
|---|---:|---:|
| 区域 500/5 | 5.57 | 6.12 |
| 区域 2000/10 | 16.15 | 19.46 |
| 区域 2000/20 | 14.90 | 19.84 |
| 区域 3000/20 | 32.95 | 38.93 |
| 区域 5000/50 | 9.57 | 11.03 |
| 区域 6000/60 | 10.69 | 14.66 |
| 区域 10000/100 | 87.13 | 108.52 |
| 全局 3000/30 | 4.05 | 4.86 |
| 全局 4000/40 | 1.16 | 1.84 |

最新表中十区域、六全局的 Auto-Hybrid 五次均值均低于现有 RK-HMA。区域算法耗时范围变为 4.40–87.13 秒。正文删除原“七个区域及两个全局更慢”的当前结果表述。

收益均未变。区域 Auto-Hybrid/RK-HMA 宏均值仍为 57.12%/56.19%，全局仍为 97.00%/97.01%。Fig. 5–7 的逐轮收益输入与之前逐字段相同，六个 PNG/SVG 的 SHA256 均保持，沿用已有图形。

## 正文、复现与构建

正文局部更新四个段落，说明 45 条全速与 35 条保留记录的构成、Normal 优先级、28 线程、单 JVM、无 warmup、计时边界和最新耗时。模型、方法、摘要收益、结论收益及参考文献保持。本轮改写完成 writing-anti-ai 轻量措辞检查，未改动数字和证据边界。

`scripts/plot_paper_current16_results.py` 默认读取本包，新增 `--tables-only` 用于收益不变时只更新表格。默认完整绘图路径仍保留，使用的收益输入已核对不变。本轮实际执行表格生成，不重画相同收益图。

现有 Pandoc、CAS 和 XeLaTeX 在 `outputs/paper-fullspeed-update-20261009/` 隔离构建；禁用 MiKTeX 自动安装。正式 PDF 只有 `vault/Writing/paper_draft.pdf`，验收后替换；旧 PDF 快照留在本轮现场 `before/`。

## 验收

- 独立使用 Decimal 复算 112 个表格单元的收益与耗时，并核对论文中的实际行；80 条 Auto-Hybrid 用同场景分母重新核算收益率。
- 验证四份输入表/manifest、135 份本次原始计时来源和六个比较图哈希。480 条基线与 35 条保留记录逐字段相同，全部 560 条收益、seed、预算保持。
- 21 页 PDF 构建成功。Fig. 1–7、Table VI–XI 及摘要数字回读通过。前 12 页 PDF 文字与改前一致，模型与参考文献原文不变。
- 检查全稿总览，逐页检查首页、13–18 页，确认新说明可读、表格数字完整、场景组未拆开、无新增裁切或重叠。日志中的三个 CAS 首页 overfull 警告与原模板一致，首页已目视核对。

## 限制与决策

45 条新记录来自 Normal、28 线程、单 JVM 全速运行；35 条 Auto-Hybrid 和全部基线仍保留历史条件。实际 seed、代码快照和运行环境并非全部相同。本包的耗时比较是现有均值的描述性比较，不构成配对显著性检验、严格公平速度排名或结构搜索的独立加速证据。

本轮不重新运行 Java 实验。采用本包 560 条表作为当前论文复现入口，原证据不覆盖。

## 文件

- [data.csv](data.csv)：论文最新 560 条记录。
- [manifest.json](manifest.json)：来源、45 条替换记录、逐源哈希、验收和发布产物。
- [报告](../../Reports/paper-fullspeed-update-20261009.md)、[论文](../../../Writing/paper_draft.md)、[PDF](../../../Writing/paper_draft.pdf)。
- 原始复测详见 [全速证据](../autohybrid-slower-than-rkhma-fullspeed-20261009/evidence.md)。构建、表格、日志和渲染现场位于 `outputs/paper-fullspeed-update-20261009/`。
