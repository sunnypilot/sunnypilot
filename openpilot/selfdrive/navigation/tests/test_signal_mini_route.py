"""Real route ownership/generation lifecycle; no HTTP or vehicle execution."""
from pathlib import Path
import ast
import importlib.util
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np

from test_navd_next_turn import Executor, Params, SM, load_navd, target


class SignalMiniRouteTests(unittest.TestCase):
  def setUp(self):
    self.navd, self.sm, self.params, self.pm, self.executor = load_navd(), SM(), Params(), Mock(), Executor()
    self.now, self.wall = 100., 1_000_000.
    self.token = patch.dict(self.navd.RouteEngine.__init__.__globals__, get_mapbox_token=Mock(return_value='pk.fixture.signature'))
    self.token.start()
    self.addCleanup(self.token.stop)
    self.engine = self.navd.RouteEngine(self.sm, self.pm, self.params, update_frequency=10)
    self.engine.signal_turn = self.navd.SignalTurnEngine(self.params, Mock(return_value=SimpleNamespace(discover=Mock())), self.executor,
      clock=lambda: self.now, wall_clock=lambda: self.wall)

  def fresh(self, longitude=0., latitude=0., heading=0.):
    self.sm.gps.longitude, self.sm.gps.latitude, self.sm.gps.bearingDeg = longitude, latitude, heading
    self.sm.gps.unixTimestampMillis = (self.wall-.001)*1000.
    self.sm.logMonoTime.update({name: int(self.now*1e9)-1000 for name in self.sm.logMonoTime})
    self.sm.recv_time.update(dict.fromkeys(self.sm.recv_time, self.now))
    self.params.values['NavModelState'] = {'updatedAt': self.now, 'supported': True}

  def ready(self):
    self.engine.update()
    self.executor.jobs[-1][0].set_result(target())
    self.engine.update()
    self.assertEqual(self.engine.route_owner, 'signal')
    self.assertEqual(self.params.values['MapboxTurnContext']['status'], 'ready')

  def enter_and_cancel(self):
    self.params.values.pop('MapboxTurnIntent', None)
    self.sm.car.leftBlinker = self.sm.car.rightBlinker = False
    self.fresh(longitude=.000025, latitude=.001, heading=90.)
    self.engine.update()

  def test_unsupported_model_still_gets_the_turn_marked_as_no_model_input(self):
    # crawl-turn steering and the corner speed use a signalled turn's shape with any model; map inputs to the model
    # itself stay gated on modelSupportsNavigation downstream
    self.params.values['NavModelState']['supported'] = False
    self.ready()
    self.assertIs(self.params.values['MapboxTurnContext']['modelSupportsNavigation'], False)
    self.assertIn('exitBearingDeg', self.params.values['MapboxTurnContext'])

  def test_supported_model_context_says_so(self):
    self.ready()
    self.assertIs(self.params.values['MapboxTurnContext']['modelSupportsNavigation'], True)

  def test_delayed_context_write_cannot_resurrect_retired_route(self):
    pending, persist = [], self.params.put

    def deferred(key, value, block=False):
      if block:
        persist(key, value, block=True)
      else:
        pending.append((key, value))

    self.params.put = deferred
    engine = self.engine.signal_turn
    engine.key = ('one', 'right')
    engine._publish(self.now, 'ready', routeOwner='signal', routeGeneration=123, retainedAfterSignalCancel=True)
    engine._clear()
    for key, value in pending:
      self.params.values[key] = value
    self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_coherent_route_arrival_all_maneuvers_and_publish_order(self):
    self.ready()
    self.assertEqual(self.engine.route[-1]['maneuver']['type'], 'arrive')
    self.assertNotIn('NavDestination', self.params.values)
    calls = self.pm.send.call_args_list
    route_index = max(i for i, call in enumerate(calls) if call.args[0] == 'navRoute')
    instruction_index = max(i for i, call in enumerate(calls) if call.args[0] == 'navInstruction')
    self.assertLess(route_index, instruction_index)
    instruction = calls[instruction_index].args[1].navInstruction
    self.assertTrue(any(item['type'] == 'turn' and item['modifier'] == 'right' for item in instruction.allManeuvers))
    self.assertEqual(self.params.values['MapboxTurnContext']['routeGeneration'], self.engine.route_generation)
    self.assertFalse(any(key == 'MapboxTurnContext' and value.get('status') == 'route_pending'
                         for key, value, _block in self.params.writes))

  def test_pending_route_can_prepare_without_authorizing_navigation_inputs(self):
    self.params.values['MapboxTurnIntent']['mode'] = 'pending'
    self.ready()
    path = Path(__file__).resolve().parents[3]/'sunnypilot/modeld_v2/navigation_input.py'
    spec = importlib.util.spec_from_file_location('mini_route_model_guard', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    guard = module.SignalRouteGuard()
    arguments = {'now': self.now, 'enabled': True, 'lateral_active': True, 'left_blinker': False,
                 'right_blinker': True, 'intent': self.params.values['MapboxTurnIntent'],
                 'context': self.params.values['MapboxTurnContext']}
    self.assertFalse(guard.check(**arguments)['ready'])
    self.params.values['MapboxTurnIntent']['mode'] = 'turn'
    self.assertTrue(guard.check(**arguments)['ready'])

  def test_lane_change_keeps_prefetch_generation_for_later_turn(self):
    self.params.values['MapboxTurnIntent']['mode'] = 'lane_change'
    self.ready()
    generation = self.engine.route_generation
    session = self.params.values['MapboxTurnIntent']['session']
    self.assertEqual(len(self.executor.jobs), 1)
    self.params.values['MapboxTurnIntent']['mode'] = 'pending'
    self.engine.update()
    self.params.values['MapboxTurnIntent']['mode'] = 'turn'
    self.engine.update()
    self.assertEqual(self.engine.route_generation, generation)
    self.assertEqual(self.params.values['MapboxTurnContext']['session'], session)
    self.assertEqual(len(self.executor.jobs), 1, 'Completing LC must not force another routing request')

  def test_lane_change_only_route_is_cleared_on_cancel_even_at_junction(self):
    self.params.values['MapboxTurnIntent']['mode'] = 'lane_change'
    self.ready()
    self.enter_and_cancel()
    self.assertIsNone(self.engine.route)
    self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_cancel_before_entry_clears_route_and_context(self):
    self.ready()
    self.params.values.pop('MapboxTurnIntent')
    self.sm.car.rightBlinker = False
    self.engine.update()
    self.assertIsNone(self.engine.route)
    self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_same_tick_first_entry_and_auto_cancel_retains_exact_generation(self):
    self.ready()
    generation = self.engine.route_generation
    self.assertFalse(self.engine.signal_turn.entered)
    self.enter_and_cancel()
    context = self.params.values['MapboxTurnContext']
    self.assertEqual(context['status'], 'ready')
    self.assertTrue(context['retainedAfterSignalCancel'])
    self.assertEqual(context['routeGeneration'], generation)
    self.assertEqual(len(self.executor.jobs), 1)

  def test_receiving_road_completion_retires_without_retarget(self):
    self.ready()
    self.enter_and_cancel()
    self.fresh(longitude=.00015, latitude=.001, heading=90.)
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['status'], 'passed')
    self.assertIsNone(self.engine.route)
    self.engine.update()
    self.assertEqual(len(self.executor.jobs), 1)

  def test_missed_junction_retires_instead_of_rerouting_to_endpoint(self):
    self.ready()
    self.fresh(latitude=.00115, heading=0.)
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['status'], 'passed')
    self.assertIsNone(self.engine.route)
    self.engine.update()
    self.assertEqual(len(self.executor.jobs), 1)

  def test_transient_gps_loss_retains_geometry_generation_but_invalidates_inputs(self):
    self.ready()
    self.enter_and_cancel()
    generation = self.engine.route_generation
    self.now += .6
    self.wall += .6
    self.params.values['NavModelState']['updatedAt'] = self.now
    self.sm.logMonoTime['carControl'] = int(self.now*1e9)-1000
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['status'], 'unavailable')
    self.assertEqual(self.engine.route_generation, generation)
    self.assertIsNotNone(self.engine.route)
    self.fresh(longitude=.00003, latitude=.001, heading=90.)
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['status'], 'ready')
    self.assertEqual(self.engine.route_generation, generation)

  def test_manual_destination_switch_cannot_label_old_route_as_new_destination(self):
    a, b = {'longitude': .002, 'latitude': 0.}, {'longitude': .003, 'latitude': 0.}
    self.params.values['NavDestination'] = a
    self.engine.install_route(target().steps, (.002, 0.))
    self.engine.send_route()
    self.engine.recompute_route = Mock()
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['destination'], a)
    self.params.values['NavDestination'] = b
    self.engine.update()  # not a1Hz legacy recompute tick
    context = self.params.values['MapboxTurnContext']
    self.assertEqual(context['status'], 'searching')
    self.assertIsNone(self.engine.route)
    self.assertEqual(self.params.values['NavDestination'], b)

  def test_signal_route_resends_at_one_hz_without_changing_generation(self):
    self.ready()
    generation = self.engine.route_generation
    before = sum(call.args[0] == 'navRoute' for call in self.pm.send.call_args_list)
    self.sm.frame = 10
    self.engine.update()
    routes = [call.args[1] for call in self.pm.send.call_args_list if call.args[0] == 'navRoute']
    self.assertEqual(len(routes), before+1)
    self.assertEqual(routes[-1].logMonoTime, generation)

  def test_manual_destination_cancel_removes_its_ready_generation_context(self):
    self.params.values['NavDestination'] = {'longitude': .002, 'latitude': 0.}
    self.engine.install_route(target().steps, (.002, 0.))
    self.engine.send_route()
    self.engine.recompute_route = Mock()
    self.engine.update()
    self.params.values.pop('NavDestination')
    self.params.values.pop('MapboxTurnIntent')
    self.sm.car.rightBlinker = False
    self.engine.update()
    self.assertIsNone(self.engine.route)
    self.assertNotIn('MapboxTurnContext', self.params.values)

  def test_malformed_route_is_contained_without_exception_text_logging(self):
    self.engine._update_route = Mock(side_effect=ValueError('secret-url-must-not-be-logged'))
    self.engine.update()
    self.assertEqual(self.params.values['MapboxTurnContext']['reason'], 'route_processing_failed')
    text = str(self.navd.cloudlog.event.call_args_list)
    self.assertNotIn('secret-url', text)


