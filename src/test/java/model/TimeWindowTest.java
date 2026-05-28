package model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class TimeWindowTest {

  @Test
  void getAttitudeRecordTimeSecondsMatchesRecordTime() {
    TimeWindow window = new TimeWindow(
      1,
      2,
      2026,
      1,
      1,
      0,
      0,
      0.0,
      2026,
      1,
      1,
      0,
      0,
      3.0
    );
    window.addAttitudeRecord(new AttitudeRecord(2026, 1, 1, 0, 0, 0.0, 0.0, 0.0));
    window.addAttitudeRecord(new AttitudeRecord(2026, 1, 1, 0, 0, 1.5, 0.0, 0.0));

    assertEquals(
      window.getAttitudeRecord(1).getTotalSeconds(),
      window.getAttitudeRecordTimeSeconds(1)
    );
    assertThrows(IndexOutOfBoundsException.class, () -> window.getAttitudeRecordTimeSeconds(2));
  }
}
