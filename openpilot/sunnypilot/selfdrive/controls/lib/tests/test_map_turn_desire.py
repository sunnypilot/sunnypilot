"""Map cue/session behavior; no vehicle control or network dependency."""
import ast
import importlib.util
from enum import IntEnum
from pathlib import Path
import sys
from types import SimpleNamespace
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
STATIONARY_POSITION = SimpleNamespace(t=[0., 1., 2., 3.], x=[0., 0., 0., 0.], y=[0., 0., 0., 0.])


class Direction(IntEnum):
  none, turnLeft, turnRight = 0, 1, 2


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


class TestMapTurnControllerIntegration(unittest.TestCase):
  def setUp(self):
    self.params = FakeParams()
    tree = ast.parse((ROOT/'lane_turn_desire.py').read_text())
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
    ns = {'custom': SimpleNamespace(ModelDataV2SP=SimpleNamespace(TurnDirection=Direction)),
          'CV': SimpleNamespace(MPH_TO_MS=.44704), 'Params': lambda: self.params, 'MapTurnGate': MAP.MapTurnGate,
          'cloudlog': SimpleNamespace(event=lambda *args, **kwargs: None)}
    exec(compile(tree, 'lane_turn_desire.py', 'exec'), ns)
    self.controller = ns['LaneTurnController'](None)
    self.controller.map_gate.clock = lambda: 10.1
    self.sessions = iter(range(1, 10))
    self.controller.map_gate.session_clock = lambda: next(self.sessions)

  def step(self, speed=3., right=True, left=False, blindspot=False, probabilities=(0., 0.), lateral_active=True,
           model_position=STATIONARY_POSITION, map_turn_supported=True):
    self.controller.update_params()
    self.controller.update_lane_turn(False, blindspot, left, right, speed, turn_probs=probabilities, lateral_active=lateral_active,
                                     model_position=model_position, map_turn_supported=map_turn_supported)
    return self.controller.get_turn_direction()

  def enable(self):
    self.params.put('MapboxNextTurnEnabled', True)
    self.controller.read_params()

  def test_disabled_map_preserves_existing_model_gate(self):
    self.assertEqual(self.step(), Direction.none)
    self.assertEqual(self.step(probabilities=(0., .8)), Direction.turnRight)
    self.assertNotIn('MapboxTurnIntent', self.params.values)

  def test_map_times_cue_even_without_readiness_and_suppresses_early_readiness(self):
    self.enable()
    self.assertEqual(self.step(probabilities=(0., .9)), Direction.none)
    self.params.put('MapboxTurnContext', context(distanceM=30.))
    self.assertEqual(self.step(probabilities=(0., .9)), Direction.none)
    self.params.put('MapboxTurnContext', context())
    self.assertEqual(self.step(), Direction.turnRight)
    self.assertEqual(self.params.get('MapboxTurnCue')['session'], '1')

  def test_speed_and_blindspot_and_single_cue_guard_are_retained(self):
    self.enable()
    self.step()
    self.params.put('MapboxTurnContext', context())
    self.assertEqual(self.step(speed=0.), Direction.none)
    self.assertEqual(self.step(blindspot=True), Direction.none)
    self.assertEqual(self.step(), Direction.turnRight)
    self.assertEqual(self.step(speed=10.), Direction.none)
    self.assertEqual(self.step(), Direction.none, 'Eligibility recovery must not create a second cue')
    self.step(right=False)
    self.step()
    self.assertEqual(self.controller.map_gate.session, '2')
    self.assertEqual(self.controller.get_turn_direction(), Direction.none)

  def test_preloads_target_while_inactive_without_consuming_cue(self):
    self.enable()
    self.step(lateral_active=False)
    self.params.put('MapboxTurnContext', context())
    self.assertEqual(self.step(lateral_active=False), Direction.none)
    self.assertFalse(self.controller.cue_sent)
    self.assertEqual(self.step(lateral_active=True), Direction.turnRight)

  def test_stopped_preparation_requires_sustained_model_movement(self):
    self.enable()
    self.step(speed=0.)
    self.params.put('MapboxTurnContext', context())
    stationary = SimpleNamespace(t=[0., 1., 2., 3.], x=[0.]*4, y=[0.]*4)
    launch = SimpleNamespace(t=[0., 1., 2., 3.], x=[0., 0., 0., 2.], y=[0.]*4)
    self.assertEqual(self.step(speed=0., model_position=stationary), Direction.none)
    for i in range(5):
      now = 10.1+i*.05
      self.controller.map_gate.clock = lambda now=now: now
      self.params.put('MapboxTurnContext', context(updatedAt=now))
      direction = self.step(speed=0., model_position=launch)
      self.assertEqual(direction, Direction.turnRight if i == 4 else Direction.none)
    self.assertEqual(self.params.get('MapboxTurnCue')['cueMode'], 'forecast_movement')

  def test_unsupported_model_retains_original_gate_and_no_map_intent(self):
    self.enable()
    self.assertEqual(self.step(probabilities=(0., .9), model_position=None, map_turn_supported=False), Direction.turnRight)
    self.assertNotIn('MapboxTurnIntent', self.params.values)

  def test_supported_model_with_missing_trajectory_refuses_a_map_cue(self):
    self.enable()
    self.step()
    self.params.put('MapboxTurnContext', context())
    self.assertEqual(self.step(probabilities=(0., .9), model_position=None), Direction.none)
    self.assertFalse(self.controller.cue_sent)


if __name__ == '__main__':
  unittest.main()
