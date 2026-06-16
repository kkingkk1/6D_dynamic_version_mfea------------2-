package main;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import common.AlgorithmConstants;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Properties;
import org.junit.jupiter.api.Test;

class RunSingleHybridConfigTest {

  @Test
  void defaultConfigUsesCurrentAutoDesignedVector() throws Exception {
    Field defaultConfig = RunSingleHybridConfig.class.getDeclaredField("DEFAULT_CONFIG");
    defaultConfig.setAccessible(true);

    assertArrayEquals(
      new int[] {
        AlgorithmConstants.ALGORITHM_INDEX_LSHADE,
        AlgorithmConstants.ALGORITHM_INDEX_EDA,
        AlgorithmConstants.UPDATE_RATIO_CODE_FULL,
        AlgorithmConstants.UPDATE_RATIO_CODE_FULL,
        AlgorithmConstants.OPERATION_ORDER_SEQUENTIAL,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_PERMUTATION
      },
      (int[]) defaultConfig.get(null)
    );
  }

  @Test
  void configToCsvSerializesAllGenesInOrder() {
    assertTrue("4,1,0,0,0,0".equals(RunSingleHybridConfig.configToCsv(
      new int[] {4, 1, 0, 0, 0, 0}
    )));
  }

  @Test
  void normalizeHybridConfigRejectsNonSixDimensionalInputs() {
    int[][] invalidConfigs = {
      {4, 1, 0, 0, 0, 0, 1},
      {4, 1, 0, 0, 0},
      {4, 1, 0, 0, 0, 0, 1, 0}
    };

    for (int[] invalidConfig : invalidConfigs) {
      assertThrows(
        IllegalArgumentException.class,
        () -> AlgorithmConstants.normalizeHybridConfig(invalidConfig)
      );
    }
  }

  @Test
  void normalizeHybridConfigKeepsCurrentSevenPolicyCodes() {
    int[] normalized = AlgorithmConstants.normalizeHybridConfig(
      new int[] {
        AlgorithmConstants.ALGORITHM_INDEX_DE_RAND_1,
        AlgorithmConstants.ALGORITHM_INDEX_PSO,
        AlgorithmConstants.UPDATE_RATIO_CODE_LOCAL_SEARCH,
        AlgorithmConstants.UPDATE_RATIO_CODE_WORST_REPAIR,
        AlgorithmConstants.OPERATION_ORDER_SEQUENTIAL,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_PERMUTATION
      }
    );

    assertArrayEquals(
      new int[] {
        AlgorithmConstants.ALGORITHM_INDEX_DE_RAND_1,
        AlgorithmConstants.ALGORITHM_INDEX_PSO,
        AlgorithmConstants.UPDATE_RATIO_CODE_LOCAL_SEARCH,
        AlgorithmConstants.UPDATE_RATIO_CODE_WORST_REPAIR,
        AlgorithmConstants.OPERATION_ORDER_SEQUENTIAL,
        AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_PERMUTATION
      },
      normalized
    );
  }

  @Test
  void parseConfigRejectsSevenDimensionalCliInput() throws Exception {
    Method parseConfig = RunSingleHybridConfig.class.getDeclaredMethod("parseConfig", String.class);
    parseConfig.setAccessible(true);

    InvocationTargetException exception = assertThrows(
      InvocationTargetException.class,
      () -> parseConfig.invoke(null, "4,1,0,0,0,0,1")
    );

    assertTrue(exception.getCause() instanceof IllegalArgumentException);
  }

  @Test
  void defaultConfigUsesBenchmarkSeedAnchor() throws Exception {
    Method stableSeed = EvaluationHyb.class.getDeclaredMethod(
      "stableSeed",
      int[].class,
      int.class,
      int.class,
      int.class
    );
    stableSeed.setAccessible(true);

    long actualSeed = (long) stableSeed.invoke(
      null,
      new int[] {4, 1, 0, 0, 0, 0},
      AlgorithmConstants.HYBRID_CONFIG_DIMENSION,
      270,
      27000
    );

    assertEquals(1103879922877097636L, actualSeed);
  }

