"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os

from openpilot.common.constants import CV

from openpilot.sunnypilot.navd.navigation_helpers.mapbox_integration import MapboxIntegration
from openpilot.sunnypilot.navd.navigation_helpers.nav_instructions import NavigationInstructions


class TestMapbox:
  @classmethod
  def setup_class(cls):
    cls.mapbox = MapboxIntegration()
    cls.nav = NavigationInstructions()

    token = os.environ.get('MAPBOX_TOKEN_CI')
    if token:
      cls.mapbox.params.put('MapboxToken', token)

    # route setup
    cls.current_lon, cls.current_lat = -119.17557, 34.23305
    cls.mapbox.params.put('MapboxRoute', '740 E Ventura Blvd. Camarillo, CA')
    cls.postvars = {"place_name": cls.mapbox.params.get('MapboxRoute')}
    cls.postvars, cls.valid_addr = cls.mapbox.set_destination(cls.postvars, cls.current_lon, cls.current_lat)
    cls.route = cls.nav.get_current_route()
    cls.progress = cls.nav.get_route_progress(cls.current_lat, cls.current_lon)

  def test_set_destination(self):
    assert self.valid_addr
    settings = self.mapbox.params.get('MapboxSettings')
    assert settings is not None
    dest_lat = settings['navData']['current']['latitude']
    dest_lon = settings['navData']['current']['longitude']
    assert dest_lat == self.postvars["latitude"] and dest_lon == self.postvars["longitude"]

  def test_get_route(self):
    assert self.route is not None
    assert 'steps' in self.route
    assert 'geometry' in self.route
    assert 'maxspeed' in self.route
    assert 'total_distance' in self.route
    assert 'total_duration' in self.route
    assert len(self.route['steps']) > 0
    assert len(self.route['geometry']) > 0
    assert len(self.route['maxspeed']) > 0

    if self.route and 'steps' in self.route:
      for step in self.route['steps']:
        assert 'modifier' in step

  def test_upcoming_turn_detection(self):
    upcoming = self.nav.get_upcoming_turn_from_progress(self.progress, self.current_lat, self.current_lon, v_ego=40.0)
    assert isinstance(upcoming, str)
    assert upcoming == 'none'

    if self.route['steps']:
      turn_lat = self.route['steps'][1]['location'].latitude
      turn_lon = self.route['steps'][1]['location'].longitude
      close_lat = turn_lat - 0.000175  # slightly before the turn
      if self.progress and self.progress.get('next_turn'):
        expected_turn = self.progress['next_turn']['modifier']
        upcoming_close = self.nav.get_upcoming_turn_from_progress(self.progress, close_lat, turn_lon, v_ego=0.0)
        if expected_turn:
          assert upcoming_close == expected_turn == 'right', "Should be a right turn upcoming"

  def test_route_progress_tracking(self):
    assert self.progress is not None
    assert 'distance_from_route' in self.progress
    assert 'next_turn' in self.progress
    assert 'current_maxspeed' in self.progress
    assert 'all_maneuvers' in self.progress
    assert 'distance_to_end_of_step' in self.progress
    assert self.progress['distance_from_route'] >= 0
    assert isinstance(self.progress['all_maneuvers'], list)

  def test_speed_limit_handling(self):
    speed_limit_metric = self.progress['current_maxspeed'][0]
    speed_limit_imperial = (round(speed_limit_metric * CV.KPH_TO_MPH))
    assert isinstance(speed_limit_metric, int)
    assert isinstance(speed_limit_imperial, int)

  def test_arrival_detection(self):
    is_arrived = self.nav.arrived_at_destination(self.progress, 2.0)
    assert isinstance(is_arrived, bool)
    assert not is_arrived

  def test_bearing_misalign(self):
    lat = self.route['steps'][1]['location'].latitude
    lon = self.route['steps'][1]['location'].longitude
    self.nav.get_route_progress(lat, lon)
    route_bearing_misaligned = self.nav.route_bearing_misalign(self.route, 45, 5.0)
    # based on math: closest index: 7, normalized bearing: 45 route bearing: 180.5486953778888, expected differential: 135.54869538
    assert route_bearing_misaligned
