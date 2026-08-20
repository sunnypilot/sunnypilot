"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Scope is deliberately narrow: a v_ego-keyed acceleration ceiling and cruise-deceleration
floor per profile. The controller does not modify lead following distance or the MPC lead
candidate. The floor only ever softens the no-lead cruise candidate (slowing for a lower
cruise speed, a curve, or a speed limit); it is excluded during forceDecel and e2e, and
min() against the untouched MPC candidate means a real lead can always still force full
ACCEL_MIN braking.

Ceiling vs floor apply on different policies: ACC (non-e2e) uses the controller's ceiling
and floor; blended (e2e) uses the controller's ceiling but always the stock floor
(A_CRUISE_MIN).
"""
import unittest

import numpy as np

from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import (
  AccelController, AccelProfile, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES,
)


class TestAccelControllerCeiling(OpenpilotTestCase):
  def setUp(self):
    self.params = Params()
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.normal, block=True)
    self.controller = AccelController()

  def test_first_call_snaps_to_table_with_no_smoothing_lag(self):
    max_a = self.controller.get_max_accel(20.0)
    expected_max = np.interp(20.0, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.normal])
    self.assertAlmostEqual(max_a, expected_max, places=6)

  def test_min_accel_first_call_snaps_to_table_not_the_neg0p01_seed(self):
    # Regression guard: get_min_accel used to have no first-run snap (unlike get_max_accel),
    # so its very first call blended the table target against a hardcoded -0.01 seed and
    # commanded a much-weaker-than-any-profile floor for the first ~10-15 frames of every drive.
    min_a = self.controller.get_min_accel(20.0)
    expected_min = np.interp(20.0, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[AccelProfile.normal])
    self.assertAlmostEqual(min_a, expected_min, places=6)

  def test_table_lookup_matches_breakpoints_per_profile(self):
    for profile, table in MAX_ACCEL_PROFILES.items():
      self.params.put("AccelPersonality", profile, block=True)
      controller = AccelController()
      for v_ego, expected in zip(MAX_ACCEL_BREAKPOINTS, table, strict=True):
        controller.first_run = True
        max_a = controller.get_max_accel(v_ego)
        self.assertAlmostEqual(max_a, expected, places=3)

  def test_smoothing_moves_gradually_not_instantly_on_profile_switch(self):
    v_ego = 8.0  # breakpoint where eco/normal/sport ceilings differ
    self.controller.get_max_accel(v_ego)  # settle first_run on normal
    start = self.controller.last_max_accel
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    self.controller.frame = int(1.0 / DT_MDL) - 1  # force the 1s refresh boundary on next update()
    self.controller.update()
    max_a = self.controller.get_max_accel(v_ego)
    target = MAX_ACCEL_PROFILES[AccelProfile.sport][MAX_ACCEL_BREAKPOINTS.index(v_ego)]
    self.assertNotEqual(start, target)
    self.assertGreater(max_a, start)
    self.assertLess(max_a, target)

  def test_eco_is_selectable_not_treated_as_falsy(self):
    self.params.put("AccelPersonality", AccelProfile.eco, block=True)
    controller = AccelController()
    self.assertEqual(controller.profile, AccelProfile.eco)
    max_a = controller.get_max_accel(0.0)
    self.assertAlmostEqual(max_a, MAX_ACCEL_PROFILES[AccelProfile.eco][0], places=3)

  def test_min_accel_never_stronger_than_stock_a_cruise_min(self):
    for v_ego in [0., 3., 4.5, 7., 9., 15., 25., 40.]:
      for _ in range(60):
        min_a = self.controller.get_min_accel(v_ego)
      self.assertGreaterEqual(min_a, -1.4)  # softer or equal to the softest stock-adjacent floor, never harsher
      self.assertLess(min_a, 0.0)

  def test_min_accel_ramps_to_stock_strength_by_highway_speed(self):
    for _ in range(200):
      min_a = self.controller.get_min_accel(25.0)
    self.assertAlmostEqual(min_a, MIN_ACCEL_PROFILES[AccelProfile.normal][-1], places=2)

  def test_min_accel_profile_ordering_eco_softest_sport_strongest(self):
    settled = {}
    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      self.params.put("AccelPersonality", profile, block=True)
      controller = AccelController()
      for _ in range(60):
        settled[profile] = controller.get_min_accel(4.5)
    self.assertGreater(settled[AccelProfile.eco], settled[AccelProfile.normal])
    self.assertGreater(settled[AccelProfile.normal], settled[AccelProfile.sport])

  def test_min_accel_never_inverts_above_max_accel(self):
    # Both feed the same np.clip call in get_cruise_accel -- independent smoothing must
    # never let the floor drift above the ceiling.
    for v_ego in [0., 3., 8., 20., 45.]:
      max_a = self.controller.get_max_accel(v_ego)
      min_a = self.controller.get_min_accel(v_ego)
      self.assertLessEqual(min_a, max_a - 0.05)

  def test_params_refresh_only_at_one_second_boundary(self):
    self.controller.frame = 0
    self.params.put("AccelPersonality", AccelProfile.sport, block=True)
    self.controller.update()  # frame=1, not a boundary
    self.assertEqual(self.controller.profile, AccelProfile.normal)
    self.controller.frame = int(1.0 / DT_MDL) - 1
    self.controller.update()  # crosses the boundary
    self.assertEqual(self.controller.profile, AccelProfile.sport)

  def test_enabled_reflects_params(self):
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    controller = AccelController()
    self.assertFalse(controller.is_enabled())
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    controller.frame = int(1.0 / DT_MDL) - 1
    controller.update()
    self.assertTrue(controller.is_enabled())

  def test_max_accel_never_exceeds_profile_ceiling(self):
    for v_ego in [0., 5., 10., 20., 30., 45., 60.]:
      max_a = self.controller.get_max_accel(v_ego)
      table_max = max(max(table) for table in MAX_ACCEL_PROFILES.values())
      self.assertLessEqual(max_a, table_max + 1e-6)


class TestOffEqualsStock(OpenpilotTestCase):
  def setUp(self):
    self.params = Params()
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)

  def test_disabled_controller_is_enabled_returns_false(self):
    controller = AccelController()
    self.assertFalse(controller.is_enabled())

  def test_get_cruise_accel_with_none_override_matches_no_kwarg(self):
    from openpilot.selfdrive.controls.lib.longitudinal_planner import get_cruise_accel
    args = (False, 10.0, 8.0, 0.5, 0.0, _fake_cp(), DT_MDL, 1.0, True)
    self.assertEqual(get_cruise_accel(*args), get_cruise_accel(*args, max_accel_override=None, min_accel_override=None))

  def test_disabled_min_accel_override_is_none(self):
    planner = _bare_planner()
    self.assertIsNone(planner.get_min_accel_override(v_ego=5.0, e2e=False, force_decel=False))

  def test_disabled_max_accel_override_is_none(self):
    planner = _bare_planner()
    self.assertIsNone(planner.get_max_accel_override(v_ego=5.0))

  def test_force_decel_excludes_min_accel_override_even_when_enabled(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    self.assertIsNone(planner.get_min_accel_override(v_ego=5.0, e2e=False, force_decel=True))

  def test_e2e_excludes_min_accel_override_even_when_enabled(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    self.assertIsNone(planner.get_min_accel_override(v_ego=5.0, e2e=True, force_decel=False))

  def test_enabled_min_accel_override_returns_a_float(self):
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    override = planner.get_min_accel_override(v_ego=5.0, e2e=False, force_decel=False)
    self.assertIsNotNone(override)
    self.assertLess(override, 0.0)

  def test_enabled_max_accel_override_applies_in_acc_and_blended(self):
    # Policy: max ceiling comes from AccelController in both ACC and blended (e2e) modes --
    # only the min floor is blended-vs-stock. get_max_accel_override no longer takes an e2e
    # arg because of this; the caller applies it unconditionally.
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    planner = _bare_planner()
    override = planner.get_max_accel_override(v_ego=5.0)
    self.assertIsNotNone(override)
    self.assertGreater(override, 0.0)

  def test_blended_min_accel_uses_stock_not_controller(self):
    # e2e/blended braking floor is deliberately left at stock's A_CRUISE_MIN, never the
    # controller's floor -- this is the "acc policy = controller min+max, blended policy =
    # controller max + stock min" split, final per product decision.
    # jerk-limiting now applies unconditionally (even in e2e, per upstream's decel-jerk fix), so
    # dt=10.0 opens the jerk-limit window wide enough that it can't mask the floor/ceiling asserted here.
    from openpilot.selfdrive.controls.lib.longitudinal_planner import get_cruise_accel, A_CRUISE_MIN
    args = {"v_cruise": -100.0, "v_ego": 20.0, "a_cruise_prev": 0.0, "angle_steers": 0.0, "CP": _fake_cp(),
            "dt": 10.0, "accel_coast": 1.0, "allow_throttle": True}
    target, active = get_cruise_accel(True, **args, min_accel_override=-0.3)
    self.assertAlmostEqual(target, A_CRUISE_MIN, places=6)
    self.assertFalse(active)  # controller's floor was ignored in favor of stock -- not "active"

  def test_blended_max_accel_uses_controller_override(self):
    # jerk-limiting now applies unconditionally (even in e2e) -- dt=10.0 opens the jerk-limit
    # window wide enough that it can't mask the override ceiling asserted here.
    from openpilot.selfdrive.controls.lib.longitudinal_planner import get_cruise_accel
    args = {"v_cruise": 100.0, "v_ego": 20.0, "a_cruise_prev": 0.0, "angle_steers": 0.0, "CP": _fake_cp(),
            "dt": 10.0, "accel_coast": 1.0, "allow_throttle": True}
    target, active = get_cruise_accel(True, **args, max_accel_override=0.4)
    self.assertAlmostEqual(target, 0.4, places=6)
    self.assertTrue(active)
    self.assertIsInstance(active, bool)
    plan = messaging.new_message('longitudinalPlanSP')
    plan.longitudinalPlanSP.accelController.active = active



def _fake_cp():
  class _CP:
    steerRatio = 15.0
    wheelbase = 2.7
  return _CP()


def _bare_planner():
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP
  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  planner.accel_controller = AccelController()
  return planner


if __name__ == "__main__":
  unittest.main()
