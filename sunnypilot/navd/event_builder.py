"""
Copyright (c) 2021-, James Vecellio, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom, messaging
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL

from sunnypilot.navd.constants import NAV_CV


class EventBuilder:
  def __init__(self):
    self._counter: int = -1
    self._enabled: bool = False
    self._params = Params()

  @staticmethod
  def _build_banner_message(metric: bool, nav_msg):
    m = nav_msg.allManeuvers[1]
    banner = m.instruction

    if metric:
      dist = f'{m.distance / NAV_CV.METERS_TO_KILO:.1f} km,'
      if m.distance < NAV_CV.SHORT_DISTANCE_METERS:
        dist = f'{int(m.distance)}m,'
    else:
      dist = f'{m.distance / NAV_CV.METERS_TO_MILE:.1f} mi,'
      if m.distance < NAV_CV.QUARTER_MILE:
        dist = f'{int(m.distance * NAV_CV.METERS_TO_FEET)}ft,'

    if m.type == 'arrive' or m.type == 'depart':
      base_msg = banner
    elif banner.startswith(('Continue', 'Drive', 'Head')):
      base_msg = f'For {dist} {banner}'
    elif 'Turn' in banner or 'Take' in banner or 'Make' in banner:
      base_msg = f'In {dist} {banner}'
    else:
      base_msg = f'For {dist} Continue on {banner}'

    return base_msg

  @staticmethod
  def _get_turning_message(upcoming_turn):
    turn_messages = {
      'left': 'Turning Left. Make sure to nudge the wheel!',
      'right': 'Turning Right. Make sure to nudge the wheel!',
      'slightLeft': 'Keeping Left',
      'slightRight': 'Keeping Right',
      'sharpLeft': 'Sharp Left Turn',
      'sharpRight': 'Sharp Right Turn',
      'straight': 'Continuing Straight',
      'uturn': 'U-Turn Ahead',
    }
    return turn_messages.get(upcoming_turn, f"Upcoming {upcoming_turn.replace('_', ' ').title()}")

  @staticmethod
  def build_navigation_events(sm: messaging.SubMaster, metric=True) -> list:
    nav_msg = sm['navigationd']
    if not nav_msg.valid:
      return []

    banner_message = EventBuilder._build_banner_message(metric, nav_msg)
    if not banner_message:
      return []

    if nav_msg.upcomingTurn != 'none':
      banner_message = EventBuilder._get_turning_message(nav_msg.upcomingTurn)

    return [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'message': banner_message,
    }]

  def update(self, sm: messaging.SubMaster) -> list:
    self._counter += 1
    if self._counter % int(3.0 / DT_MDL) == 0:
      self._enabled = self._params.get("NavEvents", return_default=True)

    if self._enabled:
      return self.build_navigation_events(sm)
    else:
      return []
