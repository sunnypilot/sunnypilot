"""Standalone recorded-schema fixtures: no credentials, network or driving code."""
from dataclasses import FrozenInstanceError
import importlib.util
import json
from pathlib import Path
import sys
import traceback
import unittest
from unittest.mock import Mock, patch

MODULE = Path(__file__).resolve().parents[1] / 'mapbox_next_turn.py'
spec = importlib.util.spec_from_file_location('mapbox_next_turn_under_test', MODULE)
next_turn = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = next_turn
spec.loader.exec_module(next_turn)

ORIGIN = (0., 0.)
JUNCTION = next_turn.offset(ORIGIN, 0., 100.)
PROBE = next_turn.offset(ORIGIN, 0., next_turn.PROBE_DISTANCE_M)
EXIT = next_turn.offset(JUNCTION, 90., next_turn.EXIT_QUERY_DISTANCE_M)
TOKEN = 'pk.synthetic.signature'


def junction(location=JUNCTION, index=1, out=0):
  return {'location': list(location), 'geometry_index': index, 'bearings': [0, 90, 180, 270],
          'entry': [True, True, False, True], 'in': 2, 'out': out}


def body(turn=False, road_class='street'):
  endpoint = EXIT if turn else PROBE
  points = [list(ORIGIN), list(JUNCTION), list(endpoint)]
  source = {'location': list(ORIGIN), 'bearings': [0], 'entry': [True], 'out': 0, 'geometry_index': 0}
  arrival = {'location': list(endpoint), 'bearings': [270 if turn else 180], 'entry': [True], 'in': 0, 'geometry_index': 2}
  at = junction(out=1 if turn else 0)
  if road_class is not None:
    at['mapbox_streets_v8'] = {'class': road_class}
  steps = [
    {'mode': 'driving', 'name': 'Approach', 'maneuver': {'type': 'depart', 'location': list(ORIGIN)},
     'geometry': {'type': 'LineString', 'coordinates': points[:2] if turn else points},
     'intersections': [source] if turn else [source, at]},
  ]
  if turn:
    steps.append({'mode': 'driving', 'name': 'Side Street', 'maneuver': {'type': 'turn', 'modifier': 'right', 'location': list(JUNCTION)},
                  'geometry': {'type': 'LineString', 'coordinates': points[1:]}, 'intersections': [at], 'bannerInstructions': []})
  steps.append({'mode': 'driving', 'name': 'End', 'maneuver': {'type': 'arrive', 'location': list(endpoint)},
                'geometry': {'type': 'LineString', 'coordinates': [points[-1]]}, 'intersections': [arrival]})
  for step in steps:
    step['distance'] = next_turn._length(step['geometry']['coordinates'])
    step['duration'] = step['distance']/4.
    step.setdefault('bannerInstructions', [])
  return {'code': 'Ok', 'uuid': 'validation-id' if turn else 'probe-id',
          'waypoints': [{'location': list(ORIGIN)}, {'location': list(endpoint)}],
          'routes': [{'geometry': {'type': 'LineString', 'coordinates': points}, 'legs': [{'steps': steps}]}]}


def response(value):
  return Mock(content=json.dumps(value).encode(), json=Mock(return_value=value), raise_for_status=Mock())


