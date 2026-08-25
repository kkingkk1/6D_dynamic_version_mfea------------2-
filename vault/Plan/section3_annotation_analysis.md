# Section III 批注分析与修改建议

## 批注位置与意图分析

### 批注1：双父协作的设计约束（Section III-A）

**原文批注（黄色高亮）**：
> "First, the design object is restricted to a pairwise collaboration between exactly two parents. This is not a loss of generality but a match to the scheduling setting: the manually fixed RK-HMA optimizer is itself a two-parent hybrid, so a pairwise structure already contains the manual baseline as one feasible point while keeping the encoding compact and expert-readable after search."

**意图分析**：
- 解释为什么设计空间限定为双父协作
- 强调这不是泛化能力的损失，而是与调度问题设置的匹配
- 说明包含手工基线RK-HMA作为可行点的优势

**问题诊断**：
1. **逻辑跳跃**：从"RK-HMA是双父"到"所以我们也限定为双父"的因果链不够完整
2. **缺少权衡讨论**：未说明三父或多父结构的潜在优势与搜索代价
3. **"match to the scheduling setting"表述模糊**：是匹配什么？耦合结构？评估成本？

**修改建议**：

```markdown
**原文（有问题的表述）**：
"First, the design object is restricted to a pairwise collaboration between exactly two parents. This is not a loss of generality but a match to the scheduling setting: the manually fixed RK-HMA optimizer is itself a two-parent hybrid, so a pairwise structure already contains the manual baseline as one feasible point while keeping the encoding compact and expert-readable after search."

**修改版A（强调公平对比+搜索可行性）**：
"Specializing the top-down design paradigm to this scheduling pipeline requires two problem-driven design decisions rather than a direct reuse of a general-purpose design method. First, the design object is restricted to a pairwise collaboration between exactly two parents. This restriction serves three purposes: (1) it matches the structure of the manually designed RK-HMA baseline, enabling a controlled comparison where the only difference is whether the collaboration structure is fixed or searched; (2) it keeps the search space tractable—adding a third parent would expand the already 172,480-candidate space by another order of magnitude; and (3) a two-parent structure provides a well-defined information-exchange channel, where both parents share one random-key population and one fitness vector, avoiding the coordination complexity of multi-way collaboration. The RK-HMA optimizer itself is a two-parent hybrid (DE/rand/1 + PSO), so the pairwise design space already contains the manual baseline as one feasible point."

**修改版B（简洁版，强调受控对比）**：
"First, the design object is restricted to a pairwise collaboration between exactly two parents. This constraint is not a limitation of the approach but a deliberate choice to match the evaluation setting: because the scheduling pipeline must run in full for every candidate (including random-key decoding and cross-satellite reassignment), and because the manually designed RK-HMA baseline is itself a two-parent hybrid, restricting the search to pairwise structures keeps the comparison controlled—the scheduling bridge and reassignment layer are shared, and the searched component is the single-satellite optimizer structure. A pairwise structure also gives a well-defined channel for information exchange: both parents share one random-key population and one fitness vector, so the collaboration factors act on a single, clearly defined interaction rather than on many entangled parents."
```

---

### 批注2：固定vs可搜索组件的划分（Section III-A）

**原文批注（黄色高亮）**：
> "The fixed scheduling pipeline follows the RK-HMA setting: initial task allocation, random-key continuous representation, greedy insertion decoding, and dynamic cross-satellite task reassignment are kept unchanged. The automatic-design layer changes only the collaboration structure of the single-satellite optimizer."

**意图分析**：
- 明确界定哪些是固定的、哪些是可搜索的
- 强调与RK-HMA共享相同的调度基础设施

**问题诊断**：
1. **顺序问题**：这段话应该更早出现，在读者还不知道"什么是RK-HMA pipeline"时就提到了
2. **缺少动机**：为什么固定这些组件？是为了公平对比？还是因为它们已经足够好？

**修改建议**：

```markdown
**建议位置**：移到Section III-A开头，在讨论设计原则之前

**修改版**：
"The proposed framework follows the top-down design idea of AutoHyb [24], where designing a collaboration-based hybrid optimizer is formulated as a meta-optimization problem. AutoHyb was developed and validated on general numerical and combinatorial benchmarks, where each candidate optimizer is cheap to evaluate. We adapt this idea to a domain setting it was not designed for: the coupled, discrete LS-AEOSTSP pipeline, where every candidate must be scored by the full scheduling process—key-decoding, greedy insertion, and dynamic cross-satellite reassignment. 

To keep the design comparison affordable and controlled, we fix the scheduling-specific components inherited from RK-HMA: initial task allocation, random-key continuous representation, greedy insertion decoding, and dynamic cross-satellite reassignment remain unchanged. The automatic-design layer searches only the collaboration structure of the single-satellite optimizer—specifically, which two parent algorithms to combine, how to update individuals, in what order to invoke the parents, and how offspring compete with the current population. This scoping decision serves two goals: (1) it keeps each candidate optimizer cheap enough to evaluate through the full scheduling pipeline, which matters because every fitness value here requires running allocation, decoding, and cross-satellite reassignment—a far more expensive operation than evaluating a numerical function; and (2) it enables a controlled comparison against the manually designed RK-HMA, which uses the same scheduling bridge and differs only in the inner single-satellite optimizer structure."
```

