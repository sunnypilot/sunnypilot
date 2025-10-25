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
    assert cls.valid_addr
    cls.route = cls.nav.get_current_route()
    assert cls.route is not None
    assert len(cls.route['steps']) > 0

  def test_set_destination(self):
    settings = self.mapbox.params.get('MapboxSettings')
    assert settings is not None
    dest_lat = settings['navData']['current']['latitude']
    dest_lon = settings['navData']['current']['longitude']
    assert dest_lat == self.postvars["latitude"] and dest_lon == self.postvars["longitude"]

  def test_get_route(self):
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
    progress = self.nav.get_route_progress(self.current_lat, self.current_lon)
    upcoming = self.nav.get_upcoming_turn_from_progress(progress, self.current_lat, self.current_lon)
    assert isinstance(upcoming, str)
    assert upcoming == 'none'

    if self.route['steps']:
      turn_lat = self.route['steps'][1]['location'].latitude
      turn_lon = self.route['steps'][1]['location'].longitude
      close_lat = turn_lat - 0.0008  # 80 ish meters before the turn
      if progress and progress.get('next_turn'):
        expected_turn = progress['next_turn']['modifier']
        upcoming_close = self.nav.get_upcoming_turn_from_progress(progress, close_lat, turn_lon)
        if expected_turn:
          assert upcoming_close == expected_turn == 'right', "Should be a right turn upcoming"

  def test_route_progress_tracking(self):
    progress = self.nav.get_route_progress(self.current_lat, self.current_lon)
    assert progress is not None
    assert 'distance_from_route' in progress
    assert 'next_turn' in progress
    assert 'current_maxspeed' in progress
    assert 'all_maneuvers' in progress
    assert 'distance_to_end_of_step' in progress
    assert progress['distance_from_route'] >= 0
    assert isinstance(progress['all_maneuvers'], list)

    speed_limit_metric = self.nav.get_current_speed_limit_from_progress(progress, True)
    speed_limit_imperial = self.nav.get_current_speed_limit_from_progress(progress, False)
    assert isinstance(speed_limit_metric, int)
    assert isinstance(speed_limit_imperial, int)
    expected_metric = int(progress['current_maxspeed'][0])
    expected_imperial = int(round(progress['current_maxspeed'][0] * CV.KPH_TO_MPH))
    assert speed_limit_metric == expected_metric
    assert speed_limit_imperial == expected_imperial
