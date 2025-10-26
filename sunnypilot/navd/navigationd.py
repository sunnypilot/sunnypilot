import math

import cereal.messaging as messaging
from cereal import custom
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.navd.helpers import Coordinate, parse_banner_instructions
from openpilot.sunnypilot.navd.navigation_helpers.mapbox_integration import MapboxIntegration
from openpilot.sunnypilot.navd.navigation_helpers.nav_instructions import NavigationInstructions


class Navigationd:
  def __init__(self):
    self.params = Params()
    self.mapbox = MapboxIntegration()
    self.nav_instructions = NavigationInstructions()

    self.sm = messaging.SubMaster(['liveLocationKalman'])
    self.pm = messaging.PubMaster(['navigationd'])
    self.rk = Ratekeeper(3) # 3 Hz

    self.route = None
    self.destination: str | None = None
    self.new_destination: str = ''

    self.recompute_allowed: bool = False
    self.allow_recompute: bool = False
    self.reroute_counter: int = 0
    self.cancel_route_counter: int = 0

    self.frame: int = -1
    self.last_position: Coordinate | None = None
    self.last_bearing: float | None = None
    self.is_metric: bool = False
    self.valid: bool = False

  def _update_params(self):
    if self.last_position is not None:
      self.frame += 1
      if self.frame % 9 == 0:
        self.is_metric = self.params.get('IsMetric', return_default=True)
        self.new_destination = self.params.get('MapboxRoute')
        self.recompute_allowed = self.params.get('MapboxRecompute', return_default=True)

      self.allow_recompute: bool = (self.new_destination != self.destination and self.new_destination != '') or (
        self.recompute_allowed and self.reroute_counter > 9 and self.route
      )

      if self.allow_recompute:
        postvars = {'place_name': self.new_destination}
        postvars, valid_addr = self.mapbox.set_destination(postvars, self.last_position.longitude, self.last_position.latitude, self.last_bearing)
        cloudlog.debug(f'Set new destination to: {self.new_destination}, valid: {valid_addr}')
        if valid_addr:
          self.destination = self.new_destination
          self.nav_instructions.clear_route_cache()
          self.route = self.nav_instructions.get_current_route()
          self.reroute_counter = 0

      if self.cancel_route_counter == 30:
        self.nav_instructions.clear_route_cache()
        self.params.put('MapboxSettings', {"navData": {"current": {}, "route": {}}})
        self.route = None
        self.destination = None

      self.valid = self.route is not None

  def _update_navigation(self) -> tuple[str, dict | None, dict]:
    banner_instructions: str = ''
    progress: dict | None = None
    nav_data: dict = {}
    if self.last_position is not None:
      if progress := self.nav_instructions.get_route_progress(self.last_position.latitude, self.last_position.longitude):
        nav_data['upcoming_turn'] = self.nav_instructions.get_upcoming_turn_from_progress(progress, self.last_position.latitude, self.last_position.longitude)
        nav_data['current_speed_limit'] = self.nav_instructions.get_current_speed_limit_from_progress(progress, self.is_metric)

        if progress['current_step']:
          parsed = parse_banner_instructions(progress['current_step']['bannerInstructions'], progress['distance_to_end_of_step'])
          if parsed:
            banner_instructions = parsed['maneuverPrimaryText']

        nav_data['distance_from_route'] = progress['distance_from_route']
        large_distance = nav_data['distance_from_route'] > 100

        if large_distance:
          self.cancel_route_counter += 1
          if self.recompute_allowed:
            self.reroute_counter += 1
        else:
          self.cancel_route_counter = 0
          self.reroute_counter = 0

        # Don't recompute in last segment to prevent reroute loops
        if self.route:
          if progress['current_step_idx'] == len(self.route['steps']) - 1:
            self.allow_recompute = False

    return banner_instructions, progress, nav_data

  def _build_navigation_message(self, banner_instructions: str, progress: dict | None, nav_data: dict, valid: bool):
    msg = messaging.new_message('navigationd')
    msg.valid = valid
    msg.navigationd.upcomingTurn = nav_data.get('upcoming_turn', 'none')
    msg.navigationd.currentSpeedLimit = nav_data.get('current_speed_limit', 0)
    msg.navigationd.bannerInstructions = banner_instructions
    msg.navigationd.distanceFromRoute = nav_data.get('distance_from_route', 0.0)
    msg.navigationd.valid = self.valid

    all_maneuvers = (
      [custom.Navigationd.Maneuver.new_message(distance=m['distance'], type=m['type'], modifier=m['modifier'],
                                               instruction=m['instruction']) for m in progress['all_maneuvers']]
      if progress
      else []
    )
    msg.navigationd.allManeuvers = all_maneuvers

    return msg

  def run(self):
    cloudlog.warning('navigationd init')

    while True:
      self.sm.update()
      location = self.sm['liveLocationKalman']
      localizer_valid = location.positionGeodetic.valid if location else False

      if localizer_valid:
        self.last_bearing = math.degrees(location.calibratedOrientationNED.value[2])
        self.last_position = Coordinate(location.positionGeodetic.value[0], location.positionGeodetic.value[1])

      self._update_params()
      banner_instructions, progress, nav_data = self._update_navigation()

      msg = self._build_navigation_message(banner_instructions, progress, nav_data, valid=localizer_valid)

      self.pm.send('navigationd', msg)
      self.rk.keep_time()


def main():
  nav = Navigationd()
  nav.run()
