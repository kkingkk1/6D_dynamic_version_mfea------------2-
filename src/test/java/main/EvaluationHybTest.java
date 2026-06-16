package main;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;

import java.util.List;
import java.util.Map;
import model.SchedulingPlan;
import org.junit.jupiter.api.Test;

class EvaluationHybTest {

  @Test
  void buildOptimizedPerRunResultUsesOptimizedResultDirectly() {
    SchedulingPlan optimizedPlan = new SchedulingPlan(List.of());
    optimizedPlan.setFitness(42.0);
    Map<Integer, SchedulingPlan> optimizedPlans = Map.of(2, optimizedPlan);
    Map<Integer, Integer> initialAssignment = Map.of(100, 1, 101, 1);
    Map<Integer, Integer> optimizedAssignment = Map.of(100, 2);

    EvaluationHyb.PerRunResult result = EvaluationHyb.buildOptimizedPerRunResult(
      3,
      initialAssignment,
      42.0,
      1,
      optimizedPlans,
      optimizedAssignment,
      List.of("initial"),
      List.of(1),
      List.of(0),
      List.of(42.0),
      25L
    );

    assertEquals(42.0, result.totalProfit);
    assertEquals(1, result.metrics.scheduledTaskCount);
    assertEquals(2, result.metrics.assignedTaskCount);
    assertEquals(optimizedAssignment, result.assignmentSnapshot);
    assertEquals(42.0, result.plansBySatellite.get(2).getFitness());
    assertNotSame(optimizedPlan, result.plansBySatellite.get(2));
  }
}
