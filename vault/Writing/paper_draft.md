# A 6D Automatically Designed Hybrid Metaheuristic with Dynamic Task Reassignment for Large-Scale Multi-Satellite Scheduling

**Abstract**--Large-scale agile earth observation satellite task scheduling is difficult because each selected task must be assigned to one feasible satellite and inserted into a feasible time window under attitude-transition and capacity constraints. This paper proposes an evolutionary automatic-design framework for constructing hybrid metaheuristics for this problem. Instead of fixing the inner optimizer manually, the framework treats the optimizer as an evolvable object. Each candidate optimizer is encoded by a six-dimensional semantic chromosome that selects two parent metaheuristics, two population-update policies, one operation-order policy, and one survivor-selection policy. The active design space contains 11 parent algorithms, 7 update policies, 8 operation-order policies, and 4 survivor-selection policies; a fixed reassignment-move library repairs cross-satellite conflicts during evaluation. An outer evolutionary search evaluates candidate chromosomes by instantiating the corresponding HybCec optimizer and running the complete multi-satellite scheduling pipeline. The selected configuration is then evaluated by a separate full-budget replay protocol. Experiments on ten benchmark instances from 500 tasks and 5 satellites to 10,000 tasks and 100 satellites show that the selected 6D configuration matches the saturated global-distribution instances and improves all non-saturated regional-distribution instances compared with the latest manually fixed 8D RK-HMA draft results. Against external baselines reported in the latest 8D draft, the selected configuration is best or tied-best by five-run average on 9 of 10 scenarios, while its best replay exceeds the cited ID1 value. The selected configuration, L-SHADE + EDA with full-population updates, sequential execution, and elitist survival, improves the average profit rate by 0.50 percentage points over the latest 8D Hybrid average, and by 0.84 percentage points on the six non-saturated instances.

**Index Terms**--agile earth observation satellite scheduling, automatic algorithm design, evolutionary automatic design, hybrid metaheuristic, random-key encoding, task reassignment

# I. Introduction

Agile earth observation satellites can observe ground targets by adjusting attitude within visibility time windows. In large-scale missions, the number of candidate tasks usually exceeds the available observation capacity. A scheduler must decide which tasks to observe, which satellite should execute each selected task, and where each task should be inserted in the satellite sequence. The resulting problem is combinatorial, constrained by visibility windows, imaging duration, attitude transition time, and task profit.

Metaheuristic methods are widely used for agile satellite scheduling because exact optimization becomes difficult on large instances. Adaptive large neighborhood search, genetic algorithms, particle swarm optimization, differential evolution, ant colony optimization, and learning-based scheduling methods have all been studied for related variants of the problem [1]-[15]. Hybrid metaheuristics are also attractive because different operators often provide complementary search behavior [16]-[19].

The latest 8D RK-HMA draft uses a manually selected sequential hybrid optimizer: DE/rand/1 first improves a random-key population, and PSO then refines the same population. That design is effective, but its algorithmic structure is fixed before the instance family is evaluated. It leaves open whether a broader library of parent algorithms and hybrid-control policies can yield a stronger configuration without manual enumeration.

This paper studies that question by turning the inner hybrid optimizer into an automatic algorithm-design target. Instead of tuning low-level parameters inside one fixed algorithm, the proposed method searches a six-dimensional semantic configuration:

```text
{parent1, parent2, update1, update2, operationOrder, survivor}
```

The two parent genes choose from 11 active metaheuristic parents. The two update genes control which individuals each parent updates. The operation-order gene controls how the two parents are scheduled inside HybCec. The survivor gene controls how parent and offspring candidates compete. Runtime settings such as insertion mode, DE scaling schedule, and parent-internal hyperparameters are kept outside the 6D chromosome. This keeps the search space compact and interpretable.

The main contributions are as follows.

1. We construct explicit component libraries for automatic hybrid metaheuristic design. The evolvable libraries cover parent-algorithm choice, update scope, operation order, and survivor selection; the scheduling evaluator further uses a fixed reassignment-move library.

2. We formulate a 6D semantic chromosome that assembles these libraries into executable HybCec optimizers. The resulting valid space contains 172,480 hybrid optimizer structures while keeping low-level runtime settings outside the chromosome.

3. We use an outer evolutionary search to search the 6D space and a replay path to verify the selected configuration under the full scheduling pipeline. The search is therefore separated from final evidence collection.

4. We show that the automatically designed optimizer improves the latest fixed 8D Hybrid result on every non-saturated scenario and matches all saturated scenarios in profit rate. Against external baselines, it is best or tied-best by average on 9 of 10 scenarios, and its best ID1 replay exceeds the cited ID1 reference.

The rest of this paper is organized as follows. Section II defines the scheduling problem. Section III describes the proposed 6D automatic hybrid design framework. Section IV reports the experiments. Section V discusses the findings, and Section VI concludes the paper.

# II. Problem Description

Consider a set of observation tasks

```math
\mathcal{T}=\{\tau_1,\tau_2,\ldots,\tau_n\}
```

