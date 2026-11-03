"""Execute navd integration with mocked messaging/HTTP and controllable futures.

Openpilot imports are supplied as test doubles so these tests also run on a Mac
without the vehicle messaging/Params native libraries. Production function and
class bodies are executed unchanged; no Mapbox/network request is made.
"""
import ast
from concurrent.futures import Future
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np

NAVIGATION = Path(__file__).resolve().parents[1]
WORKTREE = NAVIGATION.parents[2]


def source(name):
  path = NAVIGATION/name
  if path.exists():
    return path.read_text()
  return subprocess.check_output(['git', 'show', f'HEAD:openpilot/selfdrive/navigation/{name}'], cwd=WORKTREE, text=True)


class Params:
  def __init__(self, enabled=True):
    self.values = {'MapboxNextTurnEnabled': enabled, 'MapboxTurnIntent': {'session': 'one', 'direction': 'right'}}
    self.writes = []

  def get(self, key, **kwargs):
    return self.values.get(key)

  def get_bool(self, key):
    return self.values.get(key) is True

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes.append((key, value, block))

  def remove(self, key):
    self.values.pop(key, None)


class NextTurnError(Exception):
  def __init__(self, reason):
    self.reason = reason


class Executor:
  def __init__(self):
    self.jobs = []

  def submit(self, function, **kwargs):
    future = Future()
    future.set_running_or_notify_cancel()  # Simulate an HTTP request already in flight.
    self.jobs.append((future, function, kwargs))
    return future

  def shutdown(self, **kwargs):
    pass


def message(service, valid=True):
  return SimpleNamespace(valid=valid, **{service: SimpleNamespace(coordinates=[])})


def load_navd():
  route = {'__name__': 'route_test_fixture'}
  exec(compile(source('route.py'), 'route.py', 'exec'), route)
  namespace = {'__name__': 'navd_test_fixture', 'messaging': SimpleNamespace(new_message=message),
               'API_HOST': 'https://api.example.test', 'Api': Mock(), 'Params': Params, 'Ratekeeper': Mock(),
               'cloudlog': Mock(), 'MapboxNextTurnClient': Mock(), 'NextTurnError': NextTurnError,
               'latest_gps_source': lambda sm: 'gpsLocation' if sm.valid['gpsLocation'] else None,
               'along_path': route['along_path'], 'local_meters': route['local_meters']}
  tree = ast.parse(source('navd.py'))
  tree.body = [node for node in tree.body
               if not (isinstance(node, ast.ImportFrom) and node.module.startswith('openpilot.'))
               and not (isinstance(node, ast.Import) and any(item.name.startswith('openpilot.') for item in node.names))]
  exec(compile(tree, str(NAVIGATION/'navd.py'), 'exec'), namespace)
  return SimpleNamespace(**namespace)


class SM:
  def __init__(self):
    self.frame = 1
    self.valid = dict.fromkeys(('gpsLocation', 'carState'), True)
    self.recv_time = dict.fromkeys(self.valid, 100.)
    self.logMonoTime = dict.fromkeys(self.valid, 100_000_000_000)
    self.gps = SimpleNamespace(hasFix=True, longitude=0., latitude=0., bearingDeg=0., bearingAccuracyDeg=3.,
                               horizontalAccuracy=1., unixTimestampMillis=1_000_000_000)
    self.car = SimpleNamespace(vEgo=2., gearShifter='drive', leftBlinker=False, rightBlinker=True)

  def __getitem__(self, key):
    return self.car if key == 'carState' else self.gps

  def update(self, timeout):
    pass


def target(direction='right', request='validation-one', discovered=100.):
  return SimpleNamespace(direction=direction, discovered_at=discovered, approach_geometry=((0., 0.), (0., .001)),
                         geometry=((0., 0.), (0., .001), (.0004, .001)), junction=(0., .001),
                         incoming_bearing_deg=0., exit_bearing_deg=90. if direction == 'right' else 270.,
                         validation_uuid=request, probe_uuid='probe-one', name='Example Street')


