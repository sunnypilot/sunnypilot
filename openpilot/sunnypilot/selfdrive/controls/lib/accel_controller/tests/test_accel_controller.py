import math
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import log
from opendbc.car.interfaces import ACCEL_MAX, ACCEL_MIN
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import (
  STOP_DISTANCE, T_IDXS, LongitudinalMpc, LongitudinalPlanSource, get_T_FOLLOW,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelController, AccelControllerState
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  ACCEL_LIMIT_HORIZON_JERK, ACCEL_PROFILE_MAX_BP, ACCEL_PROFILE_MAX_V, ACCEL_PROFILES, CAP_FILTER_FRAMES, LAUNCH_END_SPEED,
  COMFORT_DECEL, LAUNCH_TARGET_HEADROOM, LAUNCH_TARGET_SLEW, LEAD_MATCH_ACCEL_SLEW, LEAD_SWITCH_MAX_HOLD_TIME, MATCHED_SPEED_DECEL_RATE,
  MPC_DECEL_JERK_COST_MULTIPLIER, RADAR_STALE_TIMEOUT, STOP_GAP_RESERVE, STOP_HOLD_EXIT_FRAMES, TARGET_RELEASE_SLEW,
  TARGET_SPEED_RESERVE, AccelProfile,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.helpers import build_accel_ceiling
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.lead import LeadPlan, _project_ego, calculate_lead_plan


def make_lead(*, status=False, d_rel=0.0, v_lead_k=0.0, a_lead_k=0.0, a_lead_tau=1.5, radar_track_id=-1):
  return SimpleNamespace(present=status, dRel=d_rel, vLeadK=v_lead_k, aLeadK=a_lead_k, aLeadTau=a_lead_tau,
                         radarTrackId=radar_track_id)


def make_radar(lead_one=None, lead_two=None):
  return SimpleNamespace(leadOne=lead_one or make_lead(), leadTwo=lead_two or make_lead())


def make_controller(delay=0.10):
  return AccelController(SimpleNamespace(longitudinalActuatorDelay=delay, openpilotLongitudinalControl=True))


def get_lead_plan(controller, radar_state, v_ego: float, a_ego: float, profile: int):
  return calculate_lead_plan(radar_state, v_ego, a_ego, controller.delay, profile)


def update(controller, radar_state=None, **overrides):
  args = {
    "base_speed": 25.0,
    "v_ego": 10.0,
    "a_ego": 0.0,
    "profile": AccelProfile.normal,
    "follow_personality": log.LongitudinalPersonality.standard,
    "enabled": True,
    "acc_selected": True,
    "engaged": True,
    "cruise_initialized": True,
    "stock_accel_max": ACCEL_MAX,
    "previous_should_stop": False,
  }
  args.update(overrides)
  controller.profile = args.pop("profile")
  controller.enabled = args.pop("enabled")
  controller.update(radar_state or make_radar(), **args)
  return SimpleNamespace(
    target_speed=controller.output_v_target, active=controller.is_active, launching=controller.launching,
    departure_launching=controller.departure_launching, mpc_accel_max=controller.mpc_accel_max,
    cruise_accel_max=controller.cruise_accel_max, state=controller.state,
    selected_lead=controller.selected_lead, required_decel=controller.required_decel,
  )


def effective_accel_max(result):
  return math.inf if result.mpc_accel_max is None else min(result.mpc_accel_max)


def restrictive_radar():
  return make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, a_lead_k=-0.5))


def enter_stop_hold(controller, *, base_speed=8.0, v_ego=0.1):
  stopped = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.0))
  return update(controller, stopped, base_speed=base_speed, v_ego=v_ego, previous_should_stop=True)


class TestProfiles:
  def test_lookup_table_is_explicit_and_tunable(self):
    assert ACCEL_PROFILE_MAX_BP == [0.0, 3.0, 10.0, 25.0, 40.0]
    assert ACCEL_PROFILE_MAX_V == {
      AccelProfile.eco: [1.65, 1.30, 0.72, 0.32, 0.16],
      AccelProfile.normal: [1.80, 1.50, 0.97, 0.48, 0.30],
      AccelProfile.sport: [2.00, 1.90, 1.15, 0.68, 0.42],
    }
    assert TARGET_RELEASE_SLEW == 8.75
    assert LEAD_SWITCH_MAX_HOLD_TIME == 6.0

  @pytest.mark.parametrize("profile", ACCEL_PROFILES)
  def test_lookup_interpolates_and_stays_inside_global_limit(self, profile):
    for speed, expected in zip(ACCEL_PROFILE_MAX_BP, ACCEL_PROFILE_MAX_V[profile], strict=True):
      assert AccelController.get_profile_accel_max(profile, speed) == expected

    limits = [AccelController.get_profile_accel_max(profile, speed) for speed in np.linspace(-1.0, 50.0, 201)]
    assert all(0.0 <= limit <= ACCEL_MAX for limit in limits)
    assert np.all(np.diff(limits) <= 0.0)

  @pytest.mark.parametrize("speed", ACCEL_PROFILE_MAX_BP)
  def test_profile_order_is_distinct(self, speed):
    eco, normal, sport = [AccelController.get_profile_accel_max(profile, speed) for profile in ACCEL_PROFILES]
    assert eco < normal < sport

  def test_invalid_profile_defaults_to_normal(self):
    assert AccelController._profile(999) == AccelProfile.normal

  def test_stock_limit_intersects_profile_before_mpc(self):
    controller = make_controller()
    results = [update(controller, v_ego=10.0, profile=AccelProfile.sport, stock_accel_max=0.30)
               for _ in range(controller.lead_loss_hold_frames)]
    result = results[-1]
    assert AccelController.get_profile_accel_max(AccelProfile.sport, 10.0) == pytest.approx(1.15)
    assert effective_accel_max(result) == pytest.approx(0.30)
    assert all(sample.mpc_accel_max is not None for sample in results)
    assert all(max(sample.mpc_accel_max) <= 0.30 + 1e-9 for sample in results)

  def test_runtime_profile_switch_applies_the_lookup_value_directly(self):
    controller = make_controller()
    sport = [update(controller, v_ego=10.0, profile=AccelProfile.sport, stock_accel_max=1.20)
             for _ in range(controller.lead_loss_hold_frames)][-1]
    eco = update(controller, v_ego=10.0, profile=AccelProfile.eco, stock_accel_max=1.20)

    assert effective_accel_max(sport) == pytest.approx(1.15)
    assert effective_accel_max(eco) == pytest.approx(0.72)

  def test_matched_lead_waits_until_ego_catches_the_lead(self):
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    slow_controller, caught_controller = make_controller(), make_controller()
    for controller in (slow_controller, caught_controller):
      for _ in range(CAP_FILTER_FRAMES + 10):
        update(controller, radar, v_ego=10.0, planner_accel=-0.2)

    update(slow_controller, radar, v_ego=3.0, planner_accel=-0.2)
    update(caught_controller, radar, v_ego=8.0, planner_accel=-0.2)

    assert not slow_controller.target_state.matched_lead
    assert caught_controller.target_state.matched_lead

  def test_stock_limit_reduction_applies_immediately(self):
    controller = make_controller()
    for _ in range(controller.lead_loss_hold_frames):
      update(controller, v_ego=10.0, profile=AccelProfile.sport, stock_accel_max=1.20)

    reduced = update(controller, v_ego=10.0, profile=AccelProfile.sport, stock_accel_max=0.30)
    assert effective_accel_max(reduced) == pytest.approx(0.30)
    assert reduced.mpc_accel_max is not None
    assert max(reduced.mpc_accel_max) <= 0.30 + 1e-9

  def test_one_frame_stock_zero_does_not_poison_profile_recovery(self):
    clean_controller, glitch_controller = make_controller(), make_controller()
    for _ in range(clean_controller.lead_loss_hold_frames + 10):
      clean = update(clean_controller, v_ego=10.0, stock_accel_max=1.5)
      recovered = update(glitch_controller, v_ego=10.0, stock_accel_max=1.5)

    limited = update(glitch_controller, v_ego=10.0, stock_accel_max=0.0)
    clean = update(clean_controller, v_ego=10.0, stock_accel_max=1.5)
    recovered = update(glitch_controller, v_ego=10.0, stock_accel_max=1.5)

    assert effective_accel_max(limited) == 0.0
    assert effective_accel_max(recovered) == pytest.approx(effective_accel_max(clean))

  @pytest.mark.parametrize("radar_fresh", (True, False), ids=("dropout", "stale"))
  def test_matched_lead_ceiling_obeys_current_stock_limit(self, radar_fresh):
    controller = make_controller()
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, radar, v_ego=10.0, planner_accel=-0.2)
    for _ in range(20):
      update(controller, radar, v_ego=8.0, planner_accel=-0.2)
    assert controller.target_state.matched_lead

    limited = update(controller, stock_accel_max=0.0, radar_fresh=radar_fresh)
    assert effective_accel_max(limited) == 0.0
    assert limited.mpc_accel_max is not None
    assert max(limited.mpc_accel_max) == 0.0

  def test_exact_global_max_uses_stock_ceiling(self):
    result = update(make_controller(), base_speed=8.0, v_ego=0.0, profile=AccelProfile.sport)
    assert AccelController.get_profile_accel_max(AccelProfile.sport, 0.0) == ACCEL_MAX
    assert result.mpc_accel_max is None


