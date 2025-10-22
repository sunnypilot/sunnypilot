"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom


def build_navigation_events(sm) -> list:
  nav_msg = sm.get('navigationd')
  if nav_msg is None or not nav_msg.valid:
    return []

  banner_message = _build_banner_message(nav_msg)
  if not banner_message:
    return []

  if nav_msg.upcomingTurn != 'none':
    banner_message = _get_turning_message(nav_msg.upcomingTurn)
    alert_size = 'small'
  else:
    alert_size = 'mid'

  return [{
    'name': custom.OnroadEventSP.EventName.navigationBanner,
    'type': 'warning',
    'message': banner_message,
    'size': alert_size,
  }]


def _build_banner_message(nav_msg):
  m = nav_msg.allManeuvers[0]
  if m.distance >= 1000:
    return None

  dist_str = f"{int(m.distance)}m"
  next_m = nav_msg.allManeuvers[1] if len(nav_msg.allManeuvers) > 1 else m
  banner = nav_msg.bannerInstructions

  if next_m.modifier == 'sharp right' and 'Turn right' in banner:
    banner = banner.replace('Turn right', 'Take a sharp right')
  elif next_m.modifier == 'sharp left' and 'Turn left' in banner:
    banner = banner.replace('Turn left', 'Take a sharp left')
  elif next_m.modifier == 'slight right' and 'Turn right' in banner:
    banner = banner.replace('Turn right', 'Take a slight right')
  elif next_m.modifier == 'slight left' and 'Turn left' in banner:
    banner = banner.replace('Turn left', 'Take a slight left')
  elif next_m.modifier == 'uturn' and 'Turn' in banner:
    banner = banner.replace('Turn', 'Make a U-turn', 1)

  return f"In {dist_str}, {banner}"


def _get_turning_message(upcoming_turn):
  turn_messages = {
    'left': 'Turning Left',
    'right': 'Turning Right',
    'slightLeft': 'Keeping Left',
    'slightRight': 'Keeping Right',
    'sharpLeft': 'Sharp Left Turn',
    'sharpRight': 'Sharp Right Turn',
    'straight': 'Continuing Straight',
    'uturn': 'U-Turn Ahead',
  }
  return turn_messages.get(upcoming_turn, f"Upcoming {upcoming_turn.replace('_', ' ').title()}")
