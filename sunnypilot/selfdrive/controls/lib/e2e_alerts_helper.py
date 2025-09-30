"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL

class E2EAlertsHelper:

  def __init__(self):
    self._params = Params()
    self._frame = -1

    self.greenLightAlert = False
    self.leadDepartAlert = False
    self.greenLightAlertEnabled = False
    self.leadDepartAlertEnabled = False

  def update(self, sm: messaging.SubMaster) -> None:
    self._read_params()
    self._frame += 1

    model_x: list[float] = sm['modelV2'].position.x
    max_idx = len(model_x) - 1
    lead_status: bool = sm['radarState'].leadOne.status
    lead_vRel: float = sm['radarState'].leadOne.vRel
    isStandstill: bool = sm['carState'].standstill
    gasPressed: bool = sm['carState'].gasPressed
    _greenLightAlert = False
    _leadDepartAlert = False

    # Green light alert
    if (self.greenLightAlertEnabled
            and isStandstill
            and model_x[max_idx] > 30
            and not lead_status
            and not gasPressed):
      _greenLightAlert = True
    # Lead departure alert
    elif (self.leadDepartAlertEnabled
          and isStandstill
          and model_x[max_idx] > 30
          and lead_status
          and lead_vRel > 1
          and not gasPressed):
      _leadDepartAlert = True

    self.greenLightAlert = _greenLightAlert
    self.leadDepartAlert = _leadDepartAlert

    if (self.greenLightAlert or self.leadDepartAlert):
      self.events_sp.add(custom.OnroadEventSP.EventName.e2eChime)

  def _read_params(self) -> None:
    if self._frame % int(3. / DT_MDL) == 0:
      self.greenLightAlertEnabled = self._params.get_bool("GreenLightAlert")
      self.leadDepartAlertEnabled = self._params.get_bool("LeadDepartAlert")
