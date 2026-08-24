"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car.interfaces import ACCEL_MAX
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.longitudinal_planner import (
  A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS, A_CRUISE_MIN, J_CRUISE_VALS, get_cruise_accel,
)
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
      AccelProfile.eco: self.set_profile(AccelProfile.eco),
      AccelProfile.normal: self.set_profile(AccelProfile.normal),
      AccelProfile.sport: self.set_profile(AccelProfile.sport),
    }
    previous = {profile: float("inf") for profile in controllers}

    for speed in np.linspace(0.0, 55.0, 551):
      values = {profile: controller.get_max_accel(speed) for profile, controller in controllers.items()}
      assert 0.0 <= values[AccelProfile.eco] <= values[AccelProfile.normal] <= values[AccelProfile.sport] <= 2.0
      for profile, value in values.items():
        assert value <= previous[profile]
        previous[profile] = value

  def test_profiles_stay_within_openpilot_accel_max(self):
    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      controller = self.set_profile(profile)
      for speed in np.linspace(0.0, 55.0, 551):
        assert controller.get_max_accel(speed) <= ACCEL_MAX

  def test_profiles_have_material_separation(self):
    controllers = [self.set_profile(profile) for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)]
    for speed in MAX_ACCEL_BREAKPOINTS:
      eco, normal, sport = (controller.get_max_accel(speed) for controller in controllers)
      assert normal - eco >= 0.1 - 1e-12
      assert sport - normal >= 0.1 - 1e-12
    for speed in MAX_ACCEL_BREAKPOINTS[1:-1]:
      assert controllers[2].get_max_accel(speed) - controllers[0].get_max_accel(speed) >= 0.3 - 1e-12

  def test_profiles_keep_usable_road_speed_acceleration(self):
    # A previous revision had eco at 0.20 m/s^2 at 40 m/s. 1% of road grade costs 0.098 m/s^2 of gravity, so
    # that profile cannot hold speed on anything steeper than ~2% and can never recover once it bleeds off.
    # This is a LOWER bound on purpose: the tapered upper bounds it replaces let highway accel go to zero.
    controllers = {profile: self.set_profile(profile) for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)}
    for speed in np.linspace(8.0, 40.0, 321):
      stock = float(np.interp(speed, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS))
      values = {profile: controller.get_max_accel(speed) for profile, controller in controllers.items()}
      # 0.35 m/s^2 holds a 3% grade; the fractions keep merges and passes usable.
      assert values[AccelProfile.eco] >= max(0.35, 0.60 * stock), speed
      assert values[AccelProfile.normal] >= 0.80 * stock, speed
      assert values[AccelProfile.sport] >= stock, speed

  def test_eco_never_exceeds_stock(self):
    controller = self.set_profile(AccelProfile.eco)
    for speed in np.linspace(0.0, 55.0, 551):
      assert controller.get_max_accel(speed) <= float(np.interp(speed, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)) + 1e-12, speed

  def test_comfort_profile_caps_taper_after_launch(self):
    for profile in (AccelProfile.eco, AccelProfile.normal):
      values = MAX_ACCEL_PROFILES[profile]
      assert values[3] <= 0.55 * values[0]

  def test_sport_uses_openpilot_accel_max_at_launch(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(0.0) == ACCEL_MAX
    assert all(controller.get_max_accel(speed) <= ACCEL_MAX for speed in np.linspace(0.0, 55.0, 551))

  def test_ceiling_is_continuous_in_speed(self):
    # The ceiling is the only thing the controller sets, so a step in it is a step in the commanded
    # acceleration. dt=10 makes the stock jerk limiter a no-op so nothing can hide a discontinuity.
    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      controller = self.set_profile(profile)
      speeds = np.linspace(0.0, 45.0, 451)
      spacing = float(speeds[1] - speeds[0])
      commands = np.asarray([
        get_cruise_accel(False, 60.0, speed, 0.0, 0.0, _fake_cp(), 10.0, 0.0, True, controller.get_max_accel(speed))
        for speed in speeds
      ])
      assert np.all(np.isfinite(commands)), profile
      assert np.all(np.abs(np.diff(commands)) <= spacing * 1.05 + 1e-9), profile

  def test_negative_speed_uses_standstill_value(self):
    controller = self.set_profile(AccelProfile.sport)
    assert controller.get_max_accel(-1.0) == MAX_ACCEL_PROFILES[AccelProfile.sport][0]

  def test_profile_change_has_no_controller_filter(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    controller.frame = int(1.0 / DT_MDL) - 1
    controller.update()
    index = MAX_ACCEL_BREAKPOINTS.index(10.0)
    assert controller.get_max_accel(10.0) == MAX_ACCEL_PROFILES[AccelProfile.sport][index]

  def test_params_refresh_once_per_second(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    controller.update()
    assert controller.profile == AccelProfile.normal
    controller.frame = int(1.0 / DT_MDL) - 1
    controller.update()
    assert controller.profile == AccelProfile.sport

  def test_enabled_param_refresh(self):
    controller = self.set_profile(AccelProfile.normal)
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    controller.frame = int(1.0 / DT_MDL) - 1
    controller.update()
    assert not controller.is_enabled()


class TestPlannerIntegration(OpenpilotTestCase):
  def setUp(self):
    self.params = Params()
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)

  def test_none_override_matches_stock(self):
    for e2e in (False, True):
      for allow_throttle in (False, True):
        args = (e2e, 30.0, 12.0, 0.2, 4.0, _fake_cp(), DT_MDL, -0.3, allow_throttle)
        assert get_cruise_accel(*args) == get_cruise_accel(*args, max_accel_override=None)

  def test_profiles_do_not_change_far_braking(self):
    # The ceiling is an upper bound only, so it can never participate in a deceleration. Braking authority
    # stays with stock's clip to A_CRUISE_MIN for every profile.
    args = (False, 0.0, 20.0, 0.0, 0.0, _fake_cp(), 10.0, -0.3, True)
    stock = get_cruise_accel(*args)
    assert stock == A_CRUISE_MIN
    for profile_values in MAX_ACCEL_PROFILES.values():
      assert get_cruise_accel(*args, max_accel_override=profile_values[0]) == stock

  def test_stock_jerk_limit_still_owns_smoothing(self):
    speed = 8.0
    sport_limit = np.interp(speed, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.sport])
    target = get_cruise_accel(False, 30.0, speed, 0.0, 0.0, _fake_cp(), DT_MDL, 0.0, True, sport_limit)
    jerk_limit = np.interp(speed, A_CRUISE_MAX_BP, J_CRUISE_VALS) * DT_MDL
    assert np.isclose(target, jerk_limit)

  def test_disabled_leaves_stock_limit_active(self):
    planner = _bare_planner()
    for e2e in (False, True):
      assert planner.get_max_accel_override(5.0, 30.0, e2e=e2e) is None
      assert planner.accel_controller_active is False

  def test_e2e_uses_enabled_profile(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    expected = np.interp(5.0, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.normal])
    assert planner.get_max_accel_override(5.0, 30.0, e2e=True) == expected
    assert planner.accel_controller_active is True

  def test_enabled_acc_uses_python_native_telemetry_types(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    planner = _bare_planner()
    expected = np.interp(5.0, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.sport])
    assert planner.get_max_accel_override(5.0, 30.0, e2e=False) == expected
    assert type(planner.accel_controller_active) is bool
    assert type(planner.accel_controller.is_enabled()) is bool
    assert type(planner.accel_controller.profile) is int

  def test_normal_profile_uses_tuned_limit(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.normal, block=True)
    planner = _bare_planner()
    expected = np.interp(5.0, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.normal])
    assert planner.get_max_accel_override(5.0, 30.0, e2e=False) == expected
    assert planner.accel_controller_active is True

  def test_ceiling_applies_to_every_target_source(self):
    # The ceiling is speed-scheduled only, so it is deliberately source-independent. This is what the old
    # COMFORT_SOURCES allow-list existed to qualify; with target shaping gone there is nothing to gate,
    # because an upper bound on acceleration cannot soften an SCC or speed-limit deceleration.
    from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanSource

    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    speed = 29.0
    expected = planner.accel_controller.get_max_accel(speed)

    for source in (LongitudinalPlanSource.cruise, LongitudinalPlanSource.sccVision,
                   LongitudinalPlanSource.sccMap, LongitudinalPlanSource.speedLimitAssist):
      planner.source = source
      assert np.isclose(planner.get_max_accel_override(speed, 33.0, e2e=False), expected), source

  def test_carried_accel_state_cannot_ratchet_above_the_ceiling(self):
    # get_cruise_accel clips to max_accel FIRST and applies its jerk limit SECOND, so when
    # a_cruise_prev - j*dt is above the ceiling, that second clip's lower bound pulls the command back over
    # it and can only walk down at j_cruise. a_cruise is force-set to the measured aEgo on reset_state, so
    # after the driver accelerates hard and lifts off, openpilot re-engages pinned above the profile.
    # Measured on route 000005dd: 87 frames commanding up to 1.70 m/s^2 where eco allows 0.87.
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.eco, block=True)
    planner = _bare_planner()
    v_ego = 9.84
    ceiling = planner.accel_controller.get_max_accel(v_ego)

    planner.a_cruise = 1.90  # what a hard driver launch leaves behind
    override = planner.get_max_accel_override(v_ego, 30.0, e2e=False)

    assert np.isclose(override, ceiling)
    assert planner.a_cruise <= ceiling + 1e-12
    accel = get_cruise_accel(False, 30.0, v_ego, planner.a_cruise, 0.0, _fake_cp(), DT_MDL, 0.0, True, override)
    assert accel <= ceiling + 1e-12

    # Braking must be untouched: the clamp is upper-side only.
    for carried in (-3.5, -1.2, -0.4, 0.0):
      planner.a_cruise = carried
      planner.get_max_accel_override(v_ego, 30.0, e2e=False)
      assert planner.a_cruise == carried, carried

    # Disabled must not touch the carried state at all.
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    off = _bare_planner()
    off.a_cruise = 1.90
    assert off.get_max_accel_override(v_ego, 30.0, e2e=False) is None
    assert off.a_cruise == 1.90

  def test_e2e_candidate_is_held_through_a_brake_but_not_otherwise(self):
    # Route 000005dd: e2e -> lead1 stepped +2.25 m/s^2 in one frame (45 m/s^3) and back the next, while the
    # model held desiredAcceleration at -1.63 and never moved more than 0.024. Dropping a candidate the model
    # still owns is what produced the brake/gas/brake flip.
    from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import E2E_BRAKE_HOLD_ACCEL, MpcPlanSource

    planner = _bare_planner()

    class _Mpc:
      source = MpcPlanSource.cruise

    class _Dec:
      def __init__(self):
        self._active = True
        self._mode = "acc"

      def active(self):
        return self._active

      def mode(self):
        return self._mode

    planner.mpc = _Mpc()
    planner.dec = _Dec()

    def sm(experimental: bool, model_accel: float):
      return {
        'selfdriveState': type("S", (), {"experimentalMode": experimental})(),
        'modelV2': type("M", (), {"action": type("A", (), {"desiredAcceleration": model_accel})()})(),
      }

    braking = E2E_BRAKE_HOLD_ACCEL - 1.0

    # Not experimental: never e2e, whatever the model wants.
    assert planner.is_e2e(sm(False, braking)) is False

    # DEC in acc, and the model was NOT the selected source: acc stands. This is the case that must stay
    # untouched, or a phantom model brake could be pulled into the arbitration that never won it.
    planner.mpc.source = MpcPlanSource.lead0
    assert planner.is_e2e(sm(True, braking)) is False

    # DEC in acc, model WAS selected and is still braking: hold it rather than release the brake.
    planner.mpc.source = MpcPlanSource.e2e
    assert planner.is_e2e(sm(True, braking)) is True

    # Still selected but no longer braking: release, DEC's decision stands.
    assert planner.is_e2e(sm(True, 0.0)) is False
    assert planner.is_e2e(sm(True, E2E_BRAKE_HOLD_ACCEL + 0.01)) is False

    # DEC blended, or DEC inactive, is unconditionally e2e as before.
    planner.dec._mode = "blended"
    assert planner.is_e2e(sm(True, 1.0)) is True
    planner.dec._mode = "acc"
    planner.dec._active = False
    assert planner.is_e2e(sm(True, 1.0)) is True


def _fake_cp():
  class CP:
    steerRatio = 15.0
    wheelbase = 2.7

  return CP()


def _bare_planner():
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, LongitudinalPlanSource

  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  planner.accel_controller = AccelController()
  planner.accel_controller_active = False
  planner.allow_throttle = True
  planner.a_cruise = 0.0
  planner.source = LongitudinalPlanSource.cruise
  return planner