class MapGenerationTests(unittest.TestCase):
  def test_map_eof_source_is_route_generation_not_render_completion(self):
    path = Path(__file__).resolve().parents[1]/'mapsd.py'
    tree = ast.parse(path.read_text())
    server_send = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and
      isinstance(node.func, ast.Attribute) and node.func.attr == 'send'][0]
    self.assertEqual(ast.unparse(server_send.args[-1]), 'generation')
    # Also execute the actual map class: an unchanging route resend may not
    # relabel a render with wall-clock completion time.
    namespace = {'np': np, 'time': SimpleNamespace(monotonic=lambda: 100.), 'RETRY_SECONDS': 10,
      'RouteTracker': Mock(), 'latest_gps_source': lambda sm: 'gps', 'MapRenderer': Mock(), 'PMTiles': Mock(),
      'RemoteTiles': Mock(), 'SIZE': 256, 'cloudlog': Mock()}
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'MapsD')
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), 'exec'), namespace)
    maps = namespace['MapsD']()
    maps.renderer = Mock()
    maps.renderer.render.return_value = np.zeros((256, 256), np.uint8), True
    sm = SimpleNamespace(updated={'navRoute': True}, logMonoTime={'navRoute': 123, 'gps': 99_900_000_000})
    values = {'navRoute': SimpleNamespace(coordinates=[SimpleNamespace(longitude=0., latitude=0.),
      SimpleNamespace(longitude=0., latitude=.001)]), 'gps': SimpleNamespace(longitude=0., latitude=0.)}
    class Messages:
      updated, logMonoTime = sm.updated, sm.logMonoTime
      def __getitem__(self, key):
        return values[key]
    maps.update(Messages())
    self.assertEqual(maps.route_generation, 123)


if __name__ == '__main__':
  unittest.main()
