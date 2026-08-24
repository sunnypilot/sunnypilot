from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import (
  limit_speed_limit_decel_target,
  no_lead_normal_decel_idle_active,
  speed_limit_current_limit_decel_needed,
  speed_limit_idle_active,
  speed_limit_no_brake_accel_target,
  speed_limit_no_brake_active,
)


def test_speed_limit_no_brake_requires_lower_lookahead_active():
  assert speed_limit_no_brake_active(True, True, False)
  assert not speed_limit_no_brake_active(True, False, False)


def test_speed_limit_no_brake_disabled_with_lead():
  assert not speed_limit_no_brake_active(True, True, True)


def test_speed_limit_no_brake_disabled_by_config():
  assert not speed_limit_no_brake_active(False, True, False)


def test_speed_limit_no_brake_uses_configured_accel_above_release_gap():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  assert speed_limit_no_brake_accel_target(56. * CV.KPH_TO_MS, target, gap, -0.05) == -0.05


def test_speed_limit_no_brake_releases_inside_target_gap():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  assert speed_limit_no_brake_accel_target(55. * CV.KPH_TO_MS, target, gap, -0.05) == 0.


def test_speed_limit_idle_active_above_release_gap():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  assert speed_limit_idle_active(56. * CV.KPH_TO_MS, target, gap, "idle")


def test_speed_limit_idle_inactive_inside_release_gap():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  assert not speed_limit_idle_active(55. * CV.KPH_TO_MS, target, gap, "idle")


def test_speed_limit_idle_inactive_for_other_modes():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  assert not speed_limit_idle_active(56. * CV.KPH_TO_MS, target, gap, "fixed")


def test_no_lead_normal_decel_idle_active_for_cruise_decel():
  assert no_lead_normal_decel_idle_active("idle", True, True, -0.2, -0.15, False, False)


def test_no_lead_normal_decel_idle_inactive_without_intentional_decel():
  assert not no_lead_normal_decel_idle_active("idle", False, True, -0.2, -0.15, False, False)


def test_no_lead_normal_decel_idle_inactive_with_lead():
  assert not no_lead_normal_decel_idle_active("idle", True, True, -0.2, -0.15, True, False)


def test_no_lead_normal_decel_idle_inactive_without_cruise_source():
  assert not no_lead_normal_decel_idle_active("idle", True, False, -0.2, -0.15, False, False)


def test_no_lead_normal_decel_idle_inactive_for_normal_mode():
  assert not no_lead_normal_decel_idle_active("normal", True, True, -0.2, -0.15, False, False)


def test_no_lead_normal_decel_idle_inactive_below_decel_threshold():
  assert not no_lead_normal_decel_idle_active("idle", True, True, -0.05, -0.15, False, False)


def test_no_lead_normal_decel_idle_inactive_when_stopping():
  assert not no_lead_normal_decel_idle_active("idle", True, True, -0.2, -0.15, False, True)


def test_speed_limit_current_limit_decel_needed_when_over_adjusted_limit():
  assert speed_limit_current_limit_decel_needed(True, False, 56. * CV.KPH_TO_MS, 50. * CV.KPH_TO_MS)


def test_speed_limit_current_limit_decel_not_needed_during_lower_lookahead():
  assert not speed_limit_current_limit_decel_needed(True, True, 80. * CV.KPH_TO_MS, 50. * CV.KPH_TO_MS)


def test_speed_limit_current_limit_decel_not_needed_when_at_adjusted_limit():
  assert not speed_limit_current_limit_decel_needed(True, False, 50. * CV.KPH_TO_MS, 50. * CV.KPH_TO_MS)


def test_speed_limit_current_limit_decel_respects_overspeed_margin():
  target = 50. * CV.KPH_TO_MS
  margin = 1.0 * CV.KPH_TO_MS
  assert not speed_limit_current_limit_decel_needed(True, False, 50.9 * CV.KPH_TO_MS, target, margin)
  assert speed_limit_current_limit_decel_needed(True, False, 51.1 * CV.KPH_TO_MS, target, margin)


def test_speed_limit_no_brake_fixed_mode_uses_configured_accel():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  accel = speed_limit_no_brake_accel_target(80. * CV.KPH_TO_MS, target, gap, -0.05, mode="fixed",
                                            distance=100., lookahead_speed_factor=4.)
  assert accel == -0.05


def test_speed_limit_no_brake_idle_mode_uses_zero_accel_request():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  accel = speed_limit_no_brake_accel_target(80. * CV.KPH_TO_MS, target, gap, -0.05, mode="idle")
  assert accel == 0.


def test_speed_limit_no_brake_dynamic_mode_uses_distance_based_accel():
  target = 50. * CV.KPH_TO_MS
  gap = 5. * CV.KPH_TO_MS
  accel = speed_limit_no_brake_accel_target(100. * CV.KPH_TO_MS, target, gap, -0.05, mode="dynamic",
                                            distance=300., lookahead_speed_factor=4., accel_coast=-0.3,
                                            min_accel=-1.2)
  assert accel < -0.05


def test_speed_limit_decel_target_caps_speed_limit_decel_without_lead():
  assert limit_speed_limit_decel_target(-1.0, True, False, -0.5) == -0.5


def test_speed_limit_decel_target_does_not_cap_with_lead():
  assert limit_speed_limit_decel_target(-1.0, True, True, -0.5) == -1.0


def test_speed_limit_decel_target_does_not_cap_non_speed_limit_source():
  assert limit_speed_limit_decel_target(-1.0, False, False, -0.5) == -1.0
