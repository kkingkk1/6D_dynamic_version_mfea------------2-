---
type: project
title: 6D 动态卫星调度混合元启发式项目
project: 6d-dynamic-version-mfea
status: active
tags:
  - research/project
  - satellite-scheduling
  - metaheuristic
  - optimization
updated: 2026-06-01
---

# 6D 动态卫星调度混合元启发式项目

## 页面职责

本页是 Obsidian vault 首页，只放 MFEA 主线入口和知识索引。代码结构、agent 执行规则和回环检查见根 `AGENTS.md`；项目主线、关键设计决策和阶段结论见 [[01-Plan]]。

## 项目任务

复现并扩展 AutoHyb 混合元启发式框架，用于多卫星成像任务调度优化。当前主线是 6D 纯语义混合配置搜索，并用固定基线 `{4,1,0,0,0,0}` 做对照。

## 核心索引

- [[01-Plan]]
- [[Knowledge/Codebase-Overview]]
- [[Knowledge/Source-Inventory]]
- [[Knowledge/Architecture-Deep-Dive]]
- [[Knowledge/Removed-Mechanisms|已移除机制与防回退边界]]

## 关键入口

| 场景 | 类 |
|---|---|
| 自动设计主入口 | `main.MainMFEAMOPHOA.main()` |
| 单配置复现实验 | `main.RunSingleHybridConfig.main()` |
| 多卫星协调调度 | `main.TaskAllocationCoordinator.scheduleWithReassignment()` |
| 单卫星优化器 | `core.HybCec.run()` |

## 模块依赖链

```text
main → core → strategy → algorithm → operator → common → model/utils
```

## 文件布局

- `Plan/`：新的 MFEA 搜索计划和测试方案。
- `Knowledge/`：架构、代码库概览、来源清单、已删除机制与防回退边界。
- `Writing/`：论文草稿和写作材料。
- `Daily/`：后续 MFEA 研究记录。
