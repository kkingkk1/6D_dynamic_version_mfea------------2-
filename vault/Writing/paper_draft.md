# Automatic Design of Collaboration-Based Hybrid Metaheuristics for Large-Scale Agile Earth Observation Satellite Scheduling

**Abstract**--Large-scale agile earth observation satellite scheduling has drawn growing attention as satellite constellations expand and observation demand rises. The problem couples task selection, satellite assignment, visible-window placement, and attitude-constrained sequencing, and is NP-hard at the scale of practical missions. In conventional collaboration-based hybrid metaheuristic design, the inner collaboration structure is typically fixed in advance. RK-HMA is one such artificially designed hybrid algorithm: its internal single-satellite optimizer combines DE/rand/1 and PSO, achieving good results. This paper recasts the design of this collaboration-based hybrid with two parent algorithms as an automatic structural-design problem within the same scheduling pipeline. A six-gene chromosome selects two parent algorithms, two operating levels (OL), one operating order (OO), and survivor selection. Over these component libraries, an evolutionary search on four regional design scenarios composes a hybrid optimizer. The retained configuration is evaluated on ten benchmark scenarios containing 500–10,000 tasks and 5–100 satellites covering both regional and global task distributions. It obtains the best or tied-best reported profit rate on all ten scenarios, with a maximum gap of 12.32 percentage points over the compared baselines. All methods remain near saturation on global-distribution scenarios, while Auto-Hybrid shows more substantial gains on the more challenging regional-distribution scenarios.

**Index Terms**--agile earth observation satellite scheduling, automated algorithm design, collaboration-based hybrid metaheuristic

# I. Introduction

Agile earth observation satellites (AEOS) with high attitude maneuverability have become a key platform for acquiring space-based information, supporting applications such as disaster monitoring, mapping, and reconnaissance [1]. Over the past two decades, the number of earth observation satellites in orbit has grown rapidly. Wang et al. [1] reported that AEOS scheduling has been actively studied since the early 2000s, driven by the deployment of increasingly agile platforms such as Pléiades, WorldView, and Jilin-1. Du et al. [3] noted that the growing number of satellites and observation requests has made large-scale multi-satellite scheduling a practical challenge. Efficient scheduling is thus needed to manage large constellations and maximize fulfilled observation requests.

The large-scale agile earth observation satellite task scheduling problem (LS-AEOSTSP) is harder than the classic earth observation satellite task scheduling problem (EOSTSP). As illustrated in Fig. 1, unlike conventional EOS that can only observe targets directly below their ground track, AEOS can rotate along the roll, pitch, and yaw axes to steer their imaging payloads toward off-nadir targets. This three-axis maneuverability enlarges the set of visible time windows (VTWs) for each task, but introduces time-dependent attitude transition constraints between consecutive observations. As constellations scale to tens or hundreds of satellites, the joint decision space—task-satellite assignment, VTW selection, and start time determination—grows combinatorially, making exact methods intractable for practical instances [4][5].

![Comparison of observation modes between non-agile EOS and AEOS](figures/agile_satellite_observation_modes.png)

**Fig. 1.** Comparison of observation modes between non-agile EOS and AEOS [6].

Prior work on agile satellite scheduling spans several methodological lines. Survey and exact-optimization studies clarify the main modeling variants and constraint structures: Wang et al. [1] reviewed two decades of AEOS scheduling formulations and methods, Chen et al. [2] built a mixed-integer linear programming model for multi-satellite scheduling, and Peng et al. developed exact formulations that exploit the time-dependent profit and transition-time structure of the problem [4], [5]. Because exact methods do not scale to large instances, metaheuristics have become the dominant practical approach.

Adaptive large neighborhood search (ALNS) and its variants are well studied. Liu et al. [6] designed problem-specific removal and insertion operators for time-dependent transition times, and He et al. [7] extended ALNS to multiple agile satellites with a dynamic task-allocation mechanism. Population-based evolutionary algorithms have also been applied: Yao et al. [9] proposed a bilevel evolutionary algorithm for large-scale multiobjective task scheduling, Qin et al. [10] combined simulated annealing with a genetic algorithm for multisatellite scheduling of moving targets, and Wang et al. [11] designed a strategy fusion-based multi-objective optimization approach. Related methods address further variants, including interval-varying profits [8] and the integrated agile scheduling problem [15]. However, most existing methods rely on a single algorithmic paradigm, limiting the balance between exploration and exploitation in the LS-AEOSTSP search space [1].

