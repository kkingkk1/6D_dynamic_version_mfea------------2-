# Tasks: LLM-EC Reallocation Heuristic Evolution

## Phase 0: Foundation (Java side)

- [ ] 0.1 Read TargetSatelliteRanker source, extract current feature set as baseline descriptor JSON
- [ ] 0.2 Read ReplacementMoveEvaluator source, encode current candidate selection as baseline descriptor
- [ ] 0.3 Define FeatureDTO record (remaining_capacity, vtw_overlap_count, task_priority, slewing_cost, conflict_degree, observation_duration)
- [ ] 0.4 Add ScoringPolicy interface and ExpressionScoringPolicy (whitelisted DSL: +, -, *, /, sqrt, log, max, min)
- [ ] 0.5 Add EvaluateHeuristicDescriptor entry point; accepts --heuristic-file, --scenario, --seed, --budget; outputs JSON metrics

## Phase 1: MVP — TargetSatelliteRanker

- [ ] 1.1 Add optional ScoringPolicy hook to TargetSatelliteRanker.computeCheapScore(); default = current logic
- [ ] 1.2 Verify golden baseline: EvaluateHeuristicDescriptor with expert baseline descriptor matches existing RunSingleHybridConfig profit
- [ ] 1.3 Write Python DPEC evolution loop (pop_size=10, max_gen=20, elite_exchange_every=5)
- [ ] 1.4 Write LLM initialization prompt (problem desc + feature defs + slewing constraint context + example descriptor)
- [ ] 1.5 Implement staged racing (Stage 1: 1 small scenario, 1 seed; Stage 2: 2 scenarios, 3 seeds)
- [ ] 1.6 Run 20-generation evolution on training scenario; record best evolved vs expert baseline profit gap
- [ ] 1.7 Cross-validate best operator on holdout scenarios; confirm generalization

## Phase 2: Expand to Move Evaluators

- [ ] 2.1 Add ScoringPolicy hook to ReplacementMoveEvaluator.identifyReplaceableTasks()
- [ ] 2.2 Encode expert replacement scoring as baseline descriptor
- [ ] 2.3 Run DPEC evolution for replacement policy; combine with Phase 1 best ranker
- [ ] 2.4 Add ScoringPolicy hook to TaskAllocationCoordinator.buildPrioritizedUnscheduledTasks()
- [ ] 2.5 Add ScoringPolicy hooks to SwapMoveEvaluator and BundleMoveEvaluator (lower priority)

## Phase 3: Ablation and Paper Evidence

- [ ] 3.1 Baseline vs evolved: all scenario sizes 100–400 tasks, 50 runs each
- [ ] 3.2 Ablation A: DPEC vs single-population LLM-EC (verify dual-population contribution)
- [ ] 3.3 Ablation B: with FNLE vs without FNLE in crossover prompt
- [ ] 3.4 Ablation C: TargetSatelliteRanker-only vs TargetSatelliteRanker + ReplacementMoveEvaluator
- [ ] 3.5 Cross-validation: 5-fold, operators from source scenarios applied to target scenarios
- [ ] 3.6 Draft paper section: method (hierarchical AutoEC claim), experiments, ablation table
