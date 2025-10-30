"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom
from openpilot.common.params import Params

from openpilot.sunnypilot.navd.event_builder import EventBuilder


class MockSM(dict):
  def __init__(self, nav_msg):
    super().__init__()
    self['navigationd'] = nav_msg


class TestEventBuilder:
  def setup_method(self):
    self.params = Params()
    self.event_builder = EventBuilder()

  def create_nav_msg(self, upcoming_turn='none', valid=True):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = valid
    nav_msg.upcomingTurn = upcoming_turn
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=192.84873284, type='turn', modifier='left', instruction='West Esplanade Drive'),
      custom.Navigationd.Maneuver.new_message(distance=192.84809314, type='turn', modifier='right', instruction='West Esplanade Drive'),
    ]
    return nav_msg

  def test_validity(self):
    nav_msg = self.create_nav_msg(valid=False)
    events = EventBuilder.build_navigation_events(MockSM(nav_msg))
    assert events == []

  def test_enabled(self):
    self.params.put("NavEvents", True)
    nav_msg = self.create_nav_msg()
    events = self.event_builder.update(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'For 192m, Continue on West Esplanade Drive'
    }]
    assert events == expected

    self.params.put("NavEvents", False)
    self.event_builder._counter = 59
    events = self.event_builder.update(MockSM(nav_msg))
    assert events == []


  def test_build_navigation_events(self):
    nav_msg = self.create_nav_msg()
    events = EventBuilder.build_navigation_events(MockSM(nav_msg), False)
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'For 0.1 mi, Continue on West Esplanade Drive',
    }]
    assert events == expected

  def test_distance_condition_imperial(self):
    nav_msg = self.create_nav_msg()
    nav_msg.allManeuvers[1] = custom.Navigationd.Maneuver.new_message(distance=160.0, type='continue', modifier='straight', instruction='1234 Apple Way')
    events = EventBuilder.build_navigation_events(MockSM(nav_msg), False)
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'For 500ft, Continue on 1234 Apple Way',
    }]
    assert events == expected

  def test_upcoming_turn_override(self):
    nav_msg = self.create_nav_msg(upcoming_turn='left')
    events = EventBuilder.build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'Turning Left. Make sure to nudge the wheel!',
    }]
    assert events == expected

  def test_straight(self):
    nav_msg = self.create_nav_msg()
    nav_msg.allManeuvers[1] = custom.Navigationd.Maneuver.new_message(distance=80.0, type='continue', modifier='straight', instruction='1234 Apple Way')

    events = EventBuilder.build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'For 80m, Continue on 1234 Apple Way'
    }]
    assert events == expected
