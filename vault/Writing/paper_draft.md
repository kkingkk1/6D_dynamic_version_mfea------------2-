# Automatic Design of Collaboration-Based Hybrid Metaheuristics for Large-Scale Agile Earth Observation Satellite Scheduling

**Abstract**--The large-scale agile earth observation satellite task scheduling problem (LS-AEOSTSP) critically impacts time-sensitive observation missions for growing satellite constellations. The problem couples task selection, satellite assignment, visible-window placement, and attitude-constrained sequencing, presenting an NP-hard combinatorial challenge at operational constellation scales. While collaboration-based hybrid metaheuristics can balance exploration and exploitation, existing approaches—such as the state-of-the-art RK-HMA combining differential evolution and particle swarm optimization—rely on manually crafted, fixed collaboration structures. Manual design faces a prohibitive combinatorial configuration space and struggles to generalize across diverse mission distributions. To address these limitations, this paper recasts the design of collaboration-based hybrid optimizers as an automated structural search problem within a unified scheduling pipeline. We formulate a six-gene semantic chromosome and modular component libraries that govern parent algorithm selection, population operating levels, operating orders, and survivor selection rules, while retaining the random-key scheduling bridge and multi-satellite task reassignment architecture. An evolutionary configuration-search procedure on multi-scenario training instances automatically composes an effective hybrid optimizer (Auto-Hybrid), which discovers an adaptive collaboration scheme combining estimation of distribution algorithms and genetic algorithms. Extensive comparative experiments across sixteen benchmark scenarios (500–10,000 tasks and 5–100 satellites) demonstrate that Auto-Hybrid consistently outperforms or matches RK-HMA and five classic metaheuristics. On the ten regional scenarios, Auto-Hybrid achieves higher mean profit rates across all instances with a macro mean increase of 0.93 percentage points over RK-HMA (up to 2.99 percentage points in dense instances), while maintaining competitive, near-optimal solution quality on global scenarios (97.00% versus 97.01%). These results demonstrate that automated structural search can effectively discover problem-tailored hybrid metaheuristics superior to manual expert designs for large-scale agile satellite scheduling.

**Index Terms**--Agile earth observation satellites, multi-satellite scheduling, automated algorithm design, collaboration-based hybrid metaheuristics, evolutionary search

# I. Introduction

Agile earth observation satellites (AEOS) with high attitude maneuverability have become a key platform for acquiring space-based information, supporting applications such as disaster monitoring, mapping, and reconnaissance [1]. Over the past two decades, the number of earth observation satellites in orbit has grown rapidly. Wang et al. [1] reported that AEOS scheduling has been actively studied since the early 2000s, driven by the deployment of increasingly agile platforms such as Pléiades, WorldView, and Jilin-1. Du et al. [3] noted that the growing number of satellites and observation requests has made large-scale multi-satellite scheduling a practical challenge. Efficient scheduling is thus needed to manage large constellations and maximize fulfilled observation requests.

The large-scale agile earth observation satellite task scheduling problem (LS-AEOSTSP) is harder than the classic earth observation satellite task scheduling problem (EOSTSP). As illustrated in Fig. 1, unlike conventional EOS that can only observe targets directly below their ground track, AEOS can rotate along the roll, pitch, and yaw axes to steer their imaging payloads toward off-nadir targets. This three-axis maneuverability enlarges the set of visible time windows (VTWs) for each task, but introduces time-dependent attitude transition constraints between consecutive observations. As constellations scale to tens or hundreds of satellites, the joint decision space—task-satellite assignment, VTW selection, and start time determination—grows combinatorially, making exact methods intractable for practical instances [4], [5].

![Comparison of observation modes between non-agile EOS and AEOS](figures/agile_satellite_observation_modes.png)

**Fig. 1.** Comparison of observation modes between non-agile EOS and AEOS [6].

Prior work on agile satellite scheduling spans several methodological lines. Survey and exact-optimization studies clarify the main modeling variants and constraint structures: Wang et al. [1] reviewed two decades of AEOS scheduling formulations and methods, Chen et al. [2] built a mixed-integer linear programming model for multi-satellite scheduling, and Peng et al. [4], [5] developed exact formulations that exploit the time-dependent profit and transition-time structure of the problem. Because exact methods do not scale to large instances, metaheuristics have become the dominant practical approach.

Adaptive large neighborhood search (ALNS) and its variants are well studied. Liu et al. [6] designed problem-specific removal and insertion operators for time-dependent transition times, and He et al. [7] extended ALNS to multiple agile satellites with a dynamic task-allocation mechanism. Population-based evolutionary algorithms have also been applied: Yao et al. [9] proposed a bilevel evolutionary algorithm for large-scale multiobjective task scheduling, Qin et al. [10] combined simulated annealing with a genetic algorithm for multisatellite scheduling of moving targets, and Wang et al. [11] designed a strategy fusion-based multi-objective optimization approach. Related methods address further variants, including interval-varying profits [8] and the integrated agile scheduling problem [15]. However, most existing methods rely on a single algorithmic paradigm, limiting the balance between exploration and exploitation in the LS-AEOSTSP search space [1].

Hybrid metaheuristics, which combine the strengths of multiple search strategies within a unified framework, are effective for combinatorial optimization. Blum et al. [12] surveyed hybrid metaheuristic paradigms and reported numerous successful applications where hybridization improved solution quality. In the domain of scheduling, Fan et al. [13] proposed a hybrid evolutionary algorithm using two solution representations for hybrid flow-shop scheduling, and Shu et al. [14] integrated variable neighborhood search with NSGA-II for emergency material scheduling. For LS-AEOSTSP, our previous work proposed RK-HMA [21], which connects continuous optimizers with discrete task sequences through random-key encoding, applies DE/rand/1 and PSO sequentially to the full shared population with elitist-truncation survivor selection, and uses dynamic task reassignment to coordinate satellites. RK-HMA shows that hybridization is effective for large-scale satellite scheduling. However, this manual design process has two main limitations: (i) the design cost is high—each structural decision requires expert knowledge, and changing any component requires re-design and re-validation with no guarantee that the resulting structure remains effective when the scenario changes in scale or task distribution; and (ii) the design space of collaboration-based hybrids is large—different parent algorithms, OL choices, OO choices, and survivor-selection policies can be combined in many ways, making it difficult for manual exploration to identify well-performing configurations.

