import unittest

from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import (
  AssistCategory,
  PerDriveMilestoneTracker,
  assist_category,
)


class TestPerDriveMilestoneTracker(unittest.TestCase):
  def test_classifies_actual_actuation(self):
    self.assertIsNone(assist_category(False, False))
    self.assertIsNone(assist_category(False, True))
    self.assertEqual(assist_category(True, False), AssistCategory.MADS)
    self.assertEqual(assist_category(True, True), AssistCategory.FULL_ASSIST)

  def test_tracks_categories_and_emits_repeated_milestones(self):
    tracker = PerDriveMilestoneTracker(milestone_meters=10.0)

    self.assertEqual(tracker.update(0, 10.0, AssistCategory.MADS), [])
    self.assertEqual(tracker.update(500_000_000, 10.0, AssistCategory.MADS), [])
    milestones = tracker.update(1_000_000_000, 10.0, AssistCategory.FULL_ASSIST)
    self.assertEqual([(m.category, m.distance_meters) for m in milestones], [(AssistCategory.MADS, 10.0)])

    self.assertEqual(tracker.update(1_500_000_000, 10.0, AssistCategory.FULL_ASSIST), [])
    milestones = tracker.update(2_000_000_000, 10.0, AssistCategory.FULL_ASSIST)
    self.assertEqual([(m.category, m.distance_meters) for m in milestones], [(AssistCategory.FULL_ASSIST, 10.0)])

    self.assertEqual(tracker.update(2_500_000_000, 10.0, AssistCategory.FULL_ASSIST), [])
    milestones = tracker.update(3_000_000_000, 10.0, AssistCategory.FULL_ASSIST)
    self.assertEqual([(m.category, m.distance_meters) for m in milestones], [(AssistCategory.FULL_ASSIST, 20.0)])

  def test_does_not_count_unassisted_time_or_timestamp_gaps(self):
    tracker = PerDriveMilestoneTracker(milestone_meters=10.0)

    tracker.update(0, 20.0, None)
    tracker.update(500_000_000, 20.0, AssistCategory.MADS)
    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), 0.0)

    tracker.update(2_000_000_000, 20.0, AssistCategory.MADS)
    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), 0.0)

  def test_reset_clears_per_drive_distance_and_sampling_state(self):
    tracker = PerDriveMilestoneTracker(milestone_meters=10.0)
    tracker.update(0, 10.0, AssistCategory.MADS)
    tracker.update(500_000_000, 10.0, AssistCategory.MADS)

    tracker.reset()

    self.assertEqual(tracker.distance_meters(AssistCategory.MADS), 0.0)
    self.assertEqual(tracker.update(1_000_000_000, 10.0, AssistCategory.MADS), [])


if __name__ == "__main__":
  unittest.main()
