"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import cereal.messaging as messaging
from cereal import log, custom

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class ControlsExt:
  def __init__(self, params: Params):
    cloudlog.info("controlsd_ext is waiting for CarParamsSP")
    self.CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
    cloudlog.info("controlsd_ext got CarParamsSP")

    self.sm_ext = messaging.SubMaster(['selfdriveStateSP'])
    self.pm_ext = messaging.PubMaster(['carControlSP'])

  def get_lat_active(self, selfdriveState: log.SelfdriveState) -> bool:
    ss_sp = self.sm_ext['selfdriveStateSP']

    if ss_sp.mads.available:
      return bool(ss_sp.mads.active)

    # MADS not available, use stock state to engage
    return bool(selfdriveState.active)

  def update_ext(self):
    self.sm_ext.update(15)

  def state_control_ext(self) -> custom.CarControlSP:
    CC_SP = custom.CarControlSP.new_message()

    # MADS state
    CC_SP.mads = self.sm_ext['selfdriveStateSP'].mads

    return CC_SP

  def publish_ext(self, CC_SP: custom.CarControlSP, CS: structs.CarState) -> None:
    cc_sp_send = messaging.new_message('carControlSP')
    cc_sp_send.valid = CS.canValid
    cc_sp_send.carControlSP = CC_SP

    self.pm_ext.send('carControlSP', cc_sp_send)
