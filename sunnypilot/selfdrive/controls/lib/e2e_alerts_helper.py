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

GREEN_LIGHT_X_THRESHOLD = 30


class E2EAlertsHelper:
  def __init__(self):
    self._params = Params()
    self.frame = -1

    self.green_light_alert = False
    self.green_light_alert_enabled = self._params.get_bool("GreenLightAlert")
    self.lead_depart_alert = False
    self.lead_depart_alert_enabled = self._params.get_bool("LeadDepartAlert")

    self.alert_allowed = False
    self.green_light_alert_count = 0
    self.last_lead_distance = -1
    self.last_moving_frame = -1

  def _read_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.green_light_alert_enabled = self._params.get_bool("GreenLightAlert")
      self.lead_depart_alert_enabled = self._params.get_bool("LeadDepartAlert")

  def update(self, sm: messaging.SubMaster, events_sp: EventsSP) -> None:
    self._read_params()

    CS = sm['carState']
    CC = sm['carControl']

    model_x = sm['modelV2'].position.x
    max_idx = len(model_x) - 1
    has_lead = sm['radarState'].leadOne.status
    lead_dRel = sm['radarState'].leadOne.dRel
    standstill = CS.standstill
    moving = not standstill and CS.vEgo > 0.1
    _allowed = standstill and not CS.gasPressed and not CC.enabled

    if moving:
      self.last_moving_frame = self.frame
    recent_moving = self.last_moving_frame == -1 or (self.frame - self.last_moving_frame) * DT_MDL < 2.0

    if standstill and not recent_moving:
      self.alert_allowed = True
    elif not standstill:
      self.alert_allowed = False
      self.green_light_alert_count = 0
      self.last_lead_distance = -1

    # Green Light Alert
    _green_light_alert = False
    if self.green_light_alert_enabled and _allowed and not has_lead and model_x[max_idx] > GREEN_LIGHT_X_THRESHOLD:
      if self.alert_allowed:
        self.green_light_alert_count += 1
      else:
        self.green_light_alert_count = 0

      if self.green_light_alert_count > 2 and self.alert_allowed:
        _green_light_alert = True
        self.alert_allowed = False
    else:
      self.green_light_alert_count = 0

    self.green_light_alert = _green_light_alert

    # Lead Departure Alert
    _lead_depart_alert = False
    if self.lead_depart_alert_enabled and _allowed and has_lead:
      if self.last_lead_distance == -1 or lead_dRel < self.last_lead_distance:
        self.last_lead_distance = lead_dRel

      if self.last_lead_distance != -1 and (lead_dRel - self.last_lead_distance > 1.0) and self.alert_allowed:
        _lead_depart_alert = True
        self.alert_allowed = False

    self.lead_depart_alert = _lead_depart_alert

    if self.green_light_alert or self.lead_depart_alert:
      events_sp.add(custom.OnroadEventSP.EventName.e2eChime)

    self.frame += 1
