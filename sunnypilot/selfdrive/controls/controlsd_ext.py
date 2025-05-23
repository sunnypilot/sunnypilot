"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import cereal.messaging as messaging
from cereal import custom

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class ControlsExt:
  def __init__(self, params: Params):
    self.params = params

    cloudlog.info("controlsd_ext is waiting for CarParamsSP")
    self.CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
    cloudlog.info("controlsd_ext got CarParamsSP")

    self.sm_services_ext = ['selfdriveStateSP']
    self.pm_services_ext = ['carControlSP']

    self.params_keys = [
      "HyundaiLongitudinalTuning",
    ]

    self.params_vals = {name: None for name in self.params_keys}
    self.get_params_sp()

  def get_params_sp(self) -> None:
    for k in self.params_keys:
      self.params_vals[k] = self.params.get(k, encoding='utf8')

  def publish_params(self) -> [structs.MapSP.Entry]:
    entries = []

    for k in self.params_keys:
      entry = structs.MapSP.Entry(key=k, value=self.params_vals[k])
      entries.append(entry)

    return entries

  @staticmethod
  def get_lat_active(sm: messaging.SubMaster) -> bool:
    ss_sp = sm['selfdriveStateSP']

    if ss_sp.mads.available:
      return bool(ss_sp.mads.active)

    # MADS not available, use stock state to engage
    return bool(sm['selfdriveState'].active)

  def state_control_ext(self, sm: messaging.SubMaster) -> custom.CarControlSP:
    CC_SP = custom.CarControlSP.new_message()

    # MADS state
    CC_SP.mads = sm['selfdriveStateSP'].mads

    CC_SP.params = self.publish_params()

    return CC_SP

  @staticmethod
  def publish_ext(CC_SP: custom.CarControlSP, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    cc_sp_send = messaging.new_message('carControlSP')
    cc_sp_send.valid = sm['carState'].canValid
    cc_sp_send.carControlSP = CC_SP

    pm.send('carControlSP', cc_sp_send)

  def run_ext(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    CC_SP = self.state_control_ext(sm)
    self.publish_ext(CC_SP, sm, pm)