The central question is therefore an automatic-design question: can the hybrid structure itself be composed for the scheduling pipeline? Algorithm configuration methods such as ParamILS, SMAC, and irace tune parameterized algorithms over training instances [16]-[18]. Hyper-heuristics search over heuristics or heuristic components instead of directly searching the solution space [19]. Automated algorithm design goes further by searching algorithm structures rather than only tuning parameters or choosing among fixed algorithms. Recent work on automated design of collaboration-based hybrid metaheuristics treats hybrid-optimizer design as a meta-optimization problem and uses a top-down template to generate collaboration-based hybrid algorithms [20].

This paper studies that question for LS-AEOSTSP by making the inner single-satellite optimizer a searchable structural layer. A six-gene chromosome encodes the collaboration structure—parent algorithms, OL, OO, and survivor selection—while the random-key scheduling bridge and cross-satellite reassignment layer remain fixed and provide a common evaluation environment. Each candidate chromosome is decoded into an executable optimizer and evaluated through the coupled scheduling pipeline, a setting not addressed by prior automated-design work. The detailed encoding is introduced in Section III-C.

The main contributions are as follows.

1. We propose an automatic design framework for collaboration-based hybrid metaheuristics tailored to LS-AEOSTSP. The inner single-satellite optimizer is composed by search rather than fixed by manual design.

2. We formulate a six-gene semantic chromosome and its component libraries. The chromosome exposes the collaboration structure—parent algorithms, OL, OO, and survivor selection—as interpretable structural decisions that the search can recombine.

3. We evaluate the composed optimizer on ten regional and six global benchmark scenarios with five runs per method. Auto-Hybrid has the highest displayed regional mean on all ten scenarios, including one tie, and a regional macro mean 0.93 percentage points above RK-HMA. The global comparison and the retained runtime records identify the limits of this descriptive evidence.

The remaining sections are organized as follows. Section II defines the scheduling problem. Section III describes the automatic hybrid-design framework. Section IV reports the experiments. Section V concludes the paper.

# II. Problem Description

## A. Problem Description

Given a set $T=\{t_1,\ldots,t_n\}$ of $n$ tasks and a set $AEOS=\{aeos_1,\ldots,aeos_m\}$ of $m$ agile earth observation satellites. Each task $t_i$ is associated with a geographic location (latitude and longitude), an imaging duration $l_i$, and a profit $p_i$, which are provided by the user. Each satellite $aeos_j$ is represented by its orbital parameters, including the semi-major axis, eccentricity, inclination, right ascension of the ascending node, argument of perigee, and true anomaly. Given the target location and satellite orbital parameters, the visible time windows (VTWs) of each target associated with its visible satellites are obtained through access calculation. Each VTW $w_{ijk}$ has a start time $st_{ijk}$, an end time $et_{ijk}$, and a length $d_{ijk}$. The roll, pitch, and yaw angles of the imaging payload at the corresponding observation times are also available. The notations used throughout this paper are summarized in Table I.

\clearpage
**Table I**

Notation for LS-AEOSTSP.

\begin{longtable}{@{}>{\centering\arraybackslash}p{(\linewidth - 2\tabcolsep) * \real{0.4000}} >{\centering\arraybackslash}p{(\linewidth - 2\tabcolsep) * \real{0.6000}}@{}}
\toprule
\textbf{Notation} & \textbf{Description} \\
\midrule
\endhead
\bottomrule
\endlastfoot
\(T\) & Tasks set \\
\(n\) & Number of tasks \\
\(\mathrm{AEOS}\) & Satellites set \\
\(m\) & Number of satellites \\
\(p_i\) & Profit of task \(t_i\) \\
\(l_i\) & Imaging duration of task \(t_i\) \\
\(\chi_{jt}\) & Rolling angle of \(\mathrm{aeos}_j\) at time \(t\) \\
\(\pi_{jt}\) & Pitching angle of \(\mathrm{aeos}_j\) at time \(t\) \\
\(\phi_{jt}\) & Yawing angle of \(\mathrm{aeos}_j\) at time \(t\) \\
\(w_{ijk}\) & \(k\)-th VTW for task \(t_i\) on satellite \(\mathrm{aeos}_j\) \\
\(W_{ij}\) & VTWs set for task \(t_i\) on satellite \(\mathrm{aeos}_j\) \\
\(\lvert W_{ij}\rvert\) & Number of VTWs for task \(t_i\) on satellite \(\mathrm{aeos}_j\) \\
\(st_{ijk}\) & Start time of \(w_{ijk}\) \\
\(et_{ijk}\) & End time of \(w_{ijk}\) \\
\(d_{ijk}\) & Length of \(w_{ijk}\) \\
\(c_i\) & Specified minimum imaging quality of task \(t_i\) \\
\end{longtable}

Due to the limited number of satellites compared with the number of tasks, it is difficult to execute all tasks. Therefore, the LS-AEOSTSP aims to determine the imaging times of a subset of tasks within their VTWs while maximizing the total observation profit, subject to the following assumptions.

1. Each task is a meta-task that can be directly executed by a satellite. Complex tasks such as area target coverage or moving target tracking are not considered, because they can be decomposed into meta-tasks through strip partitioning.
2. Power-capacity and storage-capacity constraints are not modeled. In normal operation, satellites charge through solar power and transmit data to ground stations or relay satellites to release onboard storage.
3. Each satellite is equipped with a single imaging payload and can execute at most one task at a time.
4. Once executed, a task cannot be aborted, and each task is executed at most once.

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

The proposed framework follows the top-down design idea of AutoHyb [20], where designing a collaboration-based hybrid optimizer is formulated as a meta-optimization problem. AutoHyb treats the optimizer structure as a searchable design object: each candidate design scheme specifies which parent algorithms to combine (e.g., DE, PSO, EDA) and how to hybridize them through a set of hybridization factors: the operating level (OL), which determines which subpopulation of the shared population each parent algorithm modifies; the operating order (OO), which determines the information dependency between the two parent algorithms; and survivor selection, which determines how newly generated and existing individuals compete for the next generation. AutoHyb was developed and validated on general numerical and combinatorial benchmarks, where each candidate optimizer can be evaluated with modest computational cost. We adapt this idea to the coupled, discrete LS-AEOSTSP, where every candidate solution must be evaluated through a full scheduling process that assigns tasks to satellites, selects visible time windows, determines observation timing, and computes attitude-dependent transition times—making each fitness evaluation far more expensive and the design problem considerably harder than on numerical benchmarks.

