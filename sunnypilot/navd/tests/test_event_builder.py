from cereal import custom

from openpilot.sunnypilot.navd.event_builder import build_navigation_events


class MockSM:
  def __init__(self, nav_msg):
    self.nav_msg = nav_msg

  def __getitem__(self, key):
    if key == 'navigationd':
      return self.nav_msg
    return None


class TestEventBuilder:
  def test_build_navigation_events(self):
    # These direction messages were taken courtesy of the autonomy repo <3
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right onto West Esplanade Drive'
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=192.848, type='depart', modifier='none'),
      custom.Navigationd.Maneuver.new_message(distance=192.64264487162754, type='turn', modifier='right')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'In 192m, Turn right onto West Esplanade Drive',
      'size': 'mid'
    }]
    assert events == expected

  def test_no_event_when_distance_too_far(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right'
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=1000.0, type='turn', modifier='right')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    assert events == []

  def test_upcoming_turn_override(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right'
    nav_msg.upcomingTurn = 'left'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=50.0, type='turn', modifier='left')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'Turning Left',
      'size': 'small'
    }]
    assert events == expected

  def test_sharp_turn_enhancement(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right onto Main St'
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=300.0, type='turn', modifier='none'),
      custom.Navigationd.Maneuver.new_message(distance=300.0, type='turn', modifier='sharp right')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'In 300m, Take a sharp right onto Main St',
      'size': 'mid'
    }]
    assert events == expected