and a set of agile satellites

```math
\mathcal{S}=\{s_1,s_2,\ldots,s_m\}.
```

Each task has a location, an imaging duration, a profit, and a required imaging quality. Each satellite has an orbit and attitude state over the scheduling horizon. Orbit propagation and access analysis produce a set of visible time windows for each task-satellite pair.

Let `\omega_{ijk}` denote the `k`-th visible time window of task `\tau_i` on satellite `s_j`. Its start time, end time, and duration are denoted by `\alpha_{ijk}`, `\beta_{ijk}`, and `\lambda_{ijk}`. Let `x_{ijk}` be a binary variable indicating whether task `\tau_i` is executed in window `\omega_{ijk}`. Let `b_{ijk}` be the observation start time when `x_{ijk}=1`.

The objective is to maximize the collected profit:

```math
\max F(P_S)=\sum_{i=1}^{n}\sum_{j=1}^{m}\sum_k r_i x_{ijk}.
```

Each task can be scheduled at most once:

```math
\sum_{j=1}^{m}\sum_k x_{ijk} \le 1,\quad \forall i.
```

If a task is selected, the observation must stay inside the chosen time window:

```math
\alpha_{ijk} \le b_{ijk}, \quad
b_{ijk}+d_i^{img}\le \beta_{ijk}.
```

For any two consecutive observations on the same satellite, the time gap must be no smaller than the attitude transition time. The transition time depends on the angular displacement between the two observations. The imaging quality of each executed task must also satisfy the required threshold.

The solution therefore has two coupled parts. First, each scheduled task must be assigned to a satellite and time window. Second, each satellite must choose a feasible task sequence. The proposed method handles this by combining random-key per-satellite sequencing with cross-satellite task reassignment.

**TABLE I: NOTATION.**

| Symbol | Description |
|---|---|
| `\mathcal{T}` | Set of observation tasks |
| `\mathcal{S}` | Set of satellites |
| `\tau_i` | Task `i` |
| `s_j` | Satellite `j` |
| `r_i` | Profit of task `\tau_i` |
| `d_i^{img}` | Imaging duration of task `\tau_i` |
| `\omega_{ijk}` | The `k`-th visible time window of task `i` on satellite `j` |
| `\alpha_{ijk}` | Start time of `\omega_{ijk}` |
| `\beta_{ijk}` | End time of `\omega_{ijk}` |
| `\lambda_{ijk}` | Duration of `\omega_{ijk}` |
| `x_{ijk}` | Binary variable indicating whether task `i` is scheduled in `\omega_{ijk}` |
| `b_{ijk}` | Observation start time |
| `F(P_S)` | Total profit of the scheduled task set |

# III. Evolutionary Automatic Design Framework

## A. Design Principle

The proposed method treats the hybrid optimizer as the design object. Rather than fixing the parent algorithms and control rules before evaluation, it defines a discrete component space and searches this space with an outer evolutionary process. A candidate in the outer population is therefore an algorithm configuration, not a task sequence.

The automatic-design loop has four levels:

1. A 6D chromosome encodes a candidate hybrid optimizer.
2. The chromosome is decoded into an executable HybCec configuration.
3. The configured HybCec optimizer is embedded in the complete multi-satellite scheduling pipeline with dynamic task reassignment.
4. An outer evolutionary search selects configurations by their measured scheduling profit.

Under this formulation, the manually fixed RK-HMA structure is one feasible point in the configuration space. The proposed method searches over such points and returns the optimizer selected by the measured scheduling objective.

The overall flow is:

```text
Component library
  -> 6D optimizer chromosome population
  -> outer evolutionary search
     -> decode chromosome into HybCec control policy
     -> run complete satellite scheduling pipeline
     -> compute profit improvement over baseline
     -> select high-fitness optimizer chromosomes
  -> best 6D optimizer
  -> full-budget replay on all benchmark scenarios
```

The design and evidence stages are separated. The outer search uses four representative training scenarios, ID1, ID3, ID5, and ID7, which cover small, medium, and conflict-heavy regional cases. The selected optimizer is then evaluated on all ten benchmark scenarios by the full-budget replay protocol. Search-stage fitness is used only for algorithm selection; the reported ten-scenario results come from the independent replay path.

## B. Component Libraries for Automatic Design

Automatic design requires a finite set of reusable algorithmic choices. The proposed method exposes four evolvable libraries for the inner hybrid optimizer: parent algorithms, update policies, operation-order policies, and survivor-selection policies. The cross-satellite reassignment layer uses a separate move library during scheduling evaluation. These reassignment moves are not genes in the 6D chromosome. They are shared by all decoded optimizers, so the outer search compares inner hybrid structures under the same scheduling repair protocol.

The runtime implementation retains archived parent-algorithm IDs for compatibility, but the automatic-design search exposes only the active parent IDs 0-10. The search-space size below is computed from this active library.

**TABLE II: PARENT-ALGORITHM LIBRARY.**

