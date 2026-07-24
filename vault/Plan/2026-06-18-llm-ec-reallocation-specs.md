---
title: LLM-EC Reallocation Heuristic Evolution — Specifications
status: draft
created: 2026-06-18
source: 10.1007/s42524-026-5124-4 analysis + codex + gemini multi-model review
---

# LLM-EC Reallocation Heuristic Evolution

## Problem Statement

Reallocation layer (TaskAllocationCoordinator sub-evaluators) uses hand-designed scoring heuristics fixed at design time. These may miss non-intuitive feature combinations (VTW tightness, conflict degree, attitude angle variance, priority, transit time). LLM-driven evolution can discover better scoring rules offline.

## Research Contribution

**Hierarchical Automated EC**: LLM generates micro-level reallocation heuristics; MFEA + CreditManager evaluates and selects them at macro-level.

Distinction from 10.1007/s42524-026-5124-4: that paper applies LLM-EC to standalone ALNS. Here, LLM-generated operators enter AutoHyb's competitive multi-algorithm ecosystem and are judged by existing credit attribution — no separate fitness function needed.

## Scope In

Offline evolution of scoring functions for:
- `TargetSatelliteRanker.computeCheapScore()` — MVP first target, lowest risk
- `ReplacementMoveEvaluator.identifyReplaceableTasks()` — phase 1
- `TaskAllocationCoordinator.buildPrioritizedUnscheduledTasks()` — phase 1
- `SwapMoveEvaluator.identifySwapCandidates()` — phase 2
- `BundleMoveEvaluator.buildBundleCandidates()` — phase 2

## Scope Out

- HybCec internals (continuous optimization)
- Outer MFEA 6D chromosome
- InsertionStrategy (feasibility-critical, high risk)
- Online/real-time LLM calls during scheduling
- Any modification to AssignmentDeltaEvaluator or delta evaluation logic

## Requirements

1. Generated heuristics are pure scoring functions — no schedule mutation allowed
2. AssignmentDeltaEvaluator remains sole profit judge
3. Evolved operators must reproduce under fixed seed (autohyb.deterministic=true)
4. Evolution is offline; online scheduling loads fixed best operator from file
5. Generalization: operator evolved on training scenario must transfer to holdout scenarios
6. Invalid or unsafe descriptors fall back silently to expert baseline

## Domain Knowledge to Inject into LLM

| Knowledge Item | Injection Difficulty |
|---|---|
| Continuous→discrete decoding (HybCec float vector → task sequence) | High |
| Attitude transition constraints, slewing time piecewise formula | High |
| VTW overlap and multi-satellite conflict degree calculation | Medium |
| Credit sliding-window evaluation mechanism | Low |
