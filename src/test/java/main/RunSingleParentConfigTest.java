package main;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import common.AlgorithmConstants;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Paths;
import operator.insertion.InsertionMode;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RunSingleParentConfigTest {

  @BeforeEach
  void resetLoggingProperties() {
    System.clearProperty(RunSingleHybridConfig.GENERATION_LOG_PROPERTY);
    System.clearProperty(RunSingleHybridConfig.GENERATION_LOG_ENABLED_PROPERTY);
    System.clearProperty(RunSingleHybridConfig.LOG_INTERVAL_PROPERTY);
  }

  @Test
  void parseConfigRejectsMultiDimensionalInput() {
    IllegalArgumentException exception = assertThrows(
      IllegalArgumentException.class,
      () -> RunSingleParentConfig.parseConfig("4,0,0")
    );

    assertTrue(exception.getMessage().contains("exactly 1 integer"));
  }

  @Test
  void parseConfigKeepsAlgorithmIndex() {
    RunSingleParentConfig.ParsedConfig parsed = RunSingleParentConfig.parseConfig("4");

    assertArrayEquals(
      new int[] {AlgorithmConstants.ALGORITHM_INDEX_DE_RAND_1},
      parsed.config
    );
  }

  @Test
  void extractRunOptionsParsesRunIndexBaseAndKeepsRemainingArgs() {
    RunSingleParentConfig.RunOptions options = RunSingleParentConfig.extractRunOptions(
      new String[] {"--run-index-base", "2", "true", "false"}
    );

    assertEquals(2, options.runIndexBase);
    assertEquals(false, options.generationLogEnabled);
    assertEquals(1, options.logInterval);
    assertArrayEquals(new String[] {"true", "false"}, options.remainingArgs);
  }

  @Test
  void extractRunOptionsParsesEqualsForm() {
    RunSingleParentConfig.RunOptions options = RunSingleParentConfig.extractRunOptions(
      new String[] {"--run-index-base=3", "true"}
    );

    assertEquals(3, options.runIndexBase);
    assertArrayEquals(new String[] {"true"}, options.remainingArgs);
  }

  @Test
  void extractRunOptionsParsesGenerationLogFlags() {
    RunSingleParentConfig.RunOptions options = RunSingleParentConfig.extractRunOptions(
      new String[] {"--generation-log", "--log-interval=10", "true"}
    );

    assertTrue(options.generationLogEnabled);
    assertEquals(10, options.logInterval);
    assertArrayEquals(new String[] {"true"}, options.remainingArgs);
  }

  @Test
  void extractRunOptionsUsesSharedJvmRunIndexBaseWhenCliFlagIsAbsent() {
    String previousRunIndexBase = System.getProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
    System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, "9");
    try {
      RunSingleParentConfig.RunOptions options = RunSingleParentConfig.extractRunOptions(
        new String[] {"true"}
      );

      assertEquals(9, options.runIndexBase);
      assertArrayEquals(new String[] {"true"}, options.remainingArgs);
    } finally {
      if (previousRunIndexBase == null) {
        System.clearProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
      } else {
        System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, previousRunIndexBase);
      }
    }
  }

  @Test
  void extractRunOptionsCliBaseOverridesSharedJvmBase() {
    String previousRunIndexBase = System.getProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
    System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, "9");
    try {
      RunSingleParentConfig.RunOptions options = RunSingleParentConfig.extractRunOptions(
        new String[] {"--run-index-base=2", "true"}
      );

      assertEquals(2, options.runIndexBase);
      assertArrayEquals(new String[] {"true"}, options.remainingArgs);
    } finally {
      if (previousRunIndexBase == null) {
        System.clearProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
      } else {
        System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, previousRunIndexBase);
      }
    }
  }

  @Test
  void explicitRunSeedBasePairsDifferentParentConfigs() {
    String previousSeedBase = System.getProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY);
    System.setProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY, "42");
    try {
      long deRandSeed = RunSingleParentConfig.resolveRunSeed(
        new int[] {4},
        270,
        27000,
        4
      );
      long psoSeed = RunSingleParentConfig.resolveRunSeed(
        new int[] {1},
        270,
        27000,
        4
      );

      assertEquals(46L, deRandSeed);
      assertEquals(deRandSeed, psoSeed);
    } finally {
      if (previousSeedBase == null) {
        System.clearProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY);
      } else {
        System.setProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY, previousSeedBase);
      }
    }
  }

  @Test
  void explicitRunSeedBasePairsParentWithHybridAcrossFiveRuns() {
    String previousSeedBase = System.getProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY);
    String previousRunIndexBase = System.getProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
    System.setProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY, "42");
    System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, "0");
    try {
      for (int runIndex = 0; runIndex < 5; runIndex++) {
        long hybridSeed = EvaluationHyb.resolveRunSeed(
          new int[] {2, 9, 0, 0, 0, 2},
          AlgorithmConstants.HYBRID_CONFIG_DIMENSION,
          270,
          27000,
          runIndex
        );
        long parentSeed = RunSingleParentConfig.resolveRunSeed(
          new int[] {4},
          270,
          27000,
          runIndex
        );

        assertEquals(42L + runIndex, hybridSeed);
        assertEquals(hybridSeed, parentSeed);
      }
    } finally {
      if (previousSeedBase == null) {
        System.clearProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY);
      } else {
        System.setProperty(EvaluationHyb.RUN_SEED_BASE_PROPERTY, previousSeedBase);
      }
      if (previousRunIndexBase == null) {
        System.clearProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY);
      } else {
        System.setProperty(EvaluationHyb.RUN_INDEX_BASE_PROPERTY, previousRunIndexBase);
      }
    }
  }

  @Test
  void extractConvergenceOptionsParsesFileAndKeepsRemainingArgs() {
    RunSingleParentConfig.ConvergenceOptions options =
      RunSingleParentConfig.extractConvergenceOptions(
        new String[] {"--convergence-file", "outputs/abc.csv", "true", "false"}
      );

    assertEquals(Paths.get("outputs/abc.csv"), options.convergenceFile);
    assertArrayEquals(new String[] {"true", "false"}, options.remainingArgs);
  }

  @Test
  void buildSingleAlgorithmConfigEnablesStandaloneOptimizerMode() {
    TaskAllocationCoordinator.HybCecConfig config = RunSingleParentConfig.buildSingleAlgorithmConfig(
      new int[] {AlgorithmConstants.ALGORITHM_INDEX_PSO},
      32,
      3200,
      InsertionMode.GREEDY,
      123L
    );

    assertArrayEquals(
      new int[] {AlgorithmConstants.ALGORITHM_INDEX_PSO, AlgorithmConstants.ALGORITHM_INDEX_PSO},
      config.parentsIndex
    );
    assertArrayEquals(
      new int[] {AlgorithmConstants.UPDATE_RATIO_CODE_FULL, AlgorithmConstants.UPDATE_RATIO_CODE_FULL},
      config.oL
    );
    assertEquals(AlgorithmConstants.OPERATION_ORDER_SEQUENTIAL, config.oO);
    assertTrue(config.singleAlgorithmMode);
  }

  @Test
  void validateArgsRejectsOutOfRangeParentIndex() throws Exception {
    Method validateArgs = RunSingleParentConfig.class.getDeclaredMethod(
      "validateArgs",
      int.class,
      int.class,
      int[].class,
      int.class,
      Integer.class,
      Integer.class,
      Double.class
    );
    validateArgs.setAccessible(true);

    assertThrows(InvocationTargetException.class, () -> validateArgs.invoke(
      null,
      500,
      5,
      new int[] {AlgorithmConstants.HYBCEC_PARENT_ALGORITHM_COUNT},
      1,
      null,
      null,
      null
    ));
  }
}