class TestMpcCeiling:
  @pytest.mark.parametrize("planner_accel", (-1.0, 0.0, 1.2, ACCEL_MAX))
  def test_ceiling_is_finite_feasible_and_jerk_bounded(self, planner_accel):
    limit = 0.50
    ceiling = np.asarray(build_accel_ceiling(limit, planner_accel))
    a0 = float(np.clip(planner_accel, ACCEL_MIN, ACCEL_MAX))

    assert ceiling.shape == T_IDXS.shape
    assert np.all(np.isfinite(ceiling))
    assert np.all((0.0 <= ceiling) & (ceiling <= ACCEL_MAX))
    assert ceiling[0] + 1e-9 >= a0
    assert np.all(ceiling + 1e-9 >= limit)
    assert np.all(np.diff(ceiling) <= 1e-9)
    assert np.all(-np.diff(ceiling) <= ACCEL_LIMIT_HORIZON_JERK * np.diff(T_IDXS) + 1e-9)

  def test_zero_limit_remains_feasible_for_positive_x0(self):
    ceiling = np.asarray(build_accel_ceiling(0.0, 0.8))
    assert ceiling[0] == pytest.approx(0.8)
    assert ceiling[-1] == pytest.approx(0.0)
    assert np.all(ceiling >= 0.0)

  def test_inactive_controller_has_no_custom_ceiling(self):
    controller = make_controller()
    result = update(controller, enabled=False)
    assert not result.active
    assert result.mpc_accel_max is None
    assert math.isinf(effective_accel_max(result))
    assert controller.target_state.target_speed is None

  def test_profile_ceiling_does_not_interfere_while_planner_is_braking(self):
    controller = make_controller()
    radar = restrictive_radar()
    warmup = [update(controller, radar, planner_accel=-0.2) for _ in range(controller.lead_loss_hold_frames)]

    assert all(sample.mpc_accel_max is None for sample in warmup)
    assert controller.target_state.lead_braking

    bypassed = update(controller, radar, planner_accel=-0.2, acc_selected=False)
    assert not bypassed.active and bypassed.mpc_accel_max is None
    assert not controller.target_state.lead_braking

  def test_eco_cruise_limit_remains_active_while_closing_on_a_lead(self):
    controller = make_controller()
    radar = make_radar(make_lead(status=True, d_rel=80.0, v_lead_k=19.25))
    result = update(controller, radar, base_speed=20.0, v_ego=20.0, profile=AccelProfile.eco, planner_accel=0.16,
                    previous_mpc_source=LongitudinalPlanSource.cruise)

    assert result.state == AccelControllerState.free
    assert result.mpc_accel_max is None
    assert result.cruise_accel_max == pytest.approx(AccelController.get_profile_accel_max(AccelProfile.eco, 20.0))

  def test_lead_cruise_limit_does_not_follow_mpc_source_or_accel_sign(self):
    controller = make_controller()
    expected = AccelController.get_profile_accel_max(AccelProfile.eco, 20.0)
    inputs = (
      (LongitudinalPlanSource.cruise, 0.02, 19.9, 100),
      (LongitudinalPlanSource.lead0, -0.02, 20.1, -1),
      (LongitudinalPlanSource.cruise, -0.10, 19.9, 101),
      (LongitudinalPlanSource.lead0, -0.12, 20.1, -1),
      (LongitudinalPlanSource.lead1, 0.02, 20.1, -1),
    )

    for source, planner_accel, lead_speed, track_id in inputs:
      radar = make_radar(make_lead(status=True, d_rel=150.0, v_lead_k=lead_speed, radar_track_id=track_id))
      result = update(controller, radar, base_speed=20.0, v_ego=20.0, profile=AccelProfile.eco,
                      planner_accel=planner_accel, previous_mpc_source=source)
      assert result.cruise_accel_max == pytest.approx(expected)

  def test_profile_ceiling_stays_continuous_while_a_lead_begins_pulling_away(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 5):
      update(controller, restrictive_radar(), v_ego=10.0, planner_accel=-0.2)

    pulling_away = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=12.0))
    result = update(controller, pulling_away, v_ego=10.0, planner_accel=0.2)

    assert result.state == AccelControllerState.restrict
    assert effective_accel_max(result) == pytest.approx(AccelController.get_profile_accel_max(AccelProfile.normal, 10.0))
    assert result.mpc_accel_max is not None

  def test_matched_lead_terminal_taper_changes_smoothly(self):
    controller = make_controller()
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for _ in range(CAP_FILTER_FRAMES + 5):
      update(controller, radar, v_ego=10.0, planner_accel=-0.2)

    braking = update(controller, radar, v_ego=8.0, planner_accel=-0.2)
    braking_limit = controller.target_state.matched_accel_limit
    accelerating = update(controller, radar, v_ego=8.0, planner_accel=0.2)

    assert controller.target_state.matched_lead
    assert braking.mpc_accel_max is not None and accelerating.mpc_accel_max is not None
    assert braking_limit is not None
    assert abs(controller.target_state.matched_accel_limit - braking_limit) <= LEAD_MATCH_ACCEL_SLEW * DT_MDL + 1e-9
    profile_accel_max = AccelController.get_profile_accel_max(AccelProfile.normal, 8.0)
    assert effective_accel_max(braking) <= profile_accel_max
    assert effective_accel_max(accelerating) <= profile_accel_max

  def test_matched_lead_ignores_two_frame_speed_jump(self):
    clean_controller, noisy_controller = make_controller(), make_controller()
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for controller in (clean_controller, noisy_controller):
      for _ in range(CAP_FILTER_FRAMES + 10):
        update(controller, radar, v_ego=10.0, planner_accel=-0.2)
      for _ in range(20):
        update(controller, radar, v_ego=8.0, planner_accel=-0.2)

    speed_jump = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=16.0))
    for _ in range(2):
      clean = update(clean_controller, radar, v_ego=8.0)
      noisy = update(noisy_controller, speed_jump, v_ego=8.0)
      assert effective_accel_max(noisy) == pytest.approx(effective_accel_max(clean))
      assert noisy.target_speed == pytest.approx(clean.target_speed)

  def test_matched_lead_ignores_two_frame_acceleration_jump(self):
    clean_controller, noisy_controller = make_controller(), make_controller()
    steady = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for controller in (clean_controller, noisy_controller):
      for _ in range(CAP_FILTER_FRAMES + 10):
        update(controller, steady, v_ego=10.0, planner_accel=-0.2)
      for _ in range(20):
        update(controller, steady, v_ego=8.0, planner_accel=-0.2)

    braking_jump = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, a_lead_k=-1.0))
    for _ in range(2):
      clean = update(clean_controller, steady, v_ego=8.0)
      noisy = update(noisy_controller, braking_jump, v_ego=8.0)
      assert effective_accel_max(noisy) == pytest.approx(effective_accel_max(clean))
      assert noisy.target_speed == pytest.approx(clean.target_speed)


