"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from cereal import custom
from opendbc.car.car_helpers import interfaces
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.vision_controller import SmartCruiseControlVision

VisionState = custom.LongitudinalPlanSP.SmartCruiseControl.VisionState


class TestSmartCruiseControlVision:

  def setup_method(self):
    self.params = Params()
    self.reset_params()
    CI = self._setup_platform(TOYOTA.TOYOTA_RAV4_TSS2_2022)
    self.scc_v = SmartCruiseControlVision(CI.CP)

  def teardown_method(self):
    self.scc_v.reset()

  def _setup_platform(self, car_name):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)
    sunnypilot_interfaces.setup_interfaces(CI, self.params)
    return CI

  def reset_params(self):
    self.params.put_bool("SmartCruiseControlVision", True)

  def test_initial_state(self):
    assert self.scc_v.state == VisionState.disabled
    assert not self.scc_v.is_active
    assert self.scc_v.output_v_target == V_CRUISE_UNSET
    assert self.scc_v.output_a_target == 0.
