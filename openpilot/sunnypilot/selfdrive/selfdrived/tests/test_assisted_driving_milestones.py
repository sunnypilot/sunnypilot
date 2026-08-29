import unittest

from openpilot.sunnypilot.selfdrive.selfdrived.assisted_driving_milestones import (
  METERS_PER_MILE,
  AssistCategory,
  AssistedDrivingMilestones,
  MilestoneStore,
  MilestoneUnit,
)


class ParamsStub:
  def __init__(self, state=None):
    self.values = {"AssistedDrivingMilestoneState": state or {}}
    self.writes = []

  def get(self, key, return_default=False):
    return self.values.get(key, {} if return_default else None)

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes.append((key, value, block))

  def flush(self):
    pass


class TestAssistedDrivingMilestones(unittest.TestCase):
  def test_emits_and_asynchronously_persists_first_imperial_milestone(self):
    params = ParamsStub({
      "version": 1,
      "distancesMeters": {"mads": METERS_PER_MILE - 5.0, "fullAssist": 0.0},
      "nextEventId": 7,
      "unit": "imperial",
    })
    milestones = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]

    self.assertIsNone(milestones.update(0, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True))
    event = milestones.update(500_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)

    self.assertIsNotNone(event)
    assert event is not None
    self.assertEqual(event.event_id, 7)
    self.assertEqual(event.category, AssistCategory.MADS)
    self.assertEqual(event.unit, MilestoneUnit.IMPERIAL)
    self.assertAlmostEqual(event.distance_meters, METERS_PER_MILE)
    self.assertFalse(params.writes[-1][2])

  def test_switching_units_schedules_only_a_future_milestone(self):
    params = ParamsStub({
      "version": 1,
      "distancesMeters": {"mads": 9_500.0, "fullAssist": 0.0},
      "nextEventId": 2,
      "unit": "imperial",
    })
    milestones = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]

    self.assertIsNone(milestones.update(0, 1_000.0, lat_active=True, long_active=False, is_metric=True, enabled=True))
    event = milestones.update(500_000_000, 1_000.0, lat_active=True, long_active=False, is_metric=True, enabled=True)

    self.assertIsNotNone(event)
    assert event is not None
    self.assertEqual(event.unit, MilestoneUnit.METRIC)
    self.assertAlmostEqual(event.distance_meters, 10_000.0)

  def test_ignores_disabled_reverse_and_timestamp_gaps(self):
    params = ParamsStub()
    milestones = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]

    milestones.update(0, 20.0, lat_active=True, long_active=False, is_metric=False, enabled=False)
    milestones.update(500_000_000, 20.0, lat_active=True, long_active=False, is_metric=False, enabled=False)
    milestones.update(1_000_000_000, -20.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    milestones.update(2_000_000_000, 20.0, lat_active=True, long_active=False, is_metric=False, enabled=True)

    self.assertEqual(milestones.snapshot().distances_meters[AssistCategory.MADS], 0.0)

  def test_close_persists_totals_and_last_drive_summary(self):
    params = ParamsStub()
    milestones = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]
    milestones.update(0, 10.0, lat_active=True, long_active=True, is_metric=False, enabled=True)
    milestones.update(500_000_000, 10.0, lat_active=True, long_active=True, is_metric=False, enabled=True)

    milestones.close()

    summary = params.values["LastDriveAssistedDrivingSummary"]
    self.assertAlmostEqual(summary["distancesMeters"]["fullAssist"], 5.0)
    self.assertTrue(params.writes[-1][2])

    write_count = len(params.writes)
    milestones.close()
    self.assertEqual(len(params.writes), write_count)

  def test_process_restart_preserves_the_current_drive_start(self):
    params = ParamsStub()
    first_process = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]
    first_process.set_drive_id("route-1")
    first_process.update(0, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    first_process.update(500_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    first_process.close()

    second_process = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]
    second_process.set_drive_id("route-1")
    second_process.update(1_000_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    second_process.update(1_500_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    second_process.close()

    summary = params.values["LastDriveAssistedDrivingSummary"]
    self.assertAlmostEqual(summary["distancesMeters"]["mads"], 10.0)

  def test_disabled_feature_does_not_publish_drive_summary(self):
    params = ParamsStub()
    milestones = AssistedDrivingMilestones(MilestoneStore(params))  # type: ignore[arg-type]
    milestones.update(0, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    milestones.update(500_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=True)
    milestones.update(1_000_000_000, 10.0, lat_active=True, long_active=False, is_metric=False, enabled=False)

    milestones.close()

    self.assertNotIn("LastDriveAssistedDrivingSummary", params.values)


if __name__ == "__main__":
  unittest.main()
