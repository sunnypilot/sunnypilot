"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car.interfaces import ACCEL_MAX
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import (
  AccelController, AccelProfile, CRUISE_DECEL_ACCEL, CRUISE_DECEL_RESPONSE_TIME, ECO_CRUISE_DECEL_BP,
  ECO_CRUISE_DECEL_V, ECO_ENGINE_OFF_MAX_ACCEL, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES,
)


class TestAccelController(OpenpilotTestCase):
  def setUp(self):
    self.params = Params()
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.normal, block=True)

  def set_profile(self, profile: int) -> AccelController:
    self.params.put("AccelPersonality", profile, block=True)
    return AccelController()

  def test_table_breakpoints(self):
    for profile, values in MAX_ACCEL_PROFILES.items():
      controller = self.set_profile(profile)
      for speed, expected in zip(MAX_ACCEL_BREAKPOINTS, values, strict=True):
        assert controller.get_max_accel(speed) == expected

  def test_profiles_are_ordered_monotonic_and_bounded(self):
    controllers = {
      profile: self.set_profile(profile)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    previous = {profile: float("inf") for profile in controllers}

    for speed in np.linspace(0.0, 55.0, 551):
      values = {profile: controller.get_max_accel(speed) for profile, controller in controllers.items()}
      assert 0.0 <= values[AccelProfile.eco] <= values[AccelProfile.normal] <= values[AccelProfile.sport] <= ACCEL_MAX
      for profile, value in values.items():
        assert value <= previous[profile]
        previous[profile] = value

  def test_engine_off_line_only_lowers_eco(self):
    speeds = np.linspace(0.0, 40.0, 401)
    eco = self.set_profile(AccelProfile.eco)
    for speed in speeds:
      assert eco.get_max_accel(speed, engine_off=True) <= eco.get_max_accel(speed) + 1e-12
    for speed, expected in zip(MAX_ACCEL_BREAKPOINTS, ECO_ENGINE_OFF_MAX_ACCEL, strict=True):
      assert eco.get_max_accel(speed, engine_off=True) == expected

    for profile in (AccelProfile.normal, AccelProfile.sport):
      controller = self.set_profile(profile)
      for speed in speeds:
        assert controller.get_max_accel(speed, engine_off=True) == controller.get_max_accel(speed)

  def test_engine_off_eco_line_respects_hybrid_power_budget(self):
    controller = self.set_profile(AccelProfile.eco)
    for kph, budget_kw in ((60, 11.5), (70, 11.5), (80, 13.5)):
      speed = kph / 3.6
      road_load = (0.010 * 1500 * 9.81 + 0.5 * 1.2 * 0.82 * speed * speed) * speed
      wheel_power = 1500 * controller.get_max_accel(speed, engine_off=True) * speed + road_load
      assert wheel_power <= budget_kw * 1e3, kph

  def test_eco_without_lead_reduces_throttle_after_launch(self):
    eco = self.set_profile(AccelProfile.eco)
    assert eco.get_max_accel(1.0, has_lead=False) == eco.get_max_accel(1.0, has_lead=True)
    assert np.isclose(eco.get_max_accel(20.0, has_lead=False), 0.85 * eco.get_max_accel(20.0, has_lead=True))

    normal = self.set_profile(AccelProfile.normal)
    assert normal.get_max_accel(20.0, has_lead=False) == normal.get_max_accel(20.0, has_lead=True)

  def test_sport_uses_openpilot_accel_max_at_launch(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(0.0) == ACCEL_MAX

  def test_negative_speed_uses_standstill_value(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(-1.0) == MAX_ACCEL_PROFILES[AccelProfile.sport][0]

  def test_eco_cruise_decel_is_speed_scheduled_not_gap_scheduled(self):
    controller = self.set_profile(AccelProfile.eco)
    a_small = controller.get_cruise_target(22.0, 20.0) - 22.0
    a_big = controller.get_cruise_target(22.0, 12.0) - 22.0
    assert np.isclose(a_small, a_big)
    assert np.isclose(controller.get_cruise_target(19.44, 10.0) - 19.44, -0.22)
    assert np.isclose(controller.get_cruise_target(15.0, 10.0) - 15.0, -0.40)
    assert -0.40 < controller.get_cruise_target(18.0, 10.0) - 18.0 < -0.22
    # with the planner's coast accel available, >= 70 km/h coasts exactly (pitch-aware), 60-70 blends into it
    assert np.isclose(controller.get_cruise_target(22.0, 10.0, accel_coast=-0.27) - 22.0, -0.27)
    assert np.isclose(controller.get_cruise_target(15.0, 10.0, accel_coast=-0.27) - 15.0, -0.40)
    assert -0.40 < controller.get_cruise_target(18.0, 10.0, accel_coast=-0.27) - 18.0 < -0.27
    # normal ignores the coast value
    normal = self.set_profile(AccelProfile.normal)
    assert normal.get_cruise_target(22.0, 20.0, accel_coast=-0.27) == normal.get_cruise_target(22.0, 20.0)
  def test_normal_and_sport_cruise_decel_latch_then_taper(self):
    for profile in (AccelProfile.normal, AccelProfile.sport):
      controller = self.set_profile(profile)
      v_target = 10.0
      a1 = controller.get_cruise_target(14.0, v_target) - 14.0
      a2 = controller.get_cruise_target(13.0, v_target) - 13.0
      expected = min(CRUISE_DECEL_ACCEL[profile], (v_target - 14.0) / CRUISE_DECEL_RESPONSE_TIME[profile])
      assert a1 < 0 and np.isclose(a1, a2)
      assert np.isclose(a1, expected)

      a_close = controller.get_cruise_target(10.2, v_target) - 10.2
      assert a1 < a_close < 0
      assert controller.get_cruise_target(10.0, v_target) == v_target
      # A new, lower target re-latches a firmer deceleration.
      a_new_target = controller.get_cruise_target(14.0, v_target - 2.0) - 14.0
      assert a_new_target <= a1
      assert CRUISE_DECEL_RESPONSE_TIME[profile] >= 3.0

  def test_non_decel_cruise_requests_clear_latched_deceleration(self):
    controller = self.set_profile(AccelProfile.normal)
    controller.get_cruise_target(14.0, 10.0)
    assert controller.get_cruise_target(10.0, 10.0) == 10.0
    assert np.isclose(controller.get_cruise_target(14.0, 10.0) - 14.0,
                      (10.0 - 14.0) / CRUISE_DECEL_RESPONSE_TIME[AccelProfile.normal])

  def test_eco_decel_table_is_valid(self):
    assert len(ECO_CRUISE_DECEL_BP) == len(ECO_CRUISE_DECEL_V)
    assert all(decel < 0.0 for decel in ECO_CRUISE_DECEL_V)

  def test_params_refresh(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    controller.update()
    assert controller.profile == AccelProfile.sport

    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    controller.update()
    assert not controller.is_enabled()