class TestSignalTurnEngine(unittest.TestCase):
  def setUp(self):
    self.navd = load_navd()
    self.params, self.sm, self.executor = Params(), SM(), Executor()
    self.now = 100.
    self.wall = 1_000_000.
    self.client_factory = Mock(return_value=SimpleNamespace(discover=Mock()))
    self.engine = self.navd.SignalTurnEngine(self.params, self.client_factory, self.executor,
                                            clock=lambda: self.now, wall_clock=lambda: self.wall)
    self.token = patch.dict(self.engine.update.__globals__, get_mapbox_token=Mock(return_value='pk.example.signature'))
    self.token.start()
    self.addCleanup(self.token.stop)

  def update(self, destination=False):
    return self.engine.update(self.sm, 'gpsLocation', destination_active=destination)

  def ready(self):
    self.assertEqual(self.update()['status'], 'searching')
    self.executor.jobs[-1][0].set_result(target())
    self.assertEqual(self.update()['status'], 'ready')

  def test_disabled_makes_no_token_client_worker_or_account_request(self):
    self.params.values['MapboxNextTurnEnabled'] = False
    with patch.dict(self.engine.update.__globals__, get_mapbox_token=Mock(side_effect=AssertionError('unexpected credential read'))):
      self.assertIsNone(self.update())
    self.client_factory.assert_not_called()
    self.assertEqual(self.executor.jobs, [])
    self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_missing_token_is_unavailable_and_read_once_per_session(self):
    getter = Mock(return_value=None)
    with patch.dict(self.engine.update.__globals__, get_mapbox_token=getter):
      for _ in range(3):
        self.assertEqual(self.update()['reason'], 'missing_token')
    getter.assert_called_once_with()
    self.assertEqual(self.executor.jobs, [])

  def test_raw_fix_distance_not_extrapolated_and_context_has_true_ages(self):
    self.ready()
    distance = self.engine.context['distanceM']
    self.now += .2
    self.wall += .2
    context = self.update()
    self.assertAlmostEqual(context['distanceM'], distance)
    self.assertAlmostEqual(context['gpsAgeSeconds'], .2)
    self.assertEqual(context['updatedAt'], self.now)
    self.assertTrue(context['headingValid'] and context['locationValid'])
    self.assertEqual(context['requestId'], 'validation-one')

  def test_opposite_signal_waits_for_single_worker_and_discards_old_result(self):
    self.update()
    self.params.values['MapboxTurnIntent'] = {'session': 'two', 'direction': 'left'}
    self.sm.car.leftBlinker, self.sm.car.rightBlinker = True, False
    self.assertEqual(self.update()['status'], 'searching')
    self.assertEqual(len(self.executor.jobs), 1)
    self.executor.jobs[0][0].set_result(target())
    self.assertEqual(self.update()['session'], 'two')
    self.assertIsNone(self.engine.target)
    self.assertEqual(len(self.executor.jobs), 2)
    self.executor.jobs[1][0].set_result(target('left', 'validation-two'))
    context = self.update()
    self.assertEqual((context['session'], context['direction'], context['status']), ('two', 'left', 'ready'))

  def test_cancel_or_disable_retires_inflight_result(self):
    for cancel in ('intent', 'disable'):
      with self.subTest(cancel=cancel):
        self.setUp()
        self.update()
        if cancel == 'intent':
          self.params.values.pop('MapboxTurnIntent')
        else:
          self.params.values['MapboxNextTurnEnabled'] = False
        self.assertIsNone(self.update())
        self.executor.jobs[0][0].set_result(target())
        self.assertIsNone(self.update())
        self.assertIsNone(self.engine.target)
        self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_explicit_destination_blocks_requests_and_retires_prior_work(self):
    self.assertEqual(self.update(destination=True)['status'], 'blocked')
    self.assertEqual(self.executor.jobs, [])
    self.client_factory.assert_not_called()
    self.update(destination=False)
    self.assertEqual(len(self.executor.jobs), 1)
    self.update(destination=True)
    self.executor.jobs[0][0].set_result(target())
    self.assertEqual(self.update(destination=True)['reason'], 'explicit_destination')
    self.assertIsNone(self.engine.target)

  def test_stale_fix_poor_accuracy_future_publication_and_reverse_block_discovery(self):
    changes = (lambda: setattr(self.sm.gps, 'unixTimestampMillis', self.sm.gps.unixTimestampMillis-1000),
               lambda: setattr(self.sm.gps, 'horizontalAccuracy', 4.),
               lambda: self.sm.logMonoTime.update(gpsLocation=101_000_000_000),
               lambda: setattr(self.sm.car, 'gearShifter', 'reverse'))
    for change in changes:
      with self.subTest(change=change):
        self.sm = SM()
        change()
        self.assertEqual(self.update()['status'], 'unavailable')
    self.assertEqual(self.executor.jobs, [])

  def test_physical_signal_cancellation_blocks_stale_intent(self):
    self.ready()
    self.sm.car.rightBlinker = False
    context = self.update()
    self.assertEqual(context['reason'], 'physical_signal_mismatch')
    self.assertIsNone(self.engine.target)
    self.assertEqual(len(self.executor.jobs), 1)

  def test_wrong_heading_or_crossroad_position_has_no_ready_context(self):
    self.ready()
    self.sm.gps.bearingDeg = 90.
    self.assertEqual(self.update()['status'], 'unavailable')
    self.sm.gps.bearingDeg = 0.
    self.sm.gps.longitude = .0002
    context = self.update()
    self.assertEqual(context['status'], 'unavailable')
    self.assertGreater(context['crossTrackM'], 20.)

  def test_expired_target_and_passed_junction_do_not_retarget_held_signal(self):
    self.ready()
    self.engine.target = target(discovered=-201.)
    self.assertEqual(self.update()['reason'], 'target_expired')
    self.engine.target = target()
    self.sm.gps.latitude = .0012
    self.assertEqual(self.update()['status'], 'passed')
    self.sm.gps.latitude = 0.
    self.assertEqual(self.update()['status'], 'passed')
    self.assertEqual(len(self.executor.jobs), 1)

  def test_discovery_exception_does_not_publish_or_log_url_or_token(self):
    self.update()
    secret = 'https://example.test/?access_token=pk.secret.signature'
    self.executor.jobs[0][0].set_exception(RuntimeError(secret))
    context = self.update()
    self.assertEqual(context['reason'], 'discovery_failed')
    self.assertNotIn(secret, str(self.params.writes))
    self.assertEqual(self.navd.cloudlog.mock_calls, [])