---

### 批注3：共享种群机制的强调（Section III-C）

**原文批注（黄色高亮）**：
> "The two parent algorithms share the random-key population. The two update genes define the population subset updated by each parent. The operating-order gene specifies how the two parent calls are arranged inside the single-satellite optimizer. The survivor gene specifies how current and generated candidates compete for the next population."

**意图分析**：
- 强调"共享种群"是真正协作的关键
- 区别于"两个独立优化器的简单并行"

**问题诊断**：
1. **埋藏太深**：这个关键机制在Section III-C才说明，应该更早出现
2. **缺少对比**：未说明"共享种群"vs"独立种群+结果合并"的区别

**修改建议**：

```markdown
**建议位置1**：在Section III-A的设计原则部分增加一段

**增补内容（放在设计原则部分）**：
"A two-parent structure also gives a well-defined channel for information exchange: both parents share one random-key population and one fitness vector, so the collaboration factors act on a single, clearly defined interaction rather than on many entangled parents. It also keeps each generated optimizer cheap enough to be evaluated through the full scheduling pipeline, which matters because every fitness value here requires running allocation, decoding, and cross-satellite reassignment in sequence. Second, because each candidate here must be evaluated by this expensive scheduling pipeline, the design stage needs an evaluation protocol that is affordable at search time yet trustworthy at reporting time. We therefore adopt a reduced-budget/full-budget protocol: a low-cost reduced-budget evaluation over a shared regional designing set guides the structural search, and an independent full-budget replay confirms the composed optimizer."

**建议位置2**：在Section III-D Decoding部分开头增强

**修改版（Section III-D开头）**：
"The decoding function maps one optimizer chromosome to a runnable single-satellite optimizer. Let Φ(h) denote the optimizer generated by chromosome h. The generated optimizer is a shared-population hybrid: it keeps one random-key population and one decoded scheduling objective. Both parents update selected individuals from the same population X^t and are evaluated by the same fitness vector F^t. This shared-population design distinguishes the approach from a simple parallel run of two independent optimizers—the update policies, operating order, and survivor selection define how the two parents collaborate on a single evolving population rather than merging results from separate searches."
```

---

### 批注4：超参数vs协议描述的区分（Table VII批注）

**原文批注（黄色高亮）**：
> "The table also omits component-library sizes, training scenario IDs, the number of replay runs, and the composed chromosome, because those items describe the protocol or the search outcome rather than tunable hyperparameters."

**意图分析**：
- 说明Table VII为什么不包含某些数值
- 区分"可调超参"vs"协议固定值"vs"搜索结果"

**问题诊断**：
1. **表格标题不准确**：标题是"HYPERPARAMETER SETTINGS"，但批注说明它不包含协议描述
2. **信息分散**：读者需要从正文多处寻找协议参数

**修改建议**：

```markdown
**修改1：调整Table VII的标题和说明**

**原标题**：
TABLE VII: HYPERPARAMETER SETTINGS.

**修改后标题**：
TABLE VII: DESIGN-STAGE AND FULL-BUDGET HYPERPARAMETERS.

**增加表格说明段落（放在表格前）**：
"Table VII reports the main hyperparameters used by the automatic-design stage and the full-budget scheduling layer. The first block describes the reduced-budget design search; the next rows describe the full-budget evaluation shared by Auto-Hybrid and RK-HMA; the last block lists the realization-form parameters referenced in Tables III-IV, which take effect only when the corresponding update or operating-order form is composed. The multi-satellite dynamic reassignment layer is inherited unchanged from RK-HMA [25]; because it is identical to the RK-HMA setting and is not part of the optimizer-design space, its parameters are not listed here. 

The table omits three categories of values: (1) component-library sizes (11 parent algorithms, 7 update policies, 8 operating orders, 4 survivor selections), because those define the search space rather than search behavior; (2) training-scenario identifiers (ID1, ID3, ID5, ID7) and the number of independent replay runs (5), because those describe the evaluation protocol rather than algorithm parameters; and (3) the final composed chromosome [2,9,0,0,0,2], because that is the search outcome, not an input setting."

**修改2：增加一个补充表格（可选）**

**TABLE VII-B: EVALUATION PROTOCOL PARAMETERS.**

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Training scenarios (design stage) | D_train | {ID1, ID3, ID5, ID7} |
| Full-budget test scenarios | D_test | {ID1-ID10} |
| Independent replay runs | - | 5 |
| Component library sizes | - | 11 parents, 7 update policies, 8 OO forms, 4 survivor forms |
```

---

### 批注5：计算成本的透明性（Section IV-C）

