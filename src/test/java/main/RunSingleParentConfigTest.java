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
  void parseConfigRejectsNonThreeDimensionalInput() {
    IllegalArgumentException exception = assertThrows(
      IllegalArgumentException.class,
      () -> RunSingleParentConfig.parseConfig("4,0,0,1")
    );

    assertTrue(exception.getMessage().contains("3 integers"));
  }

  @Test
  void parseConfigKeepsCurrentWorstRepairPolicyCode() {
    RunSingleParentConfig.ParsedConfig parsed = RunSingleParentConfig.parseConfig("4,6,0");

    assertArrayEquals(
      new int[] {
        AlgorithmConstants.ALGORITHM_INDEX_DE_RAND_1,
        AlgorithmConstants.UPDATE_RATIO_CODE_WORST_REPAIR,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_PERMUTATION
      },
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
  void extractConvergenceOptionsParsesFileAndKeepsRemainingArgs() {
    RunSingleParentConfig.ConvergenceOptions options =
      RunSingleParentConfig.extractConvergenceOptions(
        new String[] {"--convergence-file", "outputs/abc.csv", "true", "false"}
      );

    assertEquals(Paths.get("outputs/abc.csv"), options.convergenceFile);
    assertArrayEquals(new String[] {"true", "false"}, options.remainingArgs);
  }

  @Test
  void buildSingleParentHybCecConfigDuplicatesParentAndForcesRuntimeSingleParentMode() {
    TaskAllocationCoordinator.HybCecConfig config = RunSingleParentConfig.buildSingleParentHybCecConfig(
      new int[] {
        AlgorithmConstants.ALGORITHM_INDEX_PSO,
        AlgorithmConstants.UPDATE_RATIO_CODE_MIXED_SUBSET,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_CHAMPION
      },
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
      new int[] {
        AlgorithmConstants.UPDATE_RATIO_CODE_MIXED_SUBSET,
        AlgorithmConstants.UPDATE_RATIO_CODE_MIXED_SUBSET
      },
      config.oL
    );
    assertEquals(AlgorithmConstants.OPERATION_ORDER_SEQUENTIAL, config.oO);
    assertTrue(config.singleParentMode);
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
      new int[] {
        AlgorithmConstants.HYBCEC_PARENT_ALGORITHM_COUNT,
        AlgorithmConstants.UPDATE_RATIO_CODE_FULL,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_PERMUTATION
      },
      1,
      null,
      null,
      null
    ));
  }
}
