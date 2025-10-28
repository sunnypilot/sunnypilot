"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom

from openpilot.sunnypilot.navd.event_builder import build_navigation_events


class MockSM(dict):
  def __init__(self, nav_msg):
    super().__init__()
    self['navigationd'] = nav_msg


class TestEventBuilder:
  def test_build_navigation_events(self):
    # These direction messages were taken courtesy of the autonomy repo <3
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=192.84873284, type='turn', modifier='left', instruction='West Esplanade Drive'),
      custom.Navigationd.Maneuver.new_message(distance=192.84809314, type='turn', modifier='right', instruction='West Esplanade Drive'),
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'Turn right onto West Esplanade Drive in 192m',
    }]
    assert events == expected

  def test_upcoming_turn_override(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.upcomingTurn = 'left'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=50.0, type='turn', modifier='right', instruction='950 Fremont Ave'),
      custom.Navigationd.Maneuver.new_message(distance=50.0, type='turn', modifier='left', instruction='950 Fremont Ave'),
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'Turning Left. Make sure to nudge the wheel!',
    }]
    assert events == expected

  def test_straight(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=100.0, type='right', modifier='Turn right', instruction='1234 Apple Way'),
      custom.Navigationd.Maneuver.new_message(distance=80.0, type='continue', modifier='straight', instruction='1234 Apple Way'),
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': 'Continue on 1234 Apple Way for 80m'
    }]
    assert events == expected
