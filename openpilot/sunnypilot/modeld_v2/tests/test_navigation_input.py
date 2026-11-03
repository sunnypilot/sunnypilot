"""Navigation conditioning contracts without camera/GPU/process dependencies."""
import ast
from collections.abc import Callable
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('nav_inputs_under_test', SOURCE / 'navigation_input.py')
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)


def maneuver(kind='turn', modifier='right', distance=50.):
  return SimpleNamespace(type=kind, modifier=modifier, distance=distance)


class NavigationEncodingTests(unittest.TestCase):
  def test_right_left_and_distance_use_training_encoding(self):
    for modifier, index in (('right', 10), ('left', 15)):
      result = nav.navigation_input([maneuver(modifier=modifier, distance=50.)], traveled=8.)
      self.assertEqual(result.dtype, np.float32)
      self.assertEqual(result.shape, (47,))
      self.assertEqual(result[index], 1.)
      self.assertAlmostEqual(float(result[-1]), .42)
      self.assertEqual(np.count_nonzero(result), 2)

  def test_depart_arrive_merge_and_passed_steps_do_not_mask_next_turn(self):
    steps = [maneuver('depart'), maneuver('merge'), maneuver(distance=2.), maneuver(modifier='left', distance=90.), maneuver('arrive')]
    result = nav.navigation_input(steps, traveled=5.)
    self.assertEqual(result[15], 1.)
    self.assertAlmostEqual(float(result[-1]), .85)

  def test_first_eligible_step_preserves_order_and_roundabout_type(self):
    result = nav.navigation_input([maneuver('roundabout', '', 100.), maneuver(modifier='left', distance=120.)])
    self.assertEqual(result[26], 1.)
    self.assertEqual(result[15], 0.)

  def test_nonfinite_distance_cannot_enter_model(self):
    result = nav.navigation_input([maneuver(distance=float('inf')), maneuver(distance=float('nan'))])
    self.assertTrue(np.array_equal(result, np.zeros(47, np.float32)))
    self.assertFalse(nav.navigation_input([maneuver()], traveled=-1).any())

  def test_small_and_ctv3_are_not_navigation_models(self):
    good = {'nav_map': np.zeros((1, 1, 256, 256), np.float32), 'navigation': np.zeros((1, 47), np.float32)}
    self.assertTrue(nav.supports_navigation(good))
    self.assertFalse(nav.supports_navigation({}))
    self.assertFalse(nav.supports_navigation({'navigation': good['navigation']}))
    self.assertFalse(nav.supports_navigation({**good, 'nav_map': good['nav_map'].astype(np.uint8)}))
    self.assertFalse(nav.supports_navigation({**good, 'navigation': np.zeros((1, 46), np.float32)}))

  def test_navigation_needs_a_compatible_real_bundle_not_an_override(self):
    inputs = {'nav_map': np.zeros((1, 1, 256, 256), np.float32), 'navigation': np.zeros((1, 47), np.float32)}
    self.assertEqual(nav.navigation_capability(inputs, None, native=True), (False, 'model_bundle_required'))
    bundle = SimpleNamespace(generation=12, is20hz=True)
    self.assertEqual(nav.navigation_capability(inputs, bundle, native=True), (True, 'supported'))
    self.assertFalse(nav.navigation_capability(inputs, SimpleNamespace(generation=9, is20hz=True), native=True)[0])
    self.assertFalse(nav.navigation_capability(inputs, bundle, native=False)[0])