class TestApproachProjection(unittest.TestCase):
  def setUp(self):
    self.navd = load_navd()

  def test_signed_distance_uses_incoming_geometry_not_outgoing_leg(self):
    before = self.navd.approach_context(target(), (0., .0009), 0., 1.)
    after = self.navd.approach_context(target(), (0., .0011), 0., 1.)
    self.assertAlmostEqual(before['distanceM'], 11.1195, delta=.01)
    self.assertAlmostEqual(after['distanceM'], -11.1195, delta=.01)
    on_outgoing = self.navd.approach_context(target(), (.0002, .001), 90., 1.)
    self.assertFalse(on_outgoing['locationValid'])
    self.assertGreater(on_outgoing['crossTrackM'], 20.)

  def test_invalid_geometry_and_zero_accuracy_are_not_ready_and_inputs_unchanged(self):
    pose = np.array([0., 0.])
    self.assertFalse(self.navd.approach_context(target(), pose, 0., 0.)['locationValid'])
    np.testing.assert_array_equal(pose, [0., 0.])
    malformed = target()
    malformed.approach_geometry = ((float('nan'), 0.), (0., .001))
    self.assertFalse(self.navd.approach_context(malformed, pose, 0., 1.)['locationValid'])


class TestChosenHeading(unittest.TestCase):
  def setUp(self):
    self.navd = load_navd()
    self.llk = {'valid': True, 'status': 'valid', 'orientationValid': True,
                'orientationNed': [0., 0., np.pi/2], 'orientationStd': [.01, .01, .02],
                'receivedAt': 99.9, 'publishedAt': 99.8}
    self.gps = {'valid': True, 'bearingDeg': 0., 'bearingAccuracyDeg': 4.,
                'fixAgeSeconds': .1, 'receivedAt': 99.9, 'publishedAt': 99.9}

  def test_fresh_calibrated_localizer_heading_precedes_gps_course(self):
    result = self.navd.chosen_heading(100., self.llk, self.gps)
    self.assertEqual((result['headingSource'], result['headingDeg']), ('liveLocationKalman', 90.))
    self.assertAlmostEqual(result['headingAgeSeconds'], .2)

  def test_invalid_or_stale_localizer_falls_back_only_to_fresh_accurate_gps(self):
    for update in ({'status': 'uncalibrated'}, {'publishedAt': 99.}, {'publishedAt': 100.1},
                   {'orientationStd': [.01, .01, np.radians(16.)]}):
      result = self.navd.chosen_heading(100., {**self.llk, **update}, self.gps)
      self.assertEqual(result['headingSource'], 'gps')
    self.gps['bearingAccuracyDeg'] = 16.
    self.assertFalse(self.navd.chosen_heading(100., None, self.gps)['headingValid'])
    self.gps['bearingAccuracyDeg'] = 0.
    self.assertFalse(self.navd.chosen_heading(100., None, self.gps)['headingValid'])

  def test_future_nan_or_missing_samples_are_not_valid_headings(self):
    self.gps['publishedAt'] = 100.1
    for orientation in (None, [float('nan'), 0., 0.], [0., 0.], [0., 0., 0.]):
      invalid = {**self.llk, 'orientationNed': orientation, 'receivedAt': 100.1}
      self.assertFalse(self.navd.chosen_heading(100., invalid, self.gps)['headingValid'])

  def test_producer_nan_calibrated_std_uses_explicit_base_covariance_without_claiming_calibration(self):
    self.llk.update(orientationStd=[float('nan')]*3, baseOrientationValid=True, baseOrientationStd=[.01, .01, .02])
    result = self.navd.chosen_heading(100., self.llk, self.gps)
    self.assertEqual((result['headingSource'], result['headingDeg']), ('liveLocationKalman', 90.))
    self.assertEqual(result['headingUncertaintyKind'], 'base_orientation')
    self.assertFalse(result['calibrationUncertaintyKnown'])
    self.llk['baseOrientationValid'] = False
    self.assertEqual(self.navd.chosen_heading(100., self.llk, self.gps)['headingSource'], 'gps')

  def test_finite_high_calibrated_uncertainty_cannot_select_smaller_base_covariance(self):
    self.llk.update(orientationStd=[.01, .01, np.radians(16.)], baseOrientationValid=True, baseOrientationStd=[.01]*3)
    self.assertEqual(self.navd.chosen_heading(100., self.llk, self.gps)['headingSource'], 'gps')