| ID | Parent algorithm | Search behavior | Role in automatic design |
|---:|---|---|---|
| 0 | GA | Crossover and mutation over random-key vectors | Recombines task-order patterns across individuals |
| 1 | PSO | Velocity-guided movement toward personal and global best keys | Provides smooth population-level exploitation |
| 2 | EDA | Gaussian model estimated from elite individuals | Samples promising task-order distributions |
| 3 | ACO | Elite-based Gaussian ant-colony sampling | Intensifies search around high-fitness regions |
| 4 | DE/rand/1 | Random base vector plus one differential vector | Adds exploratory differential variation |
| 5 | DE/best/1 | Best base vector plus one differential vector | Exploits the current best solution region |
| 6 | DE/current-to-rand/1 | Current vector moves toward a random differential direction | Preserves diversity while perturbing each individual |
| 7 | ABC | Employed, onlooker, and scout bee updates | Perturbs solutions and replaces stagnant candidates |
| 8 | SA | Temperature-controlled local perturbation | Allows occasional worsening moves during local search |
| 9 | L-SHADE | Success-history adaptive DE with archive and population reduction | Adapts differential search parameters during optimization |
| 10 | ALNS | Destroy-and-repair sequence local search encoded back to random keys | Repairs and improves decoded task orders |

**TABLE III: UPDATE-POLICY LIBRARY.**

| ID | Update policy | Selected individuals | Purpose |
|---:|---|---|---|
| 0 | FULL | All individuals | Applies the parent algorithm to the whole population |
| 1 | TOP_SUBSET | Fixed high-fitness subset | Concentrates evaluations on strong candidates |
| 2 | MIXED_SUBSET | High-fitness subset plus random individuals | Balances exploitation and exploration |
| 3 | RANDOM_DECAY | Random subset with decaying size | Uses broader early updates and narrower late updates |
| 4 | ABOVE_MEAN | Individuals above mean fitness | Filters updates by current population quality |
| 5 | LOCAL_SEARCH | Historical best individual | Performs focused local improvement |
| 6 | WORST_REPAIR | Current worst individual | Repairs weak candidates without spending a full-population update |

**TABLE IV: OPERATION-ORDER LIBRARY.**

| ID | Operation-order policy | Execution rule | Purpose |
|---:|---|---|---|
| 0 | SEQUENTIAL | Run parent 1, then parent 2 | Builds a direct two-stage hybrid chain |
| 1 | PERIODIC_SWITCH | Switch active parent by iteration period | Alternates components with a fixed temporal rhythm |
| 2 | STAGE_SWITCH | Use different parents in different search stages | Separates early and late search behavior |
| 3 | BEST_NO_IMPROVEMENT_SWITCH | Switch when the global best stagnates | Reacts to objective-level stagnation |
| 4 | PROCESS_NO_IMPROVEMENT_SWITCH | Switch when the active process stagnates | Reacts to parent-level stagnation |
| 5 | DIVERSITY_SWITCH | Route parents according to population diversity | Changes behavior when the population contracts or disperses |
| 6 | PARALLEL | Generate parent-1 and parent-2 candidates separately, then merge | Compares two parent updates in the same iteration |
| 7 | ADAPTIVE_CREDIT | Route by recent improvement per evaluation cost | Allocates evaluations to the parent with higher recent credit |

**TABLE V: SURVIVOR-SELECTION LIBRARY.**

| ID | Survivor policy | Replacement rule | Purpose |
|---:|---|---|---|
| 0 | ELITIST_BEST_N | Merge parents and offspring, then keep top-N fitness | Preserves the best candidates deterministically |
| 1 | TOURNAMENT | Select survivors by tournament competition | Maintains selection pressure with stochasticity |
| 2 | PAIRWISE_GREEDY | Compare each offspring with its paired parent | Accepts local improvements without reshuffling the population |
| 3 | RANK_WEIGHTED | Sample merged candidates by rank-based probability | Keeps stronger candidates while retaining sampling diversity |

**TABLE VI: REASSIGNMENT-MOVE LIBRARY.**

| Move | Scope | Acceptance rule | Role in scheduling evaluation |
|---|---|---|---|
| Standard migration | Move one unscheduled task to a target satellite | Accept if local reconstruction yields positive profit gain | Recovers tasks missed by the initial allocation |
| Replacement move | Replace one scheduled task with an unscheduled task | Accept if the replacement improves affected-satellite profit | Frees capacity for a higher-value or more feasible task |
| Swap move | Exchange tasks across affected satellite schedules | Accept if the exchange improves combined local profit | Resolves conflicts that cannot be fixed by one-sided insertion |
| Bundle move | Move a small group of temporally related tasks | Accept if bundle reconstruction improves local profit | Preserves useful local task structure during reassignment |

Tables II-V define the optimizer-design space searched by the outer evolution. Table VI defines the scheduling repair library used when each decoded optimizer is evaluated. This separation isolates the contribution of the designed inner hybrid metaheuristic from the fixed multi-satellite repair mechanism.

## C. Semantic 6D Optimizer Encoding

