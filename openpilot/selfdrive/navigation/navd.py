#!/usr/bin/env python3
import copy
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests

import openpilot.cereal.messaging as messaging
from openpilot.common.api import API_HOST, Api
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.navigation.helpers import latest_gps_source
from openpilot.selfdrive.navigation.mapbox_next_turn import MapboxNextTurnClient, NextTurnError
from openpilot.selfdrive.navigation.route import RouteTracker, along_path, cumulative_distance, local_meters, nearest_segment

REROUTE_DISTANCE = 25
MANEUVER_TRANSITION_THRESHOLD = 10
REROUTE_COUNTER_MIN = 3
ROUTE_RESEND_PERIOD = 10  # updates (seconds); a restarted mapsd gets the route within this
RECOMPUTE_HOLD = 10  # updates (seconds) between route requests
MAPBOX_TOKEN_PATH = Path('/data/navigation/mapbox_token')
TURN_TARGET_TTL = 300.  # seconds; context and GPS freshness are checked independently
TURN_GPS_MAX_AGE = .5
TURN_GPS_MAX_ACCURACY = 3.
TURN_MAX_CROSS_TRACK = 6.
TURN_MAX_HEADING_ERROR = 35.
TURN_MAX_HEADING_UNCERTAINTY = 15.
TURN_RETRY_SECONDS = 5.
TURN_PASSED_DISTANCE = 10.
TURN_ENTRY_HEADING_DEG = 25.
TURN_EXIT_COMPLETION_M = 12.


def chosen_heading(now, llk, gps):
  """Select a past, fresh calibrated heading; GPS course is a bounded fallback.

  llk: valid/status/orientationValid/orientationNed/orientationStd, optional
  baseOrientationValid/baseOrientationStd, and monotonic receivedAt/publishedAt.
  gps: valid/bearingDeg/bearingAccuracyDeg/fixAgeSeconds and those timestamps.
  The f5d producer leaves calibrated std NaN; an explicit base-orientation std
  fallback describes filter uncertainty only, not unknown calibration error.
  """
  invalid = {'headingDeg': None, 'headingValid': False, 'headingSource': None,
             'headingAgeSeconds': None, 'headingUncertaintyDeg': None,
             'headingUncertaintyKind': None, 'calibrationUncertaintyKnown': False}
  def age(sample):
    values = [now-sample['receivedAt'], now-sample['publishedAt']]
    return max(values) if np.isfinite(values).all() and all(0. <= value <= TURN_GPS_MAX_AGE for value in values) else None
  try:
    values, deviations = np.asarray(llk['orientationNed'], dtype=float), np.asarray(llk['orientationStd'], dtype=float)
    uncertainty_kind, calibration_known = 'calibrated_orientation', True
    if deviations.shape != (3,) or not np.isfinite(deviations).all() or not (deviations >= 0.).all():
      if llk.get('baseOrientationValid') is not True:
        raise ValueError('No available orientation uncertainty')
      deviations = np.asarray(llk['baseOrientationStd'], dtype=float)
      uncertainty_kind, calibration_known = 'base_orientation', False
    sample_age = age(llk)
    uncertainty = float(np.degrees(deviations[2]))
    if (llk['valid'] is True and llk['status'] == 'valid' and llk['orientationValid'] is True and
        values.shape == (3,) and deviations.shape == (3,) and np.isfinite(values).all() and
        np.isfinite(deviations).all() and (deviations >= 0.).all() and sample_age is not None and
        uncertainty <= TURN_MAX_HEADING_UNCERTAINTY):
      return {'headingDeg': float(np.degrees(values[2]) % 360.), 'headingValid': True,
              'headingSource': 'liveLocationKalman', 'headingAgeSeconds': sample_age, 'headingUncertaintyDeg': uncertainty,
              'headingUncertaintyKind': uncertainty_kind, 'calibrationUncertaintyKnown': calibration_known}
  except (KeyError, TypeError, ValueError, IndexError):
    pass
  try:
    sample_age = age(gps)
    course, uncertainty, fix_age = gps['bearingDeg'], gps['bearingAccuracyDeg'], gps['fixAgeSeconds']
    if (gps['valid'] is True and sample_age is not None and np.isfinite([course, uncertainty, fix_age]).all() and
        0. <= fix_age <= TURN_GPS_MAX_AGE and 0. < uncertainty <= TURN_MAX_HEADING_UNCERTAINTY and 0. <= course <= 360.):
      return {'headingDeg': float(course % 360.), 'headingValid': True, 'headingSource': 'gps',
              'headingAgeSeconds': max(sample_age, fix_age), 'headingUncertaintyDeg': float(uncertainty),
              'headingUncertaintyKind': 'gps_course', 'calibrationUncertaintyKnown': False}
  except (KeyError, TypeError, ValueError):
    pass
  return invalid


