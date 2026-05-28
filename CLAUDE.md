# Claude Code 入口

本文件刻意保持轻量。

`AGENTS.md` 是本目录的权威项目地图，维护当前 AutoHyb 语义、入口、数据流、模块依赖和修改后回环检查规则。

在本仓库修改代码、文档、配置或实验脚本前：

1. 读取 `AGENTS.md`。
2. 执行其中的修改后回环检查。
3. 按 `AGENTS.md` 的文档索引读取被修改模块的 `AGENTS.md`。
4. 项目事实写入 `AGENTS.md`，不要写入本文件。

## Claude 专用说明

- 本地可能存在 Claude Code slash command 或 hook，但项目规则不能假设 Codex 或其他 agent 也能使用它们。
- 模块级 `AGENTS.md` 从属于根部 `AGENTS.md`。
- 计划模式、CCG、Claude 的计划模式生成的 plan 文档，统一放在 `vault/Plan/`；`vault/01-Plan.md` 只做入口和阶段性结论索引，不写原始日志。
- 如需记录 Claude 专用 command、hook、MCP 设置或工作流说明，只在这里写 Claude 专用差异。
- 不要在本文件复制全局地图、数据流、入口表或一致性检查清单。