Hybrid metaheuristics, which combine the strengths of multiple search strategies within a unified framework, are effective for combinatorial optimization. Blum et al. [12] surveyed hybrid metaheuristic paradigms and reported numerous successful applications where hybridization improved solution quality. In the domain of scheduling, Fan et al. [13] proposed a hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling, and Shu et al. [14] integrated variable neighborhood search with NSGA-II for emergency material scheduling. For LS-AEOSTSP, our previous work proposed RK-HMA [21], which connects continuous optimizers with discrete task sequences through random-key encoding, applies DE/rand/1 and PSO to a shared population, and uses dynamic task reassignment to coordinate satellites. RK-HMA shows that hybridization is effective, obtaining the best or tied-best reported profit rate on all ten benchmark scenarios. However, this manual design process has several limitations: (i) changing any structural decision requires expert re-design and re-validation, (ii) there is no guarantee that the chosen structure remains effective when the scheduling scenario changes in scale or task distribution, and (iii) the design space of collaboration-based hybrids is large—different parent algorithms, OL choices, OO choices, and survivor-selection policies can be combined in many ways, making exhaustive manual exploration impractical.

The central question is therefore an automatic-design question: can the hybrid structure itself be composed for the scheduling pipeline? Algorithm configuration methods such as ParamILS, SMAC, and irace tune parameterized algorithms over training instances [16]-[18]. Hyper-heuristics search over heuristics or heuristic components instead of directly searching the solution space [19]. Automated algorithm design goes further by searching algorithm structures rather than only tuning parameters or choosing among fixed algorithms. Recent work on automated design of collaboration-based hybrid metaheuristics treats hybrid-optimizer design as a meta-optimization problem and uses a top-down template to generate collaboration-based hybrid algorithms [20].

This paper studies that question for LS-AEOSTSP by making the inner single-satellite optimizer a searchable structural layer. A six-gene chromosome encodes the collaboration structure—parent algorithms, OL, OO, and survivor selection—while the random-key scheduling bridge and cross-satellite reassignment layer remain fixed and provide a common evaluation environment. Each candidate chromosome is decoded into an executable optimizer and evaluated through the coupled scheduling pipeline, a setting not addressed by prior automated-design work. The detailed encoding is introduced in Section III-C.

The main contributions are as follows.

1. We propose an automatic design framework for collaboration-based hybrid metaheuristics tailored to LS-AEOSTSP. The inner single-satellite optimizer is composed by search rather than fixed by manual design.

2. We formulate a six-gene semantic chromosome and its component libraries. The chromosome exposes the collaboration structure—parent algorithms, OL, OO, and survivor selection—as interpretable structural decisions that the search can recombine.

3. We evaluate the composed optimizer on ten benchmark scenarios containing 500–10,000 tasks and 5–100 satellites covering both regional and global task distributions. The retained configuration obtains the best or tied-best reported profit rate on all ten scenarios, with a maximum gap of 12.32 percentage points over the compared baselines. All methods remain near saturation on global-distribution scenarios, while Auto-Hybrid shows more substantial gains on the more challenging regional-distribution scenarios.

The remaining sections are organized as follows. Section II defines the scheduling problem. Section III describes the automatic hybrid-design framework. Section IV reports the experiments. Section V concludes the paper.

# II. Problem Description

Consider a scheduling horizon during which a set of $n$ observation tasks $\mathcal{T}=\{\tau_1,\tau_2,\ldots,\tau_n\}$ must be assigned to a constellation of $m$ agile satellites $\mathcal{S}=\{s_1,s_2,\ldots,s_m\}$. Each task $\tau_i$ is characterized by a geographic location, an imaging duration $d_i^{\text{img}}$, a profit $r_i$, and a specified minimum imaging quality $c_i$. Each satellite $s_j$ is described by its orbital elements and attitude state over the scheduling horizon. Through orbit propagation and access analysis, the visible time windows (VTWs) for each task-satellite pair can be computed. Let $\omega_{ijk}$ denote the $k$-th VTW of task $\tau_i$ on satellite $s_j$, with opening time $\alpha_{ijk}$, closing time $\beta_{ijk}$, and duration $\lambda_{ijk}=\beta_{ijk}-\alpha_{ijk}$. The satellite attitude is described by roll $\theta_{jt}^R$, pitch $\theta_{jt}^P$, and yaw $\theta_{jt}^Y$ at time $t$. The notation used throughout this paper is summarized in Table I.

Since the number of tasks typically far exceeds the observation capacity of the constellation, it is generally infeasible to execute all tasks. The LS-AEOSTSP aims to select a subset of tasks and determine their satellite, VTW, and observation start time so as to maximize the total collected profit, subject to the following assumptions.