**原文批注（黄色高亮）**：
> "The 20-generation search with population size 35, evaluating each chromosome by R = 3 scheduling runs on each of the four scenarios, completed in approximately 6 hours on the same PC described above (i7-14700kF, 28 threads)."

**意图分析**：
- 提供设计搜索的实际运行时间
- 说明硬件环境以便读者评估可复现性

**问题诊断**：
1. **计算量分解不清晰**：6小时包含了什么？35×20×3×4次完整调度评估吗？
2. **与Table IX的关系模糊**：Table IX报告的是单次运行时间，如何与设计成本关联？

**修改建议**：

```markdown
**修改版（增强版Section IV-C）**：

"The 20-generation search with population size 35, evaluating each chromosome by R = 3 scheduling runs on each of the four training scenarios (ID1, ID3, ID5, ID7), completed in approximately 6 hours on the same PC described above (i7-14700kF, 28 threads). This corresponds to 35 × 20 × 3 × 4 = 8,400 reduced-budget scheduling evaluations. Fig. 5 plots the best-so-far trajectory over 20 generations. The y-axis reports mean normalized fitness across the four design-stage training scenarios. Each candidate is evaluated by R = 3 independent scheduling runs per scenario, and each scenario result is normalized by the corresponding total task profit. Orange markers indicate generations where the incumbent optimizer improves.

**[增加一个计算分解框]**：

**Design-stage computational budget breakdown:**
- Population size: N_d = 35
- Generations: G_d = 20  
- Repeats per scenario: R = 3
- Training scenarios: 4 (ID1, ID3, ID5, ID7)
- Total evaluations: 35 × 20 × 3 × 4 = 8,400 reduced-budget runs
- Wall-clock time: ~6 hours (i7-14700kF, 28 threads)
- Average per evaluation: ~2.6 seconds

For comparison, a single full-budget replay run on ID7 (4000 tasks, 40 satellites) takes 45.60s (Table IX, RK-HMA) to 8.52s (Table IX, Auto-Hybrid), so the reduced-budget evaluation uses approximately 60% of the full budget (ρ = 0.6, Table VII), as intended by the search protocol."
```

---

## 修改优先级排序

### **优先级1（必改）**：双父协作的设计约束说明
- **位置**：Section III-A Design Principle
- **原因**：这是设计空间界定的核心论证，直接影响方法的可信度
- **建议**：采用"修改版A"，补充三个明确的理由

### **优先级2（必改）**：固定vs可搜索组件的提前说明
- **位置**：Section III-A开头
- **原因**：读者需要先知道"什么是固定的、什么是可搜索的"才能理解后续设计
- **建议**：将批注内容扩展并移到Section III-A开头

### **优先级3（强烈建议）**：共享种群机制的强调
- **位置**：Section III-A和Section III-D开头
- **原因**：这是区别于"两个独立优化器并行"的关键，但当前说明埋藏太深
- **建议**：在两处都增加强调

### **优先级4（可选）**：Table VII的重组和说明
- **位置**：Table VII标题和说明
- **原因**：提升表格的信息组织清晰度
- **建议**：调整标题，增加表格前说明段落

### **优先级5（可选）**：计算成本分解
- **位置**：Section IV-C
- **原因**：帮助读者理解设计成本的构成
- **建议**：增加计算分解框

---

## 总体修改策略

### **第一步：重写Section III-A开头（约150词）**
- 先说"我们适配AutoHyb到昂贵评估的调度问题"
- 明确固定vs可搜索的划分和原因
- 解释双父限制的三重理由（公平对比+搜索可行性+信息交换通道）

### **第二步：增强Section III-D开头（约80词）**
- 强调"共享种群协作"vs"独立优化器并行"的区别
- 说明update policies/operating order/survivor selection如何定义协作

### **第三步：修订Table VII的标题和说明（约120词）**
- 调整标题为"DESIGN-STAGE AND FULL-BUDGET HYPERPARAMETERS"
- 增加表格前说明，明确什么被省略、为什么省略

### **第四步（可选）：增强Section IV-C的计算分解（约100词）**
- 增加计算分解框
- 关联reduced-budget与full-budget的时间对比

---

## 关键术语一致性检查

批注中多次出现的关键概念，需要在全文保持一致：

1. **"shared random-key population"** vs **"shared population"**
   - 建议：首次出现用完整术语，后续可简化

2. **"scheduling pipeline"** vs **"scheduling bridge"** vs **"multi-satellite layer"**
   - 建议：统一为"scheduling pipeline"指整体，"scheduling bridge"指random-key解码

3. **"collaboration structure"** vs **"hybrid structure"** vs **"optimizer structure"**
   - 建议：优先用"collaboration structure"强调协作

4. **"reduced-budget"** vs **"design-stage budget"**
   - 建议：统一为"reduced-budget evaluation"

5. **"composed optimizer"** vs **"selected optimizer"** vs **"Auto-Hybrid"**
   - 建议："composed optimizer"指设计阶段返回的结构，"Auto-Hybrid"指完整方法名