class NextTurnClientTests(unittest.TestCase):
  def discover(self, probe=None, validated=None, third=None, direction='right', bearing=0.):
    values = [body() if probe is None else probe, body(True) if validated is None else validated]
    if third is not None:
      values.append(third)
    with patch.object(next_turn.requests, 'get', side_effect=[response(value) for value in values]) as request:
      target = next_turn.MapboxNextTurnClient(TOKEN).discover(ORIGIN, bearing, direction)
    return target, request

  def test_validated_target_excludes_synthetic_ahead_probe(self):
    target, request = self.discover()
    self.assertEqual(request.call_count, 2)
    self.assertEqual(target.junction, JUNCTION)
    self.assertAlmostEqual(target.distance_m, 100.)
    self.assertEqual(target.incoming_bearing_deg, 0.)
    self.assertEqual(target.exit_bearing_deg, 90.)
    self.assertEqual(target.geometry[-1], EXIT)
    self.assertNotEqual(target.geometry[-1], PROBE)
    self.assertEqual(target.approach_geometry, (ORIGIN, JUNCTION))
    self.assertEqual(target.turn_step_index, 1)
    self.assertEqual(target.junction_geometry_index, 1)
    self.assertFalse(target.provenance['probeEndpointIsTarget'])
    self.assertFalse(target.provenance['steeringCommandIssued'])
    for call in request.call_args_list:
      self.assertEqual(call.kwargs['timeout'], (2., 3.))
      self.assertEqual(call.kwargs['params']['snapping_include_closures'], 'false;false')
      self.assertEqual(call.kwargs['params']['snapping_include_static_closures'], 'false;false')
    self.assertNotIn(TOKEN, json.dumps(target.to_dict()))

  def test_target_and_recursive_steps_are_immutable(self):
    target, _ = self.discover()
    with self.assertRaises(FrozenInstanceError):
      target.name = 'changed'
    with self.assertRaises(TypeError):
      target.steps[1]['name'] = 'changed'
    mutable = target.to_dict()
    mutable['steps'][1]['name'] = 'changed'
    self.assertEqual(target.steps[1]['name'], 'Side Street')

  def test_restricted_entry_is_not_a_candidate(self):
    probe = body()
    probe['routes'][0]['legs'][0]['steps'][0]['intersections'][1]['entry'][1] = False
    with self.assertRaisesRegex(next_turn.NextTurnError, 'no_matching_turn'):
      self.discover(probe=probe)

  def test_incoming_heading_is_rotated_180_degrees(self):
    target, _ = self.discover()
    self.assertEqual(next_turn._delta(target.incoming_bearing_deg, target.exit_bearing_deg), 90.)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'incoming_heading_mismatch'):
      next_turn._parse_route(body(), ORIGIN, 180., PROBE, 100.)

  def test_service_exit_is_rejected_even_when_named(self):
    for road_class in ('service', 'street_limited'):
      with self.subTest(road_class=road_class), self.assertRaisesRegex(next_turn.NextTurnError, 'unsupported_road'):
        self.discover(validated=body(True, road_class))

  def test_restricted_selected_exit_is_rejected(self):
    value = body(True)
    value['routes'][0]['legs'][0]['steps'][1]['intersections'][0]['classes'] = ['restricted']
    with self.assertRaisesRegex(next_turn.NextTurnError, 'unsupported_road'):
      self.discover(validated=value)

  def test_city_trunk_street_is_allowed_but_motorway_and_ramp_are_not(self):
    target, _ = self.discover(validated=body(True, 'trunk'))
    self.assertEqual(target.road_class, 'trunk')
    for kind in ('motorway', 'restricted'):
      value = body(True, 'trunk')
      value['routes'][0]['legs'][0]['steps'][1]['intersections'][0]['classes'] = [kind]
      with self.subTest(kind=kind), self.assertRaisesRegex(next_turn.NextTurnError, 'unsupported_road'):
        self.discover(validated=value)
    value = body(True, 'trunk')
    value['routes'][0]['legs'][0]['steps'][1]['maneuver']['type'] = 'off ramp'
    with self.assertRaisesRegex(next_turn.NextTurnError, 'unsupported_junction'):
      self.discover(validated=value)

  def test_native_north_bearing_360_is_normalized_without_accepting_out_of_range(self):
    # Real 5e-15 Directions intersections contain north encoded as 360.
    probe = body()
    at = probe['routes'][0]['legs'][0]['steps'][0]['intersections'][1]
    at['bearings'][0] = 360
    target, _ = self.discover(probe=probe)
    self.assertEqual(target.incoming_bearing_deg, 0.)
    at['bearings'][0] = 361
    with self.assertRaisesRegex(next_turn.NextTurnError, 'missing_metadata'):
      self.discover(probe=probe)

  def test_missing_road_class_requires_separate_same_turn_validation(self):
    third = body(True)
    third['uuid'] = 'classification-id'
    target, request = self.discover(validated=body(True, None), third=third)
    self.assertEqual(request.call_count, 3)
    self.assertIn('/mapbox/driving/', request.call_args_list[2].args[0])
    self.assertEqual(target.classification_uuid, 'classification-id')
    with self.assertRaisesRegex(next_turn.NextTurnError, 'missing_road_class'):
      self.discover(validated=body(True, None), third=body(True, None))

  def test_missing_intermediate_legality_metadata_fails_closed(self):
    probe = body()
    del probe['routes'][0]['legs'][0]['steps'][0]['intersections'][1]['in']
    with self.assertRaisesRegex(next_turn.NextTurnError, 'missing_metadata'):
      self.discover(probe=probe)

  def test_non_boolean_entry_flags_are_not_treated_as_truth(self):
    probe = body()
    probe['routes'][0]['legs'][0]['steps'][0]['intersections'][1]['entry'][1] = 1
    with self.assertRaisesRegex(next_turn.NextTurnError, 'missing_metadata'):
      self.discover(probe=probe)

  def test_validation_cannot_turn_at_an_earlier_junction(self):
    value = body(True)
    earlier = next_turn.offset(ORIGIN, 0, 50.)
    value['routes'][0]['geometry']['coordinates'].insert(1, list(earlier))
    turn = value['routes'][0]['legs'][0]['steps'][1]['intersections'][0]
    turn.update(location=list(earlier), geometry_index=1)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'earlier_or_additional_turn'):
      self.discover(validated=value)

  def test_nearby_different_junction_is_not_the_selected_target(self):
    value = body(True)
    different = next_turn.offset(JUNCTION, 0., 5.)
    value['routes'][0]['geometry']['coordinates'][1] = list(different)
    step = value['routes'][0]['legs'][0]['steps'][1]
    step['geometry']['coordinates'][0] = list(different)
    step['intersections'][0]['location'] = list(different)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'earlier_or_additional_turn'):
      self.discover(validated=value)

  def test_two_edge_road_bend_does_not_consume_turn_intent(self):
    item = {'location': JUNCTION, 'distance': 100., 'kind': 'depart', 'step': 0,
            'incoming': 0., 'outgoing': 90., 'bearings': [90., 180.], 'entry': [True, False]}
    route = {'intersections': [item], 'steps': [{'maneuver': {'type': 'depart', 'location': ORIGIN}}]}
    with self.assertRaisesRegex(next_turn.NextTurnError, 'no_matching_turn'):
      next_turn._choose_branch(route, 'right')
    # The same two edges are eligible if the router explicitly labels a turn here.
    item['kind'] = 'turn'
    route['steps'][0]['maneuver'] = {'type': 'turn', 'location': JUNCTION}
    self.assertEqual(next_turn._choose_branch(route, 'right')['exit'], 90.)

  def test_continuing_main_road_bend_with_minor_branch_does_not_hide_next_turn(self):
    bend = {'location': JUNCTION, 'distance': 100., 'kind': 'continue', 'step': 0,
            'incoming': 0., 'outgoing': 90., 'out': 0, 'bearings': [90., 180., 270.], 'entry': [True, False, True]}
    following = {'location': next_turn.offset(JUNCTION, 90., 50.), 'distance': 150., 'kind': 'continue', 'step': 0,
                 'incoming': 90., 'outgoing': 90., 'out': 0, 'bearings': [90., 180., 270.], 'entry': [True, True, False]}
    route = {'intersections': [bend, following], 'steps': [{'maneuver': {'type': 'continue', 'location': ORIGIN}}]}
    selected = next_turn._choose_branch(route, 'right')
    self.assertEqual(selected['location'], following['location'])
    self.assertEqual(selected['exit'], 180.)

  def test_probe_uturn_can_expose_first_divided_road_branch_but_is_not_target_authority(self):
    # Native route60's ahead query U-turns at Thornbrook. Its first left edge
    # can be queried, but the second route must prove an ordinary left turn.
    item = {'location': JUNCTION, 'distance': 100., 'kind': 'continue', 'step': 0,
            'incoming': 123., 'outgoing': 37., 'out': 0,
            'bearings': [37., 122., 220., 303.], 'entry': [True, True, True, False]}
    route = {'intersections': [item],
             'steps': [{'maneuver': {'type': 'continue', 'modifier': 'uturn', 'location': JUNCTION}}]}
    selected = next_turn._choose_branch(route, 'left')
    self.assertEqual(selected['exit'], 37.)

  def test_later_turn_beyond_proven_exit_is_excluded_from_local_target(self):
    value = body(True)
    later = next_turn.offset(JUNCTION, 90., 35.)
    endpoint = next_turn.offset(later, 0., 5.)
    value['waypoints'][-1]['location'] = list(endpoint)
    points = [list(ORIGIN), list(JUNCTION), list(later), list(endpoint)]
    route = value['routes'][0]
    route['geometry']['coordinates'] = points
    steps = route['legs'][0]['steps']
    steps[1]['geometry']['coordinates'] = points[1:3]
    extra = junction(location=later, index=2, out=0)
    extra['in'] = 3
    extra['mapbox_streets_v8'] = {'class': 'service'}
    steps.insert(2, {'mode': 'driving', 'name': 'Later road',
                     'maneuver': {'type': 'turn', 'location': list(later)},
                     'geometry': {'type': 'LineString', 'coordinates': points[2:]}, 'intersections': [extra]})
    steps[-1]['maneuver']['location'] = list(endpoint)
    steps[-1]['geometry']['coordinates'] = [list(endpoint)]
    steps[-1]['intersections'][0].update(location=list(endpoint), geometry_index=3)
    parsed = next_turn._parse_route(value, ORIGIN, 0., endpoint, 15.)
    probe = next_turn._parse_route(body(), ORIGIN, 0., PROBE, 100.)
    candidate = next_turn._choose_branch(probe, 'right')
    _, _, scoped = next_turn._validate_turn(parsed, candidate, 'right')
    self.assertTrue(scoped['targetScopeTruncated'])
    with self.assertRaisesRegex(next_turn.NextTurnError, 'incomplete_navigation_route'):
      next_turn.coherent_route_steps(scoped)

  def test_additional_turn_within_first_20m_of_exit_is_rejected(self):
    value = body(True)
    near = next_turn.offset(JUNCTION, 90., 10.)
    value['routes'][0]['geometry']['coordinates'].insert(2, list(near))
    step = value['routes'][0]['legs'][0]['steps'][1]
    extra = junction(location=near, index=2, out=0)
    extra['in'] = 3
    step['intersections'].append(extra)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'earlier_or_additional_turn'):
      self.discover(validated=value)

  def test_scoped_exit_uses_along_road_length_for_gently_curved_street(self):
    value = body(True)
    first = next_turn.offset(JUNCTION, 90., 10.)
    later = next_turn.offset(first, 100., 25.)
    endpoint = next_turn.offset(later, 0., 5.)
    value['waypoints'][-1]['location'] = list(endpoint)
    points = [list(ORIGIN), list(JUNCTION), list(first), list(later), list(endpoint)]
    value['routes'][0]['geometry']['coordinates'] = points
    steps = value['routes'][0]['legs'][0]['steps']
    steps[1]['geometry']['coordinates'] = points[1:4]
    extra = {'location': list(later), 'geometry_index': 3, 'bearings': [0, 180, 280],
             'entry': [True, True, False], 'in': 2, 'out': 0, 'mapbox_streets_v8': {'class': 'street'}}
    steps.insert(2, {'mode': 'driving', 'name': 'Later street',
                     'maneuver': {'type': 'turn', 'location': list(later)},
                     'geometry': {'type': 'LineString', 'coordinates': points[3:]}, 'intersections': [extra]})
    steps[-1]['maneuver']['location'] = list(endpoint)
    steps[-1]['geometry']['coordinates'] = [list(endpoint)]
    steps[-1]['intersections'][0].update(location=list(endpoint), geometry_index=4)
    parsed = next_turn._parse_route(value, ORIGIN, 0., endpoint, 15.)
    probe = next_turn._parse_route(body(), ORIGIN, 0., PROBE, 100.)
    _, _, scoped = next_turn._validate_turn(parsed, next_turn._choose_branch(probe, 'right'), 'right')
    self.assertTrue(scoped['targetScopeTruncated'])
    self.assertAlmostEqual(next_turn._length(scoped['points'][1:]), 20., places=5)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'incomplete_navigation_route'):
      next_turn.coherent_route_steps(scoped)

  def test_validation_cannot_choose_opposite_exit(self):
    value = body(True)
    value['routes'][0]['legs'][0]['steps'][1]['intersections'][0]['out'] = 3
    with self.assertRaisesRegex(next_turn.NextTurnError, 'target_mismatch'):
      self.discover(validated=value)

  def test_clipped_discovery_is_requeried_as_a_complete_actual_exit_route(self):
    value = body(True)
    later = next_turn.offset(JUNCTION, 90., 35.)
    endpoint = next_turn.offset(later, 0., 5.)
    value['waypoints'][-1]['location'] = list(endpoint)
    points = [list(ORIGIN), list(JUNCTION), list(later), list(endpoint)]
    route = value['routes'][0]
    route['geometry']['coordinates'] = points
    steps = route['legs'][0]['steps']
    steps[1]['geometry']['coordinates'] = points[1:3]
    extra = junction(location=later, index=2, out=0)
    extra['in'] = 3
    steps.insert(2, {'mode': 'driving', 'name': 'Later', 'maneuver': {'type': 'turn', 'location': list(later)},
      'geometry': {'coordinates': points[2:]}, 'intersections': [extra]})
    steps[-1]['maneuver']['location'] = list(endpoint)
    steps[-1]['geometry']['coordinates'] = [list(endpoint)]
    steps[-1]['intersections'][0].update(location=list(endpoint), geometry_index=3)

    final = body(True)
    actual_endpoint = next_turn.offset(JUNCTION, 90., 20.)
    final['waypoints'][-1]['location'] = list(actual_endpoint)
    final_route = final['routes'][0]
    final_route['geometry']['coordinates'][-1] = list(actual_endpoint)
    final_steps = final_route['legs'][0]['steps']
    final_steps[1]['geometry']['coordinates'][-1] = list(actual_endpoint)
    final_steps[1]['distance'], final_steps[1]['duration'] = 20., 5.
    final_steps[-1]['geometry']['coordinates'] = [list(actual_endpoint)]
    final_steps[-1]['maneuver']['location'] = list(actual_endpoint)
    final_steps[-1]['intersections'][0]['location'] = list(actual_endpoint)
    target, request = self.discover(validated=value, third=final)
    self.assertEqual(request.call_count, 3)
    self.assertEqual(target.provenance['requestCount'], 3)
    self.assertTrue(target.provenance['coherentNavigationRoute'])
    self.assertFalse(target.provenance['targetScopeTruncated'])
    self.assertEqual(target.steps[-1]['maneuver']['type'], 'arrive')
    self.assertAlmostEqual(target.steps[1]['distance'], 20.)

  def test_navigation_route_rejects_missing_arrival_or_disconnected_steps(self):
    route = body(True)['routes'][0]
    steps = route['legs'][0]['steps']
    with self.assertRaisesRegex(next_turn.NextTurnError, 'incomplete_navigation_route'):
      next_turn.coherent_route_steps({'steps': steps[:-1]})
    steps[1]['geometry']['coordinates'][0] = list(next_turn.offset(JUNCTION, 0., 10.))
    steps[1]['distance'] = next_turn._length(steps[1]['geometry']['coordinates'])
    with self.assertRaisesRegex(next_turn.NextTurnError, 'disconnected_navigation_route'):
      next_turn.coherent_route_steps({'steps': steps})

  def test_close_intersection_after_corner_uses_its_local_incoming_segment(self):
    value = body(True)
    close = next_turn.offset(JUNCTION, 90., 3.)
    value['routes'][0]['geometry']['coordinates'].insert(2, list(close))
    step = value['routes'][0]['legs'][0]['steps'][1]
    step['geometry']['coordinates'].insert(1, list(close))
    step['intersections'].append({'location': list(close), 'geometry_index': 2,
                                 'bearings': [90, 270], 'entry': [True, False], 'in': 1, 'out': 0,
                                 'mapbox_streets_v8': {'class': 'street'}})
    target, _ = self.discover(validated=value)
    self.assertEqual(target.junction, JUNCTION)

  def test_unrelated_small_turn_step_cannot_be_hidden_by_bearing_threshold(self):
    value = body(True)
    extra = {'mode': 'driving', 'name': 'Detour',
             'maneuver': {'type': 'turn', 'modifier': 'slight right', 'location': list(ORIGIN)},
             'geometry': {'type': 'LineString', 'coordinates': [list(ORIGIN), list(JUNCTION)]}, 'intersections': []}
    value['routes'][0]['legs'][0]['steps'].insert(1, extra)
    with self.assertRaisesRegex(next_turn.NextTurnError, 'earlier_or_additional_turn'):
      self.discover(validated=value)

  def test_validation_rejects_uturn(self):
    value = body(True)
    at = value['routes'][0]['legs'][0]['steps'][1]['intersections'][0]
    at['out'], at['entry'][2] = 2, True
    with self.assertRaisesRegex(next_turn.NextTurnError, 'target_mismatch'):
      self.discover(validated=value)

  def test_bad_origin_snap_is_rejected(self):
    value = body()
    value['waypoints'][0]['location'] = list(next_turn.offset(ORIGIN, 90, 30.))
    with self.assertRaisesRegex(next_turn.NextTurnError, 'snapping_mismatch'):
      self.discover(probe=value)

  def test_missing_request_id_and_no_route_are_explicit(self):
    for value, reason in (({'code': 'NoRoute'}, 'no_route'), ({**body(), 'uuid': ''}, 'missing_request_id')):
      with self.subTest(reason=reason), self.assertRaisesRegex(next_turn.NextTurnError, reason):
        self.discover(probe=value)

  def test_closed_route_and_exclusion_violation_are_rejected(self):
    closed = body(True)
    closed['routes'][0]['legs'][0]['annotation'] = {'closure': [{'geometry_index_start': 1}]}
    violation = body(True)
    violation['routes'][0]['notifications'] = [{'type': 'violation'}]
    for value, reason in ((closed, 'closed_route'), (violation, 'route_violation')):
      with self.subTest(reason=reason), self.assertRaisesRegex(next_turn.NextTurnError, reason):
        self.discover(validated=value)

  def test_network_exceptions_do_not_expose_token_or_urls(self):
    with patch.object(next_turn.requests, 'get', side_effect=next_turn.requests.Timeout('https://example/?access_token='+TOKEN)):
      try:
        next_turn.MapboxNextTurnClient(TOKEN).discover(ORIGIN, 0., 'right')
      except next_turn.NextTurnError as error:
        self.assertEqual(error.reason, 'request_failed')
        self.assertNotIn(TOKEN, traceback.format_exc())
        self.assertNotIn('https://example', traceback.format_exc())
      else:
        self.fail('Expected fixed redacted failure')

  def test_invalid_direction_and_invalid_token_never_query(self):
    with patch.object(next_turn.requests, 'get') as request:
      with self.assertRaisesRegex(next_turn.NextTurnError, 'invalid_direction'):
        next_turn.MapboxNextTurnClient(TOKEN).discover(ORIGIN, 0., 'straight')
      with self.assertRaisesRegex(next_turn.NextTurnError, 'invalid_token'):
        next_turn.MapboxNextTurnClient('not a token')
      request.assert_not_called()


if __name__ == '__main__':
  unittest.main()
