"""Map cue/session behavior; no vehicle control or network dependency."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOTION_SPEC = importlib.util.spec_from_file_location('openpilot.sunnypilot.selfdrive.controls.lib.turn_motion', ROOT/'turn_motion.py')
MOTION = importlib.util.module_from_spec(MOTION_SPEC)
sys.modules[MOTION_SPEC.name] = MOTION
MOTION_SPEC.loader.exec_module(MOTION)
SPEC = importlib.util.spec_from_file_location('map_turn_desire_test_subject', ROOT/'map_turn_desire.py')
MAP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MAP
SPEC.loader.exec_module(MAP)


class FakeParams:
  def __init__(self):
    self.values = {'LaneTurnDesire': True, 'LaneTurnValue': 19., 'MapboxNextTurnEnabled': False,
                   'MapboxTurnLeadDistance': 8.}

  def get(self, name, return_default=False):
    return self.values.get(name)

  def get_bool(self, name):
    return bool(self.values.get(name))

  def put(self, name, value):
    self.values[name] = value

  def remove(self, name):
    self.values.pop(name, None)


def context(session='1', direction='right', **changes):
  return {'session': session, 'direction': direction, 'status': 'ready',
    'updatedAt': 10., 'gpsAgeSeconds': .1, 'gpsHorizontalAccuracyM': 1.5,
    'crossTrackM': 2., 'distanceM': 7., 'locationValid': True, 'headingValid': True, **changes}


class TestMapTurnGate(unittest.TestCase):
  def evaluate(self, packet=None, **changes):
    args = {'session': '1', 'direction': 'right', 'now': 10.1, 'speed': 3., 'lead_m': 8., **changes}
    return MAP.evaluate_map_turn(context() if packet is None else packet, **args)

  def test_near_target_and_short_pose_extrapolation(self):
    decision = self.evaluate()
    self.assertTrue(decision.allowed)
    self.assertAlmostEqual(decision.distance_m, 6.4)
    self.assertFalse(self.evaluate(context(distanceM=20.)).allowed)
    self.assertFalse(self.evaluate(context(distanceM=.5)).allowed)

  def test_unavailable_and_wrong_session_fail_closed(self):
    for change in ({'status': 'unavailable'}, {'locationValid': False}, {'headingValid': False},
                   {'direction': 'left'}, {'session': 'old'}):
      with self.subTest(change=change):
        self.assertFalse(self.evaluate(context(**change)).allowed)

  def test_stale_or_uncertain_or_invalid_location_fails_closed(self):
    for change in ({'updatedAt': 9.7}, {'updatedAt': 11.}, {'gpsAgeSeconds': .51}, {'gpsAgeSeconds': -.1},
                   {'gpsHorizontalAccuracyM': 3.1}, {'gpsHorizontalAccuracyM': 0.}, {'crossTrackM': 6.1},
                   {'distanceM': float('nan')}, {'distanceM': float('inf')}, {'distanceM': True},
                   {'updatedAt': 9.8, 'gpsAgeSeconds': .3}):
      with self.subTest(change=change):
        self.assertFalse(self.evaluate(context(**change)).allowed)

  def test_standstill_does_not_create_a_cue(self):
    self.assertFalse(self.evaluate(speed=0.).allowed)
    self.assertFalse(self.evaluate(speed=.3).allowed)
    self.assertTrue(self.evaluate(speed=.301).allowed)

  def test_cancel_and_opposite_signal_invalidate_old_targets(self):
    params = FakeParams()
    sessions = iter([1, 2, 3])
    gate = MAP.MapTurnGate(params, clock=lambda: 10.1, session_clock=lambda: next(sessions), use_motion=False)
    gate.configure(True, 8.)
    gate.update_signal('right', True)
    params.put('MapboxTurnContext', context())
    self.assertTrue(gate.ready(3.))
    gate.update_signal(None, True)
    self.assertNotIn('MapboxTurnIntent', params.values)
    self.assertFalse(gate.ready(3.))
    gate.update_signal('right', True)
    self.assertEqual(gate.session, '2')
    self.assertFalse(gate.ready(3.), 'Same-direction re-signal must reject the previous target')
    gate.update_signal('left', True)
    self.assertEqual(gate.session, '3')


if __name__ == '__main__':
  unittest.main()
