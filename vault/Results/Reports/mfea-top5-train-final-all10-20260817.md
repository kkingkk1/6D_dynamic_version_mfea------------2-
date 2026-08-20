---
type: results-report
status: complete
effect_on_result: candidate-confirmed
evidence_strength: descriptive-replay
used_in_paper: false
evidence_package: Results/Evidence/mfea-top5-train-final-all10-20260817
linked_experiments:
  - Plan/2026-05-29-mfea-aggressive-search-plan.md
---

# MFEA Top-5 训练筛选与全场景复现

## 研究问题

验证五个外层 MFEA seed 的 Top-5 候选经训练筛选后，是否能在 ID1-ID10 和原生固定 seed ID `10..14` 上完成全场景复现。

## 发现

- 训练阶段完成 `5 × 4 × 5 = 100` 次复核，选出 `[2,0,0,0,4,2]`；训练宏平均为 `73.3180%`。
- 训练第一、二名只差 `0.0375` 个百分点，因此这一步只应视为候选筛选，不能把该微小差异解释为稳定优势。
- 最终 ID1-ID10 批次完成 `50/50`，失败、seed 不匹配、缺失日志对和非空 stderr 均为 `0`。
- 最终十场景宏平均为 `77.0034%`；场景内五次结果在非饱和场景的标准差为 `0.0945` 至 `0.3374` 个百分点。

## 局限

最终批次只复现了筛出的一个配置。没有同批固定基线，也没有其余 Top-5 在 ID1-ID10 上的对应结果，不能报告显著性、效应量或基线优越性。

## 决策

将 `[2,0,0,0,4,2]` 记录为“完成当前全场景五 seed 复现的 MFEA 候选”，不提升为默认配置，也不写入论文主结果。

## 下一步

若需要作比较性结论，使用相同 ID1-ID10、seed ID `10..14`、预算和源码，对预先指定的固定基线或剩余 Top-5 候选做配对复核。

## 证据

[MFEA Top-5 训练筛选与全场景复现 Evidence](../Evidence/mfea-top5-train-final-all10-20260817/evidence.md)