def approach_context(target, position, bearing_deg, horizontal_accuracy):
  """Project the raw GPS fix onto the incoming route only, without extrapolation.

  Endpoint extensions preserve signed distance before/after this junction. The
  outgoing road is deliberately excluded, so a crossroad cannot capture the
  projection. This map/GPS check does not measure physical corner clearance.
  """
  invalid = {'distanceM': None, 'crossTrackM': None, 'approachBearingDeg': None,
             'headingValid': False, 'locationValid': False, 'reason': 'invalid_target_geometry'}
  try:
    coordinates = np.asarray(target.approach_geometry, dtype=np.float64).reshape((-1, 2)).copy()
    position = np.asarray(position, dtype=np.float64).reshape(2).copy()
    if len(coordinates) < 2 or not np.isfinite(coordinates).all() or not np.isfinite(position).all():
      return invalid
    # Keep the local longitude difference short across the antimeridian.
    origin = coordinates[0].copy()
    coordinates[:, 0] = origin[0] + (coordinates[:, 0]-origin[0]+180.) % 360.-180.
    position[0] = origin[0] + (position[0]-origin[0]+180.) % 360.-180.
    points, point = local_meters(coordinates, origin), local_meters(position, origin)
    vectors = np.diff(points, axis=0)
    lengths = np.linalg.norm(vectors, axis=1)
    keep = lengths > .001
    starts, vectors, lengths = points[:-1][keep], vectors[keep], lengths[keep]
    if not len(lengths) or not np.isfinite([bearing_deg, horizontal_accuracy]).all():
      return invalid
    fractions = ((point-starts)*vectors).sum(axis=1)/lengths**2
    clipped = np.clip(fractions, 0., 1.)
    clipped[0] = min(clipped[0], fractions[0])
    clipped[-1] = max(clipped[-1], fractions[-1])
    distances = np.linalg.norm(point-starts-clipped[:, None]*vectors, axis=1)
    index = int(np.argmin(distances))
    cumulative = np.r_[0., np.cumsum(lengths)]
    progress = cumulative[:-1]+clipped*lengths
    heading = float(np.degrees(np.arctan2(vectors[index, 0], vectors[index, 1])) % 360.)
    heading_error = abs((bearing_deg-heading+180.) % 360.-180.)
    ambiguous = np.any((distances <= distances[index]+1.) & (np.abs(progress-progress[index]) > 15.))
    location_valid = 0. < horizontal_accuracy <= TURN_GPS_MAX_ACCURACY and distances[index] <= TURN_MAX_CROSS_TRACK and not ambiguous
    reason = ('ambiguous_approach' if ambiguous else 'approach_location_mismatch' if not location_valid else
              'approach_heading_mismatch' if heading_error > TURN_MAX_HEADING_ERROR else 'approach_match')
    return {'distanceM': float(cumulative[-1]-progress[index]), 'crossTrackM': float(distances[index]),
            'approachBearingDeg': heading, 'headingErrorDeg': float(heading_error),
            'headingValid': bool(heading_error <= TURN_MAX_HEADING_ERROR), 'locationValid': bool(location_valid),
            'reason': reason}
  except (AttributeError, TypeError, ValueError, IndexError):
    return invalid


def turn_route_progress(target, position, heading, entered=False):
  """Observed route progress only; no future pose or steering command."""
  points = np.asarray(target.geometry, dtype=float)
  local, point = local_meters(points, points[0]), local_meters(position, points[0])
  index, fraction, cross = nearest_segment(local[:-1], local[1:], point)
  distance = cumulative_distance(points)
  progress = float(distance[index]+fraction*(distance[index+1]-distance[index]))
  junction_distance = float(distance[target.junction_geometry_index])
  sign = 1. if target.direction == 'right' else -1.
  change = ((heading-target.incoming_bearing_deg+180.) % 360.-180.)*sign
  exit_error = abs((heading-target.exit_bearing_deg+180.) % 360.-180.)
  near = np.linalg.norm(point-local[target.junction_geometry_index]) <= 25.
  entered = bool(entered or near and change >= TURN_ENTRY_HEADING_DEG and exit_error <= 65. and cross <= TURN_MAX_CROSS_TRACK)
  exit_distance = min(TURN_EXIT_COMPLETION_M, .6*max(0., distance[-1]-junction_distance))
  completed = bool(entered and progress >= junction_distance+exit_distance and exit_error <= TURN_MAX_HEADING_ERROR and cross <= TURN_MAX_CROSS_TRACK)
  approach = approach_context(target, position, heading, 1.)
  missed = bool(not entered and approach['distanceM'] is not None and approach['distanceM'] < -TURN_PASSED_DISTANCE)
  return {'entered': entered, 'completed': completed, 'missed': missed,
          'routeProgressM': progress, 'crossTrackM': cross, 'exitHeadingErrorDeg': exit_error}