Each candidate optimizer is represented by:

```math
\mathbf{g}=(g_0,g_1,g_2,g_3,g_4,g_5).
```

The gene meanings are listed in Table VII.

**TABLE VII: 6D OPTIMIZER CHROMOSOME.**

| Gene | Design decision | Candidate set |
|---|---|---|
| `g_0` | First parent algorithm | Parent-algorithm library in Table II |
| `g_1` | Second parent algorithm | Parent-algorithm library in Table II, different from `g_0` |
| `g_2` | Update policy for parent 1 | Update-policy library in Table III |
| `g_3` | Update policy for parent 2 | Update-policy library in Table III |
| `g_4` | Operation-order policy | Operation-order library in Table IV |
| `g_5` | Survivor-selection policy | Survivor-selection library in Table V |

After enforcing `g_0\ne g_1`, the valid search space contains:

```math
11\times 10\times 7\times 7\times 8\times 4 = 172{,}480
```

optimizer structures. If the parent-difference constraint is ignored before repair, the raw grid size is `188,496`.

The genes assemble reusable components into an executable hybrid optimizer; they do not tune all low-level parameters of each component. This representation keeps the search space compact while preserving a direct interpretation for the selected configuration.

Thus, each chromosome defines a complete hybrid optimizer. For example, `[9,2,0,0,0,0]` denotes L-SHADE and EDA as parent algorithms, full-population updates for both parents, sequential execution, and elitist best-N survival.

## D. Chromosome-to-Optimizer Decoding

The decoding function maps a 6D chromosome to a runnable HybCec optimizer. Let `\Phi(\mathbf{g})` denote the optimizer generated by chromosome `\mathbf{g}`.

The first two genes activate parent strategies:

```math
(g_0,g_1)\mapsto (\mathcal{A}_{g_0},\mathcal{A}_{g_1}),
```

where `\mathcal{A}_{g}` is one algorithm from the active parent library. The selected parents share the same random-key population and operate on the same decoded scheduling objective.

The update-policy genes define two masks:

```math
M_1=\mathcal{M}(g_2,X,F),\quad M_2=\mathcal{M}(g_3,X,F),
```

where `X` is the current population and `F` is the vector of individual fitness values. A full-population policy sets all mask entries to one. A top-subset policy selects high-fitness individuals. A mixed policy combines high-fitness and random individuals. A worst-repair policy targets the weakest individual.

The operation-order gene defines the parent execution schedule:

```math
\mathcal{O}_{g_4}:\left(\mathcal{A}_{g_0},\mathcal{A}_{g_1},M_1,M_2\right)\rightarrow X'.
```

For sequential execution, parent 1 updates the population before parent 2. For switching policies, the active parent changes according to iteration budget, stagnation, or diversity. For adaptive-credit routing, recent improvement per evaluation cost determines the parent route.

The survivor gene defines the replacement rule:

```math
X^{t+1}=\mathcal{S}_{g_5}(X^t,X',F^t,F').
```

This rule selects the next population from current individuals and generated candidates. It can preserve the best individuals, use tournament pressure, perform pairwise greedy replacement, or sample by rank-weighted probability.

The decoding step is the main methodological difference from a fixed hybrid optimizer. The inner search algorithm is generated from an evolvable design chromosome instead of being specified as one manually chosen operator sequence.

## E. Outer Evolutionary Search

The outer search evolves a population of optimizer chromosomes. Its objective is not the quality of a directly encoded task sequence, but the performance of the optimizer generated by each chromosome after running the full scheduling pipeline.

For a training scenario `s`, let `P(\mathbf{g},s)` be the mean profit obtained by evaluating optimizer `\Phi(\mathbf{g})` for `R` independent runs under the reduced design-stage budget. Let `B_s` be the profit of the fixed baseline configuration `{4,1,0,0,0,0}` and let `T_s` be the total profit of all tasks. The multi-scene design fitness is:

```math
\mathcal{F}(\mathbf{g})=
\sum_{s\in\mathcal{D}_{train}}
\frac{P(\mathbf{g},s)-B_s}{T_s}.
```

The denominator normalizes each scenario by total task profit, preventing large-profit scenarios from dominating the design objective only because of scale.

The outer evolutionary loop is shown in Algorithm 1.

```text
Algorithm 1: Evolutionary automatic design of 6D hybrid optimizers
Input: training scenarios D_train, component libraries A, U, O, S,
       population size N_d, generations G_d, repeat count R,
       crossover rate p_c, search budget ratio rho
Output: selected optimizer chromosome g*

1:  Initialize population P_0 of valid 6D chromosomes
2:  Evaluate every g in P_0 by F(g)
3:  g* <- best chromosome in P_0
4:  for t = 1 to G_d do
5:      Shuffle parent indices in P_{t-1}
6:      Generate offspring Q_t by one-point crossover with probability p_c
7:      Mutate genes when crossover is not applied
8:      Repair invalid chromosomes, including duplicate parent genes
9:      Evaluate every offspring g in Q_t by F(g)
10:     Merge P_{t-1} and Q_t
11:     Select the top N_d chromosomes by design fitness
12:     Update g* if a better chromosome is found
13: end for
14: return g*
```

