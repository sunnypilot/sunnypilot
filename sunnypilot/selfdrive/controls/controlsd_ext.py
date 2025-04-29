"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import cereal.messaging as messaging
from cereal import car, custom
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class ControlsdExt:
  def __init__(self, CP: car.CarParams, params: Params):
    self.CP = CP
    cloudlog.info("controlsd_ext is waiting for CarParamsSP")
    self.CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
    cloudlog.info("controlsd_ext got CarParamsSP")

    # SP SubMaster
    self.sm_sp = messaging.SubMaster(['selfdriveStateSP'])

    # SP PubMaster
    self.pm_sp = messaging.PubMaster(['carControlSP'])

  def get_lat_active(self, fallback_lat_active: bool) -> bool:
    # Determine lat active state based on MADS availability and state
    if self.sm_sp.valid['selfdriveStateSP']:
      ss_sp = self.sm_sp['selfdriveStateSP']
      if ss_sp.mads.available:
        # If MADS is available, return its state
        return bool(ss_sp.mads.active)
    # If MADS is not available, return the fallback lateral active state passed from line 105 controlsd.py
    return fallback_lat_active

  def update_state(self):
    # Update SP SubMaster messages
    self.sm_sp.update(0)

  def create_cc_sp(self) -> custom.CarControlSP:
    # Create and return a new CarControlSP message instance
    CC_SP = custom.CarControlSP.new_message()

    # MADS state
    CC_SP.mads = self.sm_sp['selfdriveStateSP'].mads

    return CC_SP

  def publish_sp(self, CC_SP: custom.CarControlSP, can_valid: bool):
    # Publish CarControlSP
    cc_sp_send = messaging.new_message('carControlSP')
    cc_sp_send.valid = can_valid
    cc_sp_send.carControlSP = CC_SP
    self.pm_sp.send('carControlSP', cc_sp_send)