class TestNavigationIntegration(unittest.TestCase):
  def test_10hz_updates_keep_destination_recompute_and_instruction_at1hz(self):
    navd, sm, params, pm = load_navd(), SM(), Params(enabled=False), Mock()
    params.values['NavDestination'] = {'longitude': 0., 'latitude': .002}
    with patch.dict(navd.RouteEngine.__init__.__globals__, get_mapbox_token=Mock(return_value=None)):
      engine = navd.RouteEngine(sm, pm, params, update_frequency=10)
    engine.recompute_route, engine.send_instruction, engine.send_route = Mock(), Mock(), Mock()
    for frame in range(1, 201):
      sm.frame = frame
      engine.update()
    self.assertEqual(engine.recompute_route.call_count, 20)
    self.assertEqual(engine.send_instruction.call_count, 20)
    self.assertEqual(engine.send_route.call_count, 2)
    engine.api.get_token.assert_not_called()

  def test_signal_preview_is_labeled_and_clears_immediately_without_destination_write(self):
    navd, sm, params, pm, executor = load_navd(), SM(), Params(), Mock(), Executor()
    with patch.dict(navd.RouteEngine.__init__.__globals__, get_mapbox_token=Mock(return_value='pk.example.signature')):
      engine = navd.RouteEngine(sm, pm, params, update_frequency=10)
      engine.signal_turn = navd.SignalTurnEngine(params, Mock(return_value=SimpleNamespace(discover=Mock())), executor,
                                                clock=lambda: 100., wall_clock=lambda: 1_000_000.)
      engine.update()
      executor.jobs[0][0].set_result(target())
      sm.frame += 1
      engine.update()
      instructions = [call.args[1] for call in pm.send.call_args_list if call.args[0] == 'navInstruction']
      self.assertEqual(instructions[-1].navInstruction.maneuverPrimaryText, 'Signal turn')
      self.assertTrue(instructions[-1].valid)
      self.assertNotIn('NavDestination', params.values)
      params.values.pop('MapboxTurnIntent')
      sm.frame += 1
      engine.update()
    instructions = [call.args[1] for call in pm.send.call_args_list if call.args[0] == 'navInstruction']
    routes = [call.args[1] for call in pm.send.call_args_list if call.args[0] == 'navRoute']
    self.assertFalse(instructions[-1].valid)
    self.assertEqual(routes[-1].navRoute.coordinates, [])


if __name__ == '__main__':
  unittest.main()
