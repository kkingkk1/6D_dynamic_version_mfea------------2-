# Automatic Design of Collaboration-Based Hybrid Metaheuristics for Large-Scale Agile Earth Observation Satellite Scheduling

**Abstract**--Large-scale agile earth observation satellite scheduling has drawn growing attention as satellite constellations expand and observation demand rises. The problem couples task selection, satellite assignment, visible-window placement, and attitude-constrained sequencing, and is NP-hard at the scale of practical missions. In conventional collaboration-based hybrid metaheuristic design, the inner collaboration structure is typically fixed in advance. RK-HMA is one such artificially designed hybrid algorithm: its internal single-satellite optimizer combines DE/rand/1 and PSO, achieving good results. This paper recasts the design of this collaboration-based hybrid with two parent algorithms as an automatic structural-design problem within the same scheduling pipeline. A six-gene chromosome selects two parent algorithms, two operating levels (OL), one operating order (OO), and survivor selection. Over these component libraries, an evolutionary search on four regional training scenarios composes a hybrid optimizer. The retained configuration is evaluated on ten benchmark scenarios containing 500–10,000 tasks and 5–100 satellites covering both regional and global task distributions. It obtains the best or tied-best profit rate on all ten scenarios, with a maximum gap of 12.32 percentage points over the compared baselines. All methods remain near saturation on global-distribution scenarios, while Auto-Hybrid shows more substantial gains on the more challenging regional-distribution scenarios.

**Index Terms**--agile earth observation satellite scheduling, automated algorithm design, collaboration-based hybrid metaheuristic

# I. Introduction

Agile earth observation satellites (AEOS) with high attitude maneuverability have become a key platform for acquiring space-based information, supporting applications such as disaster monitoring, mapping, and reconnaissance [1]. Over the past two decades, the number of earth observation satellites in orbit has grown rapidly. Wang et al. [1] reported that AEOS scheduling has been actively studied since the early 2000s, driven by the deployment of increasingly agile platforms such as Pléiades, WorldView, and Jilin-1. Du et al. [3] noted that the growing number of satellites and observation requests has made large-scale multi-satellite scheduling a practical challenge. Efficient scheduling is thus needed to manage large constellations and maximize fulfilled observation requests.

The large-scale agile earth observation satellite task scheduling problem (LS-AEOSTSP) is harder than the classic earth observation satellite task scheduling problem (EOSTSP). As illustrated in Fig. 1, unlike conventional EOS that can only observe targets directly below their ground track, AEOS can rotate along the roll, pitch, and yaw axes to steer their imaging payloads toward off-nadir targets. This three-axis maneuverability enlarges the set of visible time windows (VTWs) for each task, but introduces time-dependent attitude transition constraints between consecutive observations. As constellations scale to tens or hundreds of satellites, the joint decision space—task-satellite assignment, VTW selection, and start time determination—grows combinatorially, making exact methods intractable for practical instances [4], [5].

![Comparison of observation modes between non-agile EOS and AEOS](figures/agile_satellite_observation_modes.png)

**Fig. 1.** Comparison of observation modes between non-agile EOS and AEOS [6].

Prior work on agile satellite scheduling spans several methodological lines. Survey and exact-optimization studies clarify the main modeling variants and constraint structures: Wang et al. [1] reviewed two decades of AEOS scheduling formulations and methods, Chen et al. [2] built a mixed-integer linear programming model for multi-satellite scheduling, and Peng et al. [4], [5] developed exact formulations that exploit the time-dependent profit and transition-time structure of the problem. Because exact methods do not scale to large instances, metaheuristics have become the dominant practical approach.

Adaptive large neighborhood search (ALNS) and its variants are well studied. Liu et al. [6] designed problem-specific removal and insertion operators for time-dependent transition times, and He et al. [7] extended ALNS to multiple agile satellites with a dynamic task-allocation mechanism. Population-based evolutionary algorithms have also been applied: Yao et al. [9] proposed a bilevel evolutionary algorithm for large-scale multiobjective task scheduling, Qin et al. [10] combined simulated annealing with a genetic algorithm for multisatellite scheduling of moving targets, and Wang et al. [11] designed a strategy fusion-based multi-objective optimization approach. Related methods address further variants, including interval-varying profits [8] and the integrated agile scheduling problem [15]. However, most existing methods rely on a single algorithmic paradigm, limiting the balance between exploration and exploitation in the LS-AEOSTSP search space [1].

Hybrid metaheuristics, which combine the strengths of multiple search strategies within a unified framework, are effective for combinatorial optimization. Blum et al. [12] surveyed hybrid metaheuristic paradigms and reported numerous successful applications where hybridization improved solution quality. In the domain of scheduling, Fan et al. [13] proposed a hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling, and Shu et al. [14] integrated variable neighborhood search with NSGA-II for emergency material scheduling. For LS-AEOSTSP, our previous work proposed RK-HMA [21], which connects continuous optimizers with discrete task sequences through random-key encoding, applies DE/rand/1 and PSO to a shared population, and uses dynamic task reassignment to coordinate satellites. RK-HMA shows that hybridization is effective for large-scale satellite scheduling. However, this manual design process has two main limitations: (i) the design cost is high—each structural decision requires expert knowledge, and changing any component requires re-design and re-validation with no guarantee that the resulting structure remains effective when the scenario changes in scale or task distribution; and (ii) the design space of collaboration-based hybrids is large—different parent algorithms, OL choices, OO choices, and survivor-selection policies can be combined in many ways, making it difficult for manual exploration to identify well-performing configurations.

The central question is therefore an automatic-design question: can the hybrid structure itself be composed for the scheduling pipeline? Algorithm configuration methods such as ParamILS, SMAC, and irace tune parameterized algorithms over training instances [16]-[18]. Hyper-heuristics search over heuristics or heuristic components instead of directly searching the solution space [19]. Automated algorithm design goes further by searching algorithm structures rather than only tuning parameters or choosing among fixed algorithms. Recent work on automated design of collaboration-based hybrid metaheuristics treats hybrid-optimizer design as a meta-optimization problem and uses a top-down template to generate collaboration-based hybrid algorithms [20].

This paper studies that question for LS-AEOSTSP by making the inner single-satellite optimizer a searchable structural layer. A six-gene chromosome encodes the collaboration structure—parent algorithms, OL, OO, and survivor selection—while the random-key scheduling bridge and cross-satellite reassignment layer remain fixed and provide a common evaluation environment. Each candidate chromosome is decoded into an executable optimizer and evaluated through the coupled scheduling pipeline, a setting not addressed by prior automated-design work. The detailed encoding is introduced in Section III-C.

The main contributions are as follows.

1. We propose an automatic design framework for collaboration-based hybrid metaheuristics tailored to LS-AEOSTSP. The inner single-satellite optimizer is composed by search rather than fixed by manual design.