The evaluations in lines 2 and 9 are expensive because each chromosome must be decoded into a complete optimizer and executed through the satellite scheduling pipeline. The design stage therefore uses a reduced inner budget, while final evidence is collected by the full-budget replay protocol.

## F. Full-Budget Replay Protocol

Search-stage fitness is used only to select a promising optimizer. It is not treated as the final experimental result. After the outer search returns `\mathbf{g}^*`, the selected optimizer is replayed by the single-configuration evaluation path:

```text
RunSingleHybridConfig(g*)
  -> EvaluationHyb
  -> TaskAllocationCoordinator
  -> configured HybCec optimizer Phi(g*)
  -> dynamic task reassignment
```

This replay path uses the full inner budget and five independent runs for each reported scenario. It separates automatic design from final confirmation, which is necessary because the design stage uses fewer evaluations and can be noisy.

In the current experiment, the selected configuration is:

```text
g* = [9,2,0,0,0,0].
```

The decoded optimizer uses L-SHADE and EDA as parents. Both parents update the full population. They are executed sequentially, and elitist best-N survival selects the next generation. This discovered structure is different from the manually fixed DE/rand/1 + PSO sequence in the 8D draft.

## G. Scheduling Execution Under a Designed Optimizer

Once `\Phi(\mathbf{g})` is instantiated, each satellite is optimized through the standard random-key scheduling bridge. For a satellite with `D` assigned tasks, HybCec maintains a population:

```math
X=\{\mathbf{x}^{(1)},\mathbf{x}^{(2)},\ldots,\mathbf{x}^{(N)}\},\quad
\mathbf{x}^{(q)}\in[-u,u]^D.
```

Each vector is decoded by sorting its keys. The sorted order gives a candidate task sequence. The decoder attempts to insert tasks into feasible visible time windows and computes the collected profit:

```math
f(\mathbf{x})=\sum_{\tau_i\in P_j} r_i,
```

where `P_j` is the feasible schedule constructed for satellite `s_j`.

After per-satellite schedules are generated, the coordinator collects unscheduled tasks and invokes dynamic reassignment. Unscheduled tasks are ranked by task-side priority, constraint tightness, and unscheduled pressure. Eligible target satellites are scored by lightweight task-satellite features, including candidate-window count, total window length, earliest-start preference, deterministic task-satellite key terms, and feedback from previous attempts. Only the top-k target satellites are retained for expensive move evaluation. The top-k values are experiment settings rather than 6D genes and are reported in Table IX.

The reassignment layer then applies standard migration, replacement move, swap move, and bundle move. Each move is evaluated by local profit difference over affected satellites and is accepted only when the reconstructed schedules produce positive profit gain.

# IV. Experimental Results

## A. Scenarios

All experiments use the same ten benchmark scenarios as the latest 8D RK-HMA draft. The scenarios cover small, medium, large, and superlarge instances, with task counts from 500 to 10,000 and satellite counts from 5 to 100. Regional instances concentrate tasks geographically and therefore create stronger competition for feasible time windows.

**TABLE VIII: EXPERIMENTAL SCENARIOS.**

| ID | Scale | `n` | `m` | Start time | End time | Distribution |
|---:|---|---:|---:|---|---|---|
| 1 | Small | 500 | 5 | 00:00:00 | 23:59:59 | Regional |
| 2 | Small | 500 | 5 | 00:00:00 | 23:59:59 | Global |
| 3 | Small | 1000 | 10 | 00:00:00 | 11:59:59 | Regional |
| 4 | Small | 1000 | 10 | 12:00:00 | 23:59:59 | Global |
| 5 | Medium | 1000 | 20 | 00:00:00 | 11:59:59 | Regional |
| 6 | Medium | 2000 | 20 | 12:00:00 | 23:59:59 | Global |
| 7 | Medium | 4000 | 40 | 00:00:00 | 05:59:59 | Regional |
| 8 | Large | 6000 | 60 | 12:00:00 | 17:59:59 | Global |
| 9 | Large | 8000 | 80 | 00:00:00 | 11:59:59 | Regional |
| 10 | Superlarge | 10000 | 100 | 06:00:00 | 11:59:59 | Regional |

The primary metric is profit rate:

```math
PR=\frac{F(P_S)}{F(P_A)}\times 100\%,
```

where `F(P_S)` is the profit of scheduled tasks and `F(P_A)` is the total profit of all tasks.

## B. Parameter Settings

Table IX reports the parameters used in the current 6D experiment. The outer-search parameters define the automatic-design stage. The replay parameters define the final verification stage for the selected configuration. Low-level runtime settings, including insertion mode and reassignment top-k values, are kept outside the 6D chromosome.

**TABLE IX: PARAMETER SETTINGS.**