  @Test
  void baselineContextMatchesReturnsTrueForSameScenarioAndConfig() {
    int[] config = {4, 1, 0, 0, 0, 0};
    Properties properties = RunSingleHybridConfig.createBaselineProperties(
      "sceneA",
      500,
      5,
      config,
      1,
      25,
      250,
      "optimizedProfit",
      123.0,
      123.0,
      45.6,
      789L,
      500,
      320,
      999
    );

    assertTrue(RunSingleHybridConfig.baselineContextMatches(
      properties,
      "sceneA",
      500,
      5,
      config,
      1,
      25,
      250
    ));
  }

  @Test
  void baselineContextMatchesReturnsFalseWhenConfigDiffers() {
    Properties properties = RunSingleHybridConfig.createBaselineProperties(
      "sceneA",
      500,
      5,
      new int[] {4, 1, 0, 0, 0, 0},
      1,
      25,
      250,
      "optimizedProfit",
      123.0,
      123.0,
      45.6,
      789L,
      500,
      320,
      999
    );

    assertFalse(RunSingleHybridConfig.baselineContextMatches(
      properties,
      "sceneA",
      500,
      5,
      new int[] {4, 1, 0, 1, 0, 0},
      1,
      25,
      250
    ));
    assertNotEquals(
      properties.getProperty("configCsv"),
      RunSingleHybridConfig.configToCsv(new int[] {4, 1, 0, 1, 0, 0})
    );
  }

  @Test
  void validateArgsRejectsOutOfRangeOperationOrderAndSurvivorCodes() throws Exception {
    Method validateArgs = RunSingleHybridConfig.class.getDeclaredMethod(
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
      new int[] {4, 1, 0, 0, AlgorithmConstants.OPERATION_ORDER_COUNT, 0},
      1,
      null,
      null,
      null
    ));
    assertThrows(InvocationTargetException.class, () -> validateArgs.invoke(
      null,
      500,
      5,
      new int[] {4, 1, 0, 0, 0, AlgorithmConstants.SURVIVOR_SELECT_STRATEGY_COUNT},
      1,
      null,
      null,
      null
    ));
  }

  @Test
  void validateArgsRejectsOutOfRangeHybridParent() throws Exception {
    Method validateArgs = RunSingleHybridConfig.class.getDeclaredMethod(
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
        AlgorithmConstants.HYBCEC_ACTIVE_PARENT_ALGORITHM_COUNT,
        AlgorithmConstants.ALGORITHM_INDEX_PSO,
        0,
        0,
        0,
        0
      },
      1,
      null,
      null,
      null
    ));
  }

  @Test
  void extractBaselineOptionsKeepsEliteArchiveRecordingDisabledByDefault() throws Exception {
    Method extractBaselineOptions = RunSingleHybridConfig.class.getDeclaredMethod(
      "extractBaselineOptions",
      String[].class
    );
    extractBaselineOptions.setAccessible(true);

    Object options = extractBaselineOptions.invoke(null, (Object) new String[] {"true"});

    Field recordEliteArchive = options.getClass().getDeclaredField("recordEliteArchive");
    recordEliteArchive.setAccessible(true);
    assertFalse(recordEliteArchive.getBoolean(options));
  }

  @Test
  void extractBaselineOptionsEnablesEliteArchiveRecordingWhenRequested() throws Exception {
    Method extractBaselineOptions = RunSingleHybridConfig.class.getDeclaredMethod(
      "extractBaselineOptions",
      String[].class
    );
    extractBaselineOptions.setAccessible(true);

    Object options = extractBaselineOptions.invoke(
      null,
      (Object) new String[] {"--record-elite-archive", "true"}
    );

    Field recordEliteArchive = options.getClass().getDeclaredField("recordEliteArchive");
    recordEliteArchive.setAccessible(true);
    assertTrue(recordEliteArchive.getBoolean(options));
  }

  @Test
  void buildBudgetSummaryIncludesAutoAndEffectiveBudgetDetails() {
    String summary = RunSingleHybridConfig.buildBudgetSummary(
      2.5,
      70.0,
      109,
      273,
      19110,
      null,
      400,
      273,
      400
    );

    assertTrue(summary.contains("populationFactor=2.5000"));
    assertTrue(summary.contains("iterationCoefficient=70.0000"));
    assertTrue(summary.contains("maxAssignedTaskCount=109"));
    assertTrue(summary.contains("autoNPop=273"));
    assertTrue(summary.contains("autoMaxFes=19110"));
    assertTrue(summary.contains("effectiveNPop=273 (auto)"));
    assertTrue(summary.contains("effectiveMaxFes=400 (override)"));
  }
}