2. We formulate a six-gene semantic chromosome and its component libraries. The chromosome exposes the collaboration structure—parent algorithms, OL, OO, and survivor selection—as interpretable structural decisions that the search can recombine.

3. We evaluate the composed optimizer on ten benchmark scenarios containing 500–10,000 tasks and 5–100 satellites covering both regional and global task distributions. The retained configuration obtains the best or tied-best profit rate on all ten scenarios, with a maximum gap of 12.32 percentage points over the compared baselines. All methods remain near saturation on global-distribution scenarios, while Auto-Hybrid shows more substantial gains on the more challenging regional-distribution scenarios.

The remaining sections are organized as follows. Section II defines the scheduling problem. Section III describes the automatic hybrid-design framework. Section IV reports the experiments. Section V concludes the paper.

# II. Problem Description

## A. Problem Description

Given a set $T=\{t_1,\ldots,t_n\}$ of $n$ tasks and a set $AEOS=\{aeos_1,\ldots,aeos_m\}$ of $m$ agile earth observation satellites. Each task $t_i$ is associated with a geographic location (latitude and longitude), an imaging duration $l_i$, and a profit $p_i$, which are provided by the user. Each satellite $aeos_j$ is represented by its orbital parameters, including the semi-major axis, eccentricity, inclination, right ascension of the ascending node, argument of perigee, and true anomaly. Given the target location and satellite orbital parameters, the visible time windows (VTWs) of each target associated with its visible satellites are obtained through access calculation. Each VTW $w_{ijk}$ has a start time $st_{ijk}$, an end time $et_{ijk}$, and a length $d_{ijk}$. The roll, pitch, and yaw angles of the imaging payload at the corresponding observation times are also available. The notations used throughout this paper are summarized in Table I.

Due to the limited number of satellites compared with the number of tasks, it is difficult to execute all tasks. Therefore, the LS-AEOSTSP aims to determine the imaging times of a subset of tasks within their VTWs while maximizing the total observation profit, subject to the following assumptions.

1. Each task is a meta-task that can be directly executed by a satellite. Complex tasks such as area target coverage or moving target tracking are not considered, because they can be decomposed into meta-tasks through strip partitioning.
2. Power-capacity and storage-capacity constraints are not modeled. In normal operation, satellites charge through solar power and transmit data to ground stations or relay satellites to release onboard storage.
3. Each satellite is equipped with a single imaging payload and can execute at most one task at a time.
4. Once executed, a task cannot be aborted, and each task is executed at most once.

**TABLE I: NOTATION FOR LS-AEOSTSP.**

| Notation | Description |
|---|---|
| $T$ | Tasks set |
| $n$ | Number of tasks |
| $AEOS$ | Satellites set |
| $m$ | Number of satellites |
| $p_i$ | Profit of task $t_i$ |
| $l_i$ | Imaging duration of task $t_i$ |
| $\chi_{jt}$ | Rolling angle of $aeos_j$ at time $t$ |
| $\pi_{jt}$ | Pitching angle of $aeos_j$ at time $t$ |
| $\phi_{jt}$ | Yawing angle of $aeos_j$ at time $t$ |
| $w_{ijk}$ | $k$-th VTW for task $t_i$ on satellite $aeos_j$ |
| $W_{ij}$ | VTWs set for task $t_i$ on satellite $aeos_j$ |
| $|W_{ij}|$ | Number of VTWs for task $t_i$ on satellite $aeos_j$ |
| $st_{ijk}$ | Start time of $w_{ijk}$ |
| $et_{ijk}$ | End time of $w_{ijk}$ |
| $d_{ijk}$ | Length of $w_{ijk}$ |
| $c_i$ | Specified minimum imaging quality of task $t_i$ |

The decision variables are $x_{ijk}$ and $u_{ijk}$. The binary variable $x_{ijk}$ equals one if task $t_i$ is executed in VTW $w_{ijk}$ and zero otherwise. The continuous variable $u_{ijk}$ denotes the start time of task $t_i$ when $x_{ijk}=1$. The sequencing variable $\rho_{ijk,i^*jk^*}$ equals one if task $t_i$ is the predecessor of task $t_{i^*}$ on satellite $aeos_j$ and zero otherwise.

The mathematical formulation of the LS-AEOSTSP is given as follows.

Objective function:

$$
\max \sum_{i=1}^{n}\sum_{j=1}^{m}\sum_{k=1}^{|W_{ij}|} x_{ijk}p_i. \tag{1}
$$

The objective function maximizes the total observation profit of all scheduled tasks.

Constraints:

$$
\sum_{j=1}^{m}\sum_{k=1}^{|W_{ij}|} x_{ijk} \le 1,\quad \forall t_i\in T. \tag{2}
$$

$$
st_{ijk} \le u_{ijk} < u_{ijk}+l_i \le et_{ijk},\quad \text{if }x_{ijk}=1. \tag{3}
$$

$$
\rho_{ijk,i^*jk^*}=
\begin{cases}
1, & \text{if }t_i\text{ is the predecessor of }t_{i^*},\\
0, & \text{otherwise,}
\end{cases}
\quad \text{if }x_{ijk}=x_{i^*jk^*}=1. \tag{4}
$$

$$
u_{ijk}+l_i+\Delta t(t_i,t_{i^*})\le u_{i^*jk^*},\quad \text{if }\rho_{ijk,i^*jk^*}=1. \tag{5}
$$

The transition time is a piecewise linear function of the total angular displacement:

$$
\Delta t(t_i,t_{i^*})
=
\begin{cases}
11.66, & \Delta g(t_i,t_{i^*})\leq 10^\circ,\\
a_1+\dfrac{\Delta g(t_i,t_{i^*})}{v_1}, & 10^\circ<\Delta g(t_i,t_{i^*})\leq 30^\circ,\\
a_2+\dfrac{\Delta g(t_i,t_{i^*})}{v_2}, & 30^\circ<\Delta g(t_i,t_{i^*})\leq 60^\circ,\\
a_3+\dfrac{\Delta g(t_i,t_{i^*})}{v_3}, & 60^\circ<\Delta g(t_i,t_{i^*})\leq 90^\circ,\\
a_4+\dfrac{\Delta g(t_i,t_{i^*})}{v_4}, & \Delta g(t_i,t_{i^*})>90^\circ.
\end{cases} \tag{6}
$$

The total change in satellite look angles is computed from the attitude differences between the two observations:

$$
\Delta g(t_i,t_{i^*})
=|\chi_{j,u_{ijk}}-\chi_{j,u_{i^*jk^*}}|
+|\pi_{j,u_{ijk}}-\pi_{j,u_{i^*jk^*}}|
+|\phi_{j,u_{ijk}}-\phi_{j,u_{i^*jk^*}}|,\quad \text{if }\rho_{ijk,i^*jk^*}=1. \tag{7}
$$

