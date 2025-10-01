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

TRIGGER_THRESHOLD = 30


class E2EAlertsHelper:
  def __init__(self):
    self._params = Params()
    self._frame = -1

    self.greenLightAlert = False
    self.enabled = self._params.get_bool("GreenLightAlert")

  def _read_params(self) -> None:
    if self._frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self._params.get_bool("GreenLightAlert")

    self._frame += 1

  def update(self, sm: messaging.SubMaster, events_sp: EventsSP) -> None:
    self._read_params()

    if not self.enabled:
      return

    model_x: list[float] = sm['modelV2'].position.x
    max_idx = len(model_x) - 1
    lead_status: bool = sm['radarState'].leadOne.status
    standstill: bool = sm['carState'].standstill
    gasPressed: bool = sm['carState'].gasPressed

    # Green light alert
    if model_x[max_idx] > TRIGGER_THRESHOLD and standstill and not lead_status and not gasPressed:
      self.greenLightAlert = True
    else:
      self.greenLightAlert = False

    if self.greenLightAlert:
      events_sp.add(custom.OnroadEventSP.EventName.e2eChime)
