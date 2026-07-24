---
title: LLM-EC Reallocation Heuristic Evolution — Design
status: draft
created: 2026-06-18
---

# Architecture

```
[Python DPEC Evolution Loop]
        ↓  JSON DSL heuristic descriptor
[Java EvaluateHeuristicDescriptor entry point]
        ↓  loads descriptor → applies ScoringPolicy hook
[RunSingleHybridConfig (fixed scenario + seed + reduced budget)]
        ↓  returns JSON {profit, unscheduled, elapsed_ms, valid}
[Python: fitness = profit]
```

LLM generates descriptors. Java evaluates them. No arbitrary code execution at any step.

## Individual Representation (FNLE-style JSON DSL)

Each evolved heuristic is a JSON descriptor:

```json
{
  "id": "gen3_c1_offspring_002",
  "target": "TargetSatelliteRanker",
  "fnle": "Ranks satellites by remaining_capacity weighted by vtw_overlap_count, penalized by current_load",
  "features": ["remaining_capacity", "vtw_overlap_count", "current_load"],
  "expression": "f0 * f1 / (f2 + 1.0)",
  "constants": {}
}
```

Expression is evaluated over an immutable `FeatureDTO`. Java owns expression parsing and safety checks (whitelist of ops: +, -, *, /, sqrt, log, max, min; no IO, no reflection).

## DPEC Evolution

- **Population A** (LLM-generated, size 10): LLM generates descriptors from domain initialization prompt
- **Population B** (expert, size 10): current hand-coded scoring logic encoded as baseline descriptors
- Elite exchange: every 5 generations, swap top-2 individuals between populations
- **Crossover C1**: LLM reads FNLE texts of two parents, generates descriptor that integrates both
- **Crossover C2**: LLM simulates genetic crossover on feature sets and expression structures
- **Mutation M1**: LLM adds features from domain variable list (deepen variable understanding)
- **Mutation M2**: LLM introduces randomness / stochastic weight
- **Mutation M3**: LLM incorporates additional indicators (conflict_degree, attitude_variance, orbit_count)
- **Mutation M4**: LLM fine-tunes constants in expression

## Domain Initialization Prompt Structure

Modules (per paper Fig. 6 pattern):
1. Problem description: multi-satellite scheduling, profit maximization, reassignment goal
2. Example descriptor: expert baseline for TargetSatelliteRanker
3. Feature definitions: remaining_capacity (double), vtw_overlap_count (int), task_priority (int 1-10), slewing_cost (double seconds), conflict_degree (double), observation_duration (int seconds)
4. Constraint context: slewing time is piecewise nonlinear; each satellite has independent energy/capacity; VTW overlaps create scheduling conflicts
5. Task: generate diverse scoring descriptors that rank candidates for target satellite selection
6. Output requirements: valid JSON matching schema, no external calls, expression uses only whitelisted ops

## Evaluation Pipeline (Staged Racing)

| Stage | Scenario | Seeds | Budget | Cost/eval | Purpose |
|---|---|---|---|---|---|
| 1 | 1 small (100-task) | 1 | 30% FES | 2–5s | Eliminate invalid/weak |
| 2 | 2 scenarios | 3 | 50% FES | 20–60s | Eliminate marginal |
| 3 | holdout scenarios | 5 | full FES | minutes | Elite confirmation |

Parallel across candidates. Never run Maven compile concurrently with Java evaluator (shared target/classes).

## Java Interfaces to Add

```java
// ScoringPolicy — pure scoring, no side effects
public interface ScoringPolicy {
    double score(FeatureDTO features);
}

// FeatureDTO — immutable snapshot of candidate features
public record FeatureDTO(
    double remainingCapacity,
    int vtwOverlapCount,
    int taskPriority,
    double slewingCost,
    double conflictDegree,
    int observationDuration
) {}

// DSL evaluator loaded from descriptor JSON
public class ExpressionScoringPolicy implements ScoringPolicy { ... }

// New evaluation entry point
// Usage: --heuristic-file <path> --scenario <id> --seed <n> --budget <fes>
// Output: JSON {profit, unscheduled_count, elapsed_ms, valid, error}
public class EvaluateHeuristicDescriptor { ... }
```

Hooks into existing code:
- `TargetSatelliteRanker`: add optional `ScoringPolicy satellitePolicy` constructor param; default = current logic encoded as `ExpressionScoringPolicy`
- `ReplacementMoveEvaluator`: add optional `ScoringPolicy taskPolicy`
- All other evaluators unchanged until Phase 2

## Key Invariants (must not break)

- `AssignmentDeltaEvaluator.evaluateDelta()` is never replaced or bypassed
- `HybCec.run()` called identically regardless of active ScoringPolicy
- `autohyb.deterministic=true` preserved; evolved policy must be stateless
- No writes to `EliteConfigArchive` from heuristic evaluator path
- Invalid descriptor → fallback to expert baseline silently; log warning only