class NavigationFreshnessTests(unittest.TestCase):
  def setUp(self):
    self.buffer = nav.NavigationInputBuffer()
    self.pixels = np.zeros((256, 256), np.uint8)
    self.pixels[5, :3] = [0, 128, 255]
    self.instruction = SimpleNamespace(allManeuvers=[maneuver(distance=50.)])

  def observe(self, *, t=10., timestamp_ns=10_000_000_000):
    return self.buffer.observe_map(self.pixels, 256, 256, timestamp_ns=timestamp_ns, received_at=t, route_generation=9_000_000_000)

  def prepare(self, **changes):
    arguments = {'now': 10.1, 'enabled': True, 'instruction': self.instruction, 'instruction_valid': True,
                 'instruction_received_at': 10., 'speed': 10., 'instruction_published_ns': 10_000_000_000,
                 'expected_route_generation': 9_000_000_000}
    return self.buffer.prepare(**(arguments | changes))

  def assert_empty(self, result):
    self.assertFalse(result['nav_map'].any())
    self.assertFalse(result['navigation'].any())

  def test_real_raster_scale_and_elapsed_distance_are_preserved(self):
    self.assertTrue(self.observe())
    result = self.prepare()
    self.assertEqual(result['nav_map'].dtype, np.float32)
    np.testing.assert_array_equal(result['nav_map'][0, 0, 5, :3], [0., 128., 255.])
    self.assertAlmostEqual(float(result['navigation'][0, -1]), .49)
    self.assertEqual(self.buffer.reason, 'ready')

  def test_missing_stale_disabled_or_invalid_context_clears_both_inputs(self):
    self.assert_empty(self.prepare())
    self.observe()
    for changes in ({'enabled': False}, {'now': 10.51}, {'instruction_valid': False},
                    {'instruction_received_at': 8.}, {'instruction_received_at': 10.2}, {'speed': float('nan')}):
      self.assert_empty(self.prepare(**changes))

  def test_new_invalid_map_cannot_refresh_or_keep_previous_geometry(self):
    self.observe()
    self.assertTrue(self.prepare()['nav_map'].any())
    self.assertFalse(self.observe(timestamp_ns=0))
    self.assert_empty(self.prepare())

  def test_old_capture_is_rejected_even_if_just_received(self):
    self.assertFalse(self.observe(t=11., timestamp_ns=10_000_000_000))
    self.assert_empty(self.prepare(now=11.))
    self.assertFalse(self.observe(t=10., timestamp_ns=11_000_000_000))

  def test_wrong_sized_or_truncated_raster_is_rejected(self):
    self.assertFalse(self.buffer.observe_map(b'', 256, 256, timestamp_ns=10_000_000_000, received_at=10.))
    self.assertFalse(self.buffer.observe_map(self.pixels, 128, 256, timestamp_ns=10_000_000_000, received_at=10.))

  def test_old_route_map_or_pre_route_instruction_cannot_condition_model(self):
    self.observe()
    self.assert_empty(self.prepare(expected_route_generation=9_500_000_000))
    self.assertEqual(self.buffer.reason, 'route_generation_mismatch')
    self.assert_empty(self.prepare(instruction_published_ns=8_999_999_999))
    self.assertTrue(self.prepare()['nav_map'].any())


class SignalRouteGuardTests(unittest.TestCase):
  def setUp(self):
    self.guard = nav.SignalRouteGuard()
    self.intent = {'session': 'signal1', 'direction': 'right', 'mode': 'turn', 'modelSupportsNavigation': True, 'lateralActive': True}
    self.context = {'status': 'ready', 'session': 'signal1', 'direction': 'right', 'routeGeneration': 9_000_000_000,
                    'updatedAt': 10., 'routeOwner': 'signal', 'locationValid': True, 'headingValid': True}

  def check(self, **changes):
    arguments = {'now': 10.1, 'enabled': True, 'lateral_active': True, 'left_blinker': False, 'right_blinker': True,
                 'intent': self.intent, 'context': self.context}
    return self.guard.check(**(arguments | changes))

  def test_current_signal_session_and_generation_are_returned(self):
    result = self.check()
    self.assertTrue(result['ready'])
    self.assertEqual((result['session'], result['routeGeneration']), ('signal1', 9_000_000_000))

  def test_cancel_opposite_hazards_inactive_and_unsupported_are_blocked(self):
    for changes in ({'right_blinker': False}, {'left_blinker': True, 'right_blinker': False}, {'left_blinker': True},
                    {'lateral_active': False}, {'intent': self.intent | {'modelSupportsNavigation': False}},
                    {'intent': self.intent | {'mode': 'lane_change'}}, {'intent': self.intent | {'mode': 'pending'}},
                    {'intent': self.intent | {'session': 'new-session'}}):
      self.assertFalse(self.check(**changes)['ready'])

  def test_missing_stale_and_unowned_contexts_fail_closed(self):
    for context in (None, self.context | {'updatedAt': 9.}, self.context | {'routeOwner': 'destination'},
                    self.context | {'status': 'passed'}, self.context | {'routeGeneration': None},
                    self.context | {'headingValid': False}):
      self.assertFalse(self.check(context=context)['ready'])

  def test_retention_needs_previously_consumed_same_route_and_explicit_router_flag(self):
    retained = self.context | {'retainedAfterSignalCancel': True}
    self.assertFalse(self.check(right_blinker=False, intent=None, context=retained)['ready'])
    self.guard.consumed('signal1', 9_000_000_000)
    self.assertTrue(self.check(right_blinker=False, intent=None, context=retained)['ready'])
    self.assertFalse(self.check(right_blinker=False, intent=None)['ready'])

  def test_lateral_loss_or_new_session_revokes_retention(self):
    retained = self.context | {'retainedAfterSignalCancel': True}
    self.guard.consumed('signal1', 9_000_000_000)
    self.check(lateral_active=False)
    self.assertFalse(self.check(right_blinker=False, intent=None, context=retained)['ready'])
    self.guard.consumed('signal1', 9_000_000_000)
    self.check(intent=self.intent | {'session': 'new-session'})
    self.assertFalse(self.check(right_blinker=False, intent=None, context=retained)['ready'])

  def test_temporary_stale_context_zeros_inputs_but_can_resume_same_consumed_exit(self):
    retained = self.context | {'retainedAfterSignalCancel': True}
    self.guard.consumed('signal1', 9_000_000_000)
    self.assertFalse(self.check(now=11., right_blinker=False, intent=None, context=retained)['ready'])
    self.assertEqual(self.guard.last_consumed, ('signal1', 9_000_000_000))
    self.assertTrue(self.check(now=11.1, right_blinker=False, intent=None, context=retained | {'updatedAt': 11.})['ready'])
    self.assertFalse(self.check(context=self.context | {'status': 'completed'})['ready'])
    self.assertIsNone(self.guard.last_consumed)

  def test_auto_cancel_waits_zeroed_for_router_confirmation_then_resumes(self):
    self.guard.consumed('signal1', 9_000_000_000)
    waiting = self.check(right_blinker=False, intent=None)
    self.assertFalse(waiting['ready'])
    self.assertEqual(self.guard.last_consumed, ('signal1', 9_000_000_000))
    retained = self.context | {'retainedAfterSignalCancel': True, 'updatedAt': 10.2}
    self.assertTrue(self.check(now=10.21, right_blinker=False, intent=None, context=retained)['ready'])
    self.check(right_blinker=False, intent=None, context=self.context | {'status': 'idle'})
    self.assertIsNone(self.guard.last_consumed)


