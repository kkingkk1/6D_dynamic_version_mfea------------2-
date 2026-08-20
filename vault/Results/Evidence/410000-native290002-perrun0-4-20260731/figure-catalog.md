# 图目录

## Figure 1

- 文件：`figures/figure-01-native-seed-scene-means.png`、`.svg`
- 目的：展示两个配置在 10 个场景上的五次均值。
- 读图重点：比较每个场景的绝对收益，尤其是 Regional 场景。
- 误差条：本图不绘制误差条；精确的五次 SD 在 `scene-summary.csv` 中。

## Figure 2

- 文件：`figures/figure-02-native-seed-paired-deltas.png`、`.svg`
- 目的：展示同一场景、同一 native seed 下 `410000-290002` 的差值。
- 读图重点：正值表示 410000 更高，零值表示并列。
- 解释边界：差值以场景五次均值为主，逐 seed 明细在 `paired-deltas.csv` 中。
