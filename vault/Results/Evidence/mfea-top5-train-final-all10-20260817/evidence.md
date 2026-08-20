---
type: experiment-evidence
experiment_id: mfea-top5-train-final-all10-20260817
status: complete
primary_metric: profitRatio
primary_unit: scene-level five-run mean
---

# MFEA Top-5 训练筛选与全场景复现

## 研究问题

五个外层 MFEA seed 的候选记录中，训练场景筛出的配置能否在 ID1-ID10 的原生 `native290002` 固定 seed 上完成可复核的五次复现？

## 方法与筛选链

- 外层搜索：来源为 `outputs/mfea-native290002-training-20260806-5seeds-2026080501-2026080505-earlystop20-5-javaw` 的五个 completed outer seed。
- Top-5：按去重后历史 `bestConfig` 的最大已记录 `bestFitness` 排名，候选文件为 `candidate-selection-top5/top5-candidates.csv`。
- 训练筛选：五个候选在四个 `-train` 场景、每场景五个 `native290002` 固定 seed 下运行 100 次。胜者 `[2,0,0,0,4,2]` 的训练宏平均为 `73.3180%`，第二名为 `73.2805%`。
- 最终复现：胜者在 ID1-ID10、`perRun=0..4`、seed ID `10..14` 下运行 50 次，使用 `RunSingleHybridConfig`、deterministic 模式和 `Normal` 优先级。

## 完整性与结论

- 最终批次 `50/50` 完成，失败 `0`。
- 50 条 `actualSeed` 均与 `scene-seeds-native290002.properties` 的场景和 `perRun` 行一致；日志对缺失 `0`，非空 stderr `0`。
- 十场景宏平均 `profitRatio` 为 `77.0034%`。逐场景五次统计与 95% 区间见 `outputs/mfea-native290002-final-all10-20260817-winner-2-0-0-0-4-2-5seed/analysis/stats-appendix.md`。
- 此证据确认该配置完成了全场景复现，但没有同批基线或其余 Top-5 的全场景比较；不支持“优于基线”或“全局最优”的表述。

## 文件说明

- [data.csv](data.csv)：50 条 canonical 逐 seed 结果，不含日志路径等冗余列。
- [manifest.json](manifest.json)：源码版本、seed 合同、输入来源和 SHA256。
- 外部严格分析：`outputs/mfea-native290002-final-all10-20260817-winner-2-0-0-0-4-2-5seed/analysis/`。