class DestinationOwnershipTests(unittest.TestCase):
  def setUp(self):
    self.destination = {'latitude': 40., 'longitude': -80., 'place_name': 'example'}
    self.context = {'routeOwner': 'destination', 'status': 'ready', 'routeGeneration': 9_000_000_000,
                    'updatedAt': 10., 'destination': {'latitude': 40., 'longitude': -80.}}

  def test_matching_existing_destination_is_usable_at_boot(self):
    result = nav.destination_route_context(self.destination, self.context, 10.1)
    self.assertTrue(result['ready'])
    self.assertEqual(result['routeGeneration'], 9_000_000_000)

  def test_signal_to_manual_or_changed_destination_never_reuses_old_route(self):
    self.assertFalse(nav.destination_route_context(self.destination, self.context | {'routeOwner': 'signal'}, 10.1)['ready'])
    changed = self.destination | {'longitude': -79.}
    self.assertFalse(nav.destination_route_context(changed, self.context, 10.1)['ready'])
    self.assertFalse(nav.destination_route_context(self.destination, self.context | {'destination': None}, 10.1)['ready'])
    self.assertFalse(nav.destination_route_context(self.destination, self.context, 11.)['ready'])


class SourceModelInputTests(unittest.TestCase):
  @staticmethod
  def source_run():
    tree = ast.parse((SOURCE / 'modeld.py').read_text())
    model_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ModelState')
    run = next(node for node in model_class.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
    namespace = {'np': np, 'Callable': Callable, 'VisionBuf': object}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[run], type_ignores=[])), 'actual_modeld_run', 'exec'), namespace)
    return namespace['run']

  @staticmethod
  def model(*, navigation=True):
    arrays = {'desire': np.zeros(8, np.float32), 'traffic_convention': np.zeros(2, np.float32),
              'action_t': np.zeros(2, np.float32)}
    if navigation:
      arrays.update(nav_map=np.full((1, 1, 256, 256), 255., np.float32), navigation=np.ones((1, 47), np.float32))

    class Output:
      def numpy(self):
        return np.zeros(1, np.float32)

    model = SimpleNamespace(numpy_inputs=arrays, prev_desire=np.zeros(8, np.float32), desire_key='desire', chestnut=False,
                            _vision_input_names=[], _combined_model_type='supercombo', vision_output_slices={'plan': slice(0, 1)},
                            parser=SimpleNamespace(parse_outputs=lambda _raw: {}))
    model.adapter = SimpleNamespace(copy_frames=lambda _frames: None, is_native=True, run=lambda: Output())
    return model

  def test_actual_run_copies_nav_inputs_and_preserves_native_desire_edges(self):
    run, model = self.source_run(), self.model()
    request = np.zeros(8, np.float32)
    request[2] = 1
    inputs = {'desire': request, 'traffic_convention': np.array([1., 0.]), 'action_t': np.array([.295, .525]),
              'nav_map': np.full((1, 1, 256, 256), 128., np.float32),
              'navigation': nav.navigation_input([maneuver()]).reshape(1, 47)}
    run(model, {}, {}, inputs)
    np.testing.assert_array_equal(model.numpy_inputs['nav_map'], inputs['nav_map'])
    np.testing.assert_array_equal(model.numpy_inputs['navigation'], inputs['navigation'])
    self.assertEqual(model.numpy_inputs['desire'][2], 1.)
    run(model, {}, {}, inputs)
    self.assertEqual(model.numpy_inputs['desire'][2], 0.)
    np.testing.assert_array_equal(model.numpy_inputs['action_t'], np.array([.295, .525], np.float32))

  def test_actual_run_zeros_absent_nav_and_accepts_nonnav_fallback(self):
    run = self.source_run()
    inputs = {'desire': np.zeros(8, np.float32)}
    model = self.model()
    run(model, {}, {}, inputs)
    self.assertFalse(model.numpy_inputs['nav_map'].any())
    self.assertFalse(model.numpy_inputs['navigation'].any())
    fallback = self.model(navigation=False)
    run(fallback, {}, {}, inputs)
    self.assertNotIn('nav_map', fallback.numpy_inputs)

  def test_existing_float_host_layout_also_fits_verified_nav_graph(self):
    tree = ast.parse((SOURCE / 'frame_fusion.py').read_text())
    layout = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'pack_layout')
    namespace = {'math': math}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[layout], type_ignores=[])), 'source_layout', 'exec'), namespace)
    old = {'desire': (8,), 'traffic_convention': (1, 2), 'action_t': (1, 2)}
    before, old_size = namespace['pack_layout'](old, 4096)
    expanded, new_size = namespace['pack_layout'](old | {'nav_map': (1, 1, 256, 256), 'navigation': (1, 47)}, 4096)
    for name in ('tfm', *old):
      self.assertEqual(before[name], expanded[name])
    self.assertEqual(expanded['nav_map'], before['frames'])
    self.assertGreaterEqual(expanded['navigation'] - expanded['nav_map'], 256 * 256 * 4)
    self.assertGreater(new_size, old_size)