| Category | Parameter | Value |
|---|---|---|
| Outer search | Active parent algorithms | 11 |
| Outer search | Update policies | 7 |
| Outer search | Operation-order policies | 8 |
| Outer search | Survivor policies | 4 |
| Outer search | Training scenarios | ID1, ID3, ID5, ID7 |
| Outer search | Population size | 35 |
| Outer search | Generations | 20 |
| Outer search | Repeats per search evaluation | 3 |
| Outer search | Search budget ratio | 60% of default inner budget |
| Final replay | Selected 6D configuration | `[9,2,0,0,0,0]` |
| Final replay | Repeats per scenario | 5 |
| Inner HybCec | Random-key interval | `[-u,u]` |
| Inner HybCec | Default insertion mode | Greedy insertion |
| Dynamic reassignment | Maximum reassignment iterations | 25 |
| Dynamic reassignment | Ordinary target-satellite top-k | 2 |
| Dynamic reassignment | Prioritized target-satellite top-k | 4 |
| Dynamic reassignment | Bundle size cap | 3 |
| Dynamic reassignment | Bundle time proximity threshold | 120 |

## C. Comparison with External Baselines

Table X compares the selected 6D configuration with R-ALNS, A-ALNS, and DRL-PASA values reported in the latest 8D draft. The 6D average and best values are computed from five full-budget replay runs.

**TABLE X: PROFIT RATE COMPARISON WITH EXTERNAL BASELINES.**

| ID | Distribution | `n,m` | R-ALNS | A-ALNS | DRL-PASA | 6D AutoHyb Avg | 6D AutoHyb Best |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Regional | 500,5 | 99.05% | 98.95% | 99.60% | 99.55% | **99.64%** |
| 2 | Global | 500,5 | 99.75% | **99.89%** | **99.89%** | **99.89%** | **99.89%** |
| 3 | Regional | 1000,10 | 39.60% | 40.20% | 44.35% | **47.78%** | **48.05%** |
| 4 | Global | 1000,10 | 92.57% | 92.51% | **92.59%** | **92.59%** | **92.59%** |
| 5 | Regional | 1000,20 | 56.31% | 70.21% | 76.35% | **78.59%** | **78.77%** |
| 6 | Global | 2000,20 | 98.27% | 98.37% | 98.40% | **98.44%** | **98.44%** |
| 7 | Regional | 4000,40 | 57.54% | 62.44% | 62.58% | **67.06%** | **67.22%** |
| 8 | Global | 6000,60 | 99.93% | 99.96% | 99.98% | **100.00%** | **100.00%** |
| 9 | Regional | 8000,80 | 27.12% | 34.26% | 37.18% | **51.45%** | **51.57%** |
| 10 | Regional | 10000,100 | 20.38% | 29.25% | 33.95% | **34.43%** | **34.48%** |

By five-run average, the 6D automatically designed configuration is best or tied-best on 9 of the 10 scenarios. The only exception is ID1, where the 6D average is 99.55% and the DRL-PASA value cited in the 8D draft is 99.60%. The best 6D replay on ID1 reaches 99.64%, so the selected configuration can exceed the cited value, although its average result remains slightly lower.

Across all ten scenarios, the 6D average profit rate is 7.93 percentage points higher than R-ALNS, 4.37 percentage points higher than A-ALNS, and 2.49 percentage points higher than DRL-PASA. These are table-level comparisons against reported baseline values, not paired statistical tests under a unified rerun protocol.

## D. Comparison with the Latest 8D Draft Result

The most direct comparison is against the latest 8D RK-HMA draft. Both methods use the same scenario set, random-key scheduling bridge, and dynamic reassignment layer. The comparison therefore isolates the inner optimizer design: the 8D draft uses a manually fixed Hybrid configuration, whereas the 6D version uses the automatically searched semantic configuration.

**TABLE XI: 6D AUTOHYB VERSUS LATEST 8D HYBRID RESULTS.**

| ID | `n,m` | 8D Hybrid Max | 8D Hybrid Ave | 8D Hybrid Min | 6D Max | 6D Ave | 6D Min | Ave Gain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 500,5 | 99.60% | 99.40% | 99.09% | **99.64%** | **99.55%** | **99.45%** | +0.15 |
| 2 | 500,5 | 99.89% | 99.89% | 99.89% | 99.89% | 99.89% | 99.89% | +0.00 |
| 3 | 1000,10 | 47.41% | 47.09% | 46.60% | **48.05%** | **47.78%** | **47.51%** | +0.69 |
| 4 | 1000,10 | 92.59% | 92.59% | 92.59% | 92.59% | 92.59% | 92.59% | +0.00 |
| 5 | 1000,20 | 78.27% | 78.04% | 77.85% | **78.77%** | **78.59%** | **78.45%** | +0.55 |
| 6 | 2000,20 | 98.44% | 98.44% | 98.44% | 98.44% | 98.44% | 98.44% | +0.00 |
| 7 | 4000,40 | 64.27% | 64.05% | 63.73% | **67.22%** | **67.06%** | **66.85%** | +3.01 |
| 8 | 6000,60 | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% | +0.00 |
| 9 | 8000,80 | 51.34% | 51.17% | 51.04% | **51.57%** | **51.45%** | **51.35%** | +0.28 |
| 10 | 10000,100 | 34.15% | 34.08% | 33.96% | **34.48%** | **34.43%** | **34.37%** | +0.35 |

