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

    self.green_light_alert = False
    self.green_light_alert_enabled = self._params.get_bool("GreenLightAlert")

  def _read_params(self) -> None:
    if self._frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.green_light_alert_enabled = self._params.get_bool("GreenLightAlert")

    self._frame += 1

  def update(self, sm: messaging.SubMaster, events_sp: EventsSP) -> None:
    self._read_params()

    if not self.green_light_alert_enabled:
      return

    CS = sm['carState']
    CC = sm['carControl']

    model_x = sm['modelV2'].position.x
    max_idx = len(model_x) - 1
    has_lead = sm['radarState'].leadOne.status

    # Green light alert
    self.green_light_alert = model_x[max_idx] > TRIGGER_THRESHOLD and \
                           not has_lead and CS.standstill and not CS.gasPressed and not CC.enabled

    if self.green_light_alert:
      events_sp.add(custom.OnroadEventSP.EventName.e2eChime)