1. Each task is an atomic observation request that can be directly executed by a satellite. Complex requests such as area coverage or moving target tracking are assumed to have been decomposed into atomic tasks before scheduling.
2. Energy and onboard storage constraints are not explicitly modeled, because satellites recharge through solar panels and periodically downlink data during normal operations.
3. Each satellite carries a single imaging sensor, so at most one task can be executed at any given time.
4. Task execution is non-preemptive. Once an observation starts, it cannot be interrupted, and each task can be observed at most once across the constellation.

**TABLE I: NOTATION FOR LS-AEOSTSP.**

| Notation | Description |
|---|---|
| $\mathcal{T}$ | Set of observation tasks |
| $n$ | Number of tasks |
| $\mathcal{S}$ | Set of satellites |
| $m$ | Number of satellites |
| $\tau_i$ | Task $i$ |
| $s_j$ | Satellite $j$ |
| $r_i$ | Profit of task $\tau_i$ |
| $d_i^{\text{img}}$ | Imaging duration of task $\tau_i$ |
| $\theta_{jt}^R$ | Roll angle of satellite $s_j$ at time $t$ |
| $\theta_{jt}^P$ | Pitch angle of satellite $s_j$ at time $t$ |
| $\theta_{jt}^Y$ | Yaw angle of satellite $s_j$ at time $t$ |
| $\Omega_{ij}$ | Set of VTWs for task $\tau_i$ on satellite $s_j$ |
| $\omega_{ijk}$ | The $k$-th VTW of task $i$ on satellite $j$ |
| $|\Omega_{ij}|$ | Number of VTWs for task $\tau_i$ on satellite $s_j$ |
| $\alpha_{ijk}$ | Opening time of $\omega_{ijk}$ |
| $\beta_{ijk}$ | Closing time of $\omega_{ijk}$ |
| $\lambda_{ijk}$ | Duration of $\omega_{ijk}$ |
| $x_{ijk}$ | Binary variable indicating whether task $i$ is scheduled in $\omega_{ijk}$ |
| $b_{ijk}$ | Observation start time |
| $\sigma_{ijk,i'jk'}$ | Precedence indicator for consecutive observations on one satellite |
| $T^{\text{trans}}$ | Attitude-transition time between two consecutive observations |
| $c_i$ | Required minimum imaging quality of task $\tau_i$ |
| $q_i$ | Imaging quality of scheduled task $\tau_i$ |
| $w_{ijk}^{*}$ | Midpoint of $\omega_{ijk}$ |
| $F(P_S)$ | Total profit of the scheduled task set |

Two types of decision variables are defined. The binary variable $x_{ijk}\in\{0,1\}$ indicates whether task $\tau_i$ is scheduled in VTW $\omega_{ijk}$. The continuous variable $b_{ijk}$ specifies the observation start time of task $\tau_i$ when $x_{ijk}=1$.

The objective is to maximize the collected profit:

$$
\max F(P_S)=\sum_{i=1}^{n}\sum_{j=1}^{m}\sum_{k=1}^{|\Omega_{ij}|} x_{ijk}r_i. \tag{1}
$$

Each task can be scheduled at most once:

$$
\sum_{j=1}^{m}\sum_{k=1}^{|\Omega_{ij}|} x_{ijk} \le 1,\quad \forall \tau_i\in\mathcal{T}. \tag{2}
$$

If a task is selected, the observation must start and finish inside the chosen VTW:

$$
\alpha_{ijk} \le b_{ijk} \le \beta_{ijk}-d_i^{\text{img}},\quad \text{if }x_{ijk}=1. \tag{3}
$$

For consecutive observations on the same satellite, define