The 6D configuration improves every non-saturated instance: ID1, ID3, ID5, ID7, ID9, and ID10. It ties the four saturated or near-saturated global instances: ID2, ID4, ID6, and ID8. The largest gain occurs on ID7, where the average profit rate increases from 64.05% to 67.06%. ID7 is a regional instance with 4000 tasks and 40 satellites, so the largest gain occurs in a conflict-heavy medium-scale setting rather than only in a small case.

The average gain over the 8D Hybrid average is 0.50 percentage points across all ten instances and 0.84 percentage points across the six non-saturated instances. This supports the claim that automatic hybrid-configuration design is useful beyond manually fixing DE/rand/1 + PSO.

## E. Search-Stage Evidence

The multi-scene search selected `[9,2,0,0,0,0]`. Table XII reports the four training scenarios used for the search-stage re-evaluation. The selected configuration improves ID3, ID5, and ID7 under this summary and is slightly below the baseline on ID1:

**TABLE XII: SEARCH-STAGE 100% BUDGET RE-EVALUATION OF THE SELECTED CONFIGURATION.**

| Scenario | Profit | Profit rate | Baseline rate | Delta |
|---|---:|---:|---:|---:|
| 500-5-0-0-24 | 2733.67 | 99.37% | 99.40% | -0.03 |
| 1000-10-0-0-12 | 2661.00 | 47.77% | 47.09% | +0.68 |
| 1000-20-0-0-12 | 4406.00 | 78.59% | 78.04% | +0.55 |
| 4000-40-0-0-6 | 14398.67 | 65.90% | 64.05% | +1.85 |

The final five-run replay in Table XI is stronger than this search-stage summary on ID1 and ID7. This difference is consistent with the role of the search stage: it uses fewer repeated runs and is intended to select candidates, whereas Table XI reports the final evidence.

## F. Runtime Note

This paper focuses on solution quality. Runtime is excluded from the dominance claim because the runtime comparison mixes different implementations and because the 6D replay was run in a different project state from the 8D draft table. The final replay logs nevertheless indicate that the selected 6D configuration remains practical for the tested scale range: its average replay time ranges from 1.47 seconds on ID4 to 183.27 seconds on ID10. A strict runtime claim requires rerunning all compared methods under one implementation and hardware protocol.

# V. Discussion

The results indicate that the manually selected DE/rand/1 + PSO hybrid is not the strongest tested structure in the current component library. The selected configuration uses L-SHADE and EDA. This suggests that adaptive differential search and distribution-based sampling are a useful combination under the current random-key decoding and survivor-selection rules.

The gain is concentrated on non-saturated regional instances. This pattern is consistent with the role of dynamic reassignment and hybrid sequencing. Global-distribution instances already have high feasible coverage, so all strong methods approach saturation. Regional instances contain stronger contention among tasks and satellites, leaving more room for reassignment and sequence refinement to improve collected profit.

The 6D representation is also easier to interpret than a broad low-level hyperparameter grid. Each gene corresponds to a design decision: which parent algorithms are used, which individuals are updated, when parent algorithms run, and how survivor selection is performed. This structure makes the selected configuration suitable for analysis and for future transfer studies.

The current evidence has two limits. First, the selected 6D configuration was replayed on ten scenarios, but the outer search was not repeated many times from independent random seeds. Second, the current draft compares against existing 8D results rather than rerunning every baseline under a single unified runtime protocol. These limits do not change the table-level profit-rate comparison against the latest 8D draft, but they should be resolved before making strong runtime or search-stability claims.

# VI. Conclusion

This paper proposed a 6D automatically designed hybrid metaheuristic framework for large-scale agile earth observation satellite scheduling. The method searches a compact semantic configuration space containing parent algorithms, update policies, operation order, and survivor selection. The selected configuration, `[9,2,0,0,0,0]`, combines L-SHADE and EDA with full-population updates, sequential execution, and elitist survival.

Compared with the latest 8D RK-HMA draft results, the selected 6D configuration improves all six non-saturated instances and matches all four saturated global instances in profit rate. It improves average profit rate by 0.50 percentage points across all ten scenarios and by 0.84 percentage points on the non-saturated subset. These results support automatic semantic hybrid-configuration design as a useful alternative to manually fixing the hybrid optimizer.

Future work should repeat the outer 6D search with independent seeds, add a unified runtime protocol, and analyze which 6D genes are most responsible for the observed gains. Another direction is to add a racing or surrogate-assisted search stage so that larger configuration libraries can be explored without increasing evaluation cost.

# References

