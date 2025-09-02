"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from opendbc.car.car_helpers import interfaces
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Source
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import SpeedLimitControlState, REQUIRED_INITIAL_MAX_SET_SPEED
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_controller import SpeedLimitController, ACTIVE_STATES
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

SPEED_LIMITS = {
  'residential': 25 * CV.MPH_TO_MS,  # 25 mph
  'city': 35 * CV.MPH_TO_MS,         # 35 mph
  'highway': 65 * CV.MPH_TO_MS,      # 65 mph
  'freeway': 80 * CV.MPH_TO_MS,      # 80 mph
}


class TestSpeedLimitController:

  def _setup_platform(self, car_name):
    CarInterface = interfaces[car_name]
    CP = CarInterface.get_non_essential_params(car_name)
    CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
    CI = CarInterface(CP, CP_SP)

    sunnypilot_interfaces.setup_interfaces(CI, self.params)

    return CI
  def teardown_method(self, method):
    self.reset_state()

  def reset_state(self):
    self.reset_custom_params()
    self.slc.state = SpeedLimitControlState.disabled
    self.slc.frame = -1
    self.slc.last_op_engaged_frame = 0.0
    self.slc.op_engaged = False
    self.slc.op_engaged_prev = False
    self.slc.initial_max_set = False
    self.slc._speed_limit = 0.
    self.slc.speed_limit_prev = 0.
    self.slc.last_valid_speed_limit_offsetted = 0.
    self.slc._distance = 0.
    self.slc._source = Source.none
    self.events_sp.clear()

  def setup_method(self):
    self.params = Params()
    self.reset_custom_params()
    self.events_sp = EventsSP()
    CI = self._setup_platform(TOYOTA.TOYOTA_RAV4_TSS2_2022)
    self.slc = SpeedLimitController(CI.CP)

  def reset_custom_params(self):
    self.params.put_bool("SpeedLimitControl", True)
    self.params.put_bool("IsMetric", False)
    self.params.put("SpeedLimitOffsetType", 0)
    self.params.put("SpeedLimitValueOffset", 0)

  def test_initial_state(self):
    assert self.slc.state == SpeedLimitControlState.disabled
    assert not self.slc.is_enabled
    assert not self.slc.is_active
    assert self.slc.final_cruise_speed == V_CRUISE_UNSET

  def test_disabled(self):
    self.params.put_bool("SpeedLimitControl", False)
    for _ in range(int(10. / DT_MDL)):
      _ = self.slc.update(True, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], 0, Source.car_state, self.events_sp)
    assert self.slc.state == SpeedLimitControlState.disabled

  def test_transition_disabled_to_preactive(self):
    for _ in range(int(3. / DT_MDL)):
      _ = self.slc.update(True, SPEED_LIMITS['city'], 0, SPEED_LIMITS['highway'], SPEED_LIMITS['city'], 0, Source.car_state, self.events_sp)
    assert self.slc.state == SpeedLimitControlState.preActive
    assert self.slc.is_enabled and not self.slc.is_active

  def test_preactive_to_active_with_max_speed_confirmation(self):
    self.slc.state = SpeedLimitControlState.preActive
    v_cruise_slc = self.slc.update(True, SPEED_LIMITS['city'], 0, REQUIRED_INITIAL_MAX_SET_SPEED, SPEED_LIMITS['city'], 0, Source.car_state, self.events_sp)
    assert self.slc.state == SpeedLimitControlState.active
    assert self.slc.is_enabled and self.slc.is_active
    assert v_cruise_slc == SPEED_LIMITS['city']

  def test_no_speed_limit(self):
    for v_ego in np.linspace(0, 100, 101):
      for _ in range(int(10. / DT_MDL)):
        v_cruise_slc = self.slc.update(True, v_ego, 0, 50 * CV.MPH_TO_MS, 0, 0, Source.none, self.events_sp)
        assert v_cruise_slc == V_CRUISE_UNSET
        assert self.slc.state not in ACTIVE_STATES

  def test_long_disabled(self):
    for v_ego in np.linspace(0, 100, 101):
      for _ in range(int(10. / DT_MDL)):
        v_cruise_slc = self.slc.update(False, v_ego, 0, 50 * CV.MPH_TO_MS, 50 * CV.MPH_TO_MS, 0, Source.none, self.events_sp)
        assert v_cruise_slc == V_CRUISE_UNSET
      assert self.slc.state == SpeedLimitControlState.disabled

  def test_speed_limit_at_initial_max_set_speed(self):
    v_cruise_slc = V_CRUISE_UNSET
    speed_limit = 50 * CV.MPH_TO_MS
    offset = 0

    for source in (Source.car_state, Source.map_data):
      self.reset_state()
      for _ in range(int(10. / DT_MDL)):
        v_cruise_slc = self.slc.update(True, 40 * CV.MPH_TO_MS, 0, REQUIRED_INITIAL_MAX_SET_SPEED, speed_limit, 0, source, self.events_sp)
        offset = self.slc.get_offset(self.slc.offset_type, self.slc.offset_value)
      assert self.slc.state in ACTIVE_STATES
      assert v_cruise_slc == speed_limit + offset
