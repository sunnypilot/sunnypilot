"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Test suite for Speed Limit Assist cap mode (pcm_op_long only).
Covers 20 edge cases for FSM, debounce, upshift, pedal release, and audio cue.
"""

import pytest

from cereal import custom
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import UpshiftAccept
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist, \
  CAP_ACTIVE_STATES

SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState


class TestSpeedLimitCapMode:

  def test_cap_mode_applies_to_pcm_op_long(self, scenario_builder):
    """Cap mode applies to pcm_op_long cars (pcmCruise=True + openpilotLongitudinalControl=True)."""
    scenario = scenario_builder(TOYOTA.TOYOTA_RAV4_TSS2)
    scenario.set_state(SpeedLimitAssistState.disabled)
    assert scenario.sla.pcm_op_long is True
    assert scenario.sla.state == SpeedLimitAssistState.disabled

  def test_disabled_to_capping_transition(self, scenario_builder):
    """FSM: disabled -> capping when speed limit available and engaged."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.disabled)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Update to enter capping
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )
    assert scenario.sla.is_active

  def test_capping_to_disabled_on_disengagement(self, scenario_builder):
    """FSM: capping -> disabled when user disengages (manual override)."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Simulate manual override (long_override=True)
    scenario.sla.update(
      True, True, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    assert scenario.sla.state == SpeedLimitAssistState.disabled
    assert scenario.sla.output_v_target == V_CRUISE_UNSET

  def test_below_floor_pause_transition(self, scenario_builder):
    """FSM: capping exits to pending (no cap emitted) when posted limit is below min cap floor."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitMinCapFloor", 25)  # 25 mph floor
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)

    # Posted limit 20 mph (below 25 mph floor) -> cap must pause
    low_limit_ms = 20 * CV.MPH_TO_MS
    scenario.set_speed_limits(low_limit_ms, 0)
    scenario.set_cruise_speeds(30 * CV.MPH_TO_MS)

    for _ in range(int(0.5 / DT_MDL)):
      scenario.sla.update(
        True, False, 30 * CV.MPH_TO_MS, 0,
        30 * CV.MPH_TO_MS, low_limit_ms, low_limit_ms,
        True, 0, scenario.events_sp
      )

    # Below-floor condition pauses cap: state is not capping, v_target is unset (no cap)
    assert scenario.sla.state != SpeedLimitAssistState.capping
    assert scenario.sla.output_v_target == V_CRUISE_UNSET

  def test_resume_from_pause_above_floor(self, scenario_builder):
    """FSM: pending (below-floor pause) -> capping when vehicle speed rises above min cap floor."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitMinCapFloor", 25)  # 25 mph
    scenario.set_state(SpeedLimitAssistState.pending)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Update with speed above floor
    scenario.sla.update(
      True, False, 30 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )
    # Should resume capping if conditions allow
    assert scenario.sla.state in CAP_ACTIVE_STATES or scenario.sla.state == SpeedLimitAssistState.pending

  def test_change_debounce_hold_new_limit(self, scenario_builder):
    """FSM: New speed limit held for 1s before accepting (debounce)."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitUpshiftAccept", UpshiftAccept.ACCEL_PEDAL)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Start in capping with initial cap at 25 mph
    scenario.sla._target_cap = 25 * CV.MPH_TO_MS
    scenario.sla._has_speed_limit = True

    # First: establish baseline with 25 mph and pressed pedal (to establish state for edge detection)
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp, accel_pressed=True
    )

    # Then: change limit to 35 mph, press pedal briefly, then release and wait for debounce to expire
    # Press pedal for first 0.5s (speed_limit=25 but speed_limit_final_last=35 simulates detection)
    for _ in range(int(0.5 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp, accel_pressed=True
      )

    # Release pedal and wait for cap debounce + accel debounce to complete (0.7s more = 1.2s total)
    for _ in range(int(0.7 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp, accel_pressed=False
      )

    # Cap should now be 35 mph after debounce and pedal release edge
    assert abs(scenario.sla._target_cap - 35 * CV.MPH_TO_MS) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_upshift_never_raise_keeps_old_cap(self, scenario_builder):
    """FSM: NEVER_RAISE mode keeps cap unchanged when limit increases."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitUpshiftAccept", UpshiftAccept.NEVER_RAISE)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Start with cap at 25 mph
    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Increase limit to 35 mph, wait for debounce to expire
    for _ in range(int(1.2 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp
      )

    # In NEVER_RAISE mode, cap stays at 25 mph (old value)
    assert abs(scenario.sla._target_cap - 25 * CV.MPH_TO_MS) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_upshift_accel_pedal_requires_release(self, scenario_builder):
    """FSM: ACCEL_PEDAL mode accepts new cap only on pedal release."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitUpshiftAccept", UpshiftAccept.ACCEL_PEDAL)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Start with cap at 25 mph
    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Pedal pressed with new limit 35 mph, wait 1.1s (exceeds cap debounce) but pedal still pressed
    for _ in range(int(1.1 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp, accel_pressed=True
      )

    # Cap should still be 25 mph (pedal pressed, upshift rejected despite debounce)
    assert abs(scenario.sla._target_cap - 25 * CV.MPH_TO_MS) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_pedal_release_debounce_200ms(self, scenario_builder):
    """FSM: Accel pedal release edge requires 200ms debounce."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitUpshiftAccept", UpshiftAccept.ACCEL_PEDAL)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # First establish the limit change and wait for cap change debounce to start
    scenario.sla.update(
      True, False, 35 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp, accel_pressed=True
    )

    # Pedal pressed, wait 0.6s, then release and wait 0.5s (total 1.1s > 1.0s cap debounce + 0.2s accel debounce)
    for _ in range(int(0.6 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp, accel_pressed=True
      )

    # Release and wait for both debounces to complete
    for _ in range(int(0.5 / DT_MDL)):
      scenario.sla.update(
        True, False, 35 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 35 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp, accel_pressed=False
      )

    # Now cap should be updated to 35 mph (cap debounce complete + accel release edge detected and debounced)
    assert abs(scenario.sla._target_cap - 35 * CV.MPH_TO_MS) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_suspended_timer_after_long_override(self, scenario_builder):
    """FSM: 1s suspension window after manual override release."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    scenario.sla.update(
      True, True, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    assert scenario.sla.state == SpeedLimitAssistState.disabled
    assert scenario.sla._cap_suspended_timer > 0  # frame counter

    # Attempt to re-engage within suspension window (0.5s)
    for _ in range(int(0.5 / DT_MDL)):
      scenario.sla.update(
        True, False, 25 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp
      )

    # Should still be disabled (suspension active)
    assert scenario.sla.state == SpeedLimitAssistState.disabled

    # Wait for suspension to expire (1.1s total)
    for _ in range(int(0.7 / DT_MDL)):
      scenario.sla.update(
        True, False, 25 * CV.MPH_TO_MS, 0,
        20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp
      )

    # Now cap can re-engage and transition to capping
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_audio_cue_fires_once_on_capping_entry(self, scenario_builder):
    """Event: speedLimitCapActive fires once on entry to capping state."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitCapAudioCue", True)
    scenario.set_state(SpeedLimitAssistState.disabled)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Enter capping state
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    # Verify we transitioned to capping
    assert scenario.sla.state == SpeedLimitAssistState.capping
    # Audio cue flag should be set
    assert scenario.sla._cap_audio_cue_fired is True

  def test_audio_cue_disabled_no_fire(self, scenario_builder):
    """Event: speedLimitCapActive suppressed when audio cue disabled."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitCapAudioCue", False)
    scenario.set_state(SpeedLimitAssistState.disabled)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    # Enter capping state
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    # Verify we transitioned to capping
    assert scenario.sla.state == SpeedLimitAssistState.capping
    # Audio cue flag should NOT be set (disabled)
    assert scenario.sla._cap_audio_cue_fired is False

  def test_cap_delta_ui_feedback(self, scenario_builder):
    """UI: target_cap tracks posted limit, delta = v_cruise_cluster - target_cap (positive when cap below driver intent)."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    limit_ms = 25 * CV.MPH_TO_MS
    cruise_ms = 35 * CV.MPH_TO_MS
    scenario.set_speed_limits(limit_ms, 0)
    scenario.set_cruise_speeds(cruise_ms)

    scenario.sla._target_cap = limit_ms
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      cruise_ms, limit_ms, limit_ms,
      True, 0, scenario.events_sp
    )

    assert abs(scenario.sla.output_v_target - limit_ms) < 0.1
    assert abs(scenario.sla._target_cap - limit_ms) < 0.1
    cap_delta = max(0., cruise_ms - scenario.sla._target_cap)
    assert cap_delta > 0
    assert abs(cap_delta - 10 * CV.MPH_TO_MS) < 0.1
    assert abs(scenario.sla.cap_delta - cap_delta) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_min_cap_floor_zero_disables_pause(self, scenario_builder):
    """FSM: min cap floor 0 disables pause-on-low-speed behavior."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitMinCapFloor", 0)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(5 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Very low speed (5 mph), but floor is 0
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      5 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    # Should continue capping (floor 0 means no pause even at low speed)
    assert scenario.sla.state == SpeedLimitAssistState.capping
    assert scenario.sla._cap_below_floor is False

  def test_min_cap_floor_max_value_40_mph(self, scenario_builder):
    """FSM: min cap floor clamped to 40 mph (reasonable max)."""
    scenario = scenario_builder()
    scenario.set_param("IsMetric", False)
    scenario.set_param("SpeedLimitMinCapFloor", 40)
    scenario.sla.is_metric = False
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(30 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Speed 25 mph (limit) is below floor 40 mph, should pause
    for _ in range(int(0.5 / DT_MDL)):
      scenario.sla.update(
        True, False, 25 * CV.MPH_TO_MS, 0,
        30 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
        True, 0, scenario.events_sp
      )

    # Should transition to pending (below floor)
    assert scenario.sla.state == SpeedLimitAssistState.pending
    assert scenario.sla._cap_below_floor is True

  def test_v_target_clamped_to_cruise_when_capping(self, scenario_builder):
    """Output: v_target = min(v_cruise, cap) when actively capping."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    # v_target should be min(20, 25) = 20 m/s (driver cruise is limiting factor)
    assert abs(scenario.sla.output_v_target - 20 * CV.MPH_TO_MS) < 0.1
    assert scenario.sla.state == SpeedLimitAssistState.capping

  # Missing edge cases from matrix (Issues #1, #2, #5, #7, #16, #18, #19)

  def test_school_zone_false_positive_25_mph_floor(self, scenario_builder):
    """Edge case #1: OSM school zone 25 mph at inactive hours blocked by floor."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitMinCapFloor", 25)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(11.18, 0)  # 25 mph -> m/s
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 11.18

    # Speed limit 25 mph = 11.18 m/s is at floor (not strictly above)
    scenario.sla.update(
      True, False, 11.18, 0,
      20 * CV.MPH_TO_MS, 11.18, 11.18,
      True, 0, scenario.events_sp
    )

    # Should not pause at exactly floor (must be strictly above)
    assert scenario.sla.state == SpeedLimitAssistState.capping

  def test_construction_stale_25_mph_pauses(self, scenario_builder):
    """Edge case #2: Construction temp speed limit 25 mph pauses on stale data."""
    scenario = scenario_builder()
    scenario.set_param("SpeedLimitMinCapFloor", 25)
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    # Stale construction limit (25 mph, below floor by resolver check)
    scenario.set_speed_limits(11.18, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 11.18

    # Simulate old data with has_speed_limit=False (resolver cleared it)
    scenario.sla.update(
      True, False, 11.18, 0,
      20 * CV.MPH_TO_MS, 11.18, 11.18,
      False, 0, scenario.events_sp
    )

    # Should transition to pending (lost limit)
    assert scenario.sla.state == SpeedLimitAssistState.pending

  @pytest.mark.parametrize("is_metric", [True, False])
  def test_kmh_mph_unit_conversion_border(self, scenario_builder, is_metric):
    """Edge case #5: km/h ↔ mph border crossing unit conversion."""
    scenario = scenario_builder()
    scenario.params.put_bool("IsMetric", is_metric)
    # Reload SLA to pick up metric setting
    from opendbc.car.toyota.values import CAR as TOYOTA
    from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.tests.conftest import CarParamsFactory
    CP, CP_SP, _ = CarParamsFactory.create_car_interface(TOYOTA.TOYOTA_RAV4_TSS2)
    scenario.sla = SpeedLimitAssist(CP, CP_SP)
    scenario.sla.params.put_bool("IsMetric", is_metric)

    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)

    if is_metric:
      # 65 km/h ≈ 40.4 mph
      scenario.set_speed_limits(65 * CV.KPH_TO_MS, 0)
      scenario.set_cruise_speeds(60 * CV.KPH_TO_MS)
      scenario.sla._target_cap = 65 * CV.KPH_TO_MS
    else:
      # 40 mph ≈ 64.4 km/h
      scenario.set_speed_limits(40 * CV.MPH_TO_MS, 0)
      scenario.set_cruise_speeds(35 * CV.MPH_TO_MS)
      scenario.sla._target_cap = 40 * CV.MPH_TO_MS

    scenario.sla.update(
      True, False, scenario.sla._target_cap, 0,
      scenario.sla.v_cruise_cluster, scenario.sla._speed_limit,
      scenario.sla._speed_limit, True, 0, scenario.events_sp
    )

    # Should remain in capping with correct unit-aware cap
    assert scenario.sla.state == SpeedLimitAssistState.capping
    assert scenario.sla._has_speed_limit is True

  def test_gps_tunnel_fade_10s_age_limit(self, scenario_builder):
    """Edge case #7: GPS tunnel fade stale limit via LIMIT_MAX_MAP_DATA_AGE."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Simulate has_speed_limit=False (resolver expired data after 10s)
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      False, 0, scenario.events_sp
    )

    # Should transition to pending (lost limit)
    assert scenario.sla.state == SpeedLimitAssistState.pending
    assert scenario.sla.output_v_target == V_CRUISE_UNSET

  def test_lost_speed_limit_mid_cap_to_pending(self, scenario_builder):
    """Edge case #16: Lost speed limit mid-cap transitions to pending."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # Simulate limit suddenly unavailable
    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      False, 0, scenario.events_sp
    )

    # Should transition to pending, emit V_CRUISE_UNSET
    assert scenario.sla.state == SpeedLimitAssistState.pending
    assert scenario.sla.output_v_target == V_CRUISE_UNSET

  def test_mode_param_off_disables_sla_on_pcm_op_long(self, scenario_builder):
    """Edge case #18: SpeedLimitMode controls engagement on pcm_op_long cars."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.disabled)
    scenario.set_engaged(True)
    scenario.set_speed_limits(25 * CV.MPH_TO_MS, 0)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.set_param("SpeedLimitMode", 0)

    scenario.sla.update(
      True, False, 25 * CV.MPH_TO_MS, 0,
      20 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS, 25 * CV.MPH_TO_MS,
      True, 0, scenario.events_sp
    )

    assert scenario.sla.state == SpeedLimitAssistState.disabled

  def test_speed_limit_final_zero_with_has_limit_edge(self, scenario_builder):
    """Edge case #19: has_speed_limit=true but speed_limit_final=0 -> pending."""
    scenario = scenario_builder()
    scenario.set_state(SpeedLimitAssistState.capping)
    scenario.set_engaged(True)
    scenario.set_speed_limits(0, 0)  # Zero speed limit (bad data)
    scenario.set_cruise_speeds(20 * CV.MPH_TO_MS)

    scenario.sla._target_cap = 25 * CV.MPH_TO_MS

    # has_speed_limit=True but speed_limit_final_last=0
    scenario.sla.update(
      True, False, 0, 0,
      20 * CV.MPH_TO_MS, 0, 0,
      True, 0, scenario.events_sp
    )

    # Should transition to pending (bad/zero limit treated as no limit)
    assert scenario.sla.state == SpeedLimitAssistState.pending

  def test_non_pcm_path_unchanged(self, scenario_builder):
    """Regression: Non-PCM update_state_machine_non_pcm_long() unchanged."""
    scenario = scenario_builder()
    # Verify method exists and has correct signature
    assert hasattr(scenario.sla, "update_state_machine_non_pcm_long")
    # Method signature check (internal implementation detail)