class TestLead:
  def test_cap_matches_stopping_energy_formula(self):
    controller = make_controller()
    lead = make_lead(status=True, d_rel=50.0, v_lead_k=8.0)
    result = get_lead_plan(controller, make_radar(lead), 10.0, 0.0, AccelProfile.normal)
    delay = controller.delay
    lead_xv = LongitudinalMpc.extrapolate_lead(lead.dRel, lead.vLeadK, lead.aLeadK, lead.aLeadTau)
    x_lead = float(np.interp(delay, T_IDXS, lead_xv[:, 0]))
    v_lead = float(np.interp(delay, T_IDXS, lead_xv[:, 1]))
    x_ego, _ = _project_ego(10.0, 0.0, delay)
    safety_gap = max(x_lead - x_ego - STOP_DISTANCE - get_T_FOLLOW(log.LongitudinalPersonality.standard) * v_lead, 0.0)
    expected = v_lead + math.sqrt(2.0 * COMFORT_DECEL[AccelProfile.normal] * safety_gap)

    assert result.cap == pytest.approx(expected)
    assert result.cap != pytest.approx(math.sqrt(v_lead**2 + 2.0 * COMFORT_DECEL[AccelProfile.normal] * safety_gap))

  def test_profile_order_controls_approach_timing(self):
    radar = make_radar(make_lead(status=True, d_rel=50.0, v_lead_k=8.0))
    caps = [get_lead_plan(make_controller(), radar, 10.0, 0.0, profile).cap for profile in ACCEL_PROFILES]
    assert caps[0] < caps[1] < caps[2]

  def test_stopped_lead_reserve_only_reduces_comfort_gap(self):
    lead = get_lead_plan(make_controller(),
      make_radar(make_lead(status=True, d_rel=60.0, v_lead_k=0.0)), 5.0, 0.0, AccelProfile.normal,
    )
    comfort_decel = COMFORT_DECEL[AccelProfile.normal]
    safety_gap = (lead.departure_cap - lead.departure_lead_speed) ** 2 / (2.0 * comfort_decel)
    assert lead.required_decel < 0.30
    assert safety_gap - lead.usable_gap == pytest.approx(STOP_GAP_RESERVE)
    assert lead.departure_cap > lead.cap

  def test_more_restrictive_lead_is_selected(self):
    radar = make_radar(make_lead(status=True, d_rel=70.0, v_lead_k=12.0), make_lead(status=True, d_rel=25.0, v_lead_k=8.0))
    assert get_lead_plan(make_controller(), radar, 10.0, 0.0, AccelProfile.normal).selected_lead == 1

  @pytest.mark.parametrize("field,value", [
    ("aLeadK", math.nan), ("aLeadK", math.inf), ("aLeadTau", math.nan), ("aLeadTau", -1.0), ("radarTrackId", math.nan),
  ])
  def test_nonessential_invalid_lead_fields_are_sanitized(self, field, value):
    lead = make_lead(status=True, d_rel=30.0, v_lead_k=8.0)
    setattr(lead, field, value)
    result = get_lead_plan(make_controller(), make_radar(lead), 10.0, 0.0, AccelProfile.normal)
    assert result.selected_lead == 0
    assert math.isfinite(result.cap)

  @pytest.mark.parametrize("field,value", [("dRel", math.nan), ("dRel", -1.0), ("vLeadK", math.nan), ("vLeadK", -2.0)])
  def test_invalid_geometry_is_not_used(self, field, value):
    lead = make_lead(status=True, d_rel=30.0, v_lead_k=8.0)
    setattr(lead, field, value)
    result = get_lead_plan(make_controller(), make_radar(lead), 10.0, 0.0, AccelProfile.normal)
    assert result.selected_lead == -1
    assert result.lead_status
    assert math.isinf(result.cap)

  def test_raw_radar_is_never_mutated(self):
    lead = make_lead(status=True, d_rel=30.0, v_lead_k=8.0, a_lead_k=-15.0, a_lead_tau=math.nan)
    before = vars(lead).copy()
    get_lead_plan(make_controller(), make_radar(lead), 10.0, 0.0, AccelProfile.normal)
    assert vars(lead) == before