[1] X. Wang, G. Wu, L. Xing, and W. Pedrycz, "Agile earth observation satellite scheduling over 20 years: Formulations, methods, and future directions," *IEEE Systems Journal*, vol. 15, no. 3, pp. 3881-3892, 2020.

[2] X. Chen, G. Reinelt, G. Dai, and A. Spitz, "A mixed integer linear programming model for multi-satellite scheduling," *European Journal of Operational Research*, vol. 275, no. 2, pp. 694-707, 2019.

[3] Y. Du, T. Wang, B. Xin, L. Wang, Y. Chen, and L. Xing, "A data-driven parallel scheduling approach for multiple agile earth observation satellites," *IEEE Transactions on Evolutionary Computation*, vol. 24, no. 4, pp. 679-693, 2020.

[4] J. Wu, Y. Du, F. Yao, M. Gong, J. Sun, Y. Zhao, and L. Xing, "A deep reinforcement learning-based parallel adaptive search algorithm for solving large-scale agile earth observation satellites tasks scheduling problem," *IEEE Transactions on Geoscience and Remote Sensing*, 2024.

[5] G. Peng, G. Song, L. Xing, A. Gunawan, and P. Vansteenwegen, "An exact algorithm for agile earth observation satellite scheduling with time-dependent profits," *Computers & Operations Research*, vol. 120, p. 104946, 2020.

[6] G. Peng, G. Song, Y. He, J. Yu, S. Xiang, L. Xing, and P. Vansteenwegen, "Solving the agile earth observation satellite scheduling problem with time-dependent transition times," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 52, no. 3, pp. 1614-1625, 2020.

[7] X. Liu, G. Laporte, Y. Chen, and R. He, "An adaptive large neighborhood search metaheuristic for agile satellite scheduling with time-dependent transition time," *Computers & Operations Research*, vol. 86, pp. 41-53, 2017.

[8] L. He, X. Liu, G. Laporte, Y. Chen, and Y. Chen, "An improved adaptive large neighborhood search algorithm for multiple agile satellites scheduling," *Computers & Operations Research*, vol. 100, pp. 12-25, 2018.

[9] J. Li, J. Zhu, D. Xu, J. Wang, Z. Li, and K. Zhang, "Earth observation satellite scheduling with interval-varying profits," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 5, pp. 7185-7200, 2024.

[10] F. Yao, Y. Chen, L. Wang, Z. Chang, P.-Q. Huang, and Y. Wang, "A bilevel evolutionary algorithm for large-scale multiobjective task scheduling in multiagile earth observation satellite systems," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 54, no. 6, pp. 3512-3524, 2024.

[11] J. Qin, X. Bai, G. Du, J. Liu, N. Peng, and M. Xu, "Multisatellite scheduling for moving targets using the enhanced hybrid genetic simulated annealing algorithm and observation strip selection," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 5, pp. 5773-5800, 2024.

[12] H. Wang, W. Huang, S. Magnusson, T. Lindgren, R. Wang, and Y. Song, "A strategy fusion-based multi-objective optimization approach for agile earth observation satellite scheduling problem," *IEEE Transactions on Geoscience and Remote Sensing*, 2024.

[13] Y. He, L. Xing, Y. Chen, W. Pedrycz, L. Wang, and G. Wu, "A generic markov decision process model and reinforcement learning method for scheduling agile earth observation satellites," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 52, no. 3, pp. 1463-1474, 2020.

[14] M. Chen, Y. Du, K. Tang, L. Xing, Y. Chen, and Y. Chen, "Learning to construct a solution for the agile satellite scheduling problem with time-dependent transition times," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, 2024.

[15] Y. Song, L. Wei, Q. Yang, J. Wu, L. Xing, and Y. Chen, "RL-GA: A reinforcement learning-based genetic algorithm for electromagnetic detection satellite scheduling problem," *Swarm and Evolutionary Computation*, vol. 77, p. 101236, 2023.

[16] C. Blum, J. Puchinger, G. R. Raidl, and A. Roli, "Hybrid metaheuristics in combinatorial optimization: A survey," *Applied Soft Computing*, vol. 11, no. 6, pp. 4135-4151, 2011.

[17] J. Fan, Y. Li, J. Xie, C. Zhang, W. Shen, and L. Gao, "A hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling problem," *IEEE Transactions on Cybernetics*, vol. 53, no. 3, pp. 1752-1764, 2023.

[18] Z. Shu, A. Song, G. Wu, and W. Pedrycz, "Variable reduction strategy integrated variable neighborhood search and NSGA-II hybrid algorithm for emergency material scheduling," *Complex System Modeling and Simulation*, vol. 3, no. 2, pp. 83-101, 2023.

[19] Y. Rocha, G. O. Chagas, L. C. Coelho, and A. Subramanian, "The integrated agile earth observation satellite scheduling problem," *Computers & Operations Research*, vol. 184, p. 107212, 2025.

[20] X. Wang, G. Song, R. Leus, and C. Han, "Robust earth observation satellite scheduling with uncertainty of cloud coverage," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 56, no. 3, pp. 2450-2461, 2019.
