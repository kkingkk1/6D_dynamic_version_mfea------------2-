# AutoHyb 6D 纯语义动态版本

AutoHyb 卫星成像任务调度优化项目。当前主线使用 6D 纯语义混合配置：

```text
{parent1, parent2, update1, update2, operationOrder, survivor}
```

本文件只作为人类入口页。项目事实、agent 执行规则和回环检查以 `AGENTS.md` 为准；阶段结论和实验证据放在 `vault/`。

## 快速构建

```powershell
mvn -q test
```

## 常用运行命令

固定 6D 配置复现实验入口：

```powershell
mvn -q -DskipTests compile
$SceneRoot = if ($env:AUTOHYB_SCENE_ROOT) { $env:AUTOHYB_SCENE_ROOT } else { (Resolve-Path "..\Scene").Path }
$SceneDir = Join-Path $SceneRoot "500-5-0-0-24"
java "-Dtuning.config.path=tuning.properties" "-Dautohyb.sceneRoot=$SceneRoot" -cp "target/classes;$env:USERPROFILE\.m2\repository\org\apache\commons\commons-math3\3.6.1\commons-math3-3.6.1.jar" main.RunSingleHybridConfig true true $SceneDir 500 5 "4,1,0,0,0,0" 3 270 27000
```

自动设计搜索入口：

```powershell
mvn -q -DskipTests compile
java "-Dtuning.config.path=tuning.properties" -cp "target/classes;$env:USERPROFILE\.m2\repository\org\apache\commons\commons-math3\3.6.1\commons-math3-3.6.1.jar" main.MainMFEAMOPHOA
```

## 文档导航

- `AGENTS.md`：agent 全局地图、数据流、模块规则和回环检查。
- `CLAUDE.md`：Claude Code 入口文件，指向 `AGENTS.md`。
- `vault/00-Hub.md`：Obsidian 项目首页。
- `vault/01-Plan.md`：项目目标、关键决策和阶段结论。
- `vault/Plan/`：新的 MFEA 搜索计划和测试方案。
- `vault/Results/Reports/`：新的 MFEA 实验报告、表格、置信区间和证据。
- `vault/Knowledge/`：可复用项目知识、来源清单和防回退边界。
- `outputs/`：本地原始日志、CSV、stdout、JFR 和中间产物，不进入 Git。