$$
q_i\ge c_i,\quad \forall t_i\in T. \tag{8}
$$

When a scheduled task is executed in $w_{ijk}$, its imaging quality is computed by the distance between the observation start time and the midpoint of the selected VTW:

$$
q_i=10-9\cdot
\frac{|2u_{ijk}+l_i-2w_{ijk}^{*}|}{d_{ijk}-l_i},
\quad \text{if }x_{ijk}=1, \tag{9}
$$

$$
w_{ijk}^{*}=\frac{st_{ijk}+et_{ijk}}{2},\quad \text{if }x_{ijk}=1. \tag{10}
$$

Constraint (2) ensures that each task is executed at most once. Constraint (3) ensures that the execution interval of a scheduled task is contained in its selected VTW. Constraint (5) requires the time interval between two successive tasks on the same satellite to be no shorter than the transition time $\Delta t(t_i,t_{i^*})$. Following [5], the transition time is calculated using the segmented function in Eq. (6). The quantity $\Delta g(t_i,t_{i^*})$ represents the total change in the satellite look angles between the two tasks, as defined in Eq. (7). The angular velocities and constant terms are set to $v_1=1.5^\circ/\text{s}$, $a_1=5$, $v_2=2^\circ/\text{s}$, $a_2=10$, $v_3=2.5^\circ/\text{s}$, $a_3=16$, $v_4=3^\circ/\text{s}$, and $a_4=22$. Constraint (8) requires the imaging quality $q_i$ to be no lower than the specified minimum quality $c_i$. Equation (9) calculates $q_i$ from the task start time, and Eq. (10) defines the midpoint of the selected VTW.

# III. Automatic Hybrid-Design Framework

## A. Design Principle

The proposed framework follows the top-down design idea of AutoHyb [20], where designing a collaboration-based hybrid optimizer is formulated as a meta-optimization problem. AutoHyb treats the optimizer structure as a searchable design object: each candidate design scheme specifies which parent algorithms to combine (e.g., DE, PSO, EDA) and how to hybridize them through a set of hybridization factors: the operating level (OL), which determines which subpopulation of the shared population each parent algorithm modifies; the operating order (OO), which determines the information dependency between the two parent algorithms; and survivor selection, which determines how newly generated and existing individuals compete for the next generation. AutoHyb was developed and validated on general numerical and combinatorial benchmarks, where each candidate optimizer can be evaluated with modest computational cost. We adapt this idea to the coupled, discrete LS-AEOSTSP, where every candidate solution must be evaluated through a full scheduling process that assigns tasks to satellites, selects visible time windows, determines observation timing, and computes attitude-dependent transition times—making each fitness evaluation far more expensive than on numerical benchmarks.

This paper instantiates that template for LS-AEOSTSP. The target scheduling pipeline is inherited from RK-HMA [21], which has two layers: an outer multi-satellite layer that handles task-to-satellite allocation and cross-satellite reassignment of unscheduled tasks, and an inner single-satellite optimizer that evolves the task sequence for each satellite independently using a random-key encoding—continuous keys define task priorities, and a greedy insertion decoder maps each random-key vector to a feasible schedule by sorting tasks and inserting them into visible time windows while respecting attitude-transition constraints.

We fix the outer layer and the decoder unchanged from RK-HMA; the automatic-design layer searches only the collaboration structure of the inner single-satellite optimizer—parent algorithms, their OL choices, the OO choice, and survivor selection. We further restrict this design object to pairwise collaboration between exactly two parent algorithms. This restriction serves three purposes: (1) it keeps the design space tractable, and adding a third parent algorithm would expand this by another order of magnitude; (2) it ensures a well-defined collaboration structure—two parent algorithms form a single information-flow edge with explicit OO semantics and information dependency, whereas three or more parent algorithms would introduce multiple edges with potential cyclic dependencies or complex scheduling; (3) it supports a matched comparison with the manually designed RK-HMA baseline, which is itself a hybrid with two parent algorithms. This scoping keeps each candidate optimizer cheap enough to evaluate through the expensive scheduling pipeline.

In our design, each offspring is generated by either crossover or mutation. The two operators are mutually exclusive alternatives with complementary probabilities p_c and p_m = 1 - p_c. This exclusive choice ensures that each offspring can be unambiguously attributed to a single operator, preserving a clean interpretation of their individual effects. The design stage searches over a training subset with a reduced inner budget. Chromosomes are ranked by a multi-scenario fitness that normalizes scheduling profit across scenarios, as defined in Section III-E.

As shown in Fig. 2, the resulting workflow has five levels:

1. Component libraries define the admissible parent algorithms and hybridization factors.
2. A semantic chromosome selects one component for each algorithmic role.
3. A decoder maps the chromosome to an executable single-satellite optimizer.
4. The generated optimizer is embedded in the fixed multi-satellite scheduling pipeline.
5. An outer evolutionary search ranks chromosomes by their measured scheduling profit.

![Framework of the proposed Auto-Hybrid](figures/automatic_hybrid_design_flow.png)

**Fig. 2.** Framework of the proposed Auto-Hybrid.

## B. Component Libraries for Automatic Design

The four component libraries instantiate the searchable design space.
Tables II-V list the admissible realization forms for parent algorithms,
OL, OO, and survivor selection. In this section, an inner individual
denotes one random-key solution, whereas a design candidate denotes
one six-gene chromosome. Only these structural choices are encoded;
the numerical parameters of the library algorithms are held fixed
during the design comparison. This separation keeps the search
focused on collaboration structure.

The parent-algorithm library collects established metaheuristics that can operate on the shared random-key representation, chosen to span complementary search behaviors. It includes population-based evolutionary search through a genetic algorithm (GA) [22]; swarm intelligence through particle swarm optimization (PSO) [22]; probabilistic model building through an estimation-of-distribution algorithm (EDA) [22] and a continuous ant colony optimization (ACO) [23]; differential evolution in three mutation forms, DE/rand/1, DE/best/1, and DE/current-to-rand/1 [24]; a bee-colony algorithm (ABC) [22]; trajectory-based simulated annealing (SA) [22]; the success-history adaptive DE with linear population reduction (L-SHADE) [25]; and an adaptive large neighborhood search (ALNS) [6], [7] drawn from the scheduling literature. This mix lets the design stage combine exploratory, exploitative, model-based, and neighborhood-based dynamics. Table II summarizes the eleven parent algorithms.

**TABLE II: PARENT-ALGORITHM LIBRARY.**

