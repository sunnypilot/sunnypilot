"""Exercise source maneuver commitment without native Params or vehicle IO."""
import ast
from enum import IntEnum
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('nav_turn_intent', SOURCE/'nav_turn_intent.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NOW = 100.


class Params:
  def __init__(self):
    self.values = {}
    self.writes = 0

  def put(self, key, value, **kwargs):
    self.values[key] = value
    self.writes += 1

  def remove(self, key):
    self.values.pop(key, None)

  def get(self, key, **kwargs):
    return self.values.get(key, 19. if key == 'LaneTurnValue' else None)

  def get_bool(self, key):
    return self.values.get(key) is True


class Direction(IntEnum):
  none, turnLeft, turnRight = 0, 1, 2


class ChangeState(IntEnum):
  off, preLaneChange, laneChangeStarting = 0, 1, 2


class ChangeDirection(IntEnum):
  none, left, right = 0, 1, 2


DESIRE = SimpleNamespace(none=0, turnLeft=1, turnRight=2, laneChangeLeft=3, laneChangeRight=4)


def source_namespace(path, namespace):
  tree = ast.parse(path.read_text())
  tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
  exec(compile(tree, str(path), 'exec'), namespace)
  return namespace


def controller(dh=None):
  namespace = {'custom': SimpleNamespace(ModelDataV2SP=SimpleNamespace(TurnDirection=Direction)),
               'CV': SimpleNamespace(MPH_TO_MS=.44704), 'Params': Params, 'NavTurnIntent': module.NavTurnIntent,
               'turn_route_ready': module.turn_route_ready, 'time': SimpleNamespace(monotonic=lambda: NOW)}
  obj = source_namespace(SOURCE/'lane_turn_desire.py', namespace)['LaneTurnController'](dh)
  obj.navigation_enabled, obj.enabled = True, True
  return obj


def ready_context(obj, **overrides):
  value = {'session': obj.nav_intent.session, 'direction': obj.nav_intent.direction, 'status': 'ready',
           'routeOwner': 'signal', 'locationValid': True, 'headingValid': True, 'updatedAt': NOW,
           'routeGeneration': 123, 'distanceM': 25.}
  value.update(overrides)
  return value


class ALC:
  """Only external ALC eligibility is doubled; the actual DesireHelper FSM executes."""
  def __init__(self, _dh):
    self.lane_change_set_timer = 1
    self.auto_lane_change_allowed = True
    self.lane_change_blocked = False

  def update_params(self):
    pass

  def update_lane_change(self, blindspot, edge, brake, torque):
    self.lane_change_blocked = blindspot or edge

  def update_state(self):
    pass


def helper(enabled=True, supported=True):
  path = SOURCE.parents[3]/'selfdrive/controls/lib/desire_helper.py'
  namespace = {'log': SimpleNamespace(LaneChangeState=ChangeState, LaneChangeDirection=ChangeDirection, Desire=DESIRE),
               'custom': SimpleNamespace(ModelDataV2SP=SimpleNamespace(TurnDirection=Direction)),
               'CV': SimpleNamespace(MPH_TO_MS=.44704), 'DT_MDL': .05, 'AutoLaneChangeController': ALC,
               'AutoLaneChangeMode': SimpleNamespace(OFF=0), 'LaneTurnController': controller,
               'model_turn_probs': lambda _prediction: (0., 0.)}
  dh = source_namespace(path, namespace)['DesireHelper']()
  dh.lane_turn_controller.params.values.update(MapboxNextTurnEnabled=enabled, LaneTurnDesire=True, LaneTurnValue=19.)
  car = SimpleNamespace(vEgo=12., leftBlinker=False, rightBlinker=True, leftBlindspot=False,
                        rightBlindspot=False, steeringPressed=False, steeringTorque=0., brakePressed=False)

  def step(speed=None, active=True, lane_change_prob=.5, **kwargs):
    if speed is not None:
      car.vEgo = speed
    dh.update(car, active, lane_change_prob, map_turn_supported=supported, **kwargs)
    return dh.desire

  return dh, car, step


class NavigationSignalTests(unittest.TestCase):
  def test_delayed_parameter_writes_cannot_resurrect_canceled_signal(self):
    class DeferredParams(Params):
      def __init__(self):
        super().__init__()
        self.pending = []

      def put(self, key, value, block=False):
        if block:
          super().put(key, value)
        else:
          self.pending.append((key, value))

    params = DeferredParams()
    intent = module.NavTurnIntent(params)
    intent.update('right', True, True, True)
    intent.commit('turn')
    intent.update(None, True, True, True)
    for key, value in params.pending:
      params.values[key] = value
    self.assertNotIn('MapboxTurnIntent', params.values)

  def test_held_signal_does_not_repeat_and_new_signal_gets_new_session(self):
    params, counter = Params(), iter(range(100))
    intent = module.NavTurnIntent(params, session_clock=lambda: next(counter))
    for _ in range(100):
      intent.update('right', True, True, True)
    self.assertEqual(params.writes, 1)
    old = intent.session
    intent.update(None, True, True, True)
    self.assertNotIn('MapboxTurnIntent', params.values)
    intent.update('right', True, True, True)
    self.assertNotEqual(intent.session, old)

  def test_disable_disengage_or_hazards_retires_published_intent(self):
    for args in [('right', False, True, True), ('right', True, True, False), (None, True, True, True)]:
      intent = module.NavTurnIntent(Params())
      intent.update('right', True, True, True)
      intent.update(*args)
      self.assertNotIn('MapboxTurnIntent', intent.params.values)

  def test_fallback_updates_capability_without_rearming_signal(self):
    intent = module.NavTurnIntent(Params())
    intent.update('left', True, True, True)
    session = intent.session
    intent.update('left', True, False, True)
    self.assertEqual(intent.session, session)
    self.assertIs(intent.params.values['MapboxTurnIntent']['modelSupportsNavigation'], False)

  def test_pending_requires_explicit_commit_and_keeps_session(self):
    intent = module.NavTurnIntent(Params())
    intent.update('right', True, True, True)
    session = intent.session
    self.assertEqual(intent.mode, 'pending')
    self.assertTrue(intent.commit('turn'))
    self.assertEqual(intent.session, session)
    self.assertEqual(intent.params.values['MapboxTurnIntent']['mode'], 'turn')
    self.assertFalse(intent.commit('lane_change'))

  def test_lane_change_commit_keeps_prefetch_and_cannot_flip_without_completion(self):
    intent = module.NavTurnIntent(Params())
    intent.update('right', True, True, True)
    self.assertTrue(intent.commit('lane_change'))
    self.assertEqual(intent.params.values.get('MapboxTurnIntent', {}).get('mode'), 'lane_change')
    intent.update('right', True, True, True)
    self.assertFalse(intent.commit('turn'))
    intent.update(None, True, True, True)
    intent.update('right', True, True, True)
    self.assertEqual(intent.mode, 'pending')

  def test_direct_opposite_signal_starts_new_pending_session(self):
    intent = module.NavTurnIntent(Params())
    intent.update('left', True, True, True)
    intent.commit('turn')
    old = intent.session
    intent.update('right', True, True, True)
    self.assertEqual(intent.mode, 'pending')
    self.assertNotEqual(intent.session, old)

  def test_real_navigation_never_also_sends_a_turn_now_desire(self):
    obj = controller()
    for speed in (0., 2., 7., 12.):
      obj.update_lane_turn(False, False, False, True, speed, steering_pressed=True,
                           steering_torque=-5., turn_probs=(0., 1.), map_turn_supported=True)
      self.assertEqual(obj.get_turn_direction(), Direction.none)
      self.assertEqual(obj.params.values['MapboxTurnIntent']['mode'], 'pending')

  def test_navigation_does_not_depend_on_legacy_turn_desire_toggle(self):
    obj = controller()
    obj.enabled = False
    obj.update_lane_turn(False, False, True, False, 2., map_turn_supported=True)
    obj.params.values['MapboxTurnContext'] = ready_context(obj)
    obj.finalize_navigation_intent(False, 2., True, True)
    self.assertEqual(obj.nav_intent.mode, 'turn')
    self.assertEqual(obj.get_turn_direction(), Direction.none)

  def test_nonnav_model_keeps_legacy_behavior_and_reports_unsupported(self):
    obj = controller()
    obj.update_lane_turn(False, False, True, False, 2., turn_probs=(1., 0.), map_turn_supported=False)
    self.assertEqual(obj.get_turn_direction(), Direction.turnLeft)
    self.assertIs(obj.params.values['MapboxTurnIntent']['modelSupportsNavigation'], False)
    obj.finalize_navigation_intent(False, 2., True, False)
    self.assertEqual(obj.nav_intent.mode, 'pending')

  def test_ready_context_rejects_stale_wrong_session_passed_or_invalid(self):
    obj = controller()
    obj.update_lane_turn(False, False, False, True, 2., map_turn_supported=True)
    for overrides in ({'updatedAt': NOW-.351}, {'updatedAt': NOW+.01}, {'session': 'wrong'}, {'direction': 'left'},
                      {'distanceM': 0.}, {'distanceM': -1.}, {'distanceM': float('nan')}, {'status': 'passed'},
                      {'routeOwner': 'destination'}, {'headingValid': False}, {'locationValid': False}, {'routeGeneration': True}):
      with self.subTest(overrides=overrides):
        obj.params.values['MapboxTurnContext'] = ready_context(obj, **overrides)
        obj.finalize_navigation_intent(False, 2., True, True)
        self.assertEqual(obj.nav_intent.mode, 'pending')

  def test_speed_bsm_and_lateral_permission_block_turn_commit(self):
    for speed, bsm, active in ((9., False, True), (2., True, True), (2., False, False)):
      obj = controller()
      obj.update_lane_turn(False, bsm, False, True, speed, map_turn_supported=True)
      obj.params.values['MapboxTurnContext'] = ready_context(obj)
      obj.finalize_navigation_intent(False, speed, active, True)
      self.assertEqual(obj.nav_intent.mode, 'pending')

  def test_early_fast_signal_can_slow_to_turn_before_lc_request(self):
    dh, _car, step = helper()
    self.assertEqual(step(), DESIRE.none)
    obj = dh.lane_turn_controller
    session = obj.nav_intent.session
    self.assertEqual(dh.lane_change_state, ChangeState.preLaneChange)
    self.assertEqual(obj.nav_intent.mode, 'pending')
    obj.params.values['MapboxTurnContext'] = ready_context(obj)
    self.assertEqual(step(2.), DESIRE.none)
    self.assertEqual(obj.nav_intent.mode, 'turn')
    self.assertEqual(obj.nav_intent.session, session)
    self.assertTrue(obj.navigation_owns_signal)
    self.assertEqual(step(12.), DESIRE.none)
    self.assertEqual(dh.lane_change_state, ChangeState.off)

  def test_actual_lane_change_first_remains_lane_change_after_slowing(self):
    dh, _car, step = helper()
    step()
    obj = dh.lane_turn_controller
    obj.params.values['MapboxTurnContext'] = ready_context(obj)
    self.assertEqual(step(), DESIRE.laneChangeRight)
    self.assertEqual(obj.nav_intent.mode, 'lane_change')
    self.assertEqual(obj.params.values.get('MapboxTurnIntent', {}).get('mode'), 'lane_change')
    step(2.)
    self.assertEqual(obj.nav_intent.mode, 'lane_change')
    self.assertFalse(obj.navigation_owns_signal)

  def test_normal_lane_change_completion_allows_mapped_turn_with_same_signal_and_route(self):
    for left in (False, True):
      with self.subTest(left=left):
        dh, car, step = helper()
        car.leftBlinker, car.rightBlinker = left, not left
        step()
        obj = dh.lane_turn_controller
        session = obj.nav_intent.session
        context = ready_context(obj)
        obj.params.values['MapboxTurnContext'] = context
        self.assertEqual(step(), DESIRE.laneChangeLeft if left else DESIRE.laneChangeRight)
        self.assertEqual(obj.nav_intent.mode, 'lane_change')
        # Low speed alone cannot terminate an already Starting maneuver.
        self.assertEqual(step(2.), DESIRE.laneChangeLeft if left else DESIRE.laneChangeRight)
        self.assertFalse(obj.navigation_owns_signal)
        dh.lane_change_timer = .5
        self.assertEqual(step(lane_change_prob=0.), DESIRE.none)
        self.assertEqual(dh.lane_change_state, ChangeState.preLaneChange)
        self.assertEqual(obj.nav_intent.mode, 'turn')
        self.assertEqual(obj.nav_intent.session, session)
        self.assertIs(obj.params.values['MapboxTurnContext'], context)
        self.assertTrue(obj.navigation_owns_signal)

  def test_active_lane_change_keeps_prefetch_intent_without_turn_authority(self):
    dh, _car, step = helper()
    step()
    obj = dh.lane_turn_controller
    session = obj.nav_intent.session
    step()
    self.assertIn('MapboxTurnIntent', obj.params.values)
    self.assertEqual(obj.params.values.get('MapboxTurnIntent', {}).get('mode'), 'lane_change')
    self.assertEqual(obj.nav_intent.session, session)
    self.assertFalse(obj.navigation_owns_signal)

  def test_non_normal_resets_do_not_release_lane_change_lock(self):
    for reason in ('timeout', 'disengage', 'alc_disabled', 'low_speed', 'too_early'):
      with self.subTest(reason=reason):
        dh, _car, step = helper()
        step()
        obj = dh.lane_turn_controller
        obj.params.values['MapboxTurnContext'] = ready_context(obj)
        step()
        dh.lane_change_timer = 10.01 if reason == 'timeout' else 0. if reason == 'too_early' else .5
        if reason == 'alc_disabled':
          dh.alc.lane_change_set_timer = 0
        step(2., active=reason != 'disengage', lane_change_prob=.5 if reason == 'low_speed' else 0.)
        self.assertEqual(obj.nav_intent.mode, 'lane_change')
        self.assertFalse(obj.navigation_owns_signal)
        if reason == 'disengage':
          step(2.)
          self.assertEqual(obj.nav_intent.mode, 'lane_change')

  def test_completion_after_signal_cancel_or_switch_cannot_use_old_route(self):
    for opposite in (False, True):
      with self.subTest(opposite=opposite):
        dh, car, step = helper()
        step()
        obj = dh.lane_turn_controller
        old_session = obj.nav_intent.session
        obj.params.values['MapboxTurnContext'] = ready_context(obj)
        step()
        dh.lane_change_timer = .5
        car.rightBlinker, car.leftBlinker = False, opposite
        step(2., lane_change_prob=0.)
        self.assertNotEqual(obj.nav_intent.mode, 'turn')
        self.assertNotEqual(obj.nav_intent.session, old_session)
        self.assertFalse(obj.navigation_owns_signal)

  def test_completed_lc_waits_pending_and_new_lc_remains_authoritative(self):
    dh, _car, step = helper()
    step()
    step()
    obj = dh.lane_turn_controller
    dh.lane_change_timer = .5
    step(12., lane_change_prob=0.)
    self.assertEqual(obj.nav_intent.mode, 'pending')
    self.assertEqual(dh.lane_change_state, ChangeState.preLaneChange)
    # Still above turn speed: an actual new LC can start and must win.
    step()
    self.assertEqual(obj.nav_intent.mode, 'lane_change')
    obj.params.values['MapboxTurnContext'] = ready_context(obj)
    step(2.)
    self.assertEqual(dh.lane_change_state, ChangeState.laneChangeStarting)
    self.assertEqual(obj.nav_intent.mode, 'lane_change')
    self.assertFalse(obj.navigation_owns_signal)

  def test_pre_lane_change_blocked_by_bsm_does_not_commit(self):
    dh, car, step = helper()
    step()
    car.rightBlindspot = True
    self.assertEqual(step(), DESIRE.none)
    self.assertEqual(dh.lane_turn_controller.nav_intent.mode, 'pending')
    car.rightBlindspot = False
    dh.lane_turn_controller.params.values['MapboxTurnContext'] = ready_context(dh.lane_turn_controller)
    step(2.)
    self.assertEqual(dh.lane_turn_controller.nav_intent.mode, 'turn')

  def test_waiting_alc_timer_or_detected_edge_does_not_commit_lane_change(self):
    for edge in (False, True):
      dh, _car, step = helper()
      step()
      dh.alc.auto_lane_change_allowed = edge
      self.assertEqual(step(right_edge_detected=edge), DESIRE.none)
      self.assertEqual(dh.lane_turn_controller.nav_intent.mode, 'pending')

  def test_left_and_right_turn_commit_requires_matching_route(self):
    for left in (False, True):
      dh, car, step = helper()
      car.leftBlinker, car.rightBlinker = left, not left
      step(2.)
      obj = dh.lane_turn_controller
      obj.params.values['MapboxTurnContext'] = ready_context(obj)
      self.assertEqual(step(), DESIRE.none)
      self.assertEqual(obj.nav_intent.mode, 'turn')
      self.assertEqual(obj.nav_intent.direction, 'left' if left else 'right')

  def test_lane_change_request_wins_same_frame_ready_turn_tie(self):
    obj = controller()
    obj.update_lane_turn(False, False, False, True, 2., map_turn_supported=True)
    obj.params.values['MapboxTurnContext'] = ready_context(obj)
    obj.finalize_navigation_intent(True, 2., True, True)
    self.assertEqual(obj.nav_intent.mode, 'lane_change')
    self.assertEqual(obj.params.values.get('MapboxTurnIntent', {}).get('mode'), 'lane_change')

  def test_feature_enabled_mid_existing_lane_change_preserves_lane_change(self):
    dh, _car, step = helper(enabled=False)
    step()
    self.assertEqual(step(), DESIRE.laneChangeRight)
    obj = dh.lane_turn_controller
    obj.navigation_enabled = True
    self.assertEqual(step(), DESIRE.laneChangeRight)
    self.assertEqual(obj.nav_intent.mode, 'lane_change')

  def test_feature_off_and_unsupported_preserve_same_lane_change_sequence(self):
    traces = []
    for enabled, supported in ((False, True), (True, False)):
      dh, car, step = helper(enabled, supported)
      trace = []
      for speed, signal in ((12., True), (12., True), (2., True), (2., False), (12., True), (12., True)):
        car.rightBlinker = signal
        trace.append((step(speed), dh.lane_change_state, dh.lane_change_direction))
      traces.append(trace)
    self.assertEqual(*traces)


if __name__ == '__main__':
  unittest.main()