$$
\sigma_{ijk,i'jk'} =
\begin{cases}
1, & \text{if }\tau_i\text{ directly precedes }\tau_{i'}\text{ on }s_j,\\
0, & \text{otherwise.}
\end{cases} \tag{4}
$$

The transition-time constraint is then

$$
b_{ijk}+d_i^{\text{img}}+T^{\text{trans}}(\tau_i,\tau_{i'})\le b_{i'jk'},\quad \text{if }\sigma_{ijk,i'jk'}=1. \tag{5}
$$

The attitude-transition time is a piecewise linear function of the total angular displacement:

$$
T^{\text{trans}}(\tau_i,\tau_{i'})
=
\begin{cases}
11.66, & \Delta\Theta \leq 10^\circ,\\
c_1+\Delta\Theta/v_1, & 10^\circ<\Delta\Theta\leq 30^\circ,\\
c_2+\Delta\Theta/v_2, & 30^\circ<\Delta\Theta\leq 60^\circ,\\
c_3+\Delta\Theta/v_3, & 60^\circ<\Delta\Theta\leq 90^\circ,\\
c_4+\Delta\Theta/v_4, & \Delta\Theta>90^\circ.
\end{cases} \tag{6}
$$

The angular displacement is computed from the attitude differences between the two observations:

$$
\Delta\Theta(\tau_i,\tau_{i'})
=|\theta^R_{j,b_{ijk}}-\theta^R_{j,b_{i'jk'}}|
+|\theta^P_{j,b_{ijk}}-\theta^P_{j,b_{i'jk'}}|
+|\theta^Y_{j,b_{ijk}}-\theta^Y_{j,b_{i'jk'}}|,\quad \text{if }\sigma_{ijk,i'jk'}=1. \tag{7}
$$

The executed task must also satisfy its imaging-quality requirement:

$$
q_i\ge c_i,\quad \forall \tau_i\in\mathcal{T}. \tag{8}
$$

When a scheduled task is executed in $\omega_{ijk}$, its imaging quality is computed by the distance between the observation start time and the midpoint of the selected VTW:

$$
q_i=10-9\cdot
\frac{|2b_{ijk}+d_i^{\text{img}}-2w_{ijk}^{*}|}{\lambda_{ijk}-d_i^{\text{img}}},
\quad \text{if }x_{ijk}=1, \tag{9}
$$

where

$$
w_{ijk}^{*}=\frac{\alpha_{ijk}+\beta_{ijk}}{2},\quad \text{if }x_{ijk}=1. \tag{10}
$$

Constraint (2) ensures that each task is observed at most once across all satellites. Constraint (3) guarantees that the observation must start and finish within the selected VTW. Constraint (5) enforces that consecutive tasks on the same satellite must be separated by a sufficient transition time. The transition time is defined by Eq. (6), and the angular displacement is computed by Eq. (7). Following [5], the parameters are set to $v_1=1.5^\circ/\text{s}$, $c_1=5$, $v_2=2^\circ/\text{s}$, $c_2=10$, $v_3=2.5^\circ/\text{s}$, $c_3=16$, $v_4=3^\circ/\text{s}$, and $c_4=22$. Constraint (8) requires the imaging quality of each executed task to be no lower than the specified threshold, and Eqs. (9)-(10) compute imaging quality from the position of the start time inside the selected VTW.

The solution has two coupled parts: each scheduled task must be assigned to a satellite and VTW, and each satellite must choose a feasible task sequence. These two decisions are interdependent, because the value of an assignment depends on the sequence each satellite can realize, while a feasible sequence depends on which tasks are assigned. The LS-AEOSTSP is NP-hard, as it contains the single-satellite EOSTSP as a special case [4], [5], and the joint assignment-and-sequencing space grows on the order of $O(n!\,m^{n})$ with the number of tasks $n$ and satellites $m$. Exact methods are therefore intractable at the scales considered here, which motivates the metaheuristic scheduling pipeline described in Section III.

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

![Automatic hybrid-design workflow](figures/automatic_hybrid_design_flow.png)

**Fig. 2.** Automatic hybrid-design workflow.

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

The operating level determines which inner random-key solutions of the shared population each parent algorithm is allowed to modify. The seven realization forms below span population-, subpopulation-, and individual-level updates. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table VII.

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

The operating-order library specifies when the two parent algorithms are invoked and thereby determines their information dependency. Its realization forms comprise seven sequential options and one parallel option. The IDs retain their fixed encoding assignments. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table VII.

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
f(\mathbf{x})=\sum_{\tau_i\in P_j} r_i,
$$

where $P_j$ is the feasible schedule constructed for satellite $s_j$.

After per-satellite schedules are generated, the fixed multi-satellite layer applies the RK-HMA dynamic reassignment procedure [21] to reconsider unscheduled tasks. This layer is shared by all candidate chromosomes and is not part of the optimizer-design space.

# IV. Experimental Results

To evaluate the proposed automatic hybrid-design framework on the LS-AEOSTSP, the simulator introduced in [7] is used to generate multiple experimental scenarios. The framework and the generated optimizer are implemented in Java and run on a PC with Intel Core i7-14700kf CPU @ 3.40 GHz and 64-GB memory.

## A. Experimental Scenario And Training Scenario

Ten experimental scenarios are used for evaluation, following the benchmark scale and distribution settings used in RK-HMA [21]. They cover small-scale, medium-scale, large-scale, and superlarge-scale instances. The task count ranges from 500 to 10,000, and the satellite count ranges from 5 to 100. The distribution is categorized into regional and global distributions. In the regional setting, tasks are concentrated in the area $3^\circ\text{N}$-$53^\circ\text{N}$ and $74^\circ\text{E}$-$133^\circ\text{E}$, which creates stronger competition for feasible time windows. The imaging duration of each task is a random integer between 1 and 30, and the task profit is a random integer between 1 and 10.

Four additional regional training scenarios are generated for the design stage, with scales matching scenarios 1, 3, 5, and 7 (500 tasks/5 satellites, 1000 tasks/10 satellites, 1000 tasks/20 satellites, and 4000 tasks/40 satellites). These training scenarios follow the same construction method and simulator as the evaluation scenarios but use different random seeds to ensure they are distinct instances. These four scales are selected because they span small-to-medium problem sizes, allowing the design search to complete within reasonable computational time while covering the key characteristics of regional task competition across different instance scales.

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

## B. Baseline Methods, Evaluation Metrics, and Parameter Settings

In this section, three representative algorithms are selected for comparison:

**R-ALNS** [6]: Random-allocation ALNS extends the adaptive large neighborhood search with a random task-allocation strategy for multi-satellite scenarios. This method applies ALNS single-satellite optimization within a random task-assignment framework.

**A-ALNS** [7]: Adaptive-allocation ALNS combines ALNS single-satellite optimization with an adaptive task-allocation mechanism under a divide-and-conquer framework. This method has been reported as a highly effective algorithm for multi-satellite task scheduling.

**RK-HMA** [21]: The manually designed hybrid metaheuristic that combines DE/rand/1 and PSO as inner single-satellite optimizers with dynamic task reassignment (see Section I). It serves as the baseline for the automatic design framework.

The parameter values for Auto-hybrid are shown in Tab. VII. The profit rate ($PR$) and computational time are used to evaluate the performance of each algorithm. $PR$ is defined as:

$$
PR = \frac{F(P_S)}{F(P_A)} \times 100\% \tag{20}
$$

where $F(P_S)$ is the total profit of scheduled tasks and $F(P_A)$ is the total profit of all tasks.



**TABLE VII: DESIGN-SEARCH AND REPLAY SETTINGS.**

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

In this section, the performance of Auto-Hybrid, RK-HMA, A-ALNS, and R-ALNS is compared on all ten scenarios. The R-ALNS and A-ALNS entries use the five-run means reported in [21, Tables 4 and 5], with iteration caps of 500 and 25, respectively. Table VIII reports the profit-rate comparison. As shown in Table VIII, Auto-Hybrid obtains the best or tied-best reported profit rate on all ten scenarios. The largest gap between Auto-Hybrid and a compared baseline is 12.32 percentage points on scenario 5, while the ten-scenario mean gaps are 5.09 and 3.59 percentage points over R-ALNS and A-ALNS, respectively. Auto-Hybrid ties with the best baseline on all four global scenarios (2, 4, 6, 8), where all methods remain between 92.47% and 100.00%. The advantage of Auto-Hybrid is more pronounced on regional scenarios, where task-satellite contention is stronger. On the six regional scenarios, Auto-Hybrid achieves a mean profit rate of 63.24%, compared with 62.48% for RK-HMA, 57.27% for A-ALNS, and 54.93% for R-ALNS. The regional-scenario mean gaps are 0.76, 5.97, and 8.31 percentage points, respectively, relative to RK-HMA, A-ALNS, and R-ALNS.

**TABLE VIII: PROFIT-RATE COMPARISON ON ALL EXPERIMENTAL SCENARIOS.**

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

Fig. 5 shows the profit-rate comparison by task distribution. All four methods remain near saturation on global-distribution scenarios, achieving profit rates between 92.47% and 100.00%. The performance differences are more substantial on regional-distribution scenarios, where Auto-Hybrid shows consistent advantages over the baselines. The improvement can be explained by the automatically composed hybrid structure: the selected configuration combines SHADE and PSO at the task-list level with stage-switch ordering, allowing the optimizer to balance exploration and exploitation more effectively under stronger task-satellite contention. The differences should not be interpreted as a causal estimate of automatic structure design because the execution protocols and code states are different across the compared methods.

![Reported profit-rate comparison by task distribution](figures/auto_hybrid_distribution_comparison.svg)

**Fig. 5.** Reported profit-rate comparison by task distribution.

**Computational time.** The R-ALNS and A-ALNS times are the five-run means reported in [21, Table 5], while RK-HMA times remain from [21]. Auto-Hybrid times are current five-run means. Different implementations, hardware, and protocols make this an auxiliary comparison.

**TABLE IX: COMPUTATIONAL-TIME COMPARISON WITH REPORTED METHODS.**

| Scenario | Distribution | $n,m$ | R-ALNS | A-ALNS | RK-HMA | Auto-Hybrid (current replay) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Regional | 500,5 | 4.18 s | 2.72 s | 7.83 s | 6.929 s |
| 2 | Global | 500,5 | 2.36 s | 2.44 s | 1.23 s | 0.969 s |
| 3 | Regional | 1000,10 | 4.54 s | 2.56 s | 5.64 s | 4.402 s |
| 4 | Global | 1000,10 | 3.90 s | 3.11 s | 1.39 s | 1.004 s |
| 5 | Regional | 1000,20 | 5.57 s | 2.99 s | 4.86 s | 3.423 s |
| 6 | Global | 2000,20 | 8.00 s | 6.67 s | 2.59 s | 2.025 s |
| 7 | Regional | 4000,40 | 34.64 s | 19.31 s | 9.70 s | 7.768 s |
| 8 | Global | 6000,60 | 27.59 s | 43.20 s | 1.89 s | 0.964 s |
| 9 | Regional | 8000,80 | 94.61 s | 84.20 s | 76.79 s | 46.395 s |
| 10 | Regional | 10000,100 | 132.63 s | 86.58 s | 126.83 s | 113.658 s |

The current Auto-Hybrid replay took 937.686 s across 50 runs, or 18.754 s per run on average. Scenarios 9 and 10 account for most of this cost, with five-run totals of 231.975 s and 568.292 s, respectively. Within the current implementation, the replay remains executable at the tested scales, but the cost grows sharply for the largest regional scenarios.

The source RK-HMA paper shows five run-level points for RK-HMA on the six regional scenarios in Fig. 9. We use those plotted RK-HMA points to construct a descriptive boxplot comparison with the five current Auto-Hybrid replay values. The two methods come from different execution protocols and code states, so the figure is not a paired inferential comparison.

![Five-run profit-rate distributions of RK-HMA and Auto-Hybrid on regional scenarios](figures/rk_hma_auto_hybrid_regional_boxplots.svg)

**Fig. 6.** Five-run profit-rate distributions of RK-HMA and Auto-Hybrid on the regional scenarios.

The regional Auto-Hybrid replay is stable at the current five-run resolution, with standard deviations between 0.03 and 0.53 percentage points. Its median is above the RK-HMA median in all six plotted regional panels, although the distributions overlap on several scenarios. The numerical ten-scenario comparison above continues to use the reported RK-HMA means in Table IV of [21]; Fig. 6 uses the run-level points shown in Fig. 9 to make within-scenario variation visible. Neither source supports a paired causal estimate of automatic structure design.

# V. Conclusion

The large-scale agile earth observation satellite task scheduling problem (LS-AEOSTSP) couples task selection, satellite assignment, and attitude-constrained per-satellite sequencing, and existing hybrid solvers fix the inner single-satellite optimizer by hand. This paper presented an automatic design framework for collaboration-based hybrid metaheuristics that instead treats this inner optimizer as a design object. The task-satellite allocation layer and the sequence-to-schedule decoding layer remain unchanged; the searched part is the collaboration structure of the inner single-satellite optimizer.

The method uses component libraries and a six-gene semantic chromosome to describe parent algorithms, OL, OO, and survivor selection. Each chromosome is decoded into an executable single-satellite optimizer and evaluated through the same multi-satellite scheduling pipeline. A reduced-budget evolutionary search selects a candidate structure on four representative regional scenarios, and a full-budget replay then evaluates the composed optimizer on all ten benchmark scenarios. The training screen selects chromosome [2,0,0,0,4,2], which decodes to EDA and GA with full-population operating levels, process-no-improvement switching, and pairwise-greedy survivor selection. Its training macro mean is 73.32%, approximately 0.04 percentage points above the runner-up.

The selected configuration completes 50/50 full-budget replay runs and reaches a ten-scenario macro-mean profit rate of 77.04% under the current full-budget replay protocol. The global scenarios are close to the profit ceiling, while the regional scenarios show lower means and larger replay variation. Compared with the RK-HMA means reported in [21], the current Auto-Hybrid replay is higher on all six regional scenarios at the unrounded mean level, tied with scenario 1 at the two-decimal reporting precision, and tied on the four global scenarios at that precision; the descriptive macro-mean differences are approximately 0.46 percentage points across all ten scenarios and 0.76 percentage points on the regional subset. Because the two sources use different execution protocols and code states, these values quantify a reported-protocol comparison rather than an isolated causal effect of automatic structure design. Beyond solution quality, the automatic design stage provides an unattended route for selecting a concrete collaboration structure from the six-gene search space.

In future work, the component libraries can be enriched with more parent algorithms and hybridization forms, and large language models offer a promising route to propose or generate such components automatically; a racing or surrogate-assisted design stage would then keep the enlarged search affordable. The same searchable-structure formulation can also be applied to a wider range of scheduling and combinatorial-optimization problems beyond LS-AEOSTSP. More broadly, the results suggest that treating the inner optimizer as a searchable structural layer is a reusable way to strengthen an existing scheduling pipeline without redesigning its problem-specific components.

# References

[1] X. Wang, G. Wu, L. Xing, and W. Pedrycz, "Agile earth observation satellite scheduling over 20 years: Formulations, methods, and future directions," *IEEE Systems Journal*, vol. 15, no. 3, pp. 3881-3892, 2021, doi: 10.1109/JSYST.2020.2997050.

[2] X. Chen, G. Reinelt, G. Dai, and A. Spitz, "A mixed integer linear programming model for multi-satellite scheduling," *European Journal of Operational Research*, vol. 275, no. 2, pp. 694-707, 2019, doi: 10.1016/j.ejor.2018.11.058.

[3] Y. Du, T. Wang, B. Xin, L. Wang, Y. Chen, and L. Xing, "A data-driven parallel scheduling approach for multiple agile earth observation satellites," *IEEE Transactions on Evolutionary Computation*, vol. 24, no. 4, pp. 679-693, 2020, doi: 10.1109/TEVC.2019.2934148.

[4] G. Peng, G. Song, L. Xing, A. Gunawan, and P. Vansteenwegen, "An exact algorithm for agile earth observation satellite scheduling with time-dependent profits," *Computers & Operations Research*, vol. 120, p. 104946, 2020, doi: 10.1016/j.cor.2020.104946.

[5] G. Peng, G. Song, Y. He, J. Yu, S. Xiang, L. Xing, and P. Vansteenwegen, "Solving the agile earth observation satellite scheduling problem with time-dependent transition times," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 52, no. 3, pp. 1614-1625, 2022, doi: 10.1109/TSMC.2020.3031738.

[6] X. Liu, G. Laporte, Y. Chen, and R. He, "An adaptive large neighborhood search metaheuristic for agile satellite scheduling with time-dependent transition time," *Computers & Operations Research*, vol. 86, pp. 41-53, 2017, doi: 10.1016/j.cor.2017.04.006.

[7] L. He, X. Liu, G. Laporte, Y. Chen, and Y. Chen, "An improved adaptive large neighborhood search algorithm for multiple agile satellites scheduling," *Computers & Operations Research*, vol. 100, pp. 12-25, 2018, doi: 10.1016/j.cor.2018.06.020.

[8] J. Li, J. Zhu, D. Xu, J. Wang, Z. Li, and K. Zhang, "Earth observation satellite scheduling with interval-varying profits," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 6, pp. 8273-8288, 2024, doi: 10.1109/TAES.2024.3427090.

[9] F. Yao, Y. Chen, L. Wang, Z. Chang, P.-Q. Huang, and Y. Wang, "A bilevel evolutionary algorithm for large-scale multiobjective task scheduling in multiagile earth observation satellite systems," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 54, no. 6, pp. 3512-3524, 2024, doi: 10.1109/TSMC.2024.3359265.

[10] J. Qin, X. Bai, G. Du, J. Liu, N. Peng, and M. Xu, "Multisatellite scheduling for moving targets using the enhanced hybrid genetic simulated annealing algorithm and observation strip selection," *IEEE Transactions on Aerospace and Electronic Systems*, vol. 60, no. 5, pp. 5773-5800, 2024, doi: 10.1109/TAES.2024.3397958.

[11] H. Wang, W. Huang, S. Magnusson, T. Lindgren, R. Wang, and Y. Song, "A strategy fusion-based multiobjective optimization approach for agile earth observation satellite scheduling problem," *IEEE Transactions on Geoscience and Remote Sensing*, vol. 62, pp. 1-14, 2024, doi: 10.1109/TGRS.2024.3472749.

[12] C. Blum, J. Puchinger, G. R. Raidl, and A. Roli, "Hybrid metaheuristics in combinatorial optimization: A survey," *Applied Soft Computing*, vol. 11, no. 6, pp. 4135-4151, 2011, doi: 10.1016/j.asoc.2011.02.032.

[13] J. Fan, Y. Li, J. Xie, C. Zhang, W. Shen, and L. Gao, "A hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling problem," *IEEE Transactions on Cybernetics*, vol. 53, no. 3, pp. 1752-1764, 2023, doi: 10.1109/TCYB.2021.3120875.

[14] Z. Shu, A. Song, G. Wu, and W. Pedrycz, "Variable reduction strategy integrated variable neighborhood search and NSGA-II hybrid algorithm for emergency material scheduling," *Complex System Modeling and Simulation*, vol. 3, no. 2, pp. 83-101, 2023, doi: 10.23919/CSMS.2023.0006.

[15] Y. Rocha, G. O. Chagas, L. C. Coelho, and A. Subramanian, "The integrated agile earth observation satellite scheduling problem," *Computers & Operations Research*, vol. 184, p. 107212, 2025, doi: 10.1016/j.cor.2025.107212.

[16] F. Hutter, H. H. Hoos, K. Leyton-Brown, and T. Stutzle, "ParamILS: An automatic algorithm configuration framework," *Journal of Artificial Intelligence Research*, vol. 36, pp. 267-306, 2009, doi: 10.1613/jair.2861.

[17] F. Hutter, H. H. Hoos, and K. Leyton-Brown, "Sequential model-based optimization for general algorithm configuration," in *Learning and Intelligent Optimization*, Lecture Notes in Computer Science, vol. 6683, pp. 507-523, Springer, 2011, doi: 10.1007/978-3-642-25566-3_40.

[18] M. Lopez-Ibanez, J. Dubois-Lacoste, L. Perez Caceres, M. Birattari, and T. Stutzle, "The irace package: Iterated racing for automatic algorithm configuration," *Operations Research Perspectives*, vol. 3, pp. 43-58, 2016, doi: 10.1016/j.orp.2016.09.002.

[19] E. K. Burke, M. Gendreau, M. Hyde, G. Kendall, G. Ochoa, E. Ozcan, and R. Qu, "Hyper-heuristics: A survey of the state of the art," *Journal of the Operational Research Society*, vol. 64, no. 12, pp. 1695-1724, 2013, doi: 10.1057/jors.2013.71.

[20] Y. Wang, B. Xin, B. Liu, and Q. Wang, "Automated design of collaboration-based hybrid metaheuristics," *IEEE Transactions on Cybernetics*, vol. 54, no. 12, pp. 7877-7890, 2024, doi: 10.1109/TCYB.2024.3412997.

[21] H. Lei, X. Lin, L. He, and Y. Chen, "A random-key hybrid metaheuristic algorithm with dynamic task reassignment for large-scale multi-satellite scheduling," 2025, submitted for publication.

[22] E.-G. Talbi, *Metaheuristics: From Design to Implementation*. Hoboken, NJ, USA: Wiley, 2009.

[23] K. Socha and M. Dorigo, "Ant colony optimization for continuous domains," *European Journal of Operational Research*, vol. 185, no. 3, pp. 1155-1173, 2008, doi: 10.1016/j.ejor.2006.06.046.

[24] S. Das and P. N. Suganthan, "Differential evolution: A survey of the state-of-the-art," *IEEE Transactions on Evolutionary Computation*, vol. 15, no. 1, pp. 4-31, 2011, doi: 10.1109/TEVC.2010.2059031.

[25] R. Tanabe and A. S. Fukunaga, "Improving the search performance of SHADE using linear population size reduction," in *Proc. IEEE Congress on Evolutionary Computation (CEC)*, 2014, pp. 1658-1665, doi: 10.1109/CEC.2014.6900380.

[26] A. Santiago, B. Dorronsoro, A. J. Nebro, J. J. Durillo, O. Castillo, and H. J. Fraire, "A novel multi-objective evolutionary algorithm with fuzzy logic based adaptive selection of operators: FAME," *Information Sciences*, vol. 471, pp. 233-251, 2019, doi: 10.1016/j.ins.2018.09.005.

[27] F. Zhao, W. Lei, W. Ma, Y. Liu, and C. Zhang, "An improved SPEA2 algorithm with adaptive selection of evolutionary operators scheme for multiobjective optimization problems," *Mathematical Problems in Engineering*, vol. 2016, Art. no. 8010346, pp. 1-20, 2016, doi: 10.1155/2016/8010346.