class TestTargetLifecycle:
  def test_five_frame_median_needs_three_restrictive_samples(self):
    controller = make_controller()
    filtered_caps = []
    for _ in range(CAP_FILTER_FRAMES):
      update(controller, restrictive_radar())
      filtered_caps.append(controller.target_state.filtered_cap)
    assert math.isinf(filtered_caps[1])
    assert math.isfinite(filtered_caps[2])

  def test_restriction_uses_comfort_rate_with_one_bounded_reserve_step(self):
    controller = make_controller()
    results = [update(controller, restrictive_radar()) for _ in range(CAP_FILTER_FRAMES + 10)]
    targets = np.asarray([result.target_speed for result in results])
    max_step = COMFORT_DECEL[AccelProfile.normal] * DT_MDL

    target_steps = -np.diff(targets)
    assert np.count_nonzero(target_steps > max_step + 1e-9) == 1
    assert np.max(target_steps) <= TARGET_SPEED_RESERVE + max_step + 1e-9
    assert results[-1].state == AccelControllerState.restrict
    assert results[-1].target_speed < results[0].target_speed

  @pytest.mark.parametrize("clear_frames", (1, 2, CAP_FILTER_FRAMES + 1))
  def test_lead_acquired_after_clear_road_cannot_step_speed_to_planner(self, clear_frames):
    controller = make_controller()
    for _ in range(clear_frames):
      update(controller, base_speed=25.0, v_ego=20.0, planner_speed=25.0)

    results = [update(controller, restrictive_radar(), base_speed=25.0, v_ego=20.0, planner_speed=20.0)
               for _ in range(CAP_FILTER_FRAMES)]
    targets = np.asarray([25.0, *(result.target_speed for result in results)])
    max_step = COMFORT_DECEL[AccelProfile.normal] * DT_MDL

    target_steps = -np.diff(targets)
    assert np.count_nonzero(target_steps > max_step + 1e-9) == 1
    assert np.max(target_steps) <= TARGET_SPEED_RESERVE + max_step + 1e-9

  def test_lead_slot_is_forgotten_before_reacquisition(self):
    controller = make_controller()
    lead_one = restrictive_radar()
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, lead_one, base_speed=25.0, v_ego=20.0, planner_speed=20.0, planner_accel=-0.2)

    for _ in range(controller.lead_loss_hold_frames):
      before = update(controller, base_speed=25.0, v_ego=20.0, planner_speed=20.0, planner_accel=-0.2)
    assert controller.target_state.selected_lead == -1

    lead_two = make_radar(lead_two=make_lead(status=True, d_rel=20.0, v_lead_k=8.0, a_lead_k=-0.5))
    results = [update(controller, lead_two, base_speed=25.0, v_ego=20.0, planner_speed=5.0, planner_accel=-0.2)
               for _ in range(CAP_FILTER_FRAMES)]
    targets = np.asarray([before.target_speed, *(result.target_speed for result in results)])
    max_step = COMFORT_DECEL[AccelProfile.normal] * DT_MDL

    target_steps = -np.diff(targets)
    assert np.count_nonzero(target_steps > max_step + 1e-9) == 1
    assert np.max(target_steps) <= TARGET_SPEED_RESERVE + max_step + 1e-9

  @pytest.mark.parametrize("replacement_track_id", (200, -1), ids=("radar-track", "vision-track"))
  def test_false_relief_track_replacement_freezes_bounded_speed_release(self, replacement_track_id):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, radar_track_id=100))
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, original, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=-0.2)
    for _ in range(20):
      before = update(controller, original, base_speed=25.0, v_ego=8.0, planner_speed=8.0, planner_accel=-0.2)
    assert controller.target_state.matched_lead

    replacement = make_radar(make_lead(status=True, d_rel=40.0, v_lead_k=12.0, radar_track_id=replacement_track_id))
    switched = update(controller, replacement, base_speed=25.0, v_ego=8.0, planner_speed=5.0, planner_accel=-0.2)

    target_drop = before.target_speed - switched.target_speed
    assert -TARGET_SPEED_RESERVE - 1e-9 <= target_drop <= MATCHED_SPEED_DECEL_RATE * DT_MDL + 1e-9
    assert effective_accel_max(switched) <= AccelController.get_profile_accel_max(AccelProfile.normal, 8.0) + 1e-9
    assert switched.target_speed < 25.0
    assert controller.target_state.lead_switch_guard_frames == controller.lead_loss_hold_frames

  def test_false_relief_track_replacement_requires_stable_relief(self):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, radar_track_id=100))
    for _ in range(CAP_FILTER_FRAMES + 10):
      before = update(controller, original, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=0.2)
    assert before.state in (AccelControllerState.restrict, AccelControllerState.hold)
    assert controller.target_state.speed_reserve_armed

    replacement = make_radar(make_lead(status=True, d_rel=90.0, v_lead_k=12.0, radar_track_id=-1))
    switched = update(controller, replacement, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=0.2)

    assert switched.target_speed <= before.target_speed + 1e-9
    assert controller.target_state.lead_switch_guard_frames == controller.lead_loss_hold_frames

    for frame in range(controller.lead_loss_hold_frames * 2):
      radar = original if frame % 2 == 0 else replacement
      churn = update(controller, radar, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=0.2)
      assert churn.target_speed <= before.target_speed + 1e-9

    released = [update(controller, replacement, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=0.2)
                for _ in range(controller.lead_loss_hold_frames + 1)]
    assert controller.target_state.lead_switch_guard_frames == 0
    assert released[-1].target_speed > before.target_speed
    assert np.max(np.diff([before.target_speed, *(result.target_speed for result in released)])) <= TARGET_RELEASE_SLEW * DT_MDL + 1e-9

  def test_initial_lead_target_release_is_slewed(self):
    controller = make_controller()
    closing = make_radar(make_lead(status=True, d_rel=90.0, v_lead_k=8.0, radar_track_id=100))
    relief = make_radar(make_lead(status=True, d_rel=90.0, v_lead_k=12.0, radar_track_id=100))
    first = update(controller, closing)
    results = [update(controller, relief) for _ in range(CAP_FILTER_FRAMES)]
    targets = [first.target_speed, *(result.target_speed for result in results)]

    assert np.max(np.diff(targets)) > 0.0
    assert np.max(np.diff(targets)) <= TARGET_RELEASE_SLEW * DT_MDL + 1e-9
    assert controller.target_state.target_speed < controller.target_state.filtered_cap
    assert controller.target_state.release_slew_armed

  def test_direct_relief_slews_to_a_moving_ceiling(self):
    controller = make_controller()
    state = controller.target_state
    state.target_speed, state.state, state.release_slew_armed = 18.0, AccelControllerState.hold, True
    state.active_frames, state.selected_lead, state.selected_lead_track_id = 20, 0, 100
    state.cap_samples = [20.0] * CAP_FILTER_FRAMES
    targets = []

    for frame in range(70):
      cap = min(23.0, 20.0 + 0.1 * frame)
      lead_plan = LeadPlan(cap=cap, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=20.0, lead_status=True)
      targets.append(controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                               LongitudinalPlanSource.cruise, 20.0, 0.0))

    steps = np.diff(targets)
    assert np.all(steps >= -1e-9)
    assert np.max(steps) <= TARGET_RELEASE_SLEW * DT_MDL + 1e-9
    assert targets[-1] == 23.0
    assert state.state == AccelControllerState.hold and not state.release_slew_armed

    for cap in (23.1, 23.2) * CAP_FILTER_FRAMES:
      lead_plan = LeadPlan(cap=cap, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=20.0, lead_status=True)
      controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                LongitudinalPlanSource.cruise, 20.0, 0.0)
    assert state.target_speed == 23.0

  def test_settled_release_does_not_follow_subdeadband_cap_churn(self):
    controller = make_controller()
    state = controller.target_state
    state.target_speed, state.state = 20.0, AccelControllerState.hold
    state.active_frames, state.selected_lead, state.selected_lead_track_id = 20, 0, 100
    state.arm_release_slew()
    targets = [state.target_speed]

    for cap in (19.8, 20.2) * (2 * CAP_FILTER_FRAMES):
      state.cap_samples = [cap] * CAP_FILTER_FRAMES
      lead_plan = LeadPlan(cap=cap, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=25.0, lead_status=True)
      targets.append(controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                               LongitudinalPlanSource.cruise, 20.0, 0.0))

    assert np.max(np.diff(targets)) <= TARGET_RELEASE_SLEW * DT_MDL + 1e-9
    assert state.release_slew_armed and state.release_settle_frames == 1

    settle_updates = math.ceil((state.target_speed - 19.8) / (COMFORT_DECEL[AccelProfile.normal] * DT_MDL)) + CAP_FILTER_FRAMES
    for _ in range(settle_updates):
      state.cap_samples = [19.8] * CAP_FILTER_FRAMES
      lead_plan = LeadPlan(cap=19.8, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=25.0, lead_status=True)
      controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                LongitudinalPlanSource.cruise, 20.0, 0.0)
    assert not state.release_slew_armed

  def test_guard_timeout_uses_wall_clock_and_does_not_rearm_during_churn(self):
    controller = make_controller()
    state = controller.target_state
    state.target_speed, state.state, state.release_slew_armed = 18.0, AccelControllerState.hold, True
    state.active_frames, state.selected_lead, state.selected_lead_track_id = 20, 0, 100
    guard_history = []

    for frame in range(2 * controller.lead_switch_max_hold_frames):
      state.cap_samples = [20.0] * CAP_FILTER_FRAMES
      track_id = 200 if frame % 2 == 0 else 100
      lead_plan = LeadPlan(cap=25.0, selected_lead=0, selected_lead_track_id=track_id, selected_lead_speed=15.0,
                           closing_speed=1.0, lead_status=True)
      controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                LongitudinalPlanSource.cruise, 18.0, -0.2)
      guard_history.append(state.lead_switch_guard_frames)

    first_zero = next(index for index, guard in enumerate(guard_history[1:], 1) if guard == 0)
    assert first_zero <= controller.lead_switch_max_hold_frames
    assert all(guard == 0 for guard in guard_history[first_zero:])
    assert state.lead_switch_elapsed_frames == controller.lead_switch_max_hold_frames

    stable = LeadPlan(cap=25.0, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=25.0, lead_status=True)
    for _ in range(controller.lead_loss_hold_frames + 20):
      controller._update_target(stable, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                LongitudinalPlanSource.cruise, 20.0, 0.0)
    assert state.target_speed == 25.0 and state.state == AccelControllerState.free
    assert state.lead_switch_elapsed_frames == 0

    state.cap_samples = [15.0] * CAP_FILTER_FRAMES
    restrictive = LeadPlan(cap=15.0, selected_lead=0, selected_lead_track_id=100, selected_lead_speed=15.0,
                           closing_speed=5.0, lead_status=True)
    controller._update_target(restrictive, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                              LongitudinalPlanSource.cruise, 20.0, -0.2)
    replacement = restrictive._replace(cap=25.0, selected_lead_track_id=200, closing_speed=0.0)
    controller._update_target(replacement, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                              LongitudinalPlanSource.cruise, 20.0, -0.2)
    assert state.lead_switch_guard_frames == controller.lead_loss_hold_frames

  def test_guard_timeout_does_not_release_while_planner_is_braking(self):
    controller = make_controller()
    state = controller.target_state
    state.target_speed, state.state, state.release_slew_armed = 18.0, AccelControllerState.hold, True
    state.active_frames, state.selected_lead, state.selected_lead_track_id = 20, 0, 100
    targets = []

    for frame in range(controller.lead_switch_max_hold_frames + controller.lead_loss_hold_frames):
      state.cap_samples = [20.0] * CAP_FILTER_FRAMES
      lead_plan = LeadPlan(cap=25.0, selected_lead=0, selected_lead_track_id=200 if frame % 2 == 0 else 100,
                           selected_lead_speed=20.0, closing_speed=0.0, lead_status=True)
      targets.append(controller._update_target(lead_plan, 25.0, 20.0, AccelProfile.normal, 0.48, False,
                                               LongitudinalPlanSource.cruise, 18.0, -0.2))

    assert state.lead_switch_guard_frames == 0
    assert max(targets) == 18.0

  def test_track_id_churn_without_false_relief_does_not_arm_guard(self):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, radar_track_id=100))
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, original, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=-0.2)

    replacement = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0, radar_track_id=200))
    update(controller, replacement, base_speed=25.0, v_ego=10.0, planner_speed=10.0, planner_accel=-0.2)

    assert controller.target_state.lead_switch_guard_frames == 0

  def test_short_dropout_holds_then_releases_at_a_bounded_target_rate(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 20):
      restricted = update(controller, restrictive_radar())

    held = [update(controller) for _ in range(controller.lead_loss_hold_frames - 1)]
    assert all(result.target_speed <= restricted.target_speed + 1e-9 for result in held)

    released = [update(controller) for _ in range(40)]
    targets = np.asarray([restricted.target_speed, *(result.target_speed for result in released)])
    assert np.max(np.diff(targets)) <= TARGET_RELEASE_SLEW * DT_MDL + TARGET_SPEED_RESERVE + 1e-9
    assert released[-1].target_speed == 25.0
    assert released[-1].state == AccelControllerState.free

  def test_reacquired_lead_restarts_dropout_coast_hold(self):
    controller = make_controller()
    radar = restrictive_radar()
    for _ in range(CAP_FILTER_FRAMES + 20):
      update(controller, radar, planner_speed=9.0, planner_accel=-0.5)

    update(controller, previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=9.0, planner_accel=-0.5)
    for _ in range(controller.lead_dropout_coast_frames // 2):
      update(controller, planner_speed=9.0, planner_accel=-0.2)
    update(controller, radar, planner_speed=9.0, planner_accel=-0.2)
    synchronized = update(controller, previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=8.8, planner_accel=-0.2)
    held = [update(controller, planner_speed=8.8, planner_accel=-0.2) for _ in range(controller.lead_dropout_coast_frames - 2)]

    assert controller.target_state.target_speed == 8.8
    assert all(result.target_speed <= synchronized.target_speed + TARGET_SPEED_RESERVE + 1e-9 for result in held)

  def test_previous_lead_source_synchronizes_down_to_planner(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 10):
      restricted = update(controller, restrictive_radar())
    planner_speed = restricted.target_speed - 2.0
    synchronized = update(controller, previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=planner_speed)
    assert controller.target_state.target_speed == planner_speed
    assert synchronized.target_speed <= planner_speed
    assert synchronized.state == AccelControllerState.hold

  def test_matched_lead_dropout_synchronizes_down_to_planner(self):
    controller = make_controller()
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, radar, v_ego=10.0, planner_accel=-0.2)
    for _ in range(20):
      matched = update(controller, radar, v_ego=8.0, planner_accel=-0.2)
    assert controller.target_state.matched_lead

    planner_speed = matched.target_speed - 2.0
    synchronized = update(controller, previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=planner_speed)
    assert controller.target_state.target_speed == planner_speed
    assert synchronized.target_speed <= planner_speed
    assert synchronized.state == AccelControllerState.hold

  def test_reused_radar_holds_matched_lead_until_a_fresh_dropout(self):
    controller = make_controller()
    radar = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=8.0))
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, radar, v_ego=10.0, planner_accel=-0.2)
    for _ in range(20):
      matched = update(controller, radar, v_ego=8.0, planner_accel=-0.2)
    assert controller.target_state.matched_lead

    planner_speed = matched.target_speed - 2.0
    held = update(controller, radar, previous_mpc_source=LongitudinalPlanSource.lead0,
                  planner_speed=planner_speed, radar_fresh=False)
    synchronized = update(controller, previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=planner_speed)

    assert held.target_speed == pytest.approx(matched.target_speed)
    assert held.state == matched.state
    assert controller.target_state.target_speed == planner_speed
    assert synchronized.target_speed <= planner_speed
    assert synchronized.state == AccelControllerState.hold

  def test_clear_road_launch_has_immediate_headroom_and_bounded_target_slew(self):
    controller = make_controller()
    initial = update(controller, base_speed=12.0, v_ego=0.0, profile=AccelProfile.normal)
    rolling = update(controller, base_speed=12.0, v_ego=0.31, profile=AccelProfile.normal)

    assert initial.active and initial.launching
    assert LAUNCH_TARGET_HEADROOM <= initial.target_speed <= LAUNCH_TARGET_HEADROOM + LAUNCH_TARGET_SLEW * DT_MDL
    assert rolling.launching
    assert rolling.target_speed >= 0.31 + LAUNCH_TARGET_HEADROOM
    assert rolling.target_speed - max(initial.target_speed, 0.31 + LAUNCH_TARGET_HEADROOM) <= LAUNCH_TARGET_SLEW * DT_MDL + 1e-9

    finished = update(controller, base_speed=12.0, v_ego=LAUNCH_END_SPEED, profile=AccelProfile.normal)
    assert not finished.launching

  def test_far_stopped_lead_does_not_create_stop_hold(self):
    controller = make_controller()
    far_stopped = make_radar(make_lead(status=True, d_rel=60.0, v_lead_k=0.0))
    results = [update(controller, far_stopped, base_speed=12.0, v_ego=0.0) for _ in range(4)]
    assert all(result.state != AccelControllerState.stopHold for result in results)

  def test_renewed_stop_above_stop_hold_speed_does_not_apply_extra_launch_ramp_step(self):
    controller = make_controller()
    ramp = [update(controller, base_speed=12.0, v_ego=v_ego, profile=AccelProfile.normal) for v_ego in (0.0, 0.5)]
    assert all(result.launching for result in ramp)

    stopped_lead = make_radar(make_lead(status=True, d_rel=3.0, v_lead_k=0.0))
    renewed = update(controller, stopped_lead, base_speed=12.0, v_ego=0.5, profile=AccelProfile.normal)
    assert not renewed.launching
    assert renewed.target_speed <= ramp[-1].target_speed + 1e-9

  def test_far_stopped_lead_does_not_use_sticky_braking_history_as_stop_evidence(self):
    controller = make_controller()
    far_stopped = make_radar(make_lead(status=True, d_rel=60.0, v_lead_k=0.0))
    for _ in range(controller.lead_loss_hold_frames):
      update(controller, far_stopped, base_speed=12.0, v_ego=10.0, planner_accel=-0.2)
    assert controller.target_state.lead_braking

    result = update(controller, far_stopped, base_speed=12.0, v_ego=0.2, planner_accel=-0.2)
    assert result.state != AccelControllerState.stopHold
    assert result.target_speed > 0.0

  def test_near_stopped_lead_uses_braking_history_to_hold_completed_stop(self):
    controller = make_controller()
    stopped = make_radar(make_lead(status=True, d_rel=20.0, v_lead_k=0.0))
    for _ in range(controller.lead_loss_hold_frames):
      update(controller, stopped, base_speed=12.0, v_ego=10.0, planner_accel=-0.2)
    assert controller.target_state.lead_braking

    result = update(controller, stopped, base_speed=12.0, v_ego=0.2, planner_accel=-0.2)
    assert result.state == AccelControllerState.stopHold
    assert controller.target_state.target_speed == 0.0
    assert result.target_speed == 0.0
    assert math.isinf(effective_accel_max(result))
    assert result.mpc_accel_max is None

    stock_limited = update(controller, stopped, base_speed=12.0, v_ego=0.2, stock_accel_max=0.0)
    assert math.isinf(effective_accel_max(stock_limited))
    assert stock_limited.mpc_accel_max is None

  def test_stop_hold_needs_four_confirmed_departure_frames(self):
    controller = make_controller()
    held = enter_stop_hold(controller)
    assert controller.target_state.target_speed == 0.0
    results = [update(controller, make_radar(make_lead(status=True, d_rel=6.0 + (frame + 1) * 0.1, v_lead_k=2.0)),
                      base_speed=8.0, v_ego=0.1) for frame in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES)]
    launch_index = next(index for index, result in enumerate(results) if result.launching)

    assert held.state == AccelControllerState.stopHold
    assert held.target_speed == 0.0 and math.isinf(effective_accel_max(held))
    assert held.mpc_accel_max is None
    assert all(result.state == AccelControllerState.stopHold and not result.launching for result in results[:launch_index])
    assert launch_index == STOP_HOLD_EXIT_FRAMES - 1
    assert results[launch_index].target_speed >= 0.1 + LAUNCH_TARGET_HEADROOM
    assert results[launch_index].departure_launching
    assert effective_accel_max(results[launch_index]) == pytest.approx(
      AccelController.get_profile_accel_max(AccelProfile.normal, 0.1),
    )

  def test_stopped_governing_lead_rejects_route_51d_radar_speed_pulse_without_delaying_departure(self):
    controller = make_controller()
    enter_stop_hold(controller, v_ego=0.0)
    speed_pulse = (0.1361, 0.1731, 0.2146, 0.2253, 0.2137, 0.1877)
    distances = (6.0, 6.0, 6.0, 5.96, 6.04, 6.04)

    for distance, speed in zip(distances, speed_pulse, strict=True):
      radar = make_radar(make_lead(status=True, d_rel=distance, v_lead_k=speed, radar_track_id=4887),
                         make_lead(status=True, d_rel=6.08, v_lead_k=0.0, radar_track_id=4905))
      held = update(controller, radar, base_speed=8.0, v_ego=0.0)
      assert held.state == AccelControllerState.stopHold
      assert held.target_speed == 0.0 and not held.launching

    results = [
      update(controller, make_radar(make_lead(status=True, d_rel=6.04 + (frame + 1) * 0.1, v_lead_k=2.0, radar_track_id=4887),
                                    make_lead(status=True, d_rel=6.12 + (frame + 1) * 0.1, v_lead_k=2.0, radar_track_id=4905)),
             base_speed=8.0, v_ego=0.0)
      for frame in range(STOP_HOLD_EXIT_FRAMES)
    ]

    assert all(result.state == AccelControllerState.stopHold for result in results[:-1])
    assert results[-1].launching and results[-1].departure_launching

  def test_route_520_slow_lead_pulse_cannot_release_stop_hold_but_real_departure_can(self):
    controller = make_controller()
    enter_stop_hold(controller, v_ego=0.0)
    speeds = (0.01, 0.03, 0.07, 0.10, 0.14, 0.20, 0.26, 0.32, 0.34, 0.33, 0.31, 0.28, 0.24, 0.20, 0.15, 0.09, 0.05, 0.01)
    offsets = (0.00, 0.00, 0.00, 0.01, 0.01, 0.02, 0.03, 0.04, 0.06, 0.07, 0.09, 0.11, 0.12, 0.13, 0.14, 0.15, 0.15, 0.16)

    for offset, speed in zip(offsets, speeds, strict=True):
      pulse = make_radar(make_lead(status=True, d_rel=6.0 + offset, v_lead_k=speed, radar_track_id=2133))
      held = update(controller, pulse, base_speed=8.0, v_ego=0.0)
      assert held.state == AccelControllerState.stopHold
      assert held.target_speed == 0.0 and not held.launching

    stopped = make_radar(make_lead(status=True, d_rel=6.2, v_lead_k=0.0, radar_track_id=2133))
    assert update(controller, stopped, base_speed=8.0, v_ego=0.0).state == AccelControllerState.stopHold
    results = [update(controller, make_radar(make_lead(status=True, d_rel=6.2 + (frame + 1) * 0.1, v_lead_k=2.0, radar_track_id=2133)),
                      base_speed=8.0, v_ego=0.0) for frame in range(STOP_HOLD_EXIT_FRAMES)]

    assert all(result.state == AccelControllerState.stopHold for result in results[:-1])
    assert results[-1].launching and results[-1].departure_launching

  def test_fast_speed_signal_that_slows_without_separating_never_releases_stop_hold(self):
    controller = make_controller()
    enter_stop_hold(controller, v_ego=0.0)
    departing = make_radar(make_lead(status=True, d_rel=5.9, v_lead_k=2.0))
    results = [update(controller, departing, base_speed=8.0, v_ego=0.0) for _ in range(STOP_HOLD_EXIT_FRAMES)]
    slowed = update(controller, make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.2)), base_speed=8.0, v_ego=0.0)

    assert all(result.state == AccelControllerState.stopHold and not result.launching for result in results)
    assert slowed.state == AccelControllerState.stopHold
    assert slowed.target_speed == 0.0 and not slowed.launching

  def test_stop_hold_reseeds_departure_distance_when_radar_track_is_replaced(self):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.0, radar_track_id=100))
    update(controller, original, base_speed=8.0, v_ego=0.0, previous_should_stop=True)
    replacement = make_radar(make_lead(status=True, d_rel=6.4, v_lead_k=0.2, radar_track_id=200))
    results = [update(controller, replacement, base_speed=8.0, v_ego=0.0) for _ in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES)]

    assert all(result.state == AccelControllerState.stopHold for result in results)
    assert all(result.target_speed == 0.0 and not result.launching for result in results)

  def test_stop_hold_rejects_persistent_same_track_distance_step(self):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.0, radar_track_id=100))
    update(controller, original, base_speed=8.0, v_ego=0.0, previous_should_stop=True)
    stepped = make_radar(make_lead(status=True, d_rel=6.4, v_lead_k=0.2, radar_track_id=100))
    results = [update(controller, stepped, base_speed=8.0, v_ego=0.0) for _ in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES)]

    assert all(result.state == AccelControllerState.stopHold for result in results)
    assert all(result.target_speed == 0.0 and not result.launching for result in results)

  def test_stop_hold_reseeds_non_selected_departure_lead_when_its_track_is_replaced(self):
    controller = make_controller()
    original = make_radar(make_lead(status=True, d_rel=3.0, v_lead_k=0.2, radar_track_id=100),
                          make_lead(status=True, d_rel=6.0, v_lead_k=0.1, radar_track_id=200))
    update(controller, original, base_speed=8.0, v_ego=0.0, previous_should_stop=True)
    replacement = make_radar(make_lead(status=True, d_rel=3.4, v_lead_k=0.2, radar_track_id=101),
                             make_lead(status=True, d_rel=6.0, v_lead_k=0.1, radar_track_id=200))
    lead = get_lead_plan(controller, replacement, 0.0, 0.0, AccelProfile.normal)
    results = [update(controller, replacement, base_speed=8.0, v_ego=0.0) for _ in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES)]

    assert lead.selected_lead == 1 and lead.departure_lead_index == 0
    assert all(result.state == AccelControllerState.stopHold for result in results)
    assert all(result.target_speed == 0.0 and not result.launching for result in results)

  def test_genuine_departure_survives_lead_slot_and_track_flicker(self):
    controller = make_controller()
    enter_stop_hold(controller, v_ego=0.0)
    results = []
    for frame in range(STOP_HOLD_EXIT_FRAMES):
      moving = make_lead(status=True, d_rel=6.0 + (frame + 1) * 0.1, v_lead_k=2.0, radar_track_id=100)
      secondary = make_lead(status=True, d_rel=7.0, v_lead_k=2.0, radar_track_id=200)
      results.append(update(controller, make_radar(moving, secondary) if frame % 2 == 0 else make_radar(secondary, moving),
                            base_speed=8.0, v_ego=0.0))

    assert all(result.state == AccelControllerState.stopHold for result in results[:-1])
    assert results[-1].launching and results[-1].departure_launching

  def test_fast_speed_glitch_without_distance_progress_stays_in_stop_hold(self):
    controller = make_controller()
    stopped = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.0, radar_track_id=100))
    update(controller, stopped, base_speed=8.0, v_ego=0.0, previous_should_stop=True)
    glitch = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.9, radar_track_id=100))
    results = [update(controller, glitch, base_speed=8.0, v_ego=0.0) for _ in range(STOP_HOLD_EXIT_FRAMES)]
    results.append(update(controller, stopped, base_speed=8.0, v_ego=0.0))

    assert all(result.state == AccelControllerState.stopHold for result in results)
    assert all(result.target_speed == 0.0 and not result.launching for result in results)

  def test_moving_departure_does_not_reenter_stop_hold_when_speed_crosses_exit_threshold(self):
    controller = make_controller()
    stopped = make_radar(make_lead(status=True, d_rel=6.0, v_lead_k=0.0, radar_track_id=100))
    update(controller, stopped, base_speed=8.0, v_ego=0.0, previous_should_stop=True)
    distance = 6.0
    results = []
    for speed in (0.81, 0.82, 0.83, 0.84, 0.79, 0.76, 0.74, 0.72):
      distance += speed * DT_MDL
      radar = make_radar(make_lead(status=True, d_rel=distance, v_lead_k=speed, radar_track_id=100))
      results.append(update(controller, radar, base_speed=8.0, v_ego=0.0))

    launch_index = next(index for index, result in enumerate(results) if result.launching)
    assert all(result.state != AccelControllerState.stopHold for result in results[launch_index:])
    assert all(result.target_speed > 0.0 and result.departure_launching for result in results[launch_index:])

  def test_reused_radar_does_not_pulse_stop_hold_or_departure_target(self):
    controller = make_controller()
    enter_stop_hold(controller)

    for frame in range(STOP_HOLD_EXIT_FRAMES):
      departing = make_radar(make_lead(status=True, d_rel=6.0 + (frame + 1) * 0.1, v_lead_k=2.0))
      fresh = update(controller, departing, base_speed=8.0, v_ego=0.1)
      held = update(controller, departing, base_speed=8.0, v_ego=0.1, radar_fresh=False,
                    previous_mpc_source=LongitudinalPlanSource.lead0, planner_speed=0.01)
      assert held.target_speed == pytest.approx(fresh.target_speed)
      assert held.state == fresh.state
      assert held.selected_lead == fresh.selected_lead == 0
      assert effective_accel_max(held) == pytest.approx(effective_accel_max(fresh))
      if frame < STOP_HOLD_EXIT_FRAMES - 1:
        assert fresh.state == AccelControllerState.stopHold
        assert math.isinf(effective_accel_max(fresh))
        assert fresh.mpc_accel_max is None

    assert fresh.launching and held.launching
    assert fresh.departure_launching and held.departure_launching
    assert fresh.target_speed == held.target_speed == 8.0
    assert effective_accel_max(fresh) == pytest.approx(AccelController.get_profile_accel_max(AccelProfile.normal, 0.1))

  def test_single_frame_departure_stays_at_zero_target_without_an_accel_ceiling(self):
    controller = make_controller()
    enter_stop_hold(controller)
    departing = make_radar(make_lead(status=True, d_rel=8.0, v_lead_k=2.0))
    stopped = make_radar(make_lead(status=True, d_rel=8.0, v_lead_k=0.0))

    warm = update(controller, departing, base_speed=8.0, v_ego=0.0)
    held = update(controller, stopped, base_speed=8.0, v_ego=0.0)

    assert warm.state == held.state == AccelControllerState.stopHold
    assert not warm.launching and not held.launching
    assert math.isinf(effective_accel_max(warm)) and warm.mpc_accel_max is None
    assert math.isinf(effective_accel_max(held)) and held.mpc_accel_max is None
    assert held.target_speed == 0.0

  def test_previous_stop_without_a_lead_does_not_latch_stop_hold(self):
    result = update(
      make_controller(), base_speed=8.0, v_ego=0.0, previous_should_stop=True,
      previous_mpc_source=LongitudinalPlanSource.cruise,
    )

    assert result.state != AccelControllerState.stopHold
    assert result.target_speed >= LAUNCH_TARGET_HEADROOM

  def test_previous_lead_stop_survives_a_fresh_full_field_dropout(self):
    result = update(
      make_controller(), base_speed=8.0, v_ego=0.0, previous_should_stop=True,
      previous_mpc_source=LongitudinalPlanSource.lead0,
    )

    assert result.state == AccelControllerState.stopHold
    assert result.target_speed == 0.0
    assert math.isinf(effective_accel_max(result))
    assert result.mpc_accel_max is None

  def test_stop_hold_without_usable_lead_stays_pinned_to_zero(self):
    controller = make_controller()
    enter_stop_hold(controller)
    missing = update(controller, base_speed=8.0, v_ego=0.1)

    assert missing.state == AccelControllerState.stopHold
    assert missing.target_speed == 0.0
    assert math.isinf(effective_accel_max(missing))
    assert missing.mpc_accel_max is None

  def test_confirmed_creep_departure_does_not_reenter_stop_hold(self):
    controller = make_controller()
    enter_stop_hold(controller, v_ego=0.0)
    results = []
    for frame in range(60):
      creeping = make_radar(make_lead(status=True, d_rel=6.0 + frame * 0.01, v_lead_k=0.2))
      results.append(update(controller, creeping, base_speed=8.0, v_ego=0.0))

    launch_index = next(index for index, result in enumerate(results) if result.launching)
    assert launch_index * DT_MDL <= 2.0
    assert all(result.state != AccelControllerState.stopHold for result in results[launch_index:])
    assert all(result.target_speed > 0.0 for result in results[launch_index:])

  def test_departure_dropout_holds_without_resurrecting_stop_hold(self):
    controller = make_controller()
    enter_stop_hold(controller)
    results = [update(controller, make_radar(make_lead(status=True, d_rel=6.0 + (frame + 1) * 0.1, v_lead_k=2.0)),
                      base_speed=8.0, v_ego=0.1) for frame in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES)]
    launched = next(result for result in results if result.launching)
    before_dropout = results[-1]
    dropout = [update(controller, base_speed=8.0, v_ego=0.1) for _ in range(controller.lead_loss_hold_frames + 1)]

    assert launched.launching
    assert all(result.state != AccelControllerState.stopHold for result in dropout)
    assert all(result.target_speed <= before_dropout.target_speed + 1e-9 for result in dropout[:controller.lead_loss_hold_frames - 1])
    assert dropout[controller.lead_loss_hold_frames - 1].target_speed > before_dropout.target_speed
    assert dropout[-1].launching

  def test_invalid_departure_geometry_returns_to_stop_hold(self):
    controller = make_controller()
    enter_stop_hold(controller)
    for frame in range(CAP_FILTER_FRAMES + STOP_HOLD_EXIT_FRAMES):
      departing = make_radar(make_lead(status=True, d_rel=6.0 + (frame + 1) * 0.1, v_lead_k=2.0))
      launched = update(controller, departing, base_speed=8.0, v_ego=0.1)
    invalid = make_radar(make_lead(status=True, d_rel=math.nan, v_lead_k=2.0))
    guarded = update(controller, invalid, base_speed=8.0, v_ego=0.1)
    assert launched.launching
    assert guarded.state == AccelControllerState.stopHold
    assert guarded.target_speed == 0.0

  def test_stale_timeout_fully_resets_live_state(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 10):
      restricted = update(controller, restrictive_radar())
    stale_frames = math.ceil(RADAR_STALE_TIMEOUT / DT_MDL)
    held = [update(controller, radar_fresh=False) for _ in range(stale_frames - 1)]
    timed_out = update(controller, radar_fresh=False)

    assert all(result.active and result.target_speed == pytest.approx(restricted.target_speed) for result in held)
    assert not timed_out.active
    assert timed_out.target_speed == 25.0
    assert timed_out.mpc_accel_max is None
    assert timed_out.selected_lead == -1 and controller._held_lead_plan is None
    assert controller.target_state.target_speed is None

  @pytest.mark.parametrize("override", [{"enabled": False}, {"acc_selected": False}, {"engaged": False}, {"cruise_initialized": False}, {"a_ego": math.inf}])
  def test_bypass_or_invalid_context_resets_live_state(self, override):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, restrictive_radar())
    result = update(controller, restrictive_radar(), **override)

    assert not result.active
    assert result.target_speed == 25.0
    assert result.mpc_accel_max is None
    assert controller.target_state.target_speed is None

  def test_acc_bypass_does_not_retain_state_for_live_actuation(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 20):
      bypassed = update(controller, restrictive_radar(), acc_selected=False)
      assert not bypassed.active
      assert controller.target_state.target_speed is None
      assert controller._held_lead_plan is None
    live = update(controller)

    assert live.active and live.target_speed == 25.0
    assert math.isinf(controller.target_state.filtered_cap)

  def test_explicit_reset_clears_target_state(self):
    controller = make_controller()
    for _ in range(CAP_FILTER_FRAMES + 10):
      update(controller, restrictive_radar())
    controller._jerk_smoothing_blocked = True
    controller._required_decel_samples = [0.2]
    controller._required_decel_lead = controller._required_decel_lead_track_id = 1
    controller._lead_trend_warmup = True
    controller.target_state.lead_dropout = True
    controller.reset()

    assert controller._held_lead_plan is None
    assert not controller._jerk_smoothing_blocked
    assert controller._required_decel_samples == []
    assert controller._required_decel_lead == controller._required_decel_lead_track_id == -1
    assert not controller._lead_trend_warmup
    assert not controller.target_state.lead_dropout
    target_state = controller.target_state
    assert target_state.target_speed is None and target_state.matched_accel_limit is None
    assert target_state.state == AccelControllerState.inactive
    assert target_state.departure_frames == target_state.active_frames == target_state.lead_loss_frames == target_state.stale_frames == 0
    assert target_state.lead_switch_guard_frames == target_state.lead_switch_elapsed_frames == target_state.lead_switch_stable_frames == 0
    assert target_state.release_settle_frames == 0 and target_state.release_settle_speed is None and not target_state.release_slew_armed
    assert target_state.selected_lead == target_state.selected_lead_track_id == -1
    assert target_state.cap_samples == [math.inf] * CAP_FILTER_FRAMES
    assert target_state.lead_speed_samples == [math.inf] * CAP_FILTER_FRAMES
    assert target_state.lead_accel_samples == [0.0] * CAP_FILTER_FRAMES
    assert target_state.departure.samples == [[], []] and target_state.departure.motion_samples == []
    assert target_state.departure.references == [None, None] and target_state.departure.track_ids == [-1, -1]
    assert not target_state.launching and not target_state.departure_launch and not target_state.matched_lead
    assert not target_state.lead_braking and not target_state.e2e_braking_handoff and not target_state.speed_reserve_armed
    assert math.isinf(target_state.filtered_cap) and math.isinf(target_state.filtered_lead_speed) and target_state.filtered_lead_accel == 0.0

  @pytest.mark.parametrize("replacement_track_id", (200, -1), ids=("radar-track", "vision-track"))
  def test_track_id_change_requires_new_history_before_jerk_smoothing(self, replacement_track_id):
    controller = make_controller()
    controller.state = AccelControllerState.restrict
    controller.launching = False
    controller.selected_lead = 0
    controller.selected_lead_track_id = 100
    controller.required_decel = 0.2
    original = [controller.get_jerk_cost_multiplier(True, True, 1.0, False) for _ in range(4)]

    controller.selected_lead_track_id = replacement_track_id
    replacement = [controller.get_jerk_cost_multiplier(True, True, 1.0, False) for _ in range(4)]

    assert original == [MPC_DECEL_JERK_COST_MULTIPLIER] * 4
    assert replacement == [1.0, 1.0, 1.0, MPC_DECEL_JERK_COST_MULTIPLIER]
    assert controller._required_decel_samples == [0.2] * 4