This paper instantiates that template for LS-AEOSTSP. The target scheduling pipeline is inherited from RK-HMA [21], which has two layers: an outer multi-satellite layer that handles task-to-satellite allocation and cross-satellite reassignment of unscheduled tasks, and an inner single-satellite optimizer that evolves the task sequence for each satellite independently using a random-key encoding—continuous keys define task priorities, and a greedy insertion decoder maps each random-key vector to a feasible schedule by sorting tasks and inserting them into visible time windows while respecting attitude-transition constraints.

We fix the outer layer and the decoder unchanged from RK-HMA; the automatic-design layer searches only the collaboration structure of the inner single-satellite optimizer—parent algorithms, their OL choices, the OO choice, and survivor selection. We further restrict this design object to pairwise collaboration between exactly two parent algorithms. This restriction serves three purposes: (1) it keeps the design space tractable, and adding a third parent algorithm would expand this by another order of magnitude; (2) it ensures a well-defined collaboration structure—two parent algorithms form a single information-flow edge with explicit OO semantics and information dependency; hybridizing three or more parent algorithms could potentially offer greater search diversity, but would introduce multiple edges with cyclic dependencies or complex scheduling among components, requiring additional design dimensions that are beyond the scope of this work; (3) it supports a matched comparison with the manually designed RK-HMA baseline, which is itself a hybrid with two parent algorithms. This scoping keeps each candidate optimizer cheap enough to evaluate through the expensive scheduling pipeline.

In our design, each offspring is generated by either crossover or mutation. The two operators are mutually exclusive alternatives with complementary probabilities $p_c$ and $p_m=1-p_c$. This exclusive choice ensures that each offspring can be unambiguously attributed to a single operator, preserving a clean interpretation of their individual effects. The design stage searches over a training subset with a reduced inner budget. Chromosomes are ranked by a multi-scenario fitness that normalizes scheduling profit across scenarios, as defined in Section III-E.

As shown in Fig. 2, the resulting workflow has five levels:

1. Component libraries define the admissible parent algorithms and hybridization factors.
2. A semantic chromosome selects one component for each algorithmic role.
3. A decoder maps the chromosome to an executable single-satellite optimizer.
4. The generated optimizer is embedded in the fixed multi-satellite scheduling pipeline.
5. An outer evolutionary search ranks chromosomes by their measured scheduling profit.

![Framework of the proposed Auto-Hybrid](figures/automatic_hybrid_design_flow.png)

**Fig. 2.** Framework of the proposed Auto-Hybrid.

## B. Component Libraries for Automatic Design

Based on the design principle above, the searchable collaboration structure is defined by four component libraries. Tables II–V list the admissible realization forms for parent algorithms, OL, OO, and survivor selection. In this section, an inner individual
denotes one random-key solution, whereas a design candidate denotes one six-gene chromosome. Only these structural choices are encoded; the numerical parameters of the library algorithms are held fixed during the design comparison. This separation keeps the search focused on collaboration structure.

The parent-algorithm library collects established metaheuristics that can operate on the shared random-key representation, chosen to span complementary search behaviors. It includes population-based evolutionary search through a genetic algorithm (GA) [22]; swarm intelligence through particle swarm optimization (PSO) [22]; probabilistic model building through an estimation-of-distribution algorithm (EDA) [22] and a continuous ant colony optimization (ACO) [23]; differential evolution in three mutation forms, DE/rand/1, DE/best/1, and DE/current-to-rand/1 [24]; a bee-colony algorithm (ABC) [22]; trajectory-based simulated annealing (SA) [22]; the success-history adaptive DE with linear population reduction (L-SHADE) [25]; and an adaptive large neighborhood search (ALNS) [6], [7] drawn from the scheduling literature. This mix lets the design stage combine exploratory, exploitative, model-based, and neighborhood-based dynamics. Table II summarizes the eleven parent algorithms.

**TABLE II: PARENT-ALGORITHM LIBRARY.**

| ID | Parent algorithm | Brief description |
|--:|-----|------------|
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

The operating level determines which inner random-key solutions of the shared population each parent algorithm is allowed to modify. The seven realization forms below span population-, subpopulation-, and individual-level updates. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table IX.

| ID | Operating level | Realization form |
|--:|-----|------------|
| 0 | Full population | The parent algorithm works on all inner random-key solutions in the current population. |
| 1 | Top-subset selection | The parent algorithm works on a fixed high-fitness subpopulation of inner solutions with ratio $r_{\text{sub}}$. |
| 2 | Mixed-subset selection | The parent algorithm works on a subpopulation mixing the top fraction $r_{\text{mix}}$ with random inner solutions. |
| 3 | Random-decay selection | The parent algorithm works on a random subpopulation of inner solutions whose ratio decays from $r_{\text{dec}}$ over iterations. |
| 4 | Above-mean selection | The parent algorithm works on inner solutions whose fitness is above the population mean. |
| 5 | Local-search focus | The parent algorithm focuses on the historical best inner solution. |
| 6 | Worst-repair focus | The parent algorithm focuses on the current worst inner solution. |

**TABLE IV: OPERATING-ORDER (OO) LIBRARY.**

The operating-order library specifies when the two parent algorithms are invoked and thereby determines their information dependency. Its realization forms comprise seven sequential options and one parallel option. Parameter symbols are included directly in the corresponding realization forms, and their values are reported in Table IX.

| ID | Operating order (OO) | OO type | Corresponding realization form |
|--:|------|----|------------|
| 0 | Sequential | Sequential | Parent algorithm 1 runs before parent algorithm 2 in each iteration. |
| 1 | Periodic switching | Sequential | The active parent algorithm switches every $T_{\text{sw}}$ iterations. |
| 2 | Stage-based switching | Sequential | Parent algorithm 1 runs through stage boundary $\tau_{\text{stage}}$; parent algorithm 2 runs afterward. |
| 3 | Best-no-improvement switching | Sequential | Switches after $T_{\text{best}}$ consecutive iterations without global-best improvement. |
| 4 | Process-no-improvement switching | Sequential | Switches after $T_{\text{proc}}$ consecutive iterations without improvement in the global best or mean fitness. |
| 5 | Diversity-based switching | Sequential | Routing depends on population diversity, checked every $T_{\text{div}}$ iterations against threshold $\theta_{\text{div}}$. |
| 7 | Adaptive-credit routing | Sequential | Parent algorithm 1 is selected with probability $p_1$ derived from recent improvement per evaluation cost; parent algorithm 2 with $p_2=1-p_1$. |
| 6 | Parallel | Parallel | Both parent algorithms generate candidates separately; candidates are merged. |

**TABLE V: SURVIVOR-SELECTION LIBRARY.**

