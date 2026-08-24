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
  AccelController, AccelProfile, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES,
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

  def test_profile_ordering_and_bounds(self):
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

  def test_profiles_keep_usable_road_speed_acceleration(self):
    controllers = {
      profile: self.set_profile(profile)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    for speed in np.linspace(8.0, 40.0, 321):
      stock = float(np.interp(speed, [0.0, 10.0, 25.0, 40.0], [1.6, 1.2, 0.8, 0.6]))
      values = {profile: controller.get_max_accel(speed) for profile, controller in controllers.items()}
      assert values[AccelProfile.eco] >= max(0.35, 0.60 * stock), speed
      assert values[AccelProfile.normal] >= 0.80 * stock, speed
      assert values[AccelProfile.sport] >= stock, speed

  def test_eco_never_exceeds_stock(self):
    controller = self.set_profile(AccelProfile.eco)
    stock_breakpoints = [0.0, 10.0, 25.0, 40.0]
    stock_values = [1.6, 1.2, 0.8, 0.6]
    for speed in np.linspace(0.0, 55.0, 551):
      assert controller.get_max_accel(speed) <= np.interp(speed, stock_breakpoints, stock_values) + 1e-12

  def test_profiles_have_material_separation(self):
    controllers = [self.set_profile(profile) for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)]
    for speed in MAX_ACCEL_BREAKPOINTS:
      eco, normal, sport = (controller.get_max_accel(speed) for controller in controllers)
      assert normal - eco >= 0.1 - 1e-12
      assert sport - normal >= 0.1 - 1e-12

  def test_sport_uses_openpilot_accel_max_at_launch(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(0.0) == ACCEL_MAX

  def test_negative_speed_uses_standstill_value(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(-1.0) == MAX_ACCEL_PROFILES[AccelProfile.sport][0]

  def test_limit_accel_only_limits_positive_values(self):
    controller = self.set_profile(AccelProfile.eco)
    assert controller.limit_accel(2.0, 0.0) == controller.get_max_accel(0.0)
    assert controller.limit_accel(1.0, 0.0) == 1.0
    assert controller.limit_accel(-1.5, 0.0) == -1.5

  def test_disabled_limit_is_passthrough(self):
    controller = self.set_profile(AccelProfile.eco)
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    controller.update()
    assert controller.limit_accel(1.5, 0.0) == 1.5
    assert controller.limit_accel(-1.5, 0.0) == -1.5

  def test_profile_change_refreshes_ceiling(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    controller.update()
    assert controller.get_max_accel(10.0) == MAX_ACCEL_PROFILES[AccelProfile.sport][3]

  def test_params_refresh_every_update(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    controller.update()
    assert controller.profile == AccelProfile.sport

  def test_enabled_param_refresh(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    controller.update()
    assert not controller.is_enabled()
