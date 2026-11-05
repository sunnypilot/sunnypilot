"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import custom
from opendbc.car import structs
from opendbc.sunnypilot.car.interfaces import has_bsm

from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName


class AlwaysOnBsm:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self._params = Params()
    self._available = has_bsm(CP, CP_SP)
    self.enabled = False
    self.read_params()

  def read_params(self) -> None:
    self.enabled = self._available and self._params.get_bool("AlwaysOnBsm")

  def update(self, CS: structs.CarState, events_sp: EventsSP, lane_change_blocked: bool) -> None:
    # laneChangeBlocked already alerts for this case
    if not self.enabled or lane_change_blocked:
      return

    # Don't alert for hazards or if stopped/parked
    if (CS.leftBlinker and CS.rightBlinker) or CS.standstill:
      return

    if (CS.leftBlindspot and CS.leftBlinker) or (CS.rightBlindspot and CS.rightBlinker):
      events_sp.add(EventNameSP.blindSpotAlert)