The survivor-selection library determines how current and newly generated inner solutions compete to form the next population. Its four realization forms span deterministic truncation, pairwise-greedy replacement, stochastic tournament selection, and rank-weighted sampling, allowing the design search to vary the selection pressure applied to candidate solutions.

| ID | Survivor policy | Corresponding realization form |
|--:|-----|------------|
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

\begin{center}
\includegraphics[width=0.65\linewidth,keepaspectratio]{figures/semantic_hybrid_scheme_encoding.png}
\end{center}
\refstepcounter{figure}
\textbf{Fig. 3.} Six-gene semantic hybrid-scheme encoding.

Together, the six positions encode one structural collaboration scheme rather than a numerical parameter vector. This semantic layout makes the composed optimizer interpretable after search: each gene names a distinct algorithmic role.

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

The decoding step turns optimizer construction into part of the experiment. The inner single-satellite optimizer is generated from an evolvable semantic chromosome and evaluated inside the same scheduling pipeline.

## E. Evolutionary Configuration-Search Procedure

The design procedure evolves a population of optimizer chromosomes. Fitness is assigned to the scheduling profit obtained by the inner optimizer generated from each chromosome. Each chromosome is evaluated by running the decoded optimizer on the training scenarios with multiple independent runs per scenario. The design fitness aggregates the normalized scheduling profit across all training scenarios, where normalization by each scenario's total task profit prevents large-profit scenarios from dominating chromosome selection only because of scale. Algorithm 1 denotes this fitness as `designScore` to distinguish it from the inner scheduling objective.

Algorithm 1 summarizes the design-search procedure.

\begin{algorithm}
\caption{Evolutionary optimizer-design procedure}
\begin{algorithmic}[1]
\Statex \textbf{Input:} Training-scenario set $\mathcal{D}_{\mathrm{train}}$; component libraries $\mathcal{A}$, $\mathcal{U}$, $\mathcal{O}$, and $\mathcal{S}$; population size $N_d$; generation count $G_d$; repeat count $R$; crossover probability $p_c$; mutation probability $p_m=1-p_c$; search-budget ratio $\rho$; and full inner budget $B_{\mathrm{full}}(s)$ for each $s\in\mathcal{D}_{\mathrm{train}}$.
\Statex \textbf{Output:} Selected optimizer chromosome $\mathbf{h}^{\star}$.
\State For each $s\in\mathcal{D}_{\mathrm{train}}$, set $B_{\mathrm{design}}(s)\gets\max\{1,\operatorname{round}(\rho B_{\mathrm{full}}(s))\}$.
\State Initialize population $P_0$ with $N_d$ valid optimizer chromosomes.
\State Evaluate every $\mathbf{h}\in P_0$ using $\operatorname{designScore}(\mathbf{h};\{B_{\mathrm{design}}(s):s\in\mathcal{D}_{\mathrm{train}}\})$.
\State Set $\mathbf{h}^{\star}$ to the best chromosome in $P_0$.
\For{$t=1,\ldots,G_d$}
    \State Shuffle the chromosome indices in $P_{t-1}$.
    \For{each selected chromosome pair}
        \If{a random draw is at most $p_c$}
            \State Generate an offspring by one-point crossover.
        \Else
            \State Mutate a randomly selected nonempty subset of the six genes.
        \EndIf
        \State Repair duplicate parent-algorithm choices so that $h_0\ne h_1$.
        \State Add the offspring to $Q_t$.
    \EndFor
    \State Evaluate every offspring $\mathbf{h}\in Q_t$ using $\operatorname{designScore}(\mathbf{h};\{B_{\mathrm{design}}(s):s\in\mathcal{D}_{\mathrm{train}}\})$.
    \State Merge $P_{t-1}$ and $Q_t$.
    \State Select the top $N_d$ chromosomes by design fitness to form $P_t$.
    \State Update $\mathbf{h}^{\star}$ if a better chromosome is found.
\EndFor
\State \textbf{return} $\mathbf{h}^{\star}$.
\end{algorithmic}
\end{algorithm}

![One-point crossover and six-gene mutation of the 6D optimizer chromosome](figures/mfea_6d_crossover_mutation.png)

**Fig. 4.** Crossover and mutation of the semantic optimizer chromosome.

The complete evaluation follows a three-stage protocol that balances search efficiency with final accuracy. First, Algorithm 1 is executed five times independently on the training scenarios, with each chromosome evaluated using $R_d$ runs under the reduced budget $B_{\mathrm{design}}(s)$. This stage explores the design space quickly with coarse evaluations. Second, the top five distinct configurations from the final populations of the five independent runs are re-evaluated with $R_s$ runs per training scenario under the same reduced budget, and the configuration with the highest macro mean across the training scenarios is selected. This screening stage uses more runs to reduce stochastic noise when comparing promising candidates. Third, the selected configuration is evaluated under the full budget $B_{\mathrm{full}}(s)$ on all evaluation scenarios with $R_f$ runs per scenario to measure its true scheduling performance.

## F. Scheduling Execution Under a Designed Optimizer

Once $\Phi(\mathbf{h})$ is instantiated, each satellite is optimized through the standard random-key scheduling bridge inherited from RK-HMA. For a satellite with $D$ assigned tasks, the single-satellite optimizer maintains a population of $N$ random-key vectors, each of dimension $D$:

$$
X=\{\mathbf{x}^{(1)},\mathbf{x}^{(2)},\ldots,\mathbf{x}^{(N)}\}.
$$

Each vector is decoded by sorting its keys, and the sorted order gives a candidate task sequence. A greedy insertion decoder then places tasks one by one into their earliest feasible observation time following this priority order and computes the collected profit:

$$
f(\mathbf{x})=\sum_{t_i\in P_j} p_i,
$$

where $P_j$ is the feasible schedule constructed for satellite $aeos_j$.

After per-satellite schedules are generated, the fixed multi-satellite layer applies the RK-HMA dynamic reassignment procedure [21] to reconsider unscheduled tasks. It attempts four migration strategies in increasing order of intervention: standard migration inserts unscheduled tasks directly; replacement move removes a low-profit scheduled task to make room; swap move exchanges a scheduled task between two satellites; and bundle move clusters remaining unscheduled tasks by time proximity and migrates each group jointly. This layer is shared by all candidate chromosomes and is not part of the optimizer-design space.

# IV. Experimental Results

The simulator introduced in [7] generates the LS-AEOSTSP instances. The framework and its search-composed optimizer are implemented in Java. The recorded experiments use an Intel Core i7-14700KF CPU at 3.40 GHz and 64 GB of memory. The comparison combines retained runs and completed extension batches; the timing boundaries are specified below.

