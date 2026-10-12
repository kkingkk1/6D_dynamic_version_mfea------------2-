---
status: done
updated: 2026-10-09
experiment_id: paper-fullspeed-update-20261009
---

# 全速复测结果更新论文

## 目标与允许范围

把已验收的 45 条全速 Auto-Hybrid 记录用于论文。允许修改论文结果数据入口、Table X/XI、实验计时段落、图表复现脚本、本计划、项目计划及本轮 Evidence/Reports。正式 PDF 在隔离编译和视觉检查后替换。原始实验证据不覆盖。

## 假设与未知点

- 采用 `autohybrid-slower-than-rkhma-fullspeed-20261009` 的最新 80 条 Auto-Hybrid 记录，其中 45 条全速、35 条历史保留。配置、seed、预算及收益保持。
- 480 条基线沿用上一轮论文 canonical 表，不重新运行。RK-HMA 与新 Auto-Hybrid 的运行条件和实际 seed 不完全相同，比较保持描述性。
- 收益不变，Fig. 5–7 的图形和逐轮数值应保持。耗时更新不得被解释为结构搜索的独立加速效果。
- 英文投稿正文只局部修改。模型、方法、搜索结果、收益结论及参考文献保持。构建使用现有工具，不安装依赖。
- 尚需核对所有使用旧耗时的正文和表格位置，以及修改后 PDF 的分页。

## 执行与最小验收

- [x] 验证两份来源哈希，生成 560 条新论文表；480 条基线及全部收益、seed、预算保持，只有 45 条 Auto-Hybrid 的计时和来源更新。
- [x] 更新复现脚本入口、两份结果表和计时说明；核对 112 个表格单元，证明三张收益图输入不变。
- [x] 在 `outputs/paper-fullspeed-update-20261009/` 编译、渲染 PDF；检查变动段落和结果表页面，验收后替换正式 PDF。
- [x] 写 Evidence/Reports，更新本计划和项目计划状态。对本轮改写段落完成轻量措辞检查。

## 结果与决策

560条完整覆盖、112个表格单元独立复算和21页PDF检查通过。九处耗时均值及四个正文段落已更新，收益图保持。详见 [报告](../Results/Reports/paper-fullspeed-update-20261009.md) 与 [证据](../Results/Evidence/paper-fullspeed-update-20261009/evidence.md)。