class SignalTurnEngine:
  """Session-tagged, token-only discovery with one off-thread request at a time."""
  def __init__(self, params, client_factory=None, executor=None, clock=None, wall_clock=None):
    self.params = params
    self.client_factory = client_factory if client_factory is not None else MapboxNextTurnClient
    self.executor = executor
    self.clock = clock if clock is not None else time.monotonic
    # GNSS fix time is UTC; only this comparison needs the wall clock.
    self.wall_clock = wall_clock if wall_clock is not None else time.time  # noqa: TID251
    self.key = None
    self.generation = 0
    self.pending = None
    self.target = None
    self.context = None
    self.client = None
    self.token_loaded = False
    self.failure = None
    self.retry_at = 0.
    self.blocked = False
    self.passed = False
    self.model_supports_navigation = False
    self.signal_blocked = False
    self.entered = False
    self.retained = False
    self.intent_mode = None
    self.retired_key = None

  def _invalidate(self):
    self.generation += 1
    if self.pending is not None:
      self.pending[0].cancel()
    self.target = None
    self.client = None
    self.token_loaded = False
    self.failure = None
    self.retry_at = 0.
    self.passed = False
    self.signal_blocked = False
    self.entered = False
    self.retained = False
    self.intent_mode = None

  def _clear(self):
    if self.key is not None:
      self._invalidate()
    self.key = None
    self.blocked = False
    if self.context is not None:
      self.params.remove('MapboxTurnContext')
      self.context = None

  def _publish(self, now, status, **values):
    self.context = {'session': self.key[0], 'direction': self.key[1], 'status': status, 'updatedAt': now,
                    'distanceM': None, 'locationValid': False, 'headingValid': False,
                    'modelSupportsNavigation': self.model_supports_navigation, **values}
    # route_pending is an internal proposal. Exposing it between every ready
    # update would intermittently clear valid model inputs. The RouteEngine
    # publishes ready only after the route and instruction are coherent.
    if status != 'route_pending':
      # Preserve ordering with synchronous retirement/removal of this key.
      self.params.put('MapboxTurnContext', self.context, block=True)
    return self.context

  def _consume(self):
    if self.pending is None or not self.pending[0].done():
      return
    future, generation, key = self.pending
    self.pending = None
    if generation != self.generation or key != self.key:
      return  # A canceled/opposite signal, disable or destination change retires the result.
    try:
      self.target = future.result()
      if self.target.direction != self.key[1]:
        self.target = None
        self.failure = 'target_direction_mismatch'
    except NextTurnError as error:
      self.target = None
      self.failure = error.reason
    except Exception:
      # Never log exception text/tracebacks: request URLs can contain tokens.
      self.target = None
      self.failure = 'discovery_failed'
    self.retry_at = self.clock()+TURN_RETRY_SECONDS

  def update(self, sm, source, destination_active=False):
    now = self.clock()
    if self.params.get_bool('MapboxNextTurnEnabled') is not True:
      self._clear()
      self._consume()
      return None
    intent = self.params.get('MapboxTurnIntent')
    valid_intent = (isinstance(intent, dict) and isinstance(intent.get('session'), str) and
                    1 <= len(intent['session']) <= 128 and intent.get('direction') in ('left', 'right') and
                    intent.get('mode') in ('pending', 'lane_change', 'turn'))
    model = self.params.get('NavModelState')
    supported = (isinstance(model, dict) and model.get('supported') is True and
                 isinstance(model.get('updatedAt'), (int, float)) and 0. <= now-model['updatedAt'] <= 1.)
    try:
      control_age = now-sm.logMonoTime['carControl']*1e-9
      lateral = bool(sm.valid['carControl'] and sm['carControl'].latActive and 0. <= control_age <= TURN_GPS_MAX_AGE)
      car = sm['carState']
      canceled_after_entry = self.target is not None and self.key is not None and not car.leftBlinker and not car.rightBlinker
    except (AttributeError, KeyError, TypeError):
      lateral, canceled_after_entry = False, False
    retained = bool(canceled_after_entry and self.intent_mode == 'turn' and supported and lateral and
                    (not valid_intent or (intent['session'], intent['direction']) == self.key))
    if not valid_intent and not retained:
      self._clear()
      self._consume()
      return None
    if retained:
      intent = {'session': self.key[0], 'direction': self.key[1], 'mode': 'turn', 'modelSupportsNavigation': True, 'lateralActive': True}
    key = intent['session'], intent['direction']
    if key != self.key:
      self._invalidate()
      self.key = key
      self.retired_key = None
    if destination_active != self.blocked:
      self._invalidate()
      self.blocked = destination_active
    self.intent_mode = intent['mode']
    self._consume()
    if destination_active:
      self.retired_key = key
      return self._publish(now, 'blocked', reason='explicit_destination')
    if self.retired_key == key:
      return self._publish(now, 'blocked', reason='manual_destination_preempted')
    # A model without navigation inputs still gets the turn's shape: crawl-turn steering and the corner speed read its
    # bearings and distance (modeld_v2/turn_shaping.py, controls/lib/turn_speed.py). Map inputs to the model itself stay
    # gated on modelSupportsNavigation (modeld_v2/navigation_input.py, the turn intent), as before.
    self.model_supports_navigation = bool(supported and intent.get('modelSupportsNavigation') is True)
    if not lateral or intent.get('lateralActive') is not True:
      self.target = None
      return self._publish(now, 'unavailable', reason='lateral_inactive')
    self.retained = retained
    if self.passed:
      return self._publish(now, 'passed', reason='route_completed_or_missed')
    if source is None:
      return self._publish(now, 'unavailable', reason='gps_unavailable')
    try:
      gps, car = sm[source], sm['carState']
      receipt_age, publication_age = now-sm.recv_time[source], now-sm.logMonoTime[source]*1e-9
      message_age = max(receipt_age, publication_age)
      fix_age = self.wall_clock()-gps.unixTimestampMillis*.001
      gps_age = max(message_age, fix_age)
      accuracy = float(gps.horizontalAccuracy)
      bearing = float(gps.bearingDeg)
      position = float(gps.longitude), float(gps.latitude)
      car_receipt_age, car_publication_age = now-sm.recv_time['carState'], now-sm.logMonoTime['carState']*1e-9
      gps_valid = bool(sm.valid[source] and gps.hasFix and gps.unixTimestampMillis > 0 and
                       0. <= receipt_age <= TURN_GPS_MAX_AGE and 0. <= publication_age <= TURN_GPS_MAX_AGE and
                       0. <= fix_age <= TURN_GPS_MAX_AGE and
                       0. < accuracy <= TURN_GPS_MAX_ACCURACY and
                       np.isfinite([*position, accuracy, gps_age, car.vEgo]).all() and
                       -180. <= position[0] <= 180. and -85. < position[1] < 85. and
                       sm.valid['carState'] and 0. <= car_receipt_age <= TURN_GPS_MAX_AGE and
                       0. <= car_publication_age <= TURN_GPS_MAX_AGE and str(car.gearShifter) != 'reverse')
    except (AttributeError, KeyError, TypeError, ValueError):
      return self._publish(now, 'unavailable', reason='gps_or_car_state_invalid')
    quality = {'gpsAgeSeconds': float(gps_age), 'gpsMessageAgeSeconds': float(message_age),
               'gpsFixAgeSeconds': float(fix_age), 'gpsHorizontalAccuracyM': accuracy,
               'gpsSource': source, 'gpsLogMonoTime': int(sm.logMonoTime[source]), 'speedMps': float(car.vEgo)}
    if not gps_valid:
      # Do not serialize NaN/inf into a shared JSON context.
      quality = {key: value for key, value in quality.items() if not isinstance(value, float) or np.isfinite(value)}
      return self._publish(now, 'unavailable', reason='gps_or_car_state_invalid', **quality)
    try:
      location = sm['liveLocationKalman']
      llk = {'valid': sm.valid['liveLocationKalman'], 'status': str(location.status),
             'orientationValid': location.calibratedOrientationNED.valid,
             'orientationNed': list(location.calibratedOrientationNED.value), 'orientationStd': list(location.calibratedOrientationNED.std),
             'baseOrientationValid': location.orientationNED.valid, 'baseOrientationStd': list(location.orientationNED.std),
             'receivedAt': sm.recv_time['liveLocationKalman'], 'publishedAt': sm.logMonoTime['liveLocationKalman']*1e-9}
    except (AttributeError, KeyError, TypeError):
      llk = None
    heading = chosen_heading(now, llk, {'valid': gps_valid, 'bearingDeg': bearing, 'bearingAccuracyDeg': float(gps.bearingAccuracyDeg),
      'receivedAt': sm.recv_time[source], 'publishedAt': sm.logMonoTime[source]*1e-9, 'fixAgeSeconds': fix_age})
    quality.update({key: value for key, value in heading.items() if key != 'headingValid'})
    if not heading['headingValid']:
      return self._publish(now, 'unavailable', reason='heading_unavailable', **quality)
    bearing = heading['headingDeg']
    signal = 'left' if car.leftBlinker and not car.rightBlinker else 'right' if car.rightBlinker and not car.leftBlinker else None
    if signal != key[1] and not retained:
      if not self.signal_blocked:
        self._invalidate()
        self.signal_blocked = True
      return self._publish(now, 'blocked', reason='physical_signal_mismatch', **quality)
    self.signal_blocked = False
    if self.target is not None:
      age = now-self.target.discovered_at
      if not 0. <= age <= TURN_TARGET_TTL:
        return self._publish(now, 'unavailable', reason='target_expired', **quality)
      match = approach_context(self.target, position, bearing, accuracy)
      progress = turn_route_progress(self.target, position, bearing, self.entered)
      if retained and not progress['entered']:
        self._clear()
        return None
      self.entered = progress['entered']
      if progress['completed'] or progress['missed']:
        self.passed = True
      if self.entered:
        match.update(locationValid=progress['crossTrackM'] <= TURN_MAX_CROSS_TRACK,
                     headingValid=progress['exitHeadingErrorDeg'] <= 65.)
      status = 'passed' if self.passed else 'route_pending' if match['locationValid'] and match['headingValid'] else 'unavailable'
      return self._publish(now, status, **quality, **match, **{k:v for k,v in progress.items() if k != 'crossTrackM'},
                           retainedAfterSignalCancel=retained, routeOwner='signal', junction=list(self.target.junction),
                           incomingBearingDeg=self.target.incoming_bearing_deg, exitBearingDeg=self.target.exit_bearing_deg,
                           requestId=self.target.validation_uuid, probeRequestId=self.target.probe_uuid,
                           targetAgeSeconds=age, name=self.target.name)
    if not self.token_loaded:
      token = get_mapbox_token()  # Once per session, never at 10 Hz.
      self.token_loaded = True
      if token is None:
        self.failure = 'missing_token'
      else:
        try:
          self.client = self.client_factory(token)
        except Exception:
          self.failure = 'invalid_token'
    if self.client is not None and self.pending is None and now >= self.retry_at:
      if self.executor is None:
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='navd-signal-turn')
      self.pending = (self.executor.submit(self.client.discover, position=position, bearing_deg=bearing, direction=key[1]), self.generation, key)
      self.failure = None
    return self._publish(now, 'searching' if self.pending is not None else 'unavailable',
                         reason='discovering' if self.pending is not None else self.failure or 'retry_wait', **quality)

  def close(self):
    self._clear()
    if self.executor is not None:
      self.executor.shutdown(wait=False, cancel_futures=True)


