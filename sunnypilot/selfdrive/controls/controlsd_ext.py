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
from openpilot.sunnypilot.selfdrive.controls.lib.param_store import ParamStore


class ControlsExt:
  def __init__(self, CP: structs.CarParams, params: Params):
    self.CP = CP
    self.params = params
    self.param_store = ParamStore(self.CP)
    self.get_params_sp()

    cloudlog.info("controlsd_ext is waiting for CarParamsSP")
    self.CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
    cloudlog.info("controlsd_ext got CarParamsSP")

    self.sm_services_ext = ['longitudinalPlan', 'selfdriveStateSP', 'radarState']
    self.pm_services_ext = ['carControlSP']

  def get_params_sp(self) -> None:
    self.param_store.update(self.params)

  @staticmethod
  def get_lat_active(sm: messaging.SubMaster) -> bool:
    ss_sp = sm['selfdriveStateSP']

    if ss_sp.mads.available:
      return bool(ss_sp.mads.active)

    # MADS not available, use stock state to engage
    return bool(sm['selfdriveState'].active)

  @staticmethod
  def _set_custom_lead_vehicle_state(CC_SP: custom.CarControlSP, sm: messaging.SubMaster):
    """ Update the custom LeadVehicle state in CarControlSP. """
    CC_SP.leadDistance = 0.0
    CC_SP.leadRelSpeed = 0.0


    leadOne = sm['radarState'].leadOne
    # Set leadDistance and leadRelSpeed if the lead vehicle is detected
    CC_SP.leadDistance = leadOne.dRel if leadOne.status else 0.0
    CC_SP.leadRelSpeed = leadOne.vRel if leadOne.status else 0.0

  def state_control_ext(self, sm: messaging.SubMaster) -> custom.CarControlSP:
    CC_SP = custom.CarControlSP.new_message()

    # MADS state
    CC_SP.mads = sm['selfdriveStateSP'].mads

    CC_SP.params = self.param_store.publish()

    ControlsExt._set_custom_lead_vehicle_state(CC_SP, sm)
    CC_SP.leadVisible = sm['longitudinalPlan'].hasLead

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