| ID | Parent algorithm | Brief description |
|---:|---|---|
| 0 | GA | Evolutionary algorithm that generates offspring through selection, crossover, and mutation. |
| 1 | PSO | Swarm-intelligence algorithm that updates particles using personal and global best experience. |
| 2 | EDA | Probabilistic model-based algorithm that estimates promising distributions from selected solutions. |
| 3 | ACO | Pheromone-inspired constructive search that samples candidates according to learned desirability. |
| 4 | DE/rand/1 | Differential evolution variant that mutates a random base vector with one differential vector. |
| 5 | DE/best/1 | Differential evolution variant that mutates the current best vector with one differential vector. |
| 6 | DE/current-to-rand/1 | Differential evolution variant that moves the current vector toward a random differential direction. |
| 7 | ABC | Bee-colony algorithm that alternates employed-bee, onlooker-bee, and scout-bee search phases. |
| 8 | SA | Trajectory-based local search that uses temperature-controlled acceptance of worsening moves. |
| 9 | L-SHADE | Success-history adaptive differential evolution with external archive and linear population-size reduction. |
| 10 | ALNS | Neighborhood-search framework that alternates destroy and repair operators under adaptive selection. |

**TABLE III: OPERATING-LEVEL LIBRARY.**

The operating level determines which inner random-key solutions of the shared population each parent algorithm is allowed to modify. The seven realization forms below span population-, subpopulation-, and individual-level updates. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table VIII.

| ID | Operating level | Realization form |
|---:|---|---|
| 0 | Full population | The parent algorithm works on all inner random-key solutions in the current population. |
| 1 | Top-subset selection | The parent algorithm works on a fixed high-fitness subpopulation of inner solutions with ratio $r_{\text{sub}}$. |
| 2 | Mixed-subset selection | The parent algorithm works on a subpopulation mixing the top fraction $r_{\text{mix}}$ with random inner solutions. |
| 3 | Random-decay selection | The parent algorithm works on a random subpopulation of inner solutions whose ratio decays from $r_{\text{dec}}$ over iterations. |
| 4 | Above-mean selection | The parent algorithm works on inner solutions whose fitness is above the population mean. |
| 5 | Local-search focus | The parent algorithm focuses on the historical best inner solution. |
| 6 | Worst-repair focus | The parent algorithm focuses on the current worst inner solution. |

**TABLE IV: OPERATING-ORDER (OO) LIBRARY.**

The operating-order library specifies when the two parent algorithms are invoked and thereby determines their information dependency. Its realization forms comprise seven sequential options and one parallel option. The IDs retain their fixed encoding assignments. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table VIII.

| ID | Operating order (OO) | OO type | Corresponding realization form |
|---:|---|---|---|
| 0 | Sequential | Sequential | Inner parent algorithm 1 is invoked before inner parent algorithm 2 in each enabled iteration. |
| 1 | Periodic switching | Sequential | The active inner parent algorithm switches every $T_{\text{sw}}$ iterations. |
| 2 | Stage-based switching | Sequential | Parent algorithm 1 is enabled through the stage boundary $\tau_{\text{stage}}$, and parent algorithm 2 is enabled afterward. |
| 3 | Best-no-improvement switching | Sequential | The active parent algorithm switches after $T_{\text{best}}$ consecutive inner iterations without improvement in the historical global best. |
| 4 | Process-no-improvement switching | Sequential | The active parent algorithm switches after $T_{\text{proc}}$ consecutive inner iterations without improvement in either the global best or the mean population fitness. |
| 5 | Diversity-based switching | Sequential | Inner parent-algorithm routing depends on the population diversity state, checked every $T_{\text{div}}$ iterations against threshold $\theta_{\text{div}}$. |
| 7 | Adaptive-credit routing | Sequential | At each inner iteration, parent algorithm 1 is selected with probability $p_1$ derived from recent improvement per evaluation cost, and parent algorithm 2 is selected with probability $p_2=1-p_1$. |
| 6 | Parallel | Parallel | The two inner parent algorithms generate candidates separately and the candidates are merged. |

**TABLE V: SURVIVOR-SELECTION LIBRARY.**

The survivor-selection library determines how current and newly generated inner solutions compete to form the next population. Its four realization forms span deterministic truncation, pairwise-greedy replacement, stochastic tournament selection, and rank-weighted sampling, allowing the design search to vary the selection pressure applied to candidate solutions.

| ID | Survivor policy | Corresponding realization form |
|---:|---|---|
| 0 | Elitist truncation | Truncation selection: current and offspring inner solutions are merged and the best $N$ survive. |
| 1 | Tournament selection | Tournament selection: for each survivor slot, $k_{\mathrm{tour}}$ candidates are sampled from the merged set, and the fittest candidate is retained. |
| 2 | Pairwise greedy | One-to-one comparison: each offspring inner solution competes with its paired current solution. |
| 3 | Rank-weighted sampling | Rank-based sampling: candidates are sampled from the merged set with probabilities that decrease linearly with fitness rank. |

Together, Tables II-V define the component libraries that span the searchable optimizer-design space. Scheduling execution details are described with the evaluation protocol.

## C. Semantic Structural Optimizer Encoding

The component libraries are assembled into a searchable representation through a chromosome:
$$
\mathbf{h}=(h_0,h_1,h_2,h_3,h_4,h_5),
$$
as illustrated in Fig. 3.

<p align="center">
  <img src="figures/semantic_hybrid_scheme_encoding.png" alt="Semantic hybrid-scheme encoding" width="65%">
</p>
**Fig. 3.** Six-gene semantic hybrid-scheme encoding.

Equivalently, the six positions are denoted by $\{\text{parent}_1,\text{parent}_2,\text{OL}_1,\text{OL}_2,\text{OO},\text{survivor}\}$. Together, these positions encode one structural collaboration scheme rather than a numerical parameter vector. This semantic layout makes the composed optimizer interpretable after search: each gene names a distinct algorithmic role.

After enforcing $h_0\ne h_1$, the valid search space is:
$$
11\times 10\times 7\times 7\times 8\times 4 = 172{,}480
$$

This yields 172,480 candidate optimizer structures, which indicates the scale of the structural design space. Exhaustively evaluating all of them is impractical, because each candidate must be decoded into an optimizer and run through the scheduling pipeline. This motivates the evolutionary configuration-search procedure in Section III-E.

## D. Chromosome-to-Optimizer Decoding

The decoding function maps one optimizer chromosome to a runnable single-satellite optimizer. Let $\Phi(\mathbf{h})$ denote the optimizer generated by chromosome $\mathbf{h}$. The generated optimizer is a shared-population hybrid: it maintains one random-key population and one decoded scheduling objective. Both parent algorithms update selected individuals from this population and are evaluated using the same fitness vector $F^t$. This shared-population design distinguishes the method from running two independent optimizers and combining their outputs: the OL choices, the OO choice, and survivor selection specify how the two parent algorithms collaborate through one evolving population. The chromosome changes how these inner search operators are assembled, while the outer scheduling bridge and reassignment layer remain fixed.

