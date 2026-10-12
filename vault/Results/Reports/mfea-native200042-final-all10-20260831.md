---
type: results-report
status: complete
effect_on_result: paper-adopted
evidence_strength: descriptive-replay
used_in_paper: true
evidence_package: Results/Evidence/mfea-native200042-final-all10-20260831
---

# native200042 全场景复现结果

## 发现

- 配置 `[2,0,0,0,4,2]` 在 ID1--ID10 的 50 次 full-budget replay 全部完成。
- 采用统一 `native200042` seed 表后，十场景宏平均为 `77.0369%`，六个 regional 场景均值为 `63.2402%`。
- ID1 的 Auto-Hybrid 均值为 `99.6002%`，按两位小数报告为 `99.60%`。
- 与 [25] 报告的 RK-HMA 值相比，十场景算术差为 `+0.4589` 个百分点，regional 子集差为 `+0.7635` 个百分点。该比较仍是不同 seed 表和代码状态下的描述性比较。

## 限制

最终批次只复现了一个选定配置，没有同批固定基线或预先声明的配对对照。因此不报告显著性、效应量或自动结构设计的独立因果效果。

## 决策

论文最终 full-budget replay 统一采用 `native200042`。外层搜索和训练筛选仍保留其原有 `native290002` 协议，并在论文中明确区分两者。

## 证据

[native200042 全场景复现 Evidence](../Evidence/mfea-native200042-final-all10-20260831/evidence.md)