class NavigationStatusTests(unittest.TestCase):
  def test_status_is_throttled_but_load_and_fallback_can_publish_immediately(self):
    writes = []
    publisher = nav.NavigationStatePublisher(SimpleNamespace(put=lambda key, value: writes.append((key, value))))
    self.assertTrue(publisher.publish(now=10., supported=True, active=True, reason='ready', model_name='Nav N16'))
    self.assertFalse(publisher.publish(now=10.05, supported=True, active=True, reason='ready'))
    self.assertTrue(publisher.publish(now=10.11, supported=True, active=False, reason='map_stale'))
    self.assertTrue(publisher.publish(now=10.12, supported=False, active=False, reason='model_unsupported', force=True))
    self.assertEqual(len(writes), 3)
    self.assertEqual(writes[0][0], 'NavModelState')
    self.assertEqual(writes[0][1]['modelName'], 'Nav N16')
    self.assertFalse(writes[-1][1]['supported'])
    self.assertFalse(writes[-1][1]['active'])

  def test_status_identifiers_belong_to_the_consumed_automatic_route(self):
    writes = []
    publisher = nav.NavigationStatePublisher(SimpleNamespace(put=lambda key, value: writes.append(value)))
    publisher.publish(now=10., supported=True, active=True, reason='ready', session='signal1', route_generation=9_000_000_000)
    self.assertEqual(writes[-1]['session'], 'signal1')
    self.assertEqual(writes[-1]['routeGeneration'], 9_000_000_000)
    publisher.publish(now=10.2, supported=False, active=False, reason='model_unsupported')
    self.assertNotIn('session', writes[-1])

  def test_unsupported_model_can_never_report_active_nav(self):
    writes = []
    publisher = nav.NavigationStatePublisher(SimpleNamespace(put=lambda key, value: writes.append(value)))
    publisher.publish(now=10., supported=False, active=True, reason='model_unsupported')
    self.assertFalse(writes[-1]['active'])


if __name__ == '__main__':
  unittest.main()