At iteration $t$, the first two genes activate the two parent algorithms:

$$
(h_0,h_1)\mapsto (\mathcal{A}_{h_0},\mathcal{A}_{h_1}),
$$

where $\mathcal{A}_{h_i}$ is one algorithm from the active parent-algorithm library. The two parent calls therefore share the population state and objective evaluation described above.

The OL genes then define two individual masks:

$$
M_1=\mathcal{M}(h_2,X^t,F^t),\quad M_2=\mathcal{M}(h_3,X^t,F^t),
$$

where $X^t$ is the current random-key population and $F^t$ is the corresponding fitness vector. The masks define which inner random-key solutions each parent algorithm is allowed to modify, while the OL semantics are listed in Table III.

The OO gene schedules the two parent-algorithm calls and produces a candidate population:

$$
\mathcal{O}_{h_4}:\left(\mathcal{A}_{h_0},\mathcal{A}_{h_1},M_1,M_2\right)\rightarrow X'.
$$

The OO semantics are listed in Table IV. Each candidate key in $X'$ is decoded into a task sequence and scored by the scheduling-profit objective, giving the candidate fitness vector $F'$.

The survivor gene then builds the next population:

$$
X^{t+1}=\mathcal{S}_{h_5}(X^t,X',F^t,F').
$$

The survivor rule is selected from Table V. Applied in order, parent-algorithm activation, the two OL masks, the OO schedule, and survivor selection form one complete single-satellite optimizer iteration.

The decoding step turns optimizer construction into part of the experiment. The inner search algorithm is generated from an evolvable semantic chromosome and evaluated inside the same scheduling pipeline.

## E. Evolutionary Configuration-Search Procedure

The design procedure evolves a population of optimizer chromosomes. Fitness is assigned to the scheduling profit obtained by the inner optimizer generated from each chromosome. Each chromosome is evaluated by running the decoded optimizer on the training scenarios with multiple independent runs per scenario. The design fitness aggregates the normalized scheduling profit across all training scenarios, where normalization by each scenario's total task profit prevents large-profit scenarios from dominating chromosome selection only because of scale. Algorithm 1 denotes this fitness as `designScore` to distinguish it from the inner scheduling objective.

Algorithm 1 summarizes the design-search procedure.

```text
Algorithm 1: Evolutionary optimizer-design procedure
Input: training scenarios D_train, component libraries A, U, O, S,
       population size N_d, generations G_d, repeat count R,
       crossover probability p_c, mutation probability p_m=1-p_c,
       search budget ratio rho,
       full inner budget B_full(s) for each s in D_train
Output: composed optimizer chromosome h_star

1:  For each s, set B_design(s) <- max{1, round(rho B_full(s))}
2:  Initialize population P_0 of valid optimizer chromosomes
3:  Evaluate every h in P_0 by designScore(h; {B_design(s)})
4:  h_star <- best chromosome in P_0
5:  for t = 1 to G_d do
6:      Shuffle chromosome indices in P_{t-1}
7:      for each selected chromosome pair do
8:          with probability p_c, generate an offspring chromosome by one-point crossover;
9:          otherwise, mutate a random nonempty subset of the six genes
10:         repair duplicate parent-algorithm choices so that h_0 != h_1
11:         add the offspring chromosome to Q_t
12:     end for
13:     Evaluate every offspring chromosome h in Q_t by designScore(h; {B_design(s)})
14:     Merge P_{t-1} and Q_t
15:     Select the top N_d chromosomes by design fitness
16:     Update h_star if a better chromosome is found
17: end for
18: return h_star
```

![One-point crossover and six-gene mutation of the 6D optimizer chromosome](figures/mfea_6d_crossover_mutation.png)

**Fig. 4.** Crossover and mutation of the semantic optimizer chromosome.

The complete evaluation follows a three-stage protocol that balances search efficiency with final accuracy. First, Algorithm 1 is executed five times independently on the training scenarios, with each chromosome evaluated using $R_d$ runs under the reduced budget $B_{\mathrm{design}}(s)$. This stage explores the design space quickly with coarse evaluations. Second, the top five distinct configurations from the final populations of the five independent runs are re-evaluated with $R_s$ runs per training scenario under the same reduced budget, and the configuration with the highest macro mean across the training scenarios is selected. This screening stage uses more runs to reduce stochastic noise when comparing promising candidates. Third, the selected configuration is evaluated under the full budget $B_{\mathrm{full}}(s)$ on all evaluation scenarios with $R_f$ runs per scenario to measure its true scheduling performance.

## F. Scheduling Execution Under a Designed Optimizer

Once $\Phi(\mathbf{h})$ is instantiated, each satellite is optimized through the standard random-key scheduling bridge inherited from RK-HMA. For a satellite with $D$ assigned tasks, the single-satellite optimizer maintains a population of $N$ random-key vectors, each of dimension $D$:

$$
X=\{\mathbf{x}^{(1)},\mathbf{x}^{(2)},\ldots,\mathbf{x}^{(N)}\}.
$$

Each vector is decoded by sorting its keys, and the sorted order gives a candidate task sequence. The decoder then inserts tasks into feasible visible time windows and computes the collected profit:

$$
f(\mathbf{x})=\sum_{t_i\in P_j} p_i,
$$

where $P_j$ is the feasible schedule constructed for satellite $aeos_j$.

After per-satellite schedules are generated, the fixed multi-satellite layer applies the RK-HMA dynamic reassignment procedure [21] to reconsider unscheduled tasks. This layer is shared by all candidate chromosomes and is not part of the optimizer-design space.

# IV. Experimental Results

To evaluate the proposed automatic hybrid-design framework on the LS-AEOSTSP, the simulator introduced in [7] is used to generate multiple experimental scenarios. The framework and the generated optimizer are implemented in Java and run on a PC with Intel Core i7-14700kf CPU @ 3.40 GHz and 64-GB memory.

## A. Experimental Scenario And Training Scenario

Ten experimental scenarios are used for evaluation, following the benchmark scale and distribution settings used in RK-HMA [21]. They cover small-scale, medium-scale, large-scale, and superlarge-scale instances. The task count ranges from 500 to 10,000, and the satellite count ranges from 5 to 100. The distribution is categorized into regional and global distributions. In the regional setting, tasks are concentrated in the area $3^\circ\text{N}$-$53^\circ\text{N}$ and $74^\circ\text{E}$-$133^\circ\text{E}$, which creates stronger competition for feasible time windows. The imaging duration of each task is a random integer between 1 and 30, and the task profit is a random integer between 1 and 10.

Four additional regional training scenarios are generated for the design stage. They use the same construction method and simulator as the evaluation scenarios, but different random seeds make them independent instances. The four scales cover small-to-medium instances, so the design search remains tractable while retaining the main variation in regional task competition. Their settings are summarized in Table VII.