```{=latex}
\renewcommand{\thetable}{\Roman{table}}
\setcounter{table}{5}
```

## A. Evaluation and Training Scenarios

The evaluation comprises ten regional and six global instances containing 500–10,000 tasks and 5–100 satellites. Tables VI and VII list the current scenario order, also used in the figures. The regional set excludes the earlier 1000-task/20-satellite evaluation instance and includes the 2000-task/20-satellite instance. It also includes the 2000/10, 3000/20, 5000/50, and 6000/60 regional instances. The global set adds the 3000/30 and 4000/40 instances. Regional targets lie within $3^\circ\text{N}$–$53^\circ\text{N}$ and $74^\circ\text{E}$–$133^\circ\text{E}$; global targets follow the global-distribution generator. Imaging duration is an integer from 1 to 30 seconds, and task profit is an integer from 1 to 10.

Four separately generated regional instances are used for structural search and candidate screening (Table VIII). They have distinct instance identities and generation seeds from the evaluation instances. Some training and evaluation instances share task and satellite counts; the split is defined by instance identity, rather than by scale. The retained 1000/20 training instance is not the excluded evaluation instance.

```{=latex}
\begin{table}[H]
\centering
\small
\renewcommand{\arraystretch}{1.04}
\setlength{\tabcolsep}{4pt}
\caption{Regional experimental scenarios.}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrl@{}}
\toprule
Scenario & Tasks & Satellites & Planning interval \\
\midrule
R1 & 500 & 5 & 00:00:00--23:59:59 \\
R2 & 1000 & 10 & 00:00:00--11:59:59 \\
R3 & 2000 & 10 & 00:00:00--11:59:59 \\
R4 & 2000 & 20 & 00:00:00--11:59:59 \\
R5 & 3000 & 20 & 00:00:00--07:59:59 \\
R6 & 4000 & 40 & 00:00:00--05:59:59 \\
R7 & 5000 & 50 & 00:00:00--11:59:59 \\
R8 & 6000 & 60 & 00:00:00--05:59:59 \\
R9 & 8000 & 80 & 00:00:00--11:59:59 \\
R10 & 10000 & 100 & 06:00:00--11:59:59 \\
\bottomrule
\end{tabular*}
\end{table}
```

```{=latex}
\begin{table}[H]
\centering
\small
\renewcommand{\arraystretch}{1.04}
\setlength{\tabcolsep}{4pt}
\caption{Global experimental scenarios.}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrl@{}}
\toprule
Scenario & Tasks & Satellites & Planning interval \\
\midrule
G1 & 500 & 5 & 00:00:00--23:59:59 \\
G2 & 1000 & 10 & 12:00:00--23:59:59 \\
G3 & 2000 & 20 & 12:00:00--23:59:59 \\
G4 & 3000 & 30 & 12:00:00--19:59:59 \\
G5 & 4000 & 40 & 12:00:00--17:59:59 \\
G6 & 6000 & 60 & 12:00:00--17:59:59 \\
\bottomrule
\end{tabular*}
\end{table}
```

```{=latex}
\begin{table}[H]
\centering
\small
\renewcommand{\arraystretch}{1.04}
\setlength{\tabcolsep}{4pt}
\caption{Regional training instances used for structural search.}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}lrrl@{}}
\toprule
Training instance & Tasks & Satellites & Planning interval \\
\midrule
T1 & 500 & 5 & 00:00:00--23:59:59 \\
T2 & 1000 & 10 & 00:00:00--11:59:59 \\
T3 & 1000 & 20 & 00:00:00--11:59:59 \\
T4 & 4000 & 40 & 00:00:00--05:59:59 \\
\bottomrule
\end{tabular*}
\end{table}
```

## B. Baselines, Metrics, and Parameter Settings

Six baselines are taken from the updated RK-HMA benchmark [21]: R-ALNS, A-ALNS, HCGA, HPSO, HeDEA, and RK-HMA. R-ALNS [6] combines single-satellite ALNS with random task allocation. A-ALNS [7] uses adaptive cross-satellite task allocation. The adapted HCGA combines cellular genetic search and local refinement; HPSO combines particle swarm search and local refinement; HeDEA uses hierarchical encoding and dual-phase evolutionary search. The latter three are the adapted implementations used in the reference benchmark. RK-HMA [21] uses DE/rand/1 and PSO with sequential operating order, full-population operating level, and elitist-truncation survivor selection.

Auto-Hybrid is the retained configuration $[2,0,0,0,4,2]$: EDA and GA, full-population operating levels for both parents, process-no-improvement switching, and pairwise-greedy survivor selection. Table IX gives its search and replay settings. Each scenario-method cell contains five runs. The 80 Auto-Hybrid records comprise 45 full-speed reruns on nine scenarios and 35 retained runs on the other seven. The reruns preserve the original configuration, actual seeds, population sizes, and evaluation budgets; all 45 reported profits are unchanged. The baseline set contains 480 records. HCGA uses the latest common budget of 95,000 fitness evaluations in every scenario, population size 100, crossover probability 0.99, mutation probability 0.01, and generation and stagnation caps of 2000. Its budget was chosen by runtime calibration against historical RK-HMA results and is not an equal-budget control.

Profit rate is defined as

$$
PR = \frac{F(P_S)}{F(P_A)} \times 100\% \tag{20}
$$

where $F(P_S)$ is scheduled-task profit and $F(P_A)$ is total task profit. The Auto-Hybrid logs retain a small scheduling-slack reward in the reported numerator; this can produce a value slightly above 100% before rounding. Rates are displayed to two decimals, without interpreting such near-ceiling differences as quality gains. Twenty-nine baseline records are available only as rounded reported rates. Macro means weight scenarios equally.

The baseline batches use their fixed-table seed history. Auto-Hybrid retains the actual seeds from its native200042 profile and documented seed-table extensions. Actual seeds differ between the two sets, so corresponding run indices do not form paired observations. The 45 reruns use the accelerated implementation, Normal process priority, and 28 threads, with one JVM active at a time and no warmup. The other 35 Auto-Hybrid records and the baselines retain their historical runtime conditions. The comparisons describe these available results and do not isolate the effects of structure, implementation changes, or resource settings.

