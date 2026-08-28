import unittest

from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import (
  METERS_PER_MILE,
  PARAM_KEYS,
  AssistCategory,
  AssistedDistanceMilestoneTracker,
  MilestoneStore,
  assist_category,
  next_milestone_miles,
)


class TestAssistedDistanceMilestoneTracker(unittest.TestCase):
  def test_store_round_trips_each_category(self):
    class ParamsStub:
      def __init__(self):
        self.values = {
          PARAM_KEYS[AssistCategory.MADS]: 123.0,
          PARAM_KEYS[AssistCategory.FULL_ASSIST]: 456.0,
        }

      def get(self, key, return_default=False):
        return self.values.get(key, 0.0 if return_default else None)

      def put(self, key, value):
        self.values[key] = value

    params = ParamsStub()
    store = MilestoneStore(params)  # type: ignore[arg-type]
    self.assertEqual(store.load(), {
      AssistCategory.MADS: 123.0,
      AssistCategory.FULL_ASSIST: 456.0,
    })

    store.save({AssistCategory.MADS: 789.0, AssistCategory.FULL_ASSIST: 987.0})
    self.assertEqual(store.load(), {
      AssistCategory.MADS: 789.0,
      AssistCategory.FULL_ASSIST: 987.0,
    })

  def test_classifies_actual_actuation(self):
    self.assertIsNone(assist_category(False, False))
    self.assertIsNone(assist_category(False, True))
    self.assertEqual(assist_category(True, False), AssistCategory.MADS)
    self.assertEqual(assist_category(True, True), AssistCategory.FULL_ASSIST)

  def test_uses_a_one_two_five_milestone_ladder(self):
    cases = (
      (0.0, 1.0),
      (1.0, 2.0),
      (2.0, 5.0),
      (5.0, 10.0),
      (10.0, 20.0),
      (49.9, 50.0),
      (50.0, 100.0),
      (999.0, 1000.0),
      (1000.0, 2000.0),
    )
    for distance, expected in cases:
      with self.subTest(distance=distance):
        self.assertEqual(next_milestone_miles(distance), expected)

  def test_tracks_categories_and_emits_dynamic_milestones(self):
    tracker = AssistedDistanceMilestoneTracker({
      AssistCategory.MADS: METERS_PER_MILE - 5.0,
      AssistCategory.FULL_ASSIST: 2 * METERS_PER_MILE - 5.0,
    })

    self.assertEqual(tracker.update(0, 10.0, AssistCategory.MADS), [])
    milestones = tracker.update(500_000_000, 10.0, AssistCategory.FULL_ASSIST)
    self.assertEqual(len(milestones), 1)
    self.assertEqual(milestones[0].category, AssistCategory.MADS)
    self.assertAlmostEqual(milestones[0].previous_distance_miles, 0.0)
    self.assertAlmostEqual(milestones[0].distance_miles, 1.0)

    milestones = tracker.update(1_000_000_000, 10.0, AssistCategory.FULL_ASSIST)
    self.assertEqual(len(milestones), 1)
    self.assertEqual(milestones[0].category, AssistCategory.FULL_ASSIST)
    self.assertAlmostEqual(milestones[0].previous_distance_miles, 1.0)
    self.assertAlmostEqual(milestones[0].distance_miles, 2.0)

  def test_does_not_count_unassisted_time_or_timestamp_gaps(self):
    tracker = AssistedDistanceMilestoneTracker()

    tracker.update(0, 20.0, None)
    tracker.update(500_000_000, 20.0, AssistCategory.MADS)
    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), 0.0)

    tracker.update(2_000_000_000, 20.0, AssistCategory.MADS)
    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), 0.0)

  def test_drive_reset_preserves_persistent_distance(self):
    tracker = AssistedDistanceMilestoneTracker()
    tracker.update(0, 10.0, AssistCategory.MADS)
    tracker.update(500_000_000, 10.0, AssistCategory.MADS)
    distance_before_reset = tracker.distance_meters(AssistCategory.MADS)

    tracker.reset_sampling()

    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), distance_before_reset)
    self.assertEqual(tracker.update(1_000_000_000, 10.0, AssistCategory.MADS), [])


if __name__ == "__main__":
  unittest.main()