**TABLE VI: EXPERIMENTAL SCENARIOS.**

| Scenario | Scale | $n$ | $m$ | Start time | End time | Distribution |
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

**TABLE VII: TRAINING SCENARIOS.**

| Scenario | Scale | $n$ | $m$ | Start time | End time | Distribution |
|---:|---|---:|---:|---|---|---|
| 1 | Small | 500 | 5 | 00:00:00 | 23:59:59 | Regional |
| 2 | Small | 1000 | 10 | 00:00:00 | 11:59:59 | Regional |
| 3 | Medium | 1000 | 20 | 00:00:00 | 11:59:59 | Regional |
| 4 | Medium | 4000 | 40 | 00:00:00 | 05:59:59 | Regional |

## B. Baseline Methods, Evaluation Metrics, and Parameter Settings

In this section, three representative algorithms are selected for comparison:

**R-ALNS** [6]: Random-allocation ALNS extends the adaptive large neighborhood search with a random task-allocation strategy for multi-satellite scenarios. This method applies ALNS single-satellite optimization within a random task-assignment framework.

**A-ALNS** [7]: Adaptive-allocation ALNS combines ALNS single-satellite optimization with an adaptive task-allocation mechanism under a divide-and-conquer framework. This method has been reported as a highly effective algorithm for multi-satellite task scheduling.

**RK-HMA** [21]: The manually designed hybrid metaheuristic that combines DE/rand/1 and PSO as inner single-satellite optimizers with dynamic task reassignment (see Section I). It serves as the baseline for the automatic design framework.

The parameter values for Auto-hybrid are shown in Tab. VIII. The profit rate ($PR$) and computational time are used to evaluate the performance of each algorithm. $PR$ is defined as:

$$
PR = \frac{F(P_S)}{F(P_A)} \times 100\% \tag{20}
$$

where $F(P_S)$ is the total profit of scheduled tasks and $F(P_A)$ is the total profit of all tasks.



**TABLE VIII: DESIGN-SEARCH AND REPLAY SETTINGS.**

| Setting | Symbol | Value |
|---|---|---|
| Design population | $N_d$ | 35 |
| Outer generation cap | $G_{\max}$ | 25 |
| Early-stop minimum generations | $G_{\min}$ | 20 |
| Early-stop patience | $P$ | 5 |
| Early-stop minimum improvement | $\Delta$ | 0.001 |
| Outer evaluation repeats | $R_d$ | 2 |
| Candidate-screen repeats per training scenario | $R_s$ | 5 |
| Final replay runs per scenario | $R_f$ | 5 |
| Search budget ratio | $\rho$ | 0.6 |
| Design crossover probability | $p_c$ | 0.3 |
| Design mutation probability | $p_m=1-p_c$ | 0.7 |
| Population size | $N_{\mathrm{pop}}$ | $2.5 \times \max(n_j)$ |
| Full inner budget | $B_{\mathrm{full}}$ | $100N_{\mathrm{pop}}$ |
| Top-subset ratio | $r_{\mathrm{sub}}$ | 0.5 |
| Mixed-subset top ratio | $r_{\mathrm{mix}}$ | 0.8 |
| Random-decay start ratio | $r_{\mathrm{dec}}$ | $0.5 \rightarrow 0.2$ |
| Stage-switch boundary ratio | $\tau_{\mathrm{stage}}$ | 0.5 |
| Periodic-switch period | $T_{\mathrm{sw}}$ | $\max\{1,\lceil0.05B_{\mathrm{full}}\rceil\}$ |
| Best-no-improvement patience | $T_{\mathrm{best}}$ | $\max\{1,\lceil0.05(B_{\mathrm{full}}-N_{\mathrm{pop}}+1)\rceil\}$ |
| Process-no-improvement patience | $T_{\mathrm{proc}}$ | $\max\{1,\lceil0.05B_{\mathrm{full}}\rceil\}$ |
| Diversity-switch check interval | $T_{\mathrm{div}}$ | $\max\{1,\lceil0.01B_{\mathrm{full}}\rceil\}$ |
| Diversity-switch threshold | $\theta_{\mathrm{div}}$ | 0.02 |
| Adaptive-credit window | $W_c$ | 8 |
| Adaptive-credit default routing ratio | $\rho_c$ | 0.5 |
| Tournament size | $k_{\mathrm{tour}}$ | 2 |

## C. Comparison Results

In this section, the performance of Auto-Hybrid, RK-HMA, A-ALNS, and R-ALNS is evaluated on ten scenarios with five independent runs each. Table IX reports the comparison results in profit rate. As shown in Table IX, Auto-Hybrid obtains the best or tied-best profit rate on all ten scenarios. Fig. 5 shows the profit-rate comparison under regional and global distributions.

On regional scenarios, all algorithms show larger performance differences compared to global scenarios. With the increasing problem scale, Auto-Hybrid gradually shows its advantage over R-ALNS, A-ALNS, and RK-HMA. The maximum gap between Auto-Hybrid and R-ALNS reaches 12.32 percentage points, and the average gap reaches 8.31 percentage points. The maximum gap between Auto-Hybrid and A-ALNS reaches 8.26 percentage points, and the average gap reaches 5.97 percentage points. The maximum gap between Auto-Hybrid and RK-HMA reaches 2.99 percentage points, and the average gap reaches 0.76 percentage points. Auto-Hybrid achieves a mean profit rate of 63.24% on the regional scenarios, compared with 62.48% for RK-HMA, 57.27% for A-ALNS, and 54.93% for R-ALNS. This advantage is associated with the stronger task-satellite contention induced by the regional distribution.

On global scenarios, where tasks are uniformly distributed, the performance differences narrow considerably. The maximum gap between Auto-Hybrid and R-ALNS is only 0.65 percentage points, and the average gap is only 0.26 percentage points. The maximum gap between Auto-Hybrid and A-ALNS is only 0.08 percentage points, and the average gap is only 0.03 percentage points. Auto-Hybrid ties with RK-HMA on all four global scenarios (2, 4, 6, and 8), and all methods achieve profit rates between 92.47% and 100.00%. Across all ten scenarios, the mean gaps of Auto-Hybrid relative to R-ALNS and A-ALNS are 5.09 and 3.59 percentage points, respectively.

**TABLE IX: MEAN PROFIT RATE (%) ON ALL EXPERIMENTAL SCENARIOS.**

