# 第三节批注修改计划

## 批注来源
基于 `Automatic Design of Collaboration-Based Hybrid Metaheuristics for Large-Scale Agile Earth Observation Satellite Scheduling_version1.pdf` 第三节的黄色高亮批注。

## 核心批注要点

### 1. 设计范围的明确界定（第6页底部）
**批注原文**：
> "where every candidate must be scored by random-key decoding and cross-satellite reassignment. A general collaboration-based hybrid optimizer can be viewed as a template composed of parent optimization algorithms and hybridization factors. [...] **First, the design object is restricted to a pairwise collaboration between exactly two parents. This is not a loss of generality but a match to the scheduling setting: the manually fixed RK-HMA optimizer is itself a two-parent hybrid, so a pairwise structure already contains the manual baseline as one feasible point while keeping the encoding compact and expert-readable after search.**"

**当前 paper_draft.md 对应段落**（第163-172行）：
```markdown
The proposed framework follows the top-down design idea of AutoHyb [24], where designing 
a collaboration-based hybrid optimizer is formulated as a meta-optimization problem. [...]
We instantiate the automatic-design framework within a fixed scheduling pipeline. Each 
chromosome-generated inner optimizer is evaluated under the same initial task allocation, 
random-key representation, decoding procedure, scheduling objective, and dynamic 
cross-satellite task-reassignment layer. Thus, the automatic-design stage changes only 
the collaboration structure of the inner optimizer.
```

**问题诊断**：
- ✅ 已说明"固定调度管道"
- ✅ 已说明"仅改变内部优化器的协作结构"
- ❌ **未明确说明为什么限制为双父代**
- ❌ **未说明双父代结构与RK-HMA基线的对应关系**
- ❌ **未说明这种限制的合理性（包含手动基线作为可行点）**

**修改建议**：
在第168行"Thus, the automatic-design stage changes only..."之后，添加明确的设计范围说明：

```markdown
We restrict the design object to pairwise collaboration between exactly two parent 
algorithms. This is not a loss of generality but a match to the scheduling setting: 
the manually fixed RK-HMA optimizer is itself a two-parent hybrid (DE/rand/1 and PSO), 
so a pairwise structure already contains the manual baseline as one feasible point 
while keeping the encoding compact and expert-readable after search.
```

---

### 2. 组件库语义的精确表达（第8-9页）

#### 2.1 Update Policy 的作用
**批注原文**：
> "**Update policy determines which individuals each parent modifies**"

**当前描述**（第191-193行）：
```markdown
The update policy decides which inner random-key solutions a parent algorithm may modify
```

**问题诊断**：
- ✅ 表述基本正确
- ⚠️ 可以更强调"each parent"的独立性

**修改建议**：
```markdown
The update policy decides which subset of the shared random-key population each parent 
algorithm is allowed to modify.
```

#### 2.2 Operating Order 的依赖关系
**批注原文**：
> "**Operating order fixes the information dependency between the two parents**"

**当前描述**（第191-193行）：
```markdown
the operating order fixes the information dependency between the two parent algorithms
```

**问题诊断**：
- ✅ 表述准确，无需修改

#### 2.3 Survivor Selection 的竞争机制
**批注原文**：
> "**Survivor selection determines how generated candidates replace current individuals**"

**当前描述**（第191-193行）：
```markdown
survivor selection decides how current and generated candidates compete for the next 
inner population
```

**问题诊断**：
- ✅ 表述准确
- ⚠️ "compete"比"replace"更好地体现了选择机制

---

### 3. 编码设计的语义可解释性（第11页）

**批注原文**：
> "The two parent genes select that share **the random-key population**. The two update 
> genes define the population subset updated by each parent. The operating-order gene 
> specifies how the two parent calls are arranged inside the single-satellite optimizer. 
> The survivor gene specifies how current and generated candidates compete for the next 
> population."

**当前描述**（第267-268行）：
```markdown
The two parent genes choose the inner metaheuristics that share the random-key population. 
The two update genes define the subset of inner solutions updated by each parent algorithm. 
The operating-order gene specifies how the two parent calls are arranged inside the 
single-satellite optimizer. The survivor gene specifies how current and generated inner 
solutions compete for the next population.
```

**问题诊断**：
- ✅ 各基因的作用描述清晰
- ✅ "share the random-key population" 已明确
- ⚠️ 可以增加一句总结：这种布局使得生成的优化器在搜索后仍然可读

**修改建议**（在第268行后添加）：
```markdown
A chromosome therefore records one collaboration mode between two parent algorithms 
instead of a generic numerical setting vector. This layout makes the generated optimizer 
readable after search: each gene corresponds to a distinct algorithmic role.
```

---

### 4. 固定调度管道的明确边界（第6-7页）

**批注原文**：
> "**The fixed scheduling pipeline follows the RK-HMA setting: initial task allocation, 
> random-key continuous representation, greedy insertion decoding, and dynamic 
> cross-satellite task reassignment are kept unchanged. The automatic-design layer 
> changes only the collaboration structure of the single-satellite optimizer.**"

**当前描述**（第167行）：
```markdown
Each chromosome-generated inner optimizer is evaluated under the same initial task 
allocation, random-key representation, decoding procedure, scheduling objective, and 
dynamic cross-satellite task-reassignment layer.
```

**问题诊断**：
- ✅ 列举了固定的组件
- ❌ **未明确说明"greedy insertion decoding"**
- ❌ **未明确说明这些组件来自RK-HMA**

**修改建议**：
```markdown
Each chromosome-generated inner optimizer is evaluated under the same scheduling 
pipeline inherited from RK-HMA [25]: initial task allocation, random-key continuous 
representation, greedy insertion decoding, and dynamic cross-satellite task 
reassignment. The chromosome changes only the collaboration structure of the 
single-satellite optimizer.
```

---

## 修改优先级

### P0 - 必须修改（影响论文核心贡献的清晰度）
1. **明确双父代设计范围的合理性**（第168行后）
2. **补充"greedy insertion decoding"说明**（第167行）

### P1 - 建议修改（提升表述精确度）
3. **增强Update Policy的"each parent"独立性表述**（第192行）
4. **增加编码布局的可读性总结**（第268行后）

### P2 - 可选优化（细节完善）
5. 在Table III标题后增加说明："Parameter symbols are included directly..."可以移到表格caption中

---

## 修改后验证清单

- [ ] 设计范围的限制有明确的理由
- [ ] 固定管道的边界清晰（四个固定组件：initial allocation, random-key repr, greedy decoding, reassignment）
- [ ] 六基因的语义对应关系清楚
- [ ] 与RK-HMA基线的关系明确
- [ ] 所有批注要点在正文中有对应表述
