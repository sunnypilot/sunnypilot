"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom

from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP


class E2EAlertsHelper:

  def __init__(self):
    self._params = Params()
    self._frame = -1

    self.greenLightAlert = False
    self.greenLightAlertEnabled = self._params.get_bool("GreenLightAlert")

  def _read_params(self) -> None:
    if self._frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.greenLightAlertEnabled = self._params.get_bool("GreenLightAlert")
    self._frame += 1

  def update(self, sm: messaging.SubMaster, events_sp: EventsSP) -> None:
    self._read_params()

    model_x: list[float] = sm['modelV2'].position.x
    max_idx = len(model_x) - 1
    lead_status: bool = sm['radarState'].leadOne.status
    standstill: bool = sm['carState'].standstill
    gasPressed: bool = sm['carState'].gasPressed
    _greenLightAlert = False

    # Green light alert
    if (self.greenLightAlertEnabled
            and standstill
            and model_x[max_idx] > 30
            and not lead_status
            and not gasPressed):
      _greenLightAlert = True

    self.greenLightAlert = _greenLightAlert

    if self.greenLightAlert:
      events_sp.add(custom.OnroadEventSP.EventName.e2eChime)
