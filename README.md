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

Hybrid 的随机种子按 `$SceneDir` 的场景目录名读取根目录 seed 表。默认 source `native290002` 使用 `scene-seeds-native290002.properties`；可用 `-Devaluation.seedTable.source=native270342`、`native200042` 或 `native410000` 切换到对应表。`perRun=0..4` 对应逻辑 seed ID `10..14`；`native270342` 的前五个位置依次复用 `native290002` 的 seed ID `12,17,18,19,14`，`native200042` 的前五个位置依次复用原始 seed ID `13,17,21,24,25`。两种五种子 profile 的其余表项循环复用前五项。单独选择表项时设置 `-Devaluation.perRunStart=N`，也可用 `-Devaluation.seedTable.path=<path>` 指定完整表。直接用 VSCode 运行 `RunSingleHybridConfig` 时，可编辑 `src/main/java/main/RunSingleHybridConfig.java` 顶部的 `MANUAL_PER_RUN_START` 和 `MANUAL_SEED_TABLE_SOURCE`；显式 JVM 参数优先。直跑默认打印 `[RunSeed]` 的 source、表文件名、场景、`perRun`、seed ID 和实际 seed；可用 `-Devaluation.runSeedLog=false` 关闭。旧的 `evaluation.runIndexBase` 和 `evaluation.runSeedBase` 不参与 Hybrid seed 计算。

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