| Scenario | Distribution | $n,m$ | R-ALNS | A-ALNS | RK-HMA | Auto-Hybrid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Regional | 500, 5 | 96.52%<br>(+3.08) | 96.29%<br>(+3.31) | **99.60%**<br>(0) | **99.60%**<br>(0) |
| 2 | Global | 500, 5 | **99.89%**<br>(0) | **99.89%**<br>(0) | **99.89%**<br>(0) | **99.89%**<br>(0) |
| 3 | Regional | 1000, 10 | 38.79%<br>(+9.38) | 39.91%<br>(+8.26) | 47.50%<br>(+0.67) | **48.17%**<br>(0) |
| 4 | Global | 1000, 10 | 92.47%<br>(+0.12) | 92.58%<br>(+0.01) | **92.59%**<br>(0) | **92.59%**<br>(0) |
| 5 | Regional | 1000, 20 | 66.81%<br>(+12.32) | 71.69%<br>(+7.44) | 78.51%<br>(+0.62) | **79.13%**<br>(0) |
| 6 | Global | 2000, 20 | 98.17%<br>(+0.27) | 98.43%<br>(+0.01) | **98.44%**<br>(0) | **98.44%**<br>(0) |
| 7 | Regional | 4000, 40 | 56.59%<br>(+10.35) | 62.71%<br>(+4.23) | 63.95%<br>(+2.99) | **66.94%**<br>(0) |
| 8 | Global | 6000, 60 | 99.35%<br>(+0.65) | 99.92%<br>(+0.08) | **100.00%**<br>(0) | **100.00%**<br>(0) |
| 9 | Regional | 8000, 80 | 42.45%<br>(+8.95) | 43.41%<br>(+7.99) | 51.22%<br>(+0.18) | **51.40%**<br>(0) |
| 10 | Regional | 10000, 100 | 28.44%<br>(+5.77) | 29.61%<br>(+4.60) | 34.08%<br>(+0.13) | **34.21%**<br>(0) |



![Mean profit rate by task distribution](figures/auto_hybrid_distribution_comparison.svg)

**Fig. 5.** Mean profit rate by task distribution.

The computational times of Auto-Hybrid, RK-HMA, R-ALNS, and A-ALNS are shown in Table X. Overall, as the numbers of tasks and satellites increase, all algorithms consume more computational time. Auto-Hybrid is faster than RK-HMA on all ten scenarios; the detailed comparison is given below together with the profit-rate analysis. Compared with R-ALNS and A-ALNS, Auto-Hybrid has lower computational time in most scenarios, especially in the global scenarios, where it is the fastest method on all four cases. On regional scenarios where Auto-Hybrid requires longer runtime than A-ALNS, the higher profit rate accompanies the additional computational cost. For example, on regional scenarios 1, 3, 5, and 10, Auto-Hybrid requires 4.21, 1.84, 0.43, and 27.08 s more than A-ALNS, while achieving 3.31, 8.26, 7.44, and 4.60 percentage-point profit-rate gains, respectively. This pattern reflects two aspects: the shared-population hybrid inner optimizer introduces multiple parent-algorithm updates, while the common allocation and reassignment pipeline makes the computational cost increase with the number of tasks and satellites.

**TABLE X: MEAN COMPUTATIONAL TIME ON ALL EXPERIMENTAL SCENARIOS.**

| Scenario | Distribution | $n,m$ | R-ALNS | A-ALNS | RK-HMA | Auto-Hybrid |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Regional | 500,5 | 4.18 s | **2.72 s** | 7.83 s | 6.929 s |
| 2 | Global | 500,5 | 2.36 s | 2.44 s | 1.23 s | **0.969 s** |
| 3 | Regional | 1000,10 | 4.54 s | **2.56 s** | 5.64 s | 4.402 s |
| 4 | Global | 1000,10 | 3.90 s | 3.11 s | 1.39 s | **1.004 s** |
| 5 | Regional | 1000,20 | 5.57 s | **2.99 s** | 4.86 s | 3.423 s |
| 6 | Global | 2000,20 | 8.00 s | 6.67 s | 2.59 s | **2.025 s** |
| 7 | Regional | 4000,40 | 34.64 s | 19.31 s | 9.70 s | **7.768 s** |
| 8 | Global | 6000,60 | 27.59 s | 43.20 s | 1.89 s | **0.964 s** |
| 9 | Regional | 8000,80 | 94.61 s | 84.20 s | 76.79 s | **46.395 s** |
| 10 | Regional | 10000,100 | 132.63 s | **86.58 s** | 126.83 s | 113.658 s |

The comparison between Auto-Hybrid and RK-HMA is central to this study, because the two methods share the same random-key scheduling bridge, the same dynamic task reassignment layer, and the same benchmark scenarios; they differ only in how the inner single-satellite optimizer is designed—by automatic structural search versus by manual expert selection of DE/rand/1 and PSO. As shown in Tables IX and X, Auto-Hybrid matches or exceeds RK-HMA in profit rate on all ten scenarios while being faster on every one. Fig. 6 further compares the five-run profit-rate distributions on the six regional scenarios: the Auto-Hybrid median is above the RK-HMA median in all six panels, with standard deviations between 0.03 and 0.53 percentage points; the distributions overlap on smaller-scale scenarios where both methods approach the regional profit ceiling, while the gap widens on the larger and more contention-heavy scenarios (7, 9, 10). These results confirm the effectiveness of automatic structural search: the composed EDA–GA optimizer matches or surpasses the hand-crafted DE/rand/1–PSO combination in both solution quality and computational efficiency across all tested scenarios. Note that the two sets of runs come from different execution periods, so the comparison is descriptive rather than a paired controlled experiment.

![Profit rate distribution of RK-HMA and Auto-Hybrid on regional scenarios](figures/rk_hma_auto_hybrid_regional_boxplots.svg)

**Fig. 6.** Profit rate distribution of RK-HMA and Auto-Hybrid on regional scenarios.



# V. Conclusion

This paper presented an automatic design framework for collaboration-based hybrid metaheuristics tailored to LS-AEOSTSP. Unlike the manually designed RK-HMA, which fixes the inner single-satellite optimizer as a DE/rand/1–PSO hybrid under a predetermined collaboration structure, the proposed framework encodes the collaboration structure—parent algorithms, operating levels, operating order, and survivor selection—as a six-gene semantic chromosome and searches it through an evolutionary process. The task-satellite allocation layer and the random-key scheduling bridge remain unchanged, so the searched part is strictly the inner optimizer structure.

Experimental results on ten benchmark scenarios containing 500–10,000 tasks and 5–100 satellites show that the composed optimizer obtains the best or tied-best profit rate on all scenarios, with maximum advantages of 12.32 and 8.26 percentage points over R-ALNS and A-ALNS, respectively. Compared with RK-HMA, Auto-Hybrid achieves higher profit rates on all six regional scenarios (up to 2.99 percentage points) while being computationally faster on all ten scenarios, demonstrating that the automatically selected collaboration structure is better suited to the scheduling pipeline than the hand-crafted one. In future work, the component libraries can be enriched with more parent algorithms and hybridization forms, and the same searchable-structure formulation can be extended to complex constrained AEOSTSP variants such as resource-limited scheduling, autonomous task scheduling, and dynamic environments.

