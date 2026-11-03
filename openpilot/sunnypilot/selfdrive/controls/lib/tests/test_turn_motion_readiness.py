"""Temporal forecast permission only; no model inference or vehicle controls."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1]/'turn_motion.py'
spec = importlib.util.spec_from_file_location('turn_motion_readiness_under_test', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TurnMotionReadiness = module.TurnMotionReadiness


class TestTurnMotionReadiness(unittest.TestCase):
  def test_requires_elapsed_persistence_with_contiguous_model_frames(self):
    readiness = TurnMotionReadiness()
    for t in (100., 100.05, 100.1, 100.15):
      self.assertFalse(readiness.update('one', t, True, 1.5))
    self.assertTrue(readiness.update('one', 100.2, True, 1.5))
    self.assertEqual(readiness.since, 100.)
    self.assertEqual(readiness.last_motion_m, 1.5)
    self.assertTrue(readiness.update('one', 100.25, True, 2.))

  def test_single_spike_and_threshold_dropout_cannot_prepare_later(self):
    readiness = TurnMotionReadiness()
    self.assertFalse(readiness.update('one', 123.45, True, 1.8))
    self.assertFalse(readiness.update('one', 123.5, True, 1.49))
    self.assertIsNone(readiness.since)
    for t in (134.146, 134.196, 134.246, 134.296):
      self.assertFalse(readiness.update('one', t, True, 1.8))
    self.assertTrue(readiness.update('one', 134.346, True, 1.8))

  def test_session_change_and_explicit_reset_retire_prior_history(self):
    readiness = TurnMotionReadiness()
    for t in (0., .05, .1, .15, .2):
      readiness.update('one', t, True, 2.)
    self.assertFalse(readiness.update('two', .25, True, 2.))
    self.assertEqual(readiness.since, .25)
    readiness.reset()
    self.assertIsNone(readiness.since)
    self.assertIsNone(readiness.last_motion_m)
    self.assertIsNone(readiness.session)
    self.assertFalse(readiness.update('two', .45, True, 2.))

  def test_invalid_map_or_missing_forecast_requires_a_new_full_window(self):
    invalids = ((False, 2.), (None, 2.), ('true', 2.), (1, 2.), (True, None),
                (True, float('nan')), (True, float('inf')), (True, -.01), (True, True))
    for permission, motion in invalids:
      with self.subTest(permission=permission, motion=motion):
        readiness = TurnMotionReadiness()
        for t in (0., .05, .1, .15):
          readiness.update('one', t, True, 2.)
        self.assertFalse(readiness.update('one', .2, permission, motion))
        self.assertIsNone(readiness.since)
        self.assertIsNone(readiness.last_motion_m)
        self.assertFalse(readiness.update('one', .25, True, 2.))
        self.assertEqual(readiness.since, .25)

  def test_backward_duplicate_and_missing_native_update_restart_window(self):
    for next_time in (.1, .2, .276):
      with self.subTest(next_time=next_time):
        readiness = TurnMotionReadiness()
        for t in (0., .05, .1, .15, .2):
          readiness.update('one', t, True, 2.)
        self.assertFalse(readiness.update('one', next_time, True, 2.))
        self.assertEqual(readiness.since, next_time)
        self.assertFalse(readiness.update('one', next_time+.05, True, 2.))

  def test_invalid_clock_or_session_cannot_keep_previous_readiness(self):
    for session, timestamp in (('one', True), ('one', float('nan')), ('one', float('inf')),
                               ('one', None), ('one', '1.0'), ('one', 10**400), (None, .2), ('', .2), (True, .2)):
      with self.subTest(session=session, timestamp=timestamp):
        readiness = TurnMotionReadiness()
        readiness.update('one', 0., True, 2.)
        self.assertFalse(readiness.update(session, timestamp, True, 2.))
        self.assertIsNone(readiness.since)

  def test_gap_boundary_and_nonuniform_valid_updates_use_time_not_frame_count(self):
    readiness = TurnMotionReadiness()
    for t in (0., .075, .15):
      self.assertFalse(readiness.update('one', t, True, 2.))
    self.assertFalse(readiness.update('one', .199, True, 2.))
    self.assertTrue(readiness.update('one', .2, True, 2.))
    self.assertFalse(readiness.update('one', .276, True, 2.))

  def test_config_validation_and_explicit_zero_duration(self):
    for kwargs in ({'threshold': 0}, {'threshold': True}, {'threshold': float('nan')},
                   {'persistence': -1.}, {'persistence': True}, {'persistence': float('inf')}):
      with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
        TurnMotionReadiness(**kwargs)
    self.assertTrue(TurnMotionReadiness(persistence=0.).update('one', 0., True, 1.5))


if __name__ == '__main__':
  unittest.main()
