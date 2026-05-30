---
title: MFEA 6D 自动设计搜索 — 激进方案
status: planned
created: 2026-05-29
---

# MFEA 6D 自动设计搜索 — 激进方案

## 目标

在 ID1/ID3/ID5 三场景上用 60% HybCEC 预算做外层 MFEA 搜索，找到超过固定基线 `{4,1,0,0,0,0}` 的自动设计配置。

## 搜索空间

6D 离散空间：`11×11×7×7×8×4 = 188,496` 种组合。

## 场景参数

| ID | 场景 | 任务数 | 卫星数 | maxD ≈ | nPop | 100% maxFes | 60% maxFes |
|---|---|---|---|---|---|---|---|
| ID1 | `500-5-0-0-24` | 500 | 5 | 90 | 270 | 27000 | 16200 |
| ID3 | `1000-10-0-0-12` | 1000 | 10 | ~100 | ~300 | ~21000 | ~12600 |
| ID5 | `1000-20-0-0-12` | 1000 | 20 | ~50 | ~150 | ~10500 | ~6300 |

## Phase 1: MFEA 搜索（激进方案）

### 外层参数

| 参数 | 值 | 理由 |
|---|---|---|
| nPopHyb | 35 | 188K 组合空间需要足够多样性 |
| gMax | 20 | 给交叉算子充分收敛代数 |
| nRun | 3 | 每个候选配置评估 3 次取均值，过滤噪声 |
| maxFes | 60% of default | 短测筛选，降低单次评估耗时 |
| crossRate | 0.3 | 保持默认 |

### 运行命令模板

```bash
# ID1
java -cp target/classes \
  -Dautohyb.outer.nPopHyb=35 \
  -Dautohyb.outer.gMax=20 \
  -Dautohyb.outer.nRun=3 \
  -Dautohyb.outer.maxFes=16200 \
  main.MainMFEAMOPHOA 500 5

# ID3
java -cp target/classes \
  -Dautohyb.outer.nPopHyb=35 \
  -Dautohyb.outer.gMax=20 \
  -Dautohyb.outer.nRun=3 \
  -Dautohyb.outer.maxFes=12600 \
  main.MainMFEAMOPHOA 1000 10

# ID5
java -cp target/classes \
  -Dautohyb.outer.nPopHyb=35 \
  -Dautohyb.outer.gMax=20 \
  -Dautohyb.outer.nRun=3 \
  -Dautohyb.outer.maxFes=6300 \
  main.MainMFEAMOPHOA 1000 20
```

### 预估耗时

| ID | 单次评估(3run) | 初代(35个) | 每代(35个) | 总(20代) |
|---|---|---|---|---|
| ID1 | ~18s | ~10.5min | ~10.5min | ~3.5h |
| ID3 | ~10s | ~6min | ~6min | ~2h |
| ID5 | ~6s | ~3.5min | ~3.5min | ~1.2h |

总计约 7h（三场景串行）。可并行跑不同场景缩短到 ~3.5h。

### 总评估次数

- 初代：35 个配置
- 每代：35 个子代
- 总评估：35 + 35×20 = 735 个配置评估点

## Phase 2: Top-K 复测（100% 预算）

对每个场景的 top-3 自动设计配置：

| 参数 | 值 |
|---|---|
| 入口 | `RunSingleHybridConfig` |
| nRun | 5 |
| maxFes | 100% default |
| 对照 | 固定基线 `{4,1,0,0,0,0}` 同条件 |

### 复测命令模板

```bash
# 对每个 top config [P1,P2,U1,U2,OO,SS]
java -cp target/classes \
  main.RunSingleHybridConfig P1,P2,U1,U2,OO,SS \
  --nRun 5

# 基线对照
java -cp target/classes \
  main.RunSingleHybridConfig 4,1,0,0,0,0 \
  --nRun 5
```

## Phase 3: 结果分析

- 建立自动设计结果表：场景、基线收益、自动设计收益、绝对提升、相对提升、最优 6D 配置
- 分析 top 配置的 6D 各维分布：哪些父算法组合被选中、哪些 update policy 占优
- 检查跨场景一致性：同一配置在 ID1/ID3/ID5 是否都有收益

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| 60% 预算改变慢收敛算法排序 | SA/ABC 本身 profit 低，不影响 top 筛选；复测用 100% |
| nRun=3 方差大，微小差异被噪声淹没 | 搜索阶段只筛大差异(>10 profit)；复测用 nRun=5 |
| 5h 单场景耗时过长 | 三场景可并行；若需缩短可先跑 ID5(最快) 验证流程 |
| 搜索陷入局部最优 | nPopHyb=50 提供足够多样性；crossRate=0.3 保持探索 |

## 成功标准

- 至少一个场景的自动设计 top-1 配置在 100% 预算复测中 AvgProfit 超过基线 `{4,1,0,0,0,0}` 达 5+ profit
- 自动设计配置在 3 个场景中至少 2 个有正收益

## 执行顺序

1. `mvn compile` 确认代码可编译
2. 先跑 ID5（最快）验证 MFEA 流程正常
3. 并行跑 ID1 和 ID3
4. 收集三场景 top-3 配置
5. Phase 2 复测
6. Phase 3 分析，结果写入 `vault/Results/Reports/`