def get_mapbox_token():
  token = os.environ.get('MAPBOX_TOKEN')
  if token is not None:
    return token
  try:
    token = MAPBOX_TOKEN_PATH.read_text().strip()
  except FileNotFoundError:
    return None
  except (OSError, UnicodeError) as error:
    cloudlog.event('navd.mapbox_token_unavailable', error_type=type(error).__name__, error=True)
    return None
  if not token:
    return None
  if re.fullmatch(r'pk\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', token) is None:
    cloudlog.event('navd.mapbox_token_invalid', error=True)
    return None
  return token


def set_banner(instruction, banners, distance_to_maneuver):
  """Fill the banner fields from the banner to show now: the last one still ahead of the ego, else the first."""
  if not banners:
    return
  banner = next((b for b in reversed(banners) if distance_to_maneuver < b['distanceAlongGeometry']), banners[0])
  instruction.showFull = distance_to_maneuver < banner['distanceAlongGeometry']
  primary = banner['primary']
  instruction.maneuverPrimaryText = primary.get('text') or ''
  instruction.maneuverType = primary.get('type') or ''
  instruction.maneuverModifier = primary.get('modifier') or ''
  if banner.get('secondary') is not None:
    instruction.maneuverSecondaryText = banner['secondary']['text']


class RouteEngine:
  def __init__(self, sm, pm, params=None, update_frequency=1):
    self.sm = sm
    self.pm = pm
    self.params = params if params is not None else Params()
    if type(update_frequency) is not int or update_frequency < 1:
      raise ValueError('Navigation update frequency must be a positive integer')
    self.update_frequency = update_frequency
    self.update_counter = 0
    self.signal_turn = SignalTurnEngine(self.params)
    self.signal_preview_key = None
    self.route_owner = None
    self.route_key = None
    self.route_generation = 0
    self.route_tracker = None
    self.maneuver_distances = None

    self.last_position = None  # (longitude, latitude)
    self.last_bearing = None

    self.nav_destination = None
    self.step_idx = None
    self.route = None
    self.route_geometry = None  # an (n, 2) array of (longitude, latitude) per step

    self.recompute_hold = 0
    self.reroute_counter = 0

    self.configure_routing(get_mapbox_token())

  def configure_routing(self, token):
    self.mapbox_token = token
    self.api = Api(self.params.get("DongleId")) if self.mapbox_token is None else None
    self.mapbox_host = "https://api.mapbox.com" if self.mapbox_token is not None else API_HOST.rstrip('/') + '/v1/nav'

  def update(self):
    self.sm.update(0)
    try:
      self._update_route()
    except Exception as error:
      # API URLs can contain credentials: report only a fixed event and type.
      cloudlog.event('navd.route_processing_failed', error_type=type(error).__name__, error=True)
      self.clear_route()
      self.send_route()
      self.params.put('MapboxTurnContext', {'status': 'unavailable', 'updatedAt': time.monotonic(),
        'reason': 'route_processing_failed', 'routeGeneration': 0}, block=True)
      self.send_instruction()

  def _update_route(self):
    source = latest_gps_source(self.sm)
    if source is not None:
      gps = self.sm[source]
      self.last_position, self.last_bearing = (gps.longitude, gps.latitude), gps.bearingDeg
    destination = self.params.get('NavDestination')
    destination_active = destination is not None
    context = self.signal_turn.update(self.sm, source, destination_active=destination_active)
    legacy_tick = self.update_counter % self.update_frequency == 0
    self.update_counter += 1
    previous = self.route
    if destination_active:
      requested_destination = destination['longitude'], destination['latitude']
      if self.route_owner == 'signal' or (self.route is not None and self.nav_destination != requested_destination):
        self.clear_route()
        self.send_route()
      if legacy_tick:
        self.recompute_route(gps_ok=source is not None)
      if self.route is not previous:
        self.send_route()
      if legacy_tick or self.route is not previous:
        self.send_instruction()
      if self.route is not None and self.nav_destination == requested_destination:
        self.params.put('MapboxTurnContext', {'routeOwner': 'destination', 'status': 'ready',
          'updatedAt': time.monotonic(), 'routeGeneration': self.route_generation,
          'routePublishedAt': self.route_generation*1e-9,
          'destination': {'longitude': self.nav_destination[0], 'latitude': self.nav_destination[1]},
          'automaticStatus': 'blocked' if context is not None else None}, block=True)
      else:
        self.params.put('MapboxTurnContext', {'routeOwner': 'destination', 'status': 'searching',
          'updatedAt': time.monotonic(), 'reason': 'destination_route_pending'}, block=True)
    elif context is not None and context['status'] == 'route_pending':
      target = self.signal_turn.target
      key = context['session'], target.validation_uuid
      if self.route_owner != 'signal' or self.route_key != key:
        self.install_route([copy.deepcopy(dict(step)) for step in target.to_dict()['steps']],
                           tuple(target.geometry[-1]), owner='signal', key=key)
        self.send_route()
      self.send_instruction()
      self.signal_turn._publish(context['updatedAt'], 'ready', **{k:v for k,v in context.items()
        if k not in ('session', 'direction', 'status', 'updatedAt')}, routeGeneration=self.route_generation,
        routePublishedAt=self.route_generation*1e-9)
    else:
      target = self.signal_turn.target
      same_signal_route = (self.route_owner == 'signal' and context is not None and target is not None and
        self.route_key == (context['session'], target.validation_uuid))
      transient_unavailable = (same_signal_route and context['status'] == 'unavailable' and
        context.get('reason') not in ('target_expired', 'navigation_model_required', 'lateral_inactive', 'route_processing_failed'))
      # Keep the generation through a brief localization outage. Context and
      # instructions remain invalid, so no stale conditioning is authorized.
      if self.route_owner is not None and not transient_unavailable:
        self.clear_route()
        self.send_route()
      if context is not None:
        self.send_signal_instruction(context)
      else:
        self.params.remove('MapboxTurnContext')
        self.send_instruction()
    resend_period = self.update_frequency if self.route_owner == 'signal' else ROUTE_RESEND_PERIOD*self.update_frequency
    if self.sm.frame % resend_period == 0:
      self.send_route()

  def install_route(self, steps, destination, owner='destination', key=None):
    self.route = steps
    self.route_geometry = [np.asarray(step['geometry']['coordinates'], dtype=float).reshape((-1, 2)) for step in steps]
    self.route_tracker = RouteTracker(np.concatenate(self.route_geometry))
    starts = np.cumsum([0]+[len(path) for path in self.route_geometry[:-1]])
    self.maneuver_distances = self.route_tracker.distance[starts]
    self.step_idx, self.nav_destination = 0, destination
    self.route_owner, self.route_key = owner, key
    self.route_generation = 0

  def recompute_route(self, gps_ok: bool):
    if self.last_position is None:
      return

    destination = self.params.get("NavDestination")
    if destination is None:
      self.clear_route()
      self.recompute_hold = 0
      return
    new_destination = (destination['longitude'], destination['latitude'])

    # Don't recompute when GPS drifts in tunnels
    if not gps_ok and self.step_idx is not None:
      return

    token = get_mapbox_token()
    routing_changed = token != self.mapbox_token
    if routing_changed:
      self.configure_routing(token)
      self.recompute_hold = 0

    self.recompute_hold -= 1
    if (routing_changed or self.should_recompute() or new_destination != self.nav_destination) and self.recompute_hold <= 0:
      self.recompute_hold = RECOMPUTE_HOLD
      self.calculate_route(new_destination)
      self.reroute_counter = 0

  def calculate_route(self, destination):
    assert self.last_position is not None
    cloudlog.warning(f"Calculating route {self.last_position} -> {destination}")
    self.nav_destination = destination

    lang = self.params.get('LanguageSetting')
    if lang is not None:
      lang = lang.replace('main_', '')

    token = self.mapbox_token
    if token is None:
      token = self.api.get_token()

    params = {
      'access_token': token,
      'geometries': 'geojson',
      'overview': 'full',
      'steps': 'true',
      'banner_instructions': 'true',
      'alternatives': 'false',
      'language': lang,
    }
    if self.last_bearing is not None:
      params['bearings'] = f"{(self.last_bearing + 360) % 360:.0f},90;"

    coords_str = ';'.join(f'{lon},{lat}' for lon, lat in (self.last_position, destination))
    url = self.mapbox_host + '/directions/v5/mapbox/driving-traffic/' + coords_str
    status_code = None
    try:
      resp = requests.get(url, params=params, timeout=10)
      status_code = resp.status_code
      resp.raise_for_status()

      r = resp.json()
      if len(r['routes']):
        self.install_route(r['routes'][0]['legs'][0]['steps'], destination)
      else:
        cloudlog.warning("Got empty route response")
        self.clear_route()

    except requests.exceptions.RequestException as error:
      # HTTP errors and response bodies can contain the URL, including access_token.
      if error.response is not None:
        status_code = error.response.status_code
      cloudlog.event('navd.route_request_failed', status_code=status_code, error_type=type(error).__name__, error=True)
      self.clear_route()

  def send_instruction(self):
    msg = messaging.new_message('navInstruction', valid=True)

    if self.step_idx is None:
      msg.valid = False
      self.pm.send('navInstruction', msg)
      return

    assert self.route is not None and self.route_geometry is not None and self.last_position is not None
    step = self.route[self.step_idx]
    geometry = self.route_geometry[self.step_idx]
    along_geometry = (along_path(geometry, self.last_position)[0] if len(geometry) >= 2 else
                      float(np.linalg.norm(local_meters(self.last_position, geometry[0]))))
    distance_to_maneuver_along_geometry = step['distance'] - along_geometry

    # Banner instructions are for the following maneuver step, don't use empty last step
    banner_step = step
    if not len(banner_step.get('bannerInstructions', [])) and self.step_idx == len(self.route) - 1:
      banner_step = self.route[max(self.step_idx - 1, 0)]

    # Current instruction
    msg.navInstruction.maneuverDistance = distance_to_maneuver_along_geometry
    set_banner(msg.navInstruction, banner_step.get('bannerInstructions', []), distance_to_maneuver_along_geometry)

    # Exact afbf2e5 upstream allManeuvers semantics: each step starts at its
    # maneuver, relative to monotonic measured progress along the full route.
    progress = self.route_tracker.project(*self.last_position)
    msg.navInstruction.allManeuvers = [
      {'distance': float(distance-progress), 'type': item['maneuver']['type'], 'modifier': item['maneuver'].get('modifier', '')}
      for item, distance in zip(self.route, self.maneuver_distances, strict=True) if distance >= progress]

    # Total remaining distance and time: the rest of this step, then every step after it
    remaining = 1.0 - along_geometry / max(step['distance'], 1)
    future = self.route[self.step_idx + 1:]
    msg.navInstruction.distanceRemaining = step['distance'] * remaining + sum(s['distance'] for s in future)
    msg.navInstruction.timeRemaining = step['duration'] * remaining + sum(s['duration'] for s in future)

    self.pm.send('navInstruction', msg)

    if self.route_owner == 'signal':
      # The signal engine owns bounded completion/miss; never chase its outlet
      # with destination rerouting or remove a user-owned NavDestination.
      self.step_idx = min(int(np.searchsorted(self.maneuver_distances, progress, side='right'))-1, len(self.route)-1)
      return

    # Transition to next route segment
    if distance_to_maneuver_along_geometry < -MANEUVER_TRANSITION_THRESHOLD:
      if self.step_idx + 1 < len(self.route):
        self.step_idx += 1
        self.recompute_hold = 0
      else:
        cloudlog.warning("Destination reached")

        # Clear route if driving away from destination
        if np.linalg.norm(local_meters(self.last_position, self.nav_destination)) > REROUTE_DISTANCE:
          self.params.remove("NavDestination")
          self.clear_route()

  def send_route(self):
    coords = np.concatenate(self.route_geometry) if self.route_geometry is not None else np.empty((0, 2))
    msg = messaging.new_message('navRoute', valid=True)
    if not self.route_generation:
      self.route_generation = int(msg.logMonoTime)
    msg.logMonoTime = self.route_generation
    msg.navRoute.coordinates = [{'longitude': lon, 'latitude': lat} for lon, lat in coords.tolist()]
    self.pm.send('navRoute', msg)

  def send_signal_instruction(self, context):
    msg = messaging.new_message('navInstruction', valid=False)
    if context['status'] == 'ready':
      instruction = msg.navInstruction
      instruction.maneuverPrimaryText = 'Signal turn'
      name = context.get('name', '')
      instruction.maneuverSecondaryText = f"{context['direction'].capitalize()} onto {name}" if name else context['direction'].capitalize()
      instruction.maneuverType = 'turn'
      instruction.maneuverModifier = context['direction']
      instruction.maneuverDistance = max(0., context['distanceM'])
      instruction.distanceRemaining = max(0., context['distanceM'])
      instruction.timeRemaining = max(0., context['distanceM'])/max(context['speedMps'], 1.)
      instruction.showFull = True
    else:
      texts = {'searching': (f"Finding next {context['direction']}", 'Creating a short navigation route'),
               'unavailable': ('Navigation unavailable', 'Route conditioning withheld'),
               'blocked': ('Signal turn blocked', 'Destination navigation active'),
               'passed': ('Turn passed', 'Signal again for another turn')}
      primary, secondary = texts.get(context['status'], texts['unavailable'])
      msg.navInstruction.maneuverPrimaryText = primary
      msg.navInstruction.maneuverSecondaryText = secondary
      msg.navInstruction.maneuverType = 'notification'
      msg.navInstruction.maneuverModifier = ''
    self.pm.send('navInstruction', msg)

  def close(self):
    self.signal_turn.close()

  def clear_route(self):
    self.route = None
    self.route_geometry = None
    self.step_idx = None
    self.nav_destination = None
    self.route_owner, self.route_key = None, None
    self.route_generation = 0
    self.route_tracker, self.maneuver_distances = None, None

  def should_recompute(self):
    if self.step_idx is None:
      return True

    assert self.route is not None and self.route_geometry is not None and self.last_position is not None
    # Don't recompute in last segment, assume destination is reached
    if self.step_idx == len(self.route) - 1:
      return False

    # TODO: Check for going wrong way in segment
    if along_path(self.route_geometry[self.step_idx], self.last_position)[1] > REROUTE_DISTANCE:
      self.reroute_counter += 1
    else:
      self.reroute_counter = 0
    return self.reroute_counter > REROUTE_COUNTER_MIN


def main():
  pm = messaging.PubMaster(['navInstruction', 'navRoute'])
  sm = messaging.SubMaster(['gpsLocation', 'gpsLocationExternal', 'carState', 'carControl', 'liveLocationKalman'])

  rk = Ratekeeper(10.)
  route_engine = RouteEngine(sm, pm, update_frequency=10)
  try:
    while True:
      route_engine.update()
      rk.keep_time()
  finally:
    route_engine.close()


if __name__ == "__main__":
  main()