# References

[1] X. Wang, G. Wu, L. Xing, and W. Pedrycz, "Agile earth observation satellite scheduling over 20 years: Formulations, methods, and future directions," *IEEE Systems Journal*, vol. 15, no. 3, pp. 3881-3892, 2021.

[2] X. Chen, G. Reinelt, G. Dai, and A. Spitz, "A mixed integer linear programming model for multi-satellite scheduling," *European Journal of Operational Research*, vol. 275, no. 2, pp. 694-707, 2019.

[3] Y. Du, T. Wang, B. Xin, L. Wang, Y. Chen, and L. Xing, "A data-driven parallel scheduling approach for multiple agile earth observation satellites," *IEEE Transactions on Evolutionary Computation*, vol. 24, no. 4, pp. 679-693, 2020.

[4] G. Peng, G. Song, L. Xing, A. Gunawan, and P. Vansteenwegen, "An exact algorithm for agile earth observation satellite scheduling with time-dependent profits," *Computers & Operations Research*, vol. 120, p. 104946, 2020.

[5] G. Peng, G. Song, Y. He, J. Yu, S. Xiang, L. Xing, and P. Vansteenwegen, "Solving the agile earth observation satellite scheduling problem with time-dependent transition times," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 52, no. 3, pp. 1614-1625, 2022.

[6] X. Liu, G. Laporte, Y. Chen, and R. He, "An adaptive large neighborhood search metaheuristic for agile satellite scheduling with time-dependent transition time," *Computers & Operations Research*, vol. 86, pp. 41-53, 2017.

[7] L. He, X. Liu, G. Laporte, Y. Chen, and Y. Chen, "An improved adaptive large neighborhood search algorithm for multiple agile satellites scheduling," *Computers & Operations Research*, vol. 100, pp. 12-25, 2018.

[8] J. Li, J. Zhu, D. Xu, J. Wang, Z. Li, and K. Zhang, "Earth observation satellite scheduling with interval-varying profits," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 6, pp. 8273-8288, 2024.

[9] F. Yao, Y. Chen, L. Wang, Z. Chang, P.-Q. Huang, and Y. Wang, "A bilevel evolutionary algorithm for large-scale multiobjective task scheduling in multiagile earth observation satellite systems," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 54, no. 6, pp. 3512-3524, 2024.

[10] J. Qin, X. Bai, G. Du, J. Liu, N. Peng, and M. Xu, "Multisatellite scheduling for moving targets using the enhanced hybrid genetic simulated annealing algorithm and observation strip selection," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 5, pp. 5773-5800, 2024.

[11] H. Wang, W. Huang, S. Magnusson, T. Lindgren, R. Wang, and Y. Song, "A strategy fusion-based multiobjective optimization approach for agile earth observation satellite scheduling problem," *IEEE Transactions on Geoscience and Remote Sensing*, vol. 62, pp. 1-14, 2024.

[12] C. Blum, J. Puchinger, G. R. Raidl, and A. Roli, "Hybrid metaheuristics in combinatorial optimization: A survey," *Applied Soft Computing*, vol. 11, no. 6, pp. 4135-4151, 2011.

[13] J. Fan, Y. Li, J. Xie, C. Zhang, W. Shen, and L. Gao, "A hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling problem," *IEEE Transactions on Cybernetics*, vol. 53, no. 3, pp. 1752-1764, 2023.

[14] Z. Shu, A. Song, G. Wu, and W. Pedrycz, "Variable reduction strategy integrated variable neighborhood search and NSGA-II hybrid algorithm for emergency material scheduling," *Complex System Modeling and Simulation*, vol. 3, no. 2, pp. 83-101, 2023.

[15] Y. Rocha, G. O. Chagas, L. C. Coelho, and A. Subramanian, "The integrated agile earth observation satellite scheduling problem," *Computers & Operations Research*, vol. 184, p. 107212, 2025.

[16] F. Hutter, H. H. Hoos, K. Leyton-Brown, and T. Stutzle, "ParamILS: An automatic algorithm configuration framework," *Journal of Artificial Intelligence Research*, vol. 36, pp. 267-306, 2009.

[17] F. Hutter, H. H. Hoos, and K. Leyton-Brown, "Sequential model-based optimization for general algorithm configuration," in *Learning and Intelligent Optimization*, Lecture Notes in Computer Science, vol. 6683, pp. 507-523, Springer, 2011.

[18] M. Lopez-Ibanez, J. Dubois-Lacoste, L. Perez Caceres, M. Birattari, and T. Stutzle, "The irace package: Iterated racing for automatic algorithm configuration," *Operations Research Perspectives*, vol. 3, pp. 43-58, 2016.

[19] E. K. Burke, M. Gendreau, M. Hyde, G. Kendall, G. Ochoa, E. Ozcan, and R. Qu, "Hyper-heuristics: A survey of the state of the art," *Journal of the Operational Research Society*, vol. 64, no. 12, pp. 1695-1724, 2013.

[20] Y. Wang, B. Xin, B. Liu, and Q. Wang, "Automated design of collaboration-based hybrid metaheuristics," *IEEE Transactions on Cybernetics*, vol. 54, no. 12, pp. 7877-7890, 2024.

[21] H. Lei, X. Lin, L. He, and Y. Chen, "A random-key hybrid metaheuristic algorithm with dynamic task reassignment for large-scale multi-satellite scheduling," 2025, submitted for publication.

[22] E.-G. Talbi, *Metaheuristics: From Design to Implementation*. Hoboken, NJ, USA: Wiley, 2009.

[23] K. Socha and M. Dorigo, "Ant colony optimization for continuous domains," *European Journal of Operational Research*, vol. 185, no. 3, pp. 1155-1173, 2008.

[24] S. Das and P. N. Suganthan, "Differential evolution: A survey of the state-of-the-art," *IEEE Transactions on Evolutionary Computation*, vol. 15, no. 1, pp. 4-31, 2011.

[25] R. Tanabe and A. S. Fukunaga, "Improving the search performance of SHADE using linear population size reduction," in *Proc. IEEE Congress on Evolutionary Computation (CEC)*, 2014, pp. 1658-1665.

[26] A. Santiago, B. Dorronsoro, A. J. Nebro, J. J. Durillo, O. Castillo, and H. J. Fraire, "A novel multi-objective evolutionary algorithm with fuzzy logic based adaptive selection of operators: FAME," *Information Sciences*, vol. 471, pp. 233-251, 2019.

[27] F. Zhao, W. Lei, W. Ma, Y. Liu, and C. Zhang, "An improved SPEA2 algorithm with adaptive selection of evolutionary operators scheme for multiobjective optimization problems," *Mathematical Problems in Engineering*, vol. 2016, Art. no. 8010346, pp. 1-20, 2016.
