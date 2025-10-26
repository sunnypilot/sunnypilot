"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom


def build_navigation_events(sm) -> list:
  nav_msg = sm['navigationd']
  if not nav_msg.valid:
    return []

  banner_message = _build_banner_message(nav_msg)
  if not banner_message:
    return []

  if nav_msg.upcomingTurn != 'none':
    banner_message = _get_turning_message(nav_msg.upcomingTurn)

  return [{
    'name': custom.OnroadEventSP.EventName.navigationBanner,
    'type': 'warning',
    'message': banner_message,
  }]


def _build_banner_message(nav_msg):
  m = nav_msg.allManeuvers[0]
  banner = m.instruction
  dist = f'{int(m.distance)}m'

  if m.type == 'arrive':
    base_msg = banner
  elif m.modifier == 'left' and 'Turn left' not in banner:
    base_msg = f'Turn left onto {banner} in {dist}'
  elif m.modifier == 'right' and 'Turn right' not in banner:
    base_msg = f'Turn right onto {banner} in {dist}'
  elif 'Turn' in banner or 'Take' in banner or 'Make' in banner:
    base_msg = f'{banner} in {dist}'
  elif 'Continue' in banner:
    base_msg = f'{banner} for {dist}'
  else:
    base_msg = f'Continue on {banner} for {dist}'

  return base_msg


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