```{=latex}
\begin{table}[H]
\centering
\small
\renewcommand{\arraystretch}{1.05}
\setlength{\tabcolsep}{4pt}
\caption{Design-search and replay settings.}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}>{\raggedright\arraybackslash}p{0.42\linewidth}>{\raggedright\arraybackslash}p{0.13\linewidth}>{\raggedright\arraybackslash}p{0.37\linewidth}@{}}
\toprule
Setting & Symbol & Value \\
\midrule
Design population & $N_d$ & 35 \\
Outer generation cap & $G_{\max}$ & 25 \\
Early-stop minimum generations & $G_{\min}$ & 20 \\
Early-stop patience & $P$ & 5 \\
Early-stop minimum improvement & $\Delta$ & 0.001 \\
Outer evaluation repeats & $R_d$ & 2 \\
Candidate-screen repeats per training scenario & $R_s$ & 5 \\
Final replay runs per scenario & $R_f$ & 5 \\
Search budget ratio & $\rho$ & 0.6 \\
Design crossover probability & $p_c$ & 0.3 \\
Design mutation probability & $p_m=1-p_c$ & 0.7 \\
Population size & $N_{\mathrm{pop}}$ & $2.5 \times \max(n_j)$ \\
Full inner budget & $B_{\mathrm{full}}$ & $100N_{\mathrm{pop}}$ \\
Top-subset ratio & $r_{\mathrm{sub}}$ & 0.5 \\
Mixed-subset top ratio & $r_{\mathrm{mix}}$ & 0.8 \\
Random-decay start ratio & $r_{\mathrm{dec}}$ & $0.5 \rightarrow 0.2$ \\
Stage-switch boundary ratio & $\tau_{\mathrm{stage}}$ & 0.5 \\
Periodic-switch period & $T_{\mathrm{sw}}$ & $\max\{1,\lceil0.05B_{\mathrm{full}}\rceil\}$ \\
Best-no-improvement patience & $T_{\mathrm{best}}$ & $\max\{1,\lceil0.05(B_{\mathrm{full}}-N_{\mathrm{pop}}+1)\rceil\}$ \\
Process-no-improvement patience & $T_{\mathrm{proc}}$ & $\max\{1,\lceil0.05B_{\mathrm{full}}\rceil\}$ \\
Diversity-switch check interval & $T_{\mathrm{div}}$ & $\max\{1,\lceil0.01B_{\mathrm{full}}\rceil\}$ \\
Diversity-switch threshold & $\theta_{\mathrm{div}}$ & 0.02 \\
Adaptive-credit window & $W_c$ & 8 \\
Adaptive-credit default routing ratio & $\rho_c$ & 0.5 \\
Tournament size & $k_{\mathrm{tour}}$ & 2 \\
\bottomrule
\end{tabular*}
\end{table}
```

## C. Comparison Results

Tables X and XI report the five-run mean profit rates and elapsed times separately for regional and global scenarios. Bold profit rates mark the highest displayed mean within a scenario, including ties after rounding to two decimals. Figs. 5 and 6 use the same scenario order and method colors. The tables provide exact displayed values; the figures show differences across instances.

On the ten regional instances, Auto-Hybrid has the highest displayed mean on nine instances and ties RK-HMA on R1 at 99.60%. Its regional macro mean is 57.12%, compared with 56.19% for RK-HMA, 50.12% for A-ALNS, 46.15% for R-ALNS, 44.52% for HPSO, 43.00% for HeDEA, and 42.03% for HCGA. The mean gap over RK-HMA is 0.93 percentage points, with a maximum of 2.99 points on R6 (4000 tasks, 40 satellites). The corresponding average gaps over A-ALNS and R-ALNS are 7.00 and 10.97 points, with maxima of 10.97 and 15.80 points on R7 (5000 tasks, 50 satellites).

The newly included R4 instance (2000 tasks, 20 satellites) gives mean profit rates of 59.86% for Auto-Hybrid and 58.62% for RK-HMA. On R10 (10,000 tasks, 100 satellites), the two means are 34.21% and 34.08%. Regional profit rates vary with the individual instance and planning interval; the observed gaps do not increase monotonically with task count.

On the six global instances, the Auto-Hybrid macro mean is 97.00%, close to the RK-HMA mean of 97.01%. The two methods tie at the displayed precision on G1, G2, G3, and G6. On G4, Auto-Hybrid obtains 94.99% and RK-HMA 95.01%; on G5, their means are 96.07% and 96.12%. HeDEA also displays 96.07% on G5 and 100.00% on G6. Auto-Hybrid therefore does not have the highest mean on every global instance. All seven methods have higher global than regional macro means, although HPSO and HCGA remain below the best methods on several global instances.

