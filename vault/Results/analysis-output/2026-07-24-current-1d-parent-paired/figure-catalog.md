# 当前 1D Parent 四配置配对实验：图表目录

## 图 1：场景级平均收益率

- 文件：`figures/figure-01-scene-means.png`、`figures/figure-01-scene-means.svg`。
- 目的：逐场景显示每对配置的五次配对 run 平均收益率，区分收益方向来自哪些场景。
- 数据：`vault/Results/data/2026-07-24-current-1d-parent-paired-scene-summary.csv`。
- 图形：左侧 `hybrid-290002` 对 `hybrid-410000`；右侧 `parent-4` 对 `parent-1`。误差线为场景内五次重复均值的 95% CI。
- 观察：两组候选都在 ID3、ID5、ID7、ID9、ID10 等非饱和场景不低于基线，ID7 的 Hybrid 增益最大；ID2、ID4、ID6、ID8 接近或达到收益上限。
- 解释边界：图显示的是每个场景的重复不确定性，不能把十个场景间的折线距离解读为跨场景随机波动。
- 决策含义：候选收益并非只来自一个 seed；但饱和场景不能用于区分方法，下一轮应补充更多非饱和场景。

## 图 2：场景级收益差

- 文件：`figures/figure-02-scene-deltas.png`、`figures/figure-02-scene-deltas.svg`。
- 目的：将候选减基线的收益差直接置于零线附近，检验是否存在反向场景。
- 数据：同图 1，按共同 seed 的五次 run 配对后计算场景内均值差。误差线为该均值差的 95% CI。
- 观察：两项对比都为 6 个正差、4 个零差、没有场景级负差；Hybrid 的最大正差是 ID7 `+2.976` pp，Parent 的最大正差是 ID9 `+2.828` pp。
- 解释边界：图不显示 Holm 校正；统计结论应以 `stats-appendix.md` 为准。
- 决策含义：保留两组候选进入后续非饱和场景复验，但不将本图当成校正后显著性证据。