```{=latex}
\begingroup
\small
\renewcommand{\arraystretch}{1.03}
\setlength{\tabcolsep}{4pt}
\setlength{\LTleft}{0pt}
\setlength{\LTright}{0pt}
\makeatletter
\renewcommand{\LT@makecaption}[3]{\LT@mcol\LT@cols c{\hbox to\z@{\hss\parbox[t]{\linewidth}{\sffamily\small #1{\textbf{#2}\par}#3\par\vspace{6pt}}\hss}}}
\makeatother
\begin{longtable}{@{}p{0.12\linewidth}p{0.28\linewidth}>{\raggedleft\arraybackslash}p{0.25\linewidth}>{\raggedleft\arraybackslash}p{0.25\linewidth}@{}}
\caption{Mean profit rates and elapsed times on regional scenarios (five runs per method).}\\
\toprule
Scenario & Algorithm & Profit rate (\%) & Elapsed (s) \\
\midrule
\endfirsthead
\multicolumn{4}{@{}l}{\small\sffamily\textbf{Table \thetable} (continued)}\\
\toprule
Scenario & Algorithm & Profit rate (\%) & Elapsed (s) \\
\midrule
\endhead
\midrule
\multicolumn{4}{r@{}}{\small Continued on next page}\\
\endfoot
\bottomrule
\endlastfoot
R1 & R-ALNS & 94.47 & 7.33 \\*
 & A-ALNS & 95.39 & 7.01 \\*
 & HCGA & 94.58 & 13.92 \\*
 & HPSO & 96.58 & 8.37 \\*
 & HeDEA & 98.66 & 8.86 \\*
 & RK-HMA & \textbf{99.60} & 6.12 \\*
 & Auto-Hybrid & \textbf{99.60} & 5.57 \\
\midrule
R2 & R-ALNS & 36.91 & 11.00 \\*
 & A-ALNS & 41.95 & 11.90 \\*
 & HCGA & 44.14 & 15.40 \\*
 & HPSO & 41.73 & 7.98 \\*
 & HeDEA & 44.04 & 36.54 \\*
 & RK-HMA & 47.50 & 4.95 \\*
 & Auto-Hybrid & \textbf{48.17} & 4.40 \\
\midrule
R3 & R-ALNS & 25.76 & 32.20 \\*
 & A-ALNS & 30.90 & 32.89 \\*
 & HCGA & 29.40 & 32.35 \\*
 & HPSO & 29.10 & 25.23 \\*
 & HeDEA & 29.24 & 110.68 \\*
 & RK-HMA & 34.09 & 19.46 \\*
 & Auto-Hybrid & \textbf{34.92} & 16.15 \\
\midrule
R4 & R-ALNS & 45.42 & 42.09 \\*
 & A-ALNS & 49.23 & 50.66 \\*
 & HCGA & 48.76 & 56.77 \\*
 & HPSO & 48.67 & 49.01 \\*
 & HeDEA & 40.69 & 180.72 \\*
 & RK-HMA & 58.62 & 19.84 \\*
 & Auto-Hybrid & \textbf{59.86} & 14.90 \\
\midrule
R5 & R-ALNS & 20.81 & 54.30 \\*
 & A-ALNS & 23.82 & 62.78 \\*
 & HCGA & 20.59 & 39.07 \\*
 & HPSO & 23.43 & 52.61 \\*
 & HeDEA & 17.54 & 212.89 \\*
 & RK-HMA & 27.66 & 38.93 \\*
 & Auto-Hybrid & \textbf{28.12} & 32.95 \\
\midrule
R6 & R-ALNS & 53.67 & 169.02 \\*
 & A-ALNS & 59.70 & 213.19 \\*
 & HCGA & 48.30 & 157.48 \\*
 & HPSO & 48.09 & 214.00 \\*
 & HeDEA & 44.12 & 796.86 \\*
 & RK-HMA & 63.95 & 9.45 \\*
 & Auto-Hybrid & \textbf{66.94} & 7.77 \\
\midrule
R7 & R-ALNS & 65.39 & 130.54 \\*
 & A-ALNS & 70.22 & 196.35 \\*
 & HCGA & 49.39 & 558.40 \\*
 & HPSO & 56.67 & 189.55 \\*
 & HeDEA & 58.71 & 673.62 \\*
 & RK-HMA & 79.59 & 11.03 \\*
 & Auto-Hybrid & \textbf{81.19} & 9.57 \\
\midrule
R8 & R-ALNS & 51.27 & 165.66 \\*
 & A-ALNS & 56.00 & 243.12 \\*
 & HCGA & 36.79 & 632.50 \\*
 & HPSO & 43.14 & 224.14 \\*
 & HeDEA & 42.21 & 1008.71 \\*
 & RK-HMA & 65.62 & 14.66 \\*
 & Auto-Hybrid & \textbf{66.84} & 10.69 \\
\midrule
R9 & R-ALNS & 40.66 & 325.99 \\*
 & A-ALNS & 43.61 & 545.98 \\*
 & HCGA & 29.34 & 865.49 \\*
 & HPSO & 34.25 & 490.69 \\*
 & HeDEA & 33.43 & 2257.98 \\*
 & RK-HMA & 51.22 & 81.23 \\*
 & Auto-Hybrid & \textbf{51.40} & 46.40 \\
\midrule
R10 & R-ALNS & 27.13 & 435.24 \\*
 & A-ALNS & 30.41 & 363.74 \\*
 & HCGA & 19.01 & 1070.38 \\*
 & HPSO & 23.55 & 561.84 \\*
 & HeDEA & 21.36 & 3177.28 \\*
 & RK-HMA & 34.08 & 108.52 \\*
 & Auto-Hybrid & \textbf{34.21} & 87.13 \\
\end{longtable}
\endgroup
```

```{=latex}
\begingroup
\small
\renewcommand{\arraystretch}{1.03}
\setlength{\tabcolsep}{4pt}
\setlength{\LTleft}{0pt}
\setlength{\LTright}{0pt}
\makeatletter
\renewcommand{\LT@makecaption}[3]{\LT@mcol\LT@cols c{\hbox to\z@{\hss\parbox[t]{\linewidth}{\sffamily\small #1{\textbf{#2}\par}#3\par\vspace{6pt}}\hss}}}
\makeatother
\begin{longtable}{@{}p{0.12\linewidth}p{0.28\linewidth}>{\raggedleft\arraybackslash}p{0.25\linewidth}>{\raggedleft\arraybackslash}p{0.25\linewidth}@{}}
\caption{Mean profit rates and elapsed times on global scenarios (five runs per method).}\\
\toprule
Scenario & Algorithm & Profit rate (\%) & Elapsed (s) \\
\midrule
\endfirsthead
\multicolumn{4}{@{}l}{\small\sffamily\textbf{Table \thetable} (continued)}\\
\toprule
Scenario & Algorithm & Profit rate (\%) & Elapsed (s) \\
\midrule
\endhead
\midrule
\multicolumn{4}{r@{}}{\small Continued on next page}\\
\endfoot
\bottomrule
\endlastfoot
G1 & R-ALNS & 99.88 & 0.30 \\*
 & A-ALNS & \textbf{99.89} & 0.89 \\*
 & HCGA & \textbf{99.89} & 10.96 \\*
 & HPSO & \textbf{99.89} & 3.10 \\*
 & HeDEA & \textbf{99.89} & 1.08 \\*
 & RK-HMA & \textbf{99.89} & 1.27 \\*
 & Auto-Hybrid & \textbf{99.89} & 0.97 \\
\midrule
G2 & R-ALNS & 92.22 & 2.99 \\*
 & A-ALNS & 92.52 & 3.86 \\*
 & HCGA & 92.41 & 24.49 \\*
 & HPSO & 92.50 & 7.97 \\*
 & HeDEA & 92.57 & 18.07 \\*
 & RK-HMA & \textbf{92.59} & 1.25 \\*
 & Auto-Hybrid & \textbf{92.59} & 1.00 \\
\midrule
G3 & R-ALNS & 97.86 & 11.37 \\*
 & A-ALNS & 98.33 & 14.95 \\*
 & HCGA & 97.37 & 72.47 \\*
 & HPSO & 97.02 & 28.13 \\*
 & HeDEA & 98.43 & 25.88 \\*
 & RK-HMA & \textbf{98.44} & 2.48 \\*
 & Auto-Hybrid & \textbf{98.44} & 2.03 \\
\midrule
G4 & R-ALNS & 93.39 & 20.54 \\*
 & A-ALNS & 94.07 & 27.84 \\*
 & HCGA & 92.18 & 121.17 \\*
 & HPSO & 91.27 & 53.26 \\*
 & HeDEA & 94.78 & 51.98 \\*
 & RK-HMA & \textbf{95.01} & 4.86 \\*
 & Auto-Hybrid & 94.99 & 4.05 \\
\midrule
G5 & R-ALNS & 93.98 & 32.80 \\*
 & A-ALNS & 94.84 & 39.99 \\*
 & HCGA & 92.01 & 201.55 \\*
 & HPSO & 90.68 & 86.53 \\*
 & HeDEA & 96.07 & 76.50 \\*
 & RK-HMA & \textbf{96.12} & 1.84 \\*
 & Auto-Hybrid & 96.07 & 1.16 \\
\midrule
G6 & R-ALNS & 98.50 & 73.23 \\*
 & A-ALNS & 99.58 & 145.81 \\*
 & HCGA & 96.92 & 341.42 \\*
 & HPSO & 94.58 & 213.37 \\*
 & HeDEA & \textbf{100.00} & 93.37 \\*
 & RK-HMA & \textbf{100.00} & 2.63 \\*
 & Auto-Hybrid & \textbf{100.00} & 0.96 \\
\end{longtable}
\endgroup
```

Elapsed time uses the original solver boundary when all five solver records are available, and otherwise uses all five whole-process records if they have a precise timing boundary. Whole-process time includes JVM startup, data loading, solving, and output. Coarse polling records are not substituted for precise timing; a dash denotes an unavailable mean. A-ALNS on G1 uses the Windows process-creation-to-exit supplement with the same five seeds and unchanged profits. RK-HMA solver time excludes initial scene loading, and R-ALNS includes random allocation. Auto-Hybrid measures the complete scheduling evaluation, including reassignment and calibration, but excludes JVM startup, input loading, initial allocation, and subsequent result output. The new Auto-Hybrid times use precise elapsed-millisecond records from the replay entry. Timing boundaries, budgets, and runtime conditions differ across the full comparison.

The updated Auto-Hybrid regional elapsed means range from 4.40 to 87.13 seconds. Seven regional and two global scenarios were selected for rerunning because their earlier Auto-Hybrid means exceeded the recorded RK-HMA means. After the reruns, Auto-Hybrid has a lower recorded mean on all ten regional and six global instances. On R10, the means are 87.13 seconds for Auto-Hybrid and 108.52 seconds for RK-HMA; on G4 and G5, they are 4.05 versus 4.86 seconds and 1.16 versus 1.84 seconds. These are comparisons with existing RK-HMA records. The selected reruns, retained historical results, and different resource conditions do not establish a controlled computational advantage or an independent speed benefit from structural search.

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\includegraphics[width=0.96\linewidth,keepaspectratio]{figures/auto_hybrid_current16_regional.png}
\par\vspace{4pt}
\begin{minipage}{0.96\linewidth}\sffamily\small\textbf{Fig. 5.} Mean profit rates of seven algorithms on the ten regional scenarios in Table VI. Each bar averages five runs. Colors and scenario order follow the updated RK-HMA benchmark, with Auto-Hybrid added in orange. HCGA uses 95,000 evaluations per run; the comparison is descriptive.\end{minipage}
\end{minipage}
\end{center}
```

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\includegraphics[width=0.96\linewidth,keepaspectratio]{figures/auto_hybrid_current16_global.png}
\par\vspace{4pt}
\begin{minipage}{0.96\linewidth}\sffamily\small\textbf{Fig. 6.} Mean profit rates of seven algorithms on the six global scenarios in Table VII. Each bar averages five runs. Method colors and the zero-origin axis match Fig. 5; small differences are resolved in Table XI.\end{minipage}
\end{minipage}
\end{center}
```

## D. Designed-Optimizer Comparison

RK-HMA and Auto-Hybrid implement different inner collaboration structures within the same scheduling architecture. RK-HMA uses sequential DE/rand/1–PSO with elitist truncation; Auto-Hybrid uses EDA–GA with process-no-improvement switching and pairwise-greedy selection. Both use full-population operating levels. The scheduling bridge and reassignment procedures are fixed during structural search, but the reused comparison records do not establish identical executable kernels across batches.

Fig. 7 shows all five observations for both methods on each regional instance. Each panel has an independent vertical scale. Auto-Hybrid sample standard deviations range from 0.026 to 0.289 percentage points. The displayed means tie on R1, and Auto-Hybrid means exceed RK-HMA on R2–R10; the widest mean gap occurs on R6. The figure shows the distributions of the available seed samples, rather than paired differences. A same-kernel, same-budget replay with common actual seeds would be needed to attribute these differences to structural search or to compare computational efficiency.

```{=latex}
\begin{center}
\begin{minipage}{\linewidth}
\centering
\includegraphics[width=0.96\linewidth,height=0.84\textheight,keepaspectratio]{figures/rk_hma_auto_hybrid_current10_boxplots.png}
\par\vspace{4pt}
\begin{minipage}{0.96\linewidth}\sffamily\small\textbf{Fig. 7.} Five-run profit-rate distributions for RK-HMA and Auto-Hybrid on R1–R10. Dots show individual runs; boxes span the first and third quartiles, center lines show medians, and whiskers extend to observations within 1.5 interquartile ranges. Independent vertical scales resolve local differences and must not be used to compare gap sizes across panels. Actual seeds differ between methods.\end{minipage}
\end{minipage}
\end{center}
```

\clearpage
# V. Conclusion

This paper presented an automatic design framework for collaboration-based hybrid metaheuristics tailored to LS-AEOSTSP. A six-gene semantic chromosome represents parent algorithms, operating levels, operating order, and survivor selection. Evolutionary search composes the inner optimizer while the random-key scheduling bridge and cross-satellite reassignment procedures are fixed within the search pipeline. The retained configuration combines EDA and GA with full-population updates, process-no-improvement switching, and pairwise-greedy selection.

Five-run results on ten regional and six global instances cover 500–10,000 tasks and 5–100 satellites. Auto-Hybrid has the highest displayed regional mean on nine instances and ties on one, with a macro mean of 57.12% compared with 56.19% for RK-HMA. Its largest regional gap over RK-HMA is 2.99 percentage points. On the global instances, the macro means are 97.00% and 97.01%, and RK-HMA has slightly higher means on the two added instances. Because the comparison combines different seed histories, code snapshots, timing boundaries, and method-specific budgets, it supports a descriptive assessment of the selected optimizer rather than a causal or speed-superiority claim. Future work should first evaluate the selected structure under a common-kernel, common-seed protocol, then examine richer component libraries and resource-constrained scheduling variants.

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
