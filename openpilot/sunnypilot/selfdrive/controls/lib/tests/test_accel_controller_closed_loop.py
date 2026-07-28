from collections.abc import Callable
from dataclasses import dataclass
import gc
import math

import numpy as np
import pytest

from opendbc.car.interfaces import ACCEL_MAX, ACCEL_MIN
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalPlanSource, STOP_DISTANCE, get_T_FOLLOW
from openpilot.selfdrive.controls.lib.longitudinal_planner import get_max_accel
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PRIUS_TSS2_ROUTE_MODEL, LeadObservation, PlantSP as Plant
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller import accel_controller as accel_controller_module
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelControllerState
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  LEAD_LOSS_HOLD_TIME, MATCHED_SPEED_DECEL_RATE, MPC_DECEL_JERK_COST_MULTIPLIER, MPC_DECEL_JERK_MAX_REQUIRED_DECEL,
  MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE, MPC_DECEL_TREND_FRAMES, TARGET_RELEASE_SLEW, TARGET_SPEED_RESERVE, STOP_HOLD_EXIT_FRAMES, AccelProfile,
)

ACTUATOR_DYNAMICS = (
  (0.10, 0.20),
  (0.15, 0.25),
  (0.20, 0.20),
  (0.25, 0.30),
  (0.30, 0.35),
)
ACTUATOR_IDS = ("toyota", "honda", "gm", "hyundai", "ford")
ROUTINE_GAP_TOLERANCE = 0.10
ROUTINE_DECEL_TOLERANCE = 0.10
DROPOUT_GAP_TOLERANCE = 0.15
MOVING_LEAD_GAP_TOLERANCE = 0.12


@dataclass
class ClosedLoopTrace:
  time: np.ndarray
  speed: np.ndarray
  distance: np.ndarray
  distance_lead: np.ndarray
  a_target: np.ndarray
  acceleration: np.ndarray
  should_stop: np.ndarray
  fcw: np.ndarray
  source: list
  dec_mode: list[str]
  active: np.ndarray
  launching: np.ndarray
  departure_launching: np.ndarray
  target_speed: np.ndarray
  raw_cap: np.ndarray
  selected_lead: np.ndarray
  profile_accel_max: np.ndarray
  accel_ceiling_active: np.ndarray
  state: np.ndarray
  required_decel: np.ndarray
  planner_seed_accel: np.ndarray
  mpc_seed_accel: np.ndarray
  mpc_upper_first: np.ndarray
  mpc_upper_min: np.ndarray
  stock_bounds_valid: np.ndarray
  raw_radar_passthrough: np.ndarray
  solver_status: np.ndarray
  mpc_calls: np.ndarray
  solver_failures: int
  solver_failure_times: list[float]


def _configure_plant(plant: Plant, *, enabled: bool, profile: int = 1, dec_enabled: bool = False) -> None:
  plant.planner.accel_controller.enabled = enabled
  plant.planner.accel_controller.profile = profile
  plant.planner.accel_controller.update_params = lambda: None
  plant.planner.dec._enabled = dec_enabled
  plant.planner.dec._read_params = lambda: None


def _run(
  *,
  duration: float,
  controller_enabled: bool,
  profile: int = 1,
  v_lead: float | Callable[[float], float] = 0.0,
  v_cruise: float = 30.0,
  dec_enabled: bool = False,
  radar_fresh_fn: Callable[[int], bool] | None = None,
  **plant_kwargs,
) -> ClosedLoopTrace:
  gc.collect()
  plant = Plant(**plant_kwargs)
  _configure_plant(plant, enabled=controller_enabled, profile=profile, dec_enabled=dec_enabled)
  plant.v_lead_prev = float(v_lead) if isinstance(v_lead, (int, float)) else float(v_lead(0.0))
  if radar_fresh_fn is not None:
    radar_frame = 0

    def patterned_radar_freshness(_sm):
      nonlocal radar_frame
      fresh = radar_fresh_fn(radar_frame)
      radar_frame += 1
      return fresh

    plant.planner._update_radar_freshness = patterned_radar_freshness

  solver_failures = 0
  solver_failure_times = []
  mpc_call_count = 0
  controller_radar = None
  radar_passthrough = []
  seed_calls = []
  original_controller_update = plant.planner.accel_controller.update
  original_mpc_reset = plant.planner.mpc.reset
  original_mpc_set_cur_state = plant.planner.mpc.set_cur_state
  original_mpc_update = plant.planner.mpc.update

  def record_controller_radar(radar_state, *args, **kwargs):
    nonlocal controller_radar
    controller_radar = radar_state
    return original_controller_update(radar_state, *args, **kwargs)

  def count_failed_solve(*args, **kwargs) -> None:
    nonlocal solver_failures
    if plant.planner.mpc.solution_status != 0:
      solver_failures += 1
      solver_failure_times.append(plant.current_time)
    original_mpc_reset(*args, **kwargs)

  def record_seed(v_ego, a_ego):
    seed_calls.append((float(plant.planner.a_desired), float(a_ego)))
    return original_mpc_set_cur_state(v_ego, a_ego)

  def count_mpc_call(radar_state, *args, **kwargs):
    nonlocal mpc_call_count
    mpc_call_count += 1
    radar_passthrough.append(radar_state is controller_radar)
    return original_mpc_update(radar_state, *args, **kwargs)

  plant.planner.accel_controller.update = record_controller_radar
  plant.planner.mpc.reset = count_failed_solve
  plant.planner.mpc.set_cur_state = record_seed
  plant.planner.mpc.update = count_mpc_call
  rows = []
  sources = []
  dec_modes = []
  try:
    while plant.current_time < duration:
      lead_speed = float(v_lead) if isinstance(v_lead, (int, float)) else float(v_lead(plant.current_time))
      calls_before = mpc_call_count
      radar_checks_before = len(radar_passthrough)
      seed_calls_before = len(seed_calls)
      result = plant.step(v_lead=lead_speed, v_cruise=v_cruise)
      controller = plant.planner.accel_controller
      calls_this_frame = mpc_call_count - calls_before
      passthrough_this_frame = (len(radar_passthrough) > radar_checks_before
                                and all(radar_passthrough[radar_checks_before:]))
      if len(seed_calls) > seed_calls_before:
        planner_seed_accel, mpc_seed_accel = seed_calls[-1]
      else:
        planner_seed_accel = mpc_seed_accel = np.nan
      lower = plant.planner.mpc.params[:, 0]
      upper = plant.planner.mpc.params[:, 1]
      lead = plant.planner.accel_controller._held_lead_plan
      raw_cap = lead.cap if lead is not None else math.inf
      profile_accel_max = (plant.planner.accel_controller.get_profile_accel_max(
        controller.profile, result["published_v_ego"],
      ) if controller.is_active else math.inf)
      bounds_valid = (np.allclose(lower, ACCEL_MIN) and np.all(np.isfinite(upper))
                      and np.all(upper >= lower) and np.all(upper <= ACCEL_MAX + 1e-9))
      rows.append((
        plant.current_time, result["speed"], result["distance"], result["distance_lead"], result["a_target"],
        result["realized_acceleration"], result["should_stop"], result["fcw"], controller.is_active,
        controller.launching, controller.departure_launching, controller.output_v_target, raw_cap, controller.selected_lead,
        profile_accel_max, controller.mpc_accel_max is not None, controller.state, controller.required_decel, planner_seed_accel,
        mpc_seed_accel, upper[0], np.min(upper), bounds_valid, passthrough_this_frame,
        plant.planner.mpc.last_solution_status, calls_this_frame,
      ))
      sources.append(result["mpc_source"])
      dec_modes.append(result["dec_mode"])
  finally:
    plant.planner.accel_controller.update = original_controller_update
    plant.planner.mpc.reset = original_mpc_reset
    plant.planner.mpc.set_cur_state = original_mpc_set_cur_state
    plant.planner.mpc.update = original_mpc_update

  data = np.asarray(rows, dtype=float)
  trace = ClosedLoopTrace(
    time=data[:, 0], speed=data[:, 1], distance=data[:, 2], distance_lead=data[:, 3], a_target=data[:, 4], acceleration=data[:, 5],
    should_stop=data[:, 6].astype(bool), fcw=data[:, 7].astype(bool), source=sources, dec_mode=dec_modes,
    active=data[:, 8].astype(bool), launching=data[:, 9].astype(bool), departure_launching=data[:, 10].astype(bool),
    target_speed=data[:, 11], raw_cap=data[:, 12], selected_lead=data[:, 13].astype(int), profile_accel_max=data[:, 14],
    accel_ceiling_active=data[:, 15].astype(bool), state=data[:, 16].astype(int), required_decel=data[:, 17], planner_seed_accel=data[:, 18],
    mpc_seed_accel=data[:, 19], mpc_upper_first=data[:, 20], mpc_upper_min=data[:, 21],
    stock_bounds_valid=data[:, 22].astype(bool), raw_radar_passthrough=data[:, 23].astype(bool),
    solver_status=data[:, 24].astype(int), mpc_calls=data[:, 25].astype(int), solver_failures=solver_failures,
    solver_failure_times=solver_failure_times,
  )
  gc.collect()
  return trace


def _first_time_below(trace: ClosedLoopTrace, threshold: float, after: float = 0.0) -> float:
  indices = np.flatnonzero((trace.time >= after) & (trace.a_target <= threshold))
  assert len(indices), f"never reached {threshold} m/s²"
  return float(trace.time[indices[0]])


def _sustained_time_below(trace: ClosedLoopTrace, threshold: float, *, after: float = 0.5, duration: float = 0.5) -> float:
  required_frames = round(duration / DT_MDL)
  below = (trace.time >= after) & (trace.a_target <= threshold)
  sustained = np.convolve(below.astype(int), np.ones(required_frames, dtype=int), mode="valid") == required_frames
  indices = np.flatnonzero(sustained)
  assert len(indices), f"never sustained {threshold} m/s² for {duration} s"
  return float(trace.time[indices[0]])


def _command_jerk(trace: ClosedLoopTrace, after: float = 0.0) -> np.ndarray:
  indices = np.flatnonzero(trace.time >= after)
  assert len(indices) >= 2
  return np.diff(trace.a_target[indices]) / DT_MDL


def _filtered_realized_jerk(trace: ClosedLoopTrace, after: float = 1.0) -> np.ndarray:
  filtered_acceleration = np.convolve(trace.acceleration, np.ones(3) / 3.0, mode="valid")
  samples = trace.time[2:-1] >= after
  return (np.diff(filtered_acceleration) / DT_MDL)[samples]


def _has_brake_coast_brake(values: np.ndarray, brake: float = -0.8, coast: float = -0.35, frames: int = 2) -> bool:
  phase = 0
  for index in range(len(values) - frames + 1):
    window = values[index:index + frames]
    if np.all(window <= brake):
      if phase == 2:
        return True
      phase = 1
    elif phase == 1 and np.all(window >= coast):
      phase = 2
  return False


def _has_propulsion_after_braking(values: np.ndarray, propulsion: float = 0.2, brake: float = -0.2, frames: int = 2) -> bool:
  braking = False
  for index in range(len(values) - frames + 1):
    window = values[index:index + frames]
    if np.all(window <= brake):
      braking = True
    elif braking and np.all(window >= propulsion):
      return True
  return False


def _has_propulsion_brake_cycle(values: np.ndarray, propulsion: float = 0.2, brake: float = -0.2, frames: int = 2) -> bool:
  phases = []
  for index in range(len(values) - frames + 1):
    window = values[index:index + frames]
    phase = 1 if np.all(window >= propulsion) else -1 if np.all(window <= brake) else 0
    if phase and (not phases or phase != phases[-1]):
      phases.append(phase)
      if len(phases) >= 3 and phases[-1] == phases[-3]:
        return True
  return False


def _assert_non_actuating_matches_stock(trace: ClosedLoopTrace, baseline: ClosedLoopTrace) -> None:
  np.testing.assert_allclose(trace.a_target, baseline.a_target, atol=1e-6, rtol=0.0)
  np.testing.assert_array_equal(trace.should_stop, baseline.should_stop)
  np.testing.assert_array_equal(trace.fcw, baseline.fcw)
  np.testing.assert_array_equal(trace.solver_status, baseline.solver_status)
  assert trace.source == baseline.source
  assert trace.solver_failures == baseline.solver_failures
  assert trace.solver_failure_times == baseline.solver_failure_times


def _assert_no_new_solver_failures(trace: ClosedLoopTrace, baseline: ClosedLoopTrace) -> None:
  assert trace.solver_failures <= baseline.solver_failures


@pytest.mark.parametrize(
  "plant_kwargs",
  [
    {"enabled": False, "lead_relevancy": True, "speed": 20.0, "distance_lead": 70.0},
    {"e2e": True, "lead_relevancy": False, "speed": 20.0},
  ],
  ids=("disengaged", "e2e"),
)
def test_non_actuating_modes_match_stock(plant_kwargs):
  common = dict(duration=2.0, v_lead=14.0, **plant_kwargs)
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)

  _assert_non_actuating_matches_stock(trace, baseline)
  assert not trace.active.any()
  np.testing.assert_allclose(trace.mpc_upper_min, baseline.mpc_upper_min)
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)


def test_disabled_profiles_are_identical():
  common = dict(duration=2.0, controller_enabled=False, lead_relevancy=True, speed=20.0, distance_lead=70.0, v_lead=14.0)
  traces = [_run(profile=profile, **common) for profile in range(3)]
  for trace in traces[1:]:
    _assert_non_actuating_matches_stock(trace, traces[0])


def test_planner_configures_controller_before_one_stock_mpc_solve():
  plant = Plant(enabled=True, lead_relevancy=False, speed=0.0, actuator_delay=0.15, actuator_lag=0.20)
  _configure_plant(plant, enabled=True)
  plant.step(v_lead=0.0, v_cruise=22.352)
  calls = []
  mpc = plant.planner.mpc
  controller_update = plant.planner.accel_controller.update
  set_params = mpc.set_accel_controller_params
  set_weights = mpc.set_weights
  set_cur_state = mpc.set_cur_state
  update = mpc.update

  def record_controller(radar_state, *args, **kwargs):
    calls.append(("controller", radar_state, args, kwargs))
    return controller_update(radar_state, *args, **kwargs)

  def record(name, method):
    def wrapped(*args, **kwargs):
      calls.append((name, args, kwargs))
      return method(*args, **kwargs)
    return wrapped

  plant.planner.accel_controller.update = record_controller
  mpc.set_accel_controller_params = record("configure", set_params)
  mpc.set_weights = record("weights", set_weights)
  mpc.set_cur_state = record("state", set_cur_state)
  mpc.update = record("update", update)
  plant.step(v_lead=0.0, v_cruise=22.352)

  names = [call[0] for call in calls]
  assert names == ["controller", "configure", "weights", "state", "update"]
  assert calls[0][1] is calls[4][1][0]
  assert calls[2][2]["personality"] == calls[4][2]["personality"]


@pytest.mark.parametrize("lead_relevancy", (False, True), ids=("clear-road", "lead"))
def test_force_decel_matches_stock(lead_relevancy):
  common = dict(duration=2.0, force_decel=True, lead_relevancy=lead_relevancy, speed=20.0,
                distance_lead=70.0, v_lead=14.0, profile=0)
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  _assert_non_actuating_matches_stock(trace, baseline)
  assert not trace.active.any()
  np.testing.assert_allclose(trace.mpc_upper_min, ACCEL_MAX)


@pytest.mark.parametrize("profile", range(3), ids=("eco", "normal", "sport"))
def test_active_controller_uses_one_raw_mpc_solve_and_feasible_stock_bounds(profile):
  trace = _run(
    duration=4.0, controller_enabled=True, profile=profile, lead_relevancy=False, speed=0.0,
    v_cruise=22.352, actuator_delay=0.15, actuator_lag=0.20,
  )

  assert trace.active.all()
  assert np.all(trace.mpc_calls == 1)
  assert trace.raw_radar_passthrough.all()
  assert trace.stock_bounds_valid.all()
  np.testing.assert_allclose(trace.mpc_seed_accel, trace.planner_seed_accel, atol=1e-12, rtol=0.0)
  assert np.all(trace.mpc_upper_first + 1e-9 >= trace.mpc_seed_accel)
  assert np.all(trace.mpc_upper_min >= 0.0)
  assert np.any(trace.mpc_upper_min < ACCEL_MAX - 0.05)
  assert trace.solver_failures == 0


def test_e2e_to_radar_acc_handoff_keeps_braking_continuous():
  def run_handoff(controller_enabled: bool):
    plant = Plant(
      lead_relevancy=True, speed=10.0, distance_lead=30.0, actuator_delay=0.15, actuator_lag=0.20,
      model_action_fn=lambda current_time, _v_ego, _a_ego: (-1.0 if current_time < 2.0 else 0.0, False),
    )
    _configure_plant(plant, enabled=controller_enabled)
    rows = []
    while plant.current_time < 2.4:
      plant.e2e = plant.current_time < 2.0
      result = plant.step(v_lead=8.0, v_cruise=20.0)
      rows.append((plant.current_time, result["a_target"], plant.planner.mpc.last_solution_status,
                   plant.planner.accel_controller.is_active))
    return np.asarray(rows, dtype=float).T

  baseline_time, baseline_accel, baseline_status, _ = run_handoff(False)
  time_values, acceleration, solver_status, active = run_handoff(True)
  np.testing.assert_allclose(time_values, baseline_time, atol=0.0, rtol=0.0)
  transition = np.flatnonzero(time_values > 2.0)[0]
  baseline_jump = abs(baseline_accel[transition] - baseline_accel[transition - 1])
  controlled_jump = abs(acceleration[transition] - acceleration[transition - 1])
  baseline_jerk = np.max(np.abs(np.diff(baseline_accel[transition:]) / DT_MDL))
  controlled_jerk = np.max(np.abs(np.diff(acceleration[transition:]) / DT_MDL))

  assert controlled_jump <= baseline_jump + 1e-6
  assert controlled_jerk <= baseline_jerk + 0.10
  assert np.count_nonzero(solver_status[transition:]) <= np.count_nonzero(baseline_status[transition:])
  assert active[transition]


def test_clear_road_launch_is_prompt_and_profiles_separate_above_launch_speed():
  traces = [
    _run(
      duration=12.0, controller_enabled=True, profile=profile, lead_relevancy=False, speed=0.0,
      v_cruise=22.352, actuator_delay=0.15, actuator_lag=0.20,
    )
    for profile in range(3)
  ]

  for trace in traces:
    positive = np.flatnonzero(trace.a_target > 0.05)
    moving = np.flatnonzero(trace.speed > 0.01)
    target_steps = np.diff(trace.target_speed)
    release = int(np.argmax(target_steps))
    assert len(positive) and trace.time[positive[0]] <= 4 * DT_MDL
    assert len(moving) and trace.time[moving[0]] <= 1.0
    assert np.interp(1.0, trace.time, trace.speed) >= 0.33
    assert target_steps[release] > TARGET_RELEASE_SLEW * DT_MDL
    assert trace.time[release + 1] <= 0.5
    assert abs(_command_jerk(trace)[release]) < 5.0
    assert abs(np.diff(trace.acceleration)[release] / DT_MDL) < 1.0
    assert not np.any(trace.a_target < -0.05)
    assert not _has_propulsion_brake_cycle(trace.a_target)
    assert trace.solver_failures == 0

  launch_window = traces[0].time <= 0.5
  np.testing.assert_allclose(traces[1].a_target[launch_window], traces[0].a_target[launch_window], atol=0.10, rtol=0.0)
  np.testing.assert_allclose(traces[2].a_target[launch_window], traces[0].a_target[launch_window], atol=0.10, rtol=0.0)
  speed_at_eight = [float(np.interp(8.0, trace.time, trace.speed)) for trace in traces]
  assert speed_at_eight[0] + 0.75 < speed_at_eight[1]
  assert speed_at_eight[1] + 0.30 < speed_at_eight[2]
  final_speed = [float(trace.speed[-1]) for trace in traces]
  assert final_speed[0] + 1.25 < final_speed[1]
  assert final_speed[1] + 0.75 < final_speed[2]
  ceiling_at_ten = [float(np.interp(10.0, trace.speed, trace.mpc_upper_min)) for trace in traces]
  assert ceiling_at_ten[0] < ceiling_at_ten[1] < ceiling_at_ten[2]


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_high_speed_lead_seed_release_has_no_target_snap(actuator_delay, actuator_lag):
  dropout_time = 5.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if lead_name == "leadTwo" or current_time >= dropout_time else truth

  common = dict(
    duration=7.0, profile=AccelProfile.eco, lead_relevancy=True, speed=22.0,
    distance_lead=100.0, v_lead=20.0, v_cruise=30.0, lead_observation_fn=observe,
    actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  response = (trace.time >= dropout_time - 0.5) & (trace.time <= dropout_time + 2.0)
  response_steps = (trace.time[1:] >= dropout_time) & (trace.time[1:] <= dropout_time + 2.0)
  steps = np.diff(trace.target_speed)
  release = np.flatnonzero(response_steps & (steps > 1e-6))

  assert len(release) and trace.time[release[0] + 1] <= dropout_time + LEAD_LOSS_HOLD_TIME + DT_MDL + 1e-9
  assert np.max(steps[response_steps]) <= TARGET_RELEASE_SLEW * DT_MDL + TARGET_SPEED_RESERVE + 1e-9
  assert trace.target_speed[trace.time >= dropout_time + 2.0][0] == 30.0
  assert np.max(np.abs(_command_jerk(trace)[response_steps])) <= np.max(np.abs(_command_jerk(baseline)[response_steps])) + 1e-9
  release_response = response_steps.copy()
  release_response[:release[0]] = False
  assert np.max(np.abs(_command_jerk(trace)[release_response])) < 1.0
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert not trace.fcw.any() and trace.solver_failures == 0


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_route_537_lead_dropout_does_not_pulse_throttle_before_reacquisition(actuator_delay, actuator_lag):
  dropout_start, brief_return, second_dropout, reacquisition = 5.0, 5.7, 5.9, 7.4

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    visible = current_time < dropout_start or brief_return <= current_time < second_dropout or current_time >= reacquisition
    return truth if lead_name == "leadOne" and visible else None

  common = dict(
    duration=10.0, profile=AccelProfile.eco, lead_relevancy=True, speed=22.0,
    distance_lead=70.0, v_lead=18.0, v_cruise=30.0, lead_observation_fn=observe,
    actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  trace = _run(controller_enabled=True, **common)
  dropout = (trace.time >= dropout_start) & (trace.time < reacquisition)
  response = (trace.time >= dropout_start - 0.5) & (trace.time <= reacquisition + 2.0)

  assert np.max(trace.a_target[dropout]) <= 0.2
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.min(trace.distance_lead[response] - trace.distance[response]) > 5.0 * STOP_DISTANCE
  assert trace.raw_radar_passthrough.all() and np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any() and trace.solver_failures == 0


@pytest.mark.parametrize(
  ("speed", "v_cruise"),
  ((0.0, 22.352), (25.0, 30.0), (35.0, 35.0)),
)
def test_decel_smoothing_does_not_change_clear_road_acceleration_at_representative_speeds(monkeypatch, speed, v_cruise):
  common = dict(
    duration=3.0, controller_enabled=True, profile=AccelProfile.sport, lead_relevancy=False,
    speed=speed, v_cruise=v_cruise, actuator_delay=0.15, actuator_lag=0.20,
  )
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_COST_MULTIPLIER", 1.0)
  stock_weight = _run(**common)
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_COST_MULTIPLIER", MPC_DECEL_JERK_COST_MULTIPLIER)
  smoothed = _run(**common)

  np.testing.assert_allclose(smoothed.a_target, stock_weight.a_target, atol=1e-9, rtol=0.0)
  np.testing.assert_allclose(smoothed.speed, stock_weight.speed, atol=1e-9, rtol=0.0)
  np.testing.assert_allclose(smoothed.mpc_upper_min, stock_weight.mpc_upper_min, atol=1e-9, rtol=0.0)
  assert smoothed.solver_failures == stock_weight.solver_failures == 0


def test_lead_bound_routine_decel_uses_smoothing_without_delaying_initial_braking(monkeypatch):
  def lead_speed(current_time: float) -> float:
    return max(22.5, 25.0 - 0.4 * current_time)

  common = dict(
    duration=8.0, controller_enabled=True, profile=AccelProfile.eco, lead_relevancy=True, speed=29.0,
    distance_lead=80.0, v_lead=lead_speed, v_cruise=33.528, actuator_delay=0.15, actuator_lag=0.20,
  )
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_COST_MULTIPLIER", 1.0)
  baseline = _run(**common)
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_COST_MULTIPLIER", MPC_DECEL_JERK_COST_MULTIPLIER)
  smoothed = _run(**common)
  response = smoothed.time >= 0.5
  baseline_gap = baseline.distance_lead - baseline.distance
  gap = smoothed.distance_lead - smoothed.distance

  assert set(np.asarray(smoothed.source)[response]) <= {LongitudinalPlanSource.lead0, LongitudinalPlanSource.lead1}
  assert np.max(smoothed.required_decel[response]) < 0.80
  assert float(np.percentile(np.abs(_filtered_realized_jerk(smoothed)), 95)) < float(np.percentile(np.abs(_filtered_realized_jerk(baseline)), 95))
  assert float(np.percentile(np.abs(_command_jerk(smoothed, after=0.5)), 95)) < float(np.percentile(np.abs(_command_jerk(baseline, after=0.5)), 95))
  assert _first_time_below(smoothed, -0.2) <= _first_time_below(baseline, -0.2) + 1e-6
  assert _first_time_below(smoothed, -0.5) <= _first_time_below(baseline, -0.5) + 0.25 + 1e-6
  assert np.min(gap) >= np.min(baseline_gap) - 0.25
  assert np.max(np.abs(_command_jerk(smoothed, after=0.5))) < 3.0
  assert not _has_propulsion_brake_cycle(smoothed.a_target[response])
  assert not smoothed.fcw.any()
  assert smoothed.solver_failures == 0


def test_tightening_lead_releases_smoothing_before_late_catchup(monkeypatch):
  event_time = 3.0
  lead_jerk = 1.02
  max_lead_decel = 2.22
  ramp_time = max_lead_decel / lead_jerk

  def lead_speed(current_time: float) -> float:
    braking_time = max(current_time - event_time, 0.0)
    ramp = min(braking_time, ramp_time)
    return 16.9 - 0.5 * lead_jerk * ramp**2 - max_lead_decel * max(braking_time - ramp_time, 0.0)

  common = dict(
    duration=7.0, profile=AccelProfile.eco, lead_relevancy=True, speed=15.9, distance_lead=35.7,
    v_lead=lead_speed, v_cruise=17.4, actuator_delay=0.15, actuator_lag=0.20,
  )
  stock = _run(controller_enabled=False, **common)
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE", np.inf)
  always_smoothed = _run(controller_enabled=True, **common)
  monkeypatch.setattr(accel_controller_module, "MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE", MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE)
  trace = _run(controller_enabled=True, **common)
  response = trace.time >= event_time
  response_jerk = trace.time[1:] >= event_time
  required_decel_rate = (trace.required_decel[3:] - trace.required_decel[:-3]) / (3 * DT_MDL)
  gap = trace.distance_lead - trace.distance
  always_smoothed_gap = always_smoothed.distance_lead - always_smoothed.distance

  assert np.max(required_decel_rate[trace.required_decel[3:] >= 0.15]) > MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE
  assert _first_time_below(trace, -0.5) <= _first_time_below(stock, -0.5) + 1e-9
  assert _first_time_below(trace, -0.5) <= _first_time_below(always_smoothed, -0.5) - DT_MDL + 1e-9
  assert np.max(np.abs(np.diff(trace.a_target)[response_jerk] / DT_MDL)) < 3.0
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.min(gap) >= np.min(always_smoothed_gap) - 1e-6
  assert not stock.fcw.any() and not always_smoothed.fcw.any() and not trace.fcw.any()
  assert stock.solver_failures == always_smoothed.solver_failures == trace.solver_failures == 0


def test_same_slot_track_replacement_never_delays_tightening_lead_braking():
  event_time = 3.0
  lead_jerk = 1.02
  max_lead_decel = 2.22
  ramp_time = max_lead_decel / lead_jerk

  def lead_speed(current_time: float) -> float:
    braking_time = max(current_time - event_time, 0.0)
    ramp = min(braking_time, ramp_time)
    return 16.9 - 0.5 * lead_jerk * ramp**2 - max_lead_decel * max(braking_time - ramp_time, 0.0)

  def observe(switch_time: float | None):
    def observation(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
      if lead_name == "leadTwo":
        return None
      track_id = 200 if switch_time is not None and current_time >= switch_time else 100
      return truth | {"radar": True, "radarTrackId": track_id}
    return observation

  common = dict(
    duration=8.0, controller_enabled=True, profile=AccelProfile.eco, lead_relevancy=True, speed=15.9, distance_lead=35.7,
    v_lead=lead_speed, v_cruise=17.4, actuator_delay=0.15, actuator_lag=0.20,
  )
  baseline = _run(lead_observation_fn=observe(None), **common)
  history = MPC_DECEL_TREND_FRAMES - 1
  rate = np.full_like(baseline.required_decel, -math.inf)
  rate[history:] = (baseline.required_decel[history:] - baseline.required_decel[:-history]) / (history * DT_MDL)
  candidates = np.flatnonzero(
    (baseline.time >= event_time)
    & (baseline.state == int(AccelControllerState.restrict))
    & (baseline.required_decel > 0.0)
    & (baseline.required_decel < MPC_DECEL_JERK_MAX_REQUIRED_DECEL)
    & (rate > MPC_DECEL_JERK_MAX_REQUIRED_DECEL_RATE)
    & (baseline.a_target > -1.0)
  )
  assert len(candidates)
  switch_time = float(baseline.time[candidates[0]])
  switched = _run(lead_observation_fn=observe(switch_time), **common)
  response = switched.time >= switch_time
  baseline_gap = baseline.distance_lead - baseline.distance
  switched_gap = switched.distance_lead - switched.distance

  def minimum_ttc(trace: ClosedLoopTrace, gap: np.ndarray) -> float:
    closing_speed = trace.speed - np.asarray([lead_speed(current_time) for current_time in trace.time])
    closing = closing_speed > 0.1
    assert closing.any()
    return float(np.min(gap[closing] / closing_speed[closing]))

  assert np.all(baseline.selected_lead[response] == 0)
  assert np.all(switched.selected_lead[response] == 0)
  for threshold in (-1.0, -2.0):
    assert _first_time_below(switched, threshold) <= _first_time_below(baseline, threshold) + 1e-9
  assert np.min(switched_gap) >= np.min(baseline_gap) - 0.02
  assert minimum_ttc(switched, switched_gap) >= minimum_ttc(baseline, baseline_gap) - 0.02
  assert np.min(switched_gap) > 0.0
  assert not switched.fcw.any()
  assert baseline.solver_failures == switched.solver_failures == 0


def test_prius_route_model_launches_without_a_dead_pedal():
  trace = _run(
    duration=3.0, controller_enabled=True, profile=1, lead_relevancy=False, speed=0.0,
    v_cruise=22.352, actuator_model=PRIUS_TSS2_ROUTE_MODEL,
  )
  positive = np.flatnonzero(trace.a_target > 0.05)
  moving = np.flatnonzero(trace.speed > 0.05)
  assert len(positive) and trace.time[positive[0]] <= 4 * DT_MDL
  assert len(moving) and trace.time[moving[0]] <= 1.0
  assert trace.solver_failures == 0


def test_stop_hold_survives_short_full_field_dropout():
  def observe(current_time: float, _lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if 1.0 <= current_time < 1.1 else truth

  common = dict(
    duration=2.0, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=0.0, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  baseline = _run(**(common | {"controller_enabled": False}))
  trace = _run(**common)
  assert np.max(trace.speed) < 1e-3
  assert np.all(trace.target_speed == 0.0)
  assert np.all(trace.state == int(AccelControllerState.stopHold))
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)


@pytest.mark.parametrize("replacement_track_id", (100, 200), ids=("same-track", "replacement"))
def test_stop_hold_rejects_persistent_same_slot_range_step(replacement_track_id):
  step_time = 1.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    stepped = current_time >= step_time
    speed = 0.2 if stepped else 0.0
    return truth | {"dRel": truth["dRel"] + 0.4 * stepped, "vLead": speed, "vLeadK": speed, "vRel": speed,
                    "aLeadK": 0.0, "radarTrackId": replacement_track_id if stepped else 100, "radar": True}

  trace = _run(
    duration=2.5, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=0.0, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )

  assert np.all(trace.state == int(AccelControllerState.stopHold))
  assert np.all(trace.target_speed == 0.0)
  assert trace.should_stop.all()
  assert np.max(trace.speed) < 1e-3
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_moving_departure_crossing_exit_speed_releases_once():
  departure_time = 1.0
  speeds = (0.81, 0.82, 0.83, 0.84, 0.79, 0.76, 0.74, 0.72)

  def lead_speed(current_time: float) -> float:
    frame = round((current_time - departure_time) / DT_MDL)
    return 0.0 if frame < 0 else speeds[min(frame, len(speeds) - 1)]

  def observe(_current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if lead_name == "leadTwo" else truth | {"aLeadK": 0.0, "radarTrackId": 100, "radar": True}

  trace = _run(
    duration=3.0, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lead_speed, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  after_departure = trace.time >= departure_time
  stop_hold = int(AccelControllerState.stopHold)
  releases = np.flatnonzero((trace.state[:-1] == stop_hold) & (trace.state[1:] != stop_hold)) + 1

  assert len(releases) == 1
  assert trace.launching[releases[0]]
  assert not np.any(trace.state[releases[0]:] == stop_hold)
  assert np.count_nonzero(np.diff(trace.should_stop[after_departure].astype(int))) == 1
  assert not _has_propulsion_brake_cycle(trace.a_target[after_departure])
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_route_51d_duplicate_lead_speed_pulse_cannot_release_stop_hold():
  pulse_start = 1.0
  departure_time = 2.0
  pulse_speeds = (0.1361, 0.1731, 0.2146, 0.2253, 0.2137, 0.1877)
  pulse_distances = (6.0, 6.0, 6.0, 5.96, 6.04, 6.04)

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 2.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation:
    result = truth | {"radar": True, "radarTrackId": 4887 if lead_name == "leadOne" else 4905}
    pulse_frame = round((current_time - pulse_start) / DT_MDL)
    if 0 <= pulse_frame < len(pulse_speeds):
      speed = pulse_speeds[pulse_frame] if lead_name == "leadOne" else 0.0
      distance = pulse_distances[pulse_frame] if lead_name == "leadOne" else 6.08
      result |= {"dRel": distance, "vLead": speed, "vLeadK": speed, "vRel": speed, "aLeadK": 0.0}
    return result

  trace = _run(
    duration=3.0, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lead_speed, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  pulse = (trace.time >= pulse_start) & (trace.time < pulse_start + len(pulse_speeds) * DT_MDL)
  launched = np.flatnonzero((trace.time >= departure_time) & trace.launching)

  assert np.all(trace.state[pulse] == int(AccelControllerState.stopHold))
  assert np.all(trace.target_speed[pulse] == 0.0)
  assert np.max(trace.speed[pulse]) < 0.01
  assert len(launched) and trace.time[launched[0]] <= departure_time + STOP_HOLD_EXIT_FRAMES * DT_MDL + 1e-9
  assert not _has_propulsion_brake_cycle(trace.a_target[trace.time >= departure_time])
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_route_520_slow_lead_pulse_cannot_release_stop_hold_or_dampen_real_departure():
  pulse_start = 1.0
  departure_time = 2.5
  pulse_speeds = (0.01, 0.03, 0.07, 0.10, 0.14, 0.20, 0.26, 0.32, 0.34, 0.33, 0.31, 0.28, 0.24, 0.20, 0.15, 0.09, 0.05, 0.01)
  pulse_offsets = (0.00, 0.00, 0.00, 0.01, 0.01, 0.02, 0.03, 0.04, 0.06, 0.07, 0.09, 0.11, 0.12, 0.13, 0.14, 0.15, 0.15, 0.16)

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 2.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    pulse_frame = round((current_time - pulse_start) / DT_MDL)
    if 0 <= pulse_frame < len(pulse_speeds):
      speed = pulse_speeds[pulse_frame]
      return truth | {"dRel": 6.0 + pulse_offsets[pulse_frame], "vLead": speed, "vLeadK": speed, "vRel": speed,
                      "aLeadK": 0.0, "radarTrackId": 2133, "radar": True}
    return truth | {"aLeadK": 0.0, "radarTrackId": 2133, "radar": True}

  common = dict(
    duration=4.0, lead_relevancy=True, speed=0.0, distance_lead=6.0, v_lead=lead_speed, v_cruise=8.0,
    lead_observation_fn=observe, actuator_model=PRIUS_TSS2_ROUTE_MODEL,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  pulse = (trace.time >= pulse_start) & (trace.time < pulse_start + len(pulse_speeds) * DT_MDL)
  release = np.flatnonzero((trace.time >= departure_time) & trace.launching)

  assert np.all(trace.state[pulse] == int(AccelControllerState.stopHold))
  assert np.all(trace.target_speed[pulse] == 0.0)
  assert np.max(trace.speed[trace.time < departure_time]) < 0.01
  assert len(release) and trace.time[release[0]] <= departure_time + STOP_HOLD_EXIT_FRAMES * DT_MDL + 1e-9
  assert trace.a_target[release[0]] > 0.05
  assert np.allclose(trace.a_target[release[0]:], baseline.a_target[release[0]:], atol=1e-5, rtol=0.0)
  assert not _has_propulsion_brake_cycle(trace.a_target[trace.time >= departure_time])
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_stopped_lead_requires_four_departure_frames_and_launches_within_one_second(actuator_delay, actuator_lag):
  departure_time = 1.0

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 2.0

  trace = _run(
    duration=2.5, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lead_speed, v_cruise=8.0, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  first_three = (trace.time > departure_time) & (trace.time <= departure_time + 3 * DT_MDL + 1e-9)
  release = np.flatnonzero((trace.time >= departure_time) & trace.launching)
  moving = np.flatnonzero((trace.time >= departure_time) & (trace.speed > 0.05))

  assert not trace.launching[first_three].any()
  assert trace.should_stop[first_three].all()
  assert len(release) and trace.time[release[0]] >= departure_time + 3 * DT_MDL
  assert not trace.should_stop[release[0]]
  assert len(moving) and trace.time[moving[0]] <= departure_time + 3 * DT_MDL + 1.0
  assert not _has_propulsion_brake_cycle(trace.a_target[trace.time >= departure_time])
  assert trace.solver_failures == 0


def test_stop_hold_departure_survives_radar_staleness():
  departure_time = 1.0
  dropout_start_time = 1.3
  dropout_len_frames = round(0.8 / DT_MDL)
  dropout_start_frame = round(dropout_start_time / DT_MDL)

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 2.0

  def radar_fresh_fn(frame: int) -> bool:
    return not (dropout_start_frame <= frame < dropout_start_frame + dropout_len_frames)

  common = dict(
    duration=4.0, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lead_speed, v_cruise=8.0, actuator_delay=0.15, actuator_lag=0.25,
  )
  baseline = _run(**common)
  trace = _run(radar_fresh_fn=radar_fresh_fn, **common)
  just_before_dropout = (trace.time >= dropout_start_time - 2 * DT_MDL) & (trace.time < dropout_start_time)
  after_recovery = trace.time >= dropout_start_time + dropout_len_frames * DT_MDL
  gap = trace.distance_lead - trace.distance
  baseline_gap = baseline.distance_lead - baseline.distance

  assert trace.departure_launching[just_before_dropout].all()
  assert not _has_propulsion_brake_cycle(trace.a_target)
  assert not _has_brake_coast_brake(trace.a_target)
  assert np.max(np.abs(np.diff(trace.a_target) / DT_MDL)) < 3.0
  assert np.min(gap) >= np.min(baseline_gap) - DROPOUT_GAP_TOLERANCE
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)
  assert trace.solver_failures == 0
  assert trace.launching[after_recovery].any()
  assert trace.time[np.flatnonzero(after_recovery & trace.launching)[0]] <= dropout_start_time + dropout_len_frames * DT_MDL + 1.0


def test_confirmed_departure_full_field_dropout_does_not_worsen_stock_response():
  departure_time = 1.0
  dropout_start = 1.3
  dropout_end = 1.45
  dropped: list[tuple[int, str]] = []

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 2.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if dropout_start <= current_time < dropout_end:
      dropped.append((round(current_time / DT_MDL), lead_name))
      return None
    return truth

  common = dict(
    duration=4.0, lead_relevancy=True, speed=0.0, distance_lead=6.0, v_lead=lead_speed,
    v_cruise=8.0, actuator_delay=0.15, actuator_lag=0.25, lead_observation_fn=observe,
  )
  baseline = _run(controller_enabled=False, **common)
  dropped.clear()
  trace = _run(controller_enabled=True, **common)
  before_dropout = (trace.time >= dropout_start - 2 * DT_MDL) & (trace.time < dropout_start)
  dropout = (trace.time > dropout_start) & (trace.time <= dropout_end)
  jerk_window = (trace.time[1:] > dropout_start) & (trace.time[1:] <= dropout_end + 0.25)
  dropped_by_frame: dict[int, set[str]] = {}
  for frame, lead_name in dropped:
    dropped_by_frame.setdefault(frame, set()).add(lead_name)

  assert trace.departure_launching[before_dropout].all()
  assert len(dropped_by_frame) == round((dropout_end - dropout_start) / DT_MDL)
  assert all(lead_names == {"leadOne", "leadTwo"} for lead_names in dropped_by_frame.values())
  assert np.all(trace.selected_lead[dropout] == -1) and np.all(np.isinf(trace.raw_cap[dropout]))
  assert not np.any(trace.state[dropout] == int(AccelControllerState.stopHold))
  assert not _has_propulsion_brake_cycle(trace.a_target) and not _has_brake_coast_brake(trace.a_target)
  assert np.max(np.abs(np.diff(trace.a_target)[jerk_window] / DT_MDL)) <= np.max(np.abs(np.diff(baseline.a_target)[jerk_window] / DT_MDL)) + 0.01
  assert np.min(trace.distance_lead - trace.distance) >= np.min(baseline.distance_lead - baseline.distance) - DROPOUT_GAP_TOLERANCE
  assert not trace.fcw.any()
  np.testing.assert_array_equal(trace.solver_status, baseline.solver_status)
  assert trace.solver_failure_times == baseline.solver_failure_times


def test_reused_radar_frames_do_not_pulse_stop_state_during_departure():
  departure_time = 1.0
  trace = _run(
    duration=3.0, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lambda current_time: 0.0 if current_time < departure_time else 2.0,
    v_cruise=8.0, actuator_delay=0.15, actuator_lag=0.25, radar_fresh_fn=lambda frame: frame % 2 == 0,
  )
  after_departure = trace.time >= departure_time
  should_stop = trace.should_stop[after_departure]
  release = np.flatnonzero(after_departure & trace.launching)
  moving = np.flatnonzero(after_departure & (trace.speed > 0.05))

  assert np.count_nonzero(np.diff(should_stop.astype(int))) <= 1
  assert len(release) and len(moving)
  assert trace.time[moving[0]] <= trace.time[release[0]] + 1.0
  assert not _has_propulsion_brake_cycle(trace.a_target[after_departure])
  assert trace.solver_failures == 0


@pytest.mark.parametrize("departure_frames", [1, 2, 3])
def test_short_false_departure_does_not_launch_the_vehicle(departure_frames):
  trace = _run(
    duration=2.5, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lambda current_time: 2.0 if 1.0 <= current_time < 1.0 + departure_frames * DT_MDL else 0.0,
    v_cruise=8.0, actuator_delay=0.10, actuator_lag=0.20,
  )

  assert np.max(trace.speed) < 0.01
  assert not trace.launching.any()
  assert trace.should_stop.all()
  assert trace.state[-1] == int(AccelControllerState.stopHold)
  assert trace.solver_failures == 0


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_matched_lead_recovery_preserves_profile_ordering(actuator_delay, actuator_lag):
  traces = [
    _run(
      duration=32.0, controller_enabled=True, profile=profile, lead_relevancy=True, speed=20.0,
      distance_lead=100.0, v_lead=10.0, v_cruise=30.0, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
    )
    for profile in range(3)
  ]
  response = (traces[0].time >= 15.0) & (traces[0].time <= 28.5)
  mean_accel = [float(np.mean(trace.a_target[response])) for trace in traces]
  final_speed = [float(trace.speed[np.flatnonzero(response)[-1]]) for trace in traces]

  assert mean_accel[0] + 0.06 < mean_accel[1]
  assert mean_accel[1] + 0.025 < mean_accel[2]
  assert final_speed[0] < final_speed[1] < final_speed[2]
  assert max(final_speed) < 13.5
  assert all(not _has_propulsion_brake_cycle(trace.a_target[response]) for trace in traces)
  assert all(trace.solver_failures == 0 for trace in traces)


def test_creeping_lead_departure_is_prompt_and_safe():
  departure_time = 1.0

  def lead_speed(current_time: float) -> float:
    if current_time < departure_time:
      return 0.0
    if current_time < departure_time + 0.5:
      return 1.6 * (current_time - departure_time)
    return min(2.5, 0.8 + 0.7 * (current_time - departure_time - 0.5))

  def observe(_current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if lead_name == "leadTwo" else truth | {"aLeadK": 0.0, "radarTrackId": 2133, "radar": True}

  common = dict(
    duration=6.0, profile=0, lead_relevancy=True, speed=0.0, distance_lead=3.6, v_lead=lead_speed,
    v_cruise=22.352, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  after_departure = trace.time >= departure_time
  lead_speeds = np.array([lead_speed(max(0.0, current_time - DT_MDL)) for current_time in trace.time])
  baseline_moving = np.flatnonzero((baseline.time >= departure_time) & (baseline.speed > 0.05))
  moving = np.flatnonzero(after_departure & (trace.speed > 0.05))

  assert len(baseline_moving) and len(moving)
  assert trace.time[moving[0]] <= baseline.time[baseline_moving[0]]
  assert np.all(trace.speed[after_departure] <= lead_speeds[after_departure] + 0.20)
  assert not _has_brake_coast_brake(trace.a_target[after_departure])
  assert np.min(trace.distance_lead - trace.distance) >= np.min(baseline.distance_lead - baseline.distance) - 1e-3
  assert trace.solver_failures == 0


def test_constant_creep_departure_does_not_pulse_between_launch_and_stop_hold():
  departure_time = 1.0

  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < departure_time else 0.2

  def observe(_current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if lead_name == "leadTwo" else truth | {"aLeadK": 0.0, "radarTrackId": 2133, "radar": True}

  trace = _run(
    duration=8.0, controller_enabled=True, profile=0, lead_relevancy=True, speed=0.0, distance_lead=3.6,
    v_lead=lead_speed, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  launched = np.flatnonzero((trace.time >= departure_time) & trace.launching)
  assert len(launched)
  assert trace.time[launched[0]] <= departure_time + 2.0
  after_launch = slice(launched[0], None)

  assert not np.any(trace.state[after_launch] == int(AccelControllerState.stopHold))
  assert not _has_propulsion_brake_cycle(trace.a_target[after_launch])
  assert np.max(trace.speed[after_launch]) <= 0.4
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_invalid_departure_geometry_aborts_launch_until_reconfirmed():
  def lead_speed(current_time: float) -> float:
    return 0.0 if current_time < 1.0 else 2.0

  def observe(current_time: float, _lead_name: str, truth: LeadObservation) -> LeadObservation:
    return truth | {"vLeadK": -2.0} if 1.45 <= current_time < 1.70 else truth

  trace = _run(
    duration=2.5, controller_enabled=True, lead_relevancy=True, speed=0.0, distance_lead=6.0,
    v_lead=lead_speed, v_cruise=8.0, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  invalid = (trace.time >= 1.50) & (trace.time < 1.75)
  assert invalid.any()
  assert not trace.launching[invalid].any()
  assert np.max(trace.speed[invalid]) < 0.10
  assert np.max(trace.target_speed[invalid]) == 0.0
  assert np.all(np.isfinite(trace.a_target))
  assert trace.solver_failures == 0


def test_moving_full_field_dropout_never_releases_speed_or_adds_solver_failures():
  dropout_start = 2.0
  dropout_end = 2.15

  def observe(current_time: float, _lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    return None if dropout_start <= current_time < dropout_end else truth

  common = dict(
    duration=4.0, lead_relevancy=True, speed=22.0, distance_lead=85.0, v_lead=14.0, v_cruise=30.0,
    lead_observation_fn=observe, actuator_delay=0.20, actuator_lag=0.25,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  before = trace.target_speed[np.flatnonzero(trace.time < dropout_start)[-1]]
  response = (trace.time >= dropout_start) & (trace.time <= dropout_end + 0.5)

  assert np.max(trace.target_speed[response]) <= before + 1e-6
  assert not _has_propulsion_after_braking(trace.a_target[response])
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.min(trace.distance_lead - trace.distance) >= np.min(baseline.distance_lead - baseline.distance) - DROPOUT_GAP_TOLERANCE
  _assert_no_new_solver_failures(trace, baseline)


def test_false_range_relief_matches_clean_controller_response():
  glitch_start = 3.0
  glitch_end = 3.15

  def observe(current_time: float, _lead_name: str, truth: LeadObservation) -> LeadObservation:
    return truth | {"dRel": truth["dRel"] + 5.0} if glitch_start <= current_time < glitch_end else truth

  common = dict(
    duration=4.0, lead_relevancy=True, speed=22.0, distance_lead=85.0, v_lead=14.0,
    v_cruise=30.0, actuator_delay=0.20, actuator_lag=0.25,
  )
  baseline = _run(controller_enabled=False, lead_observation_fn=observe, **common)
  clean = _run(controller_enabled=True, **common)
  trace = _run(controller_enabled=True, lead_observation_fn=observe, **common)
  response = (trace.time >= glitch_start) & (trace.time <= glitch_end + 0.5)
  jerk_response = (trace.time[1:] >= glitch_start) & (trace.time[1:] <= glitch_end + 0.5)

  assert np.max(np.abs(trace.a_target[response] - clean.a_target[response])) < 0.07
  assert np.max(np.abs(np.diff(trace.a_target)[jerk_response] / DT_MDL)) < 3.0
  assert not _has_propulsion_after_braking(trace.a_target[response])
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  _assert_no_new_solver_failures(trace, baseline)


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_route_52f_radar_vision_switch_does_not_release_restricted_pace(actuator_delay, actuator_lag):
  glitch_start = 20.0
  glitch_end = 24.0

  def lead_speed(current_time: float) -> float:
    return 25.0 if current_time < glitch_end else min(33.0, 25.0 + 2.0 * (current_time - glitch_end))

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    if not glitch_start <= current_time < glitch_end:
      return truth | {"radar": True, "radarTrackId": 1119}

    phase = int((current_time - glitch_start) / 0.20)
    if phase % 2 == 0:
      return truth | {"vLeadK": truth["vLeadK"] - 0.3, "vRel": truth["vRel"] - 0.3,
                      "radar": True, "radarTrackId": 1119 if phase % 4 == 0 else 1176}
    distance_offset = (15.0, 30.0, 60.0)[phase % 3]
    return truth | {"dRel": truth["dRel"] + distance_offset, "vLead": truth["vLead"] + 1.0,
                    "vLeadK": truth["vLeadK"] + 1.0, "vRel": truth["vRel"] + 1.0,
                    "radar": False, "radarTrackId": -1}

  common = dict(
    duration=28.0, controller_enabled=True, profile=AccelProfile.eco, lead_relevancy=True, speed=28.0,
    distance_lead=40.0, v_lead=lead_speed, v_cruise=34.72, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  baseline = _run(**common)
  trace = _run(lead_observation_fn=observe, **common)
  before = trace.target_speed[np.flatnonzero(trace.time < glitch_start)[-1]]
  glitch = (trace.time >= glitch_start) & (trace.time < glitch_end)
  response = (trace.time >= glitch_start - 0.5) & (trace.time <= glitch_end + 1.0)
  recovered = (trace.time >= glitch_end + 0.8) & (trace.time <= glitch_end + 2.0)
  gap = trace.distance_lead - trace.distance
  baseline_gap = baseline.distance_lead - baseline.distance
  glitch_sources = {trace.source[index] for index in np.flatnonzero(glitch)}

  assert {LongitudinalPlanSource.cruise, LongitudinalPlanSource.lead0} <= glitch_sources
  assert np.max(trace.target_speed[glitch]) <= before + 0.05
  assert np.max(trace.target_speed[recovered]) > before + 0.1
  assert np.max(np.diff(trace.target_speed)[response[1:]]) <= TARGET_RELEASE_SLEW * DT_MDL + TARGET_SPEED_RESERVE + 1e-9
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert np.min(gap[response]) >= np.min(baseline_gap[response]) - DROPOUT_GAP_TOLERANCE
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_route_533_same_track_relief_has_no_target_snap(actuator_delay, actuator_lag):
  glitch_start = 20.0
  glitch_end = 24.0

  def lead_speed(current_time: float) -> float:
    return 25.0 if current_time < glitch_end else min(33.0, 25.0 + 2.0 * (current_time - glitch_end))

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    observed = truth | {"radar": True, "radarTrackId": 1119}
    if not glitch_start <= current_time < glitch_end:
      return observed
    phase = int((current_time - glitch_start) / 0.20)
    if phase % 2 == 0:
      return observed | {"vLeadK": truth["vLeadK"] - 0.3, "vRel": truth["vRel"] - 0.3}
    return observed | {"dRel": truth["dRel"] + (8.0, 12.0, 18.0)[phase % 3], "vLead": truth["vLead"] + 0.5,
                       "vLeadK": truth["vLeadK"] + 0.5, "vRel": truth["vRel"] + 0.5}

  common = dict(
    duration=28.0, controller_enabled=True, profile=AccelProfile.eco, lead_relevancy=True, speed=28.0,
    distance_lead=40.0, v_lead=lead_speed, v_cruise=34.72, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  clean = _run(**common)
  trace = _run(lead_observation_fn=observe, **common)
  glitch = (trace.time >= glitch_start) & (trace.time < glitch_end)
  response = (trace.time >= glitch_start - 0.5) & (trace.time <= glitch_end + 1.0)
  clean_gap = clean.distance_lead - clean.distance
  gap = trace.distance_lead - trace.distance
  glitch_sources = {trace.source[index] for index in np.flatnonzero(glitch)}

  assert {LongitudinalPlanSource.cruise, LongitudinalPlanSource.lead0} <= glitch_sources
  assert np.max(np.diff(trace.target_speed)[response[1:]]) <= TARGET_RELEASE_SLEW * DT_MDL + TARGET_SPEED_RESERVE + 1e-9
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert float(np.percentile(np.abs(_filtered_realized_jerk(trace)), 95)) <= float(np.percentile(np.abs(_filtered_realized_jerk(clean)), 95)) + 0.02
  assert np.min(gap[response]) >= np.min(clean_gap[response]) - DROPOUT_GAP_TOLERANCE
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, clean)


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_route_532_sustained_switch_churn_has_no_target_snap(actuator_delay, actuator_lag):
  glitch_start = 20.0
  glitch_end = 32.0

  def lead_speed(current_time: float) -> float:
    return 25.0 if current_time < glitch_end else min(33.0, 25.0 + 2.0 * (current_time - glitch_end))

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    if not glitch_start <= current_time < glitch_end:
      return truth | {"radar": True, "radarTrackId": 1119}
    phase = int((current_time - glitch_start) / 0.20)
    if phase % 2 == 0:
      return truth | {"vLeadK": truth["vLeadK"] - 0.3, "vRel": truth["vRel"] - 0.3,
                      "radar": True, "radarTrackId": 1119 if phase % 4 == 0 else 1176}
    return truth | {"dRel": truth["dRel"] + (15.0, 30.0, 60.0)[phase % 3], "vLead": truth["vLead"] + 1.0,
                    "vLeadK": truth["vLeadK"] + 1.0, "vRel": truth["vRel"] + 1.0, "radar": False, "radarTrackId": -1}

  common = dict(
    duration=36.0, profile=AccelProfile.eco, lead_relevancy=True, speed=28.0,
    distance_lead=40.0, v_lead=lead_speed, v_cruise=34.72, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  baseline = _run(controller_enabled=False, lead_observation_fn=observe, **common)
  trace = _run(controller_enabled=True, lead_observation_fn=observe, **common)
  before = trace.target_speed[np.flatnonzero(trace.time < glitch_start)[-1]]
  protected = (trace.time >= glitch_start) & (trace.time < glitch_start + 4.0)
  response = (trace.time >= glitch_start - 0.5) & (trace.time <= glitch_end + 1.0)
  gap = trace.distance_lead - trace.distance

  assert np.max(trace.target_speed[protected]) <= before + 0.05
  assert np.max(np.diff(trace.target_speed)[response[1:]]) <= TARGET_RELEASE_SLEW * DT_MDL + TARGET_SPEED_RESERVE + 1e-9
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert np.min(gap[response]) > STOP_DISTANCE + 10.0
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_sustained_switch_churn_timeout_preserves_braking_safety(monkeypatch, actuator_delay, actuator_lag):
  churn_start = 20.0
  braking_start = 26.0
  churn_end = 32.0

  def lead_speed(current_time: float) -> float:
    progress = np.clip((current_time - braking_start) / 4.0, 0.0, 1.0)
    return float(25.0 - 3.0 * (3.0 * progress**2 - 2.0 * progress**3))

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    observed = truth | {"aLeadK": 0.0}
    if not churn_start <= current_time < churn_end:
      return observed | {"radar": True, "radarTrackId": 1119}
    phase = int((current_time - churn_start) / 0.20)
    if phase % 2 == 0:
      return observed | {"vLeadK": truth["vLeadK"] - 0.3, "vRel": truth["vRel"] - 0.3,
                         "radar": True, "radarTrackId": 1119 if phase % 4 == 0 else 1176}
    return observed | {"dRel": truth["dRel"] + (15.0, 30.0, 60.0)[phase % 3], "vLead": truth["vLead"] + 1.0,
                       "vLeadK": truth["vLeadK"] + 1.0, "vRel": truth["vRel"] + 1.0, "radar": False, "radarTrackId": -1}

  common = dict(
    duration=churn_end, controller_enabled=True, profile=AccelProfile.eco, lead_relevancy=True, speed=28.0,
    distance_lead=50.0, v_lead=lead_speed, v_cruise=34.72, lead_observation_fn=observe,
    actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  with monkeypatch.context() as patch:
    patch.setattr(accel_controller_module, "LEAD_SWITCH_MAX_HOLD_TIME", common["duration"])
    guarded = _run(**common)
  trace = _run(**common)
  after_timeout = (trace.time[1:] >= churn_start + accel_controller_module.LEAD_SWITCH_MAX_HOLD_TIME) & (trace.time[1:] < churn_end)
  planner_braking = trace.planner_seed_accel[1:] <= accel_controller_module.PLANNER_BRAKING_ACCEL_THRESHOLD
  gap = trace.distance_lead - trace.distance
  guarded_gap = guarded.distance_lead - guarded.distance
  lead_speeds = np.asarray([lead_speed(current_time) for current_time in trace.time])
  closing = trace.speed - lead_speeds
  guarded_closing = guarded.speed - lead_speeds
  ttc = np.min(gap[closing > 0.1] / closing[closing > 0.1])
  guarded_ttc = np.min(guarded_gap[guarded_closing > 0.1] / guarded_closing[guarded_closing > 0.1])

  assert np.any(after_timeout & planner_braking)
  assert np.max(np.diff(trace.target_speed)[after_timeout & planner_braking]) <= 1e-9
  for threshold in (-0.5, -1.0):
    timeout = churn_start + accel_controller_module.LEAD_SWITCH_MAX_HOLD_TIME
    assert _first_time_below(trace, threshold, timeout) <= _first_time_below(guarded, threshold, timeout) + 1e-9
  assert np.min(gap) >= np.min(guarded_gap) - 0.02
  assert ttc >= guarded_ttc - 0.02
  assert not trace.fcw.any()
  assert trace.solver_failures == guarded.solver_failures == 0


@pytest.mark.parametrize("profile", range(3), ids=("eco", "normal", "sport"))
@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_route_507_braking_lead_slot_switch_has_no_false_relief_cycle(profile, actuator_delay, actuator_lag):
  glitch_start = 67.0
  glitch_end = 67.5

  def lead_speed(current_time: float) -> float:
    braking_time = np.clip(current_time - 60.0, 0.0, 7.0)
    return 10.0 - 0.42 * braking_time

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if glitch_start <= current_time < glitch_end:
      if lead_name == "leadOne":
        return None
      return truth | {
        "dRel": truth["dRel"] + 20.0,
        "vLead": truth["vLead"] + 4.0,
        "vLeadK": truth["vLeadK"] + 4.0,
        "vRel": truth["vRel"] + 4.0,
        "aLeadK": 0.0,
        "radar": True,
        "radarTrackId": 200,
      }
    if lead_name == "leadTwo":
      return None
    return truth | {"aLeadK": -0.42 if 60.0 <= current_time < glitch_start else 0.0, "radar": True, "radarTrackId": 100}

  common = dict(
    duration=73.0, controller_enabled=True, profile=profile, lead_relevancy=True, speed=20.0,
    distance_lead=100.0, v_lead=lead_speed, v_cruise=30.0, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  clean = _run(**common)
  trace = _run(lead_observation_fn=observe, **common)
  response = (trace.time >= 66.0) & (trace.time <= 72.0)
  jerk_response = (trace.time[1:] >= 66.0) & (trace.time[1:] <= 72.0)
  clean_gap = clean.distance_lead - clean.distance
  gap = trace.distance_lead - trace.distance

  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert np.max(np.abs(np.diff(trace.a_target)[jerk_response] / DT_MDL)) < 3.0
  assert np.max(-np.diff(trace.target_speed)[jerk_response]) <= max(TARGET_SPEED_RESERVE, MATCHED_SPEED_DECEL_RATE * DT_MDL) + 1e-9
  assert np.min(gap[response]) >= np.min(clean_gap[response]) - DROPOUT_GAP_TOLERANCE
  assert not trace.fcw.any()
  assert trace.solver_failures == 0
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)


@pytest.mark.parametrize("profile", range(3), ids=("eco", "normal", "sport"))
def test_profile_ceiling_and_speed_stay_smooth_through_slot_switch_noise(profile):
  glitch_start = 24.0
  glitch_end = 28.0

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if not glitch_start <= current_time < glitch_end:
      return truth if lead_name == "leadOne" else None

    selected_slot = "leadOne" if round(current_time / DT_MDL) % 2 == 0 else "leadTwo"
    if lead_name != selected_slot:
      return None
    sign = 1.0 if lead_name == "leadOne" else -1.0
    speed_offset = 0.25 * sign
    return truth | {
      "dRel": max(0.0, truth["dRel"] + 1.5 * sign),
      "vLead": max(0.0, truth["vLead"] + speed_offset),
      "vLeadK": max(0.0, truth["vLeadK"] + speed_offset),
      "vRel": truth["vRel"] + speed_offset,
      "aLeadK": 0.0,
      "radar": True,
      "radarTrackId": 100 if lead_name == "leadOne" else 200,
    }

  common = dict(
    duration=32.0, controller_enabled=True, profile=profile, lead_relevancy=True, speed=20.0,
    distance_lead=100.0, v_lead=10.0, v_cruise=30.0, actuator_delay=0.15, actuator_lag=0.25,
  )
  baseline = _run(**common)
  trace = _run(lead_observation_fn=observe, **common)
  glitch = (trace.time >= glitch_start) & (trace.time < glitch_end)
  response = (trace.time >= glitch_start - 0.5) & (trace.time <= glitch_end + 1.0)
  applied_accel_max = trace.mpc_upper_min[response]
  selected_leads = trace.selected_lead[glitch]
  controller_limited = trace.accel_ceiling_active[response]
  stock_accel_max = np.asarray([get_max_accel(speed) for speed in trace.speed[response]])

  assert set(selected_leads) == {0, 1}
  assert np.count_nonzero(np.diff(selected_leads)) > 20
  assert controller_limited.any()
  assert np.all(applied_accel_max[controller_limited] <= trace.profile_accel_max[response][controller_limited] + 1e-6)
  assert np.all(applied_accel_max[controller_limited] <= stock_accel_max[controller_limited] + 1e-6)
  assert np.max(trace.a_target[response]) > 0.2
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert trace.raw_radar_passthrough.all()
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)


@pytest.mark.parametrize("profile", range(3), ids=("eco", "normal", "sport"))
def test_matched_lead_dropout_keeps_the_profile_acceleration_ceiling(profile):
  dropout_start = 25.0
  dropout_end = 25.15

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo" or dropout_start <= current_time < dropout_end:
      return None
    return truth

  common = dict(
    duration=28.0, controller_enabled=True, profile=profile, lead_relevancy=True, speed=20.0,
    distance_lead=100.0, v_lead=10.0, v_cruise=30.0, actuator_delay=0.15, actuator_lag=0.25,
  )
  clean = _run(**common)
  trace = _run(lead_observation_fn=observe, **common)
  dropout = (trace.time >= dropout_start) & (trace.time <= dropout_end)
  response = (trace.time >= dropout_start - 0.5) & (trace.time <= dropout_end + 0.75)

  assert trace.accel_ceiling_active[dropout].all()
  assert np.max(np.abs(trace.a_target[response] - clean.a_target[response])) < 0.08
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, clean)


def test_low_speed_lead_stop_has_no_release_then_rebrake():
  def lead_speed(current_time: float) -> float:
    return max(0.0, 1.9 - 1.16 * current_time)

  def observe(current_time: float, lead_name: str, truth: LeadObservation) -> LeadObservation | None:
    if lead_name == "leadTwo":
      return None
    moving = lead_speed(current_time) > 0.0
    return truth | {"vLeadK": truth["vLeadK"] if moving else -0.01, "aLeadK": -1.16 if moving else 0.0,
                    "radarTrackId": 7, "radar": True}

  common = dict(
    duration=6.0, profile=0, lead_relevancy=True, speed=4.5, distance_lead=18.0, v_lead=lead_speed,
    v_cruise=23.056, lead_observation_fn=observe, actuator_delay=0.15, actuator_lag=0.20,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  stop_hold = trace.state == int(AccelControllerState.stopHold)
  stopped_response = trace.time >= trace.time[np.flatnonzero(trace.speed < 1e-3)[0]]

  assert stop_hold.any()
  assert np.max(trace.speed[stopped_response]) <= np.max(baseline.speed[stopped_response]) + 0.01
  assert np.max(trace.a_target[stopped_response]) <= np.max(baseline.a_target[stopped_response]) + 0.05
  assert not _has_brake_coast_brake(trace.a_target[trace.time >= 1.0])
  assert np.min(trace.a_target) >= np.min(baseline.a_target) - ROUTINE_GAP_TOLERANCE
  assert np.min(trace.distance_lead - trace.distance) >= np.min(baseline.distance_lead - baseline.distance) - ROUTINE_GAP_TOLERANCE
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_high_speed_stopped_lead_approach_holds_the_completed_stop(actuator_delay, actuator_lag):
  trace = _run(
    duration=14.0, controller_enabled=True, profile=1, lead_relevancy=True, speed=20.0,
    distance_lead=130.0, v_lead=0.0, v_cruise=30.0, actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  stopped = np.flatnonzero(trace.speed < 0.05)
  assert len(stopped)
  after_stop = slice(stopped[0], None)
  gap = trace.distance_lead - trace.distance

  assert STOP_DISTANCE <= np.min(gap[after_stop]) <= 25.0
  assert np.max(trace.speed[after_stop]) < 0.10
  assert not _has_propulsion_brake_cycle(trace.a_target[after_stop])
  assert trace.state[-1] == int(AccelControllerState.stopHold)
  assert trace.raw_radar_passthrough.all()
  assert np.all(trace.mpc_calls == 1)
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_decelerating_moving_lead_is_stock_safe_without_propulsion_reversal():
  def lead_speed(current_time: float) -> float:
    if current_time < 2.0:
      return 15.0
    progress = min((current_time - 2.0) / 6.0, 1.0)
    return 15.0 - 5.0 * (3.0 * progress**2 - 2.0 * progress**3)

  common = dict(
    duration=14.0, profile=1, lead_relevancy=True, speed=20.0, distance_lead=110.0,
    v_lead=lead_speed, v_cruise=30.0, actuator_delay=0.20, actuator_lag=0.25,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  response = trace.time >= 1.0
  baseline_p95 = float(np.percentile(np.abs(_filtered_realized_jerk(baseline)), 95))
  trace_p95 = float(np.percentile(np.abs(_filtered_realized_jerk(trace)), 95))

  assert not _has_brake_coast_brake(trace.a_target[response])
  assert not _has_propulsion_after_braking(trace.a_target[response])
  assert trace_p95 <= baseline_p95 + 0.02
  assert np.min(trace.acceleration) >= np.min(baseline.acceleration) - ROUTINE_DECEL_TOLERANCE
  assert np.min(trace.distance_lead - trace.distance) >= np.min(baseline.distance_lead - baseline.distance) - MOVING_LEAD_GAP_TOLERANCE
  assert not trace.fcw.any()
  _assert_no_new_solver_failures(trace, baseline)


def test_severe_closing_never_delays_stock_braking_or_reduces_clearance():
  common = dict(
    duration=12.0, lead_relevancy=True, speed=20.0, distance_lead=160.0, v_lead=3.5,
    actuator_delay=0.20, actuator_lag=0.20,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  for threshold in (-1.0, -2.0):
    assert _first_time_below(trace, threshold) <= _first_time_below(baseline, threshold) + 1e-9

  baseline_gap = baseline.distance_lead - baseline.distance
  controlled_gap = trace.distance_lead - trace.distance
  baseline_closing = baseline.speed - 3.5
  controlled_closing = trace.speed - 3.5
  baseline_ttc = np.min(baseline_gap[baseline_closing > 0.1] / baseline_closing[baseline_closing > 0.1])
  controlled_ttc = np.min(controlled_gap[controlled_closing > 0.1] / controlled_closing[controlled_closing > 0.1])
  onset = (trace.time[1:] > 0.5) & (trace.time[1:] < 3.0)

  assert np.min(controlled_gap) >= np.min(baseline_gap) - 0.02
  assert controlled_ttc >= baseline_ttc - 0.02
  assert np.min(controlled_gap) > 0.0
  assert np.max(np.abs(np.diff(trace.a_target)[onset] / DT_MDL)) < 4.0
  assert trace.solver_failures == 0


@pytest.mark.parametrize(("actuator_delay", "actuator_lag"), ACTUATOR_DYNAMICS, ids=ACTUATOR_IDS)
def test_far_lead_profiles_start_early_in_order_without_solver_failures(actuator_delay, actuator_lag):
  common = dict(
    duration=11.0, lead_relevancy=True, speed=25.0, distance_lead=200.0, v_lead=15.0,
    actuator_delay=actuator_delay, actuator_lag=actuator_lag,
  )
  baseline = _run(controller_enabled=False, **common)
  traces = [_run(controller_enabled=True, profile=profile, **common) for profile in range(3)]
  baseline_onset = _sustained_time_below(baseline, -0.10)
  baseline_jerk_p95 = float(np.percentile(np.abs(_filtered_realized_jerk(baseline)), 95))
  required_improvement = max(0.002, 0.02 * baseline_jerk_p95)
  onsets = [_sustained_time_below(trace, -0.10) for trace in traces]

  assert onsets[0] <= baseline_onset - 0.5 + 1e-9
  assert onsets[1] <= baseline_onset + 1e-9
  assert onsets[2] <= baseline_onset + 1e-9
  assert onsets[0] <= onsets[1] + DT_MDL + 1e-9
  assert onsets[1] <= onsets[2] + DT_MDL + 1e-9
  first_finite_caps = [trace.raw_cap[np.flatnonzero(np.isfinite(trace.raw_cap))[0]] for trace in traces]
  assert first_finite_caps[0] < first_finite_caps[1] < first_finite_caps[2]
  for trace in traces:
    assert trace.acceleration.min() >= baseline.acceleration.min() - 0.1
    assert float(np.percentile(np.abs(_filtered_realized_jerk(trace)), 95)) <= baseline_jerk_p95 - required_improvement
    assert np.max(np.abs(_command_jerk(trace, after=0.5))) < 1.0
    assert not _has_brake_coast_brake(trace.a_target[trace.time >= 1.0])
    assert not _has_propulsion_brake_cycle(trace.a_target[trace.time >= 1.0])
    assert not trace.fcw.any()
    assert trace.solver_failures == 0


def test_steady_slow_lead_has_no_gas_brake_cycle():
  duration = 60.0
  lead_speed = 10.0
  common = dict(
    duration=duration, lead_relevancy=True, speed=20.0, distance_lead=100.0, v_lead=lead_speed,
    v_cruise=30.0, actuator_delay=0.15, actuator_lag=0.25,
  )
  baseline = _run(controller_enabled=False, **common)
  trace = _run(controller_enabled=True, **common)
  response = trace.time >= 1.0
  settled = trace.time >= duration - 5.0
  desired_gap = STOP_DISTANCE + get_T_FOLLOW() * lead_speed
  baseline_gap = baseline.distance_lead - baseline.distance
  gap = trace.distance_lead - trace.distance
  max_settled_gap = max(np.mean(baseline_gap[settled]) + 10.0, desired_gap + 30.0)

  assert np.mean(trace.speed[settled]) >= lead_speed - 2.0
  assert np.mean(gap[settled]) <= max_settled_gap
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.min(gap) >= desired_gap - 1.6
  assert np.min(trace.a_target) >= np.min(baseline.a_target) - ROUTINE_GAP_TOLERANCE
  _assert_no_new_solver_failures(trace, baseline)


def test_matched_lead_slowdown_stays_smooth_without_a_second_braking_stage():
  slowdown_time = 70.0
  settled_lead_speed = 7.0

  def lead_speed(current_time: float) -> float:
    return 10.0 if current_time < slowdown_time else max(settled_lead_speed, 10.0 - 0.5 * (current_time - slowdown_time))

  trace = _run(
    duration=100.0, controller_enabled=True, profile=1, lead_relevancy=True, speed=20.0,
    distance_lead=100.0, v_lead=lead_speed, v_cruise=30.0, actuator_delay=0.15, actuator_lag=0.25,
  )
  matched = (trace.time >= slowdown_time - 5.0) & (trace.time < slowdown_time)
  response = trace.time >= slowdown_time
  settled = trace.time >= 95.0
  gap = trace.distance_lead - trace.distance
  desired_gap = STOP_DISTANCE + get_T_FOLLOW() * settled_lead_speed

  assert abs(np.mean(trace.speed[matched]) - 10.0) < 0.5
  assert trace.accel_ceiling_active[matched].all()
  np.testing.assert_allclose(trace.mpc_upper_min[matched], trace.profile_accel_max[matched], atol=1e-6)
  assert not np.any(trace.state[response] == int(AccelControllerState.stopHold))
  assert not trace.launching[response].any()
  assert not _has_brake_coast_brake(trace.a_target[response])
  assert not _has_propulsion_brake_cycle(trace.a_target[response])
  assert np.max(np.abs(_command_jerk(trace)[response[1:]])) < 3.0
  assert float(np.percentile(np.abs(_filtered_realized_jerk(trace, after=slowdown_time)), 95)) < 0.30
  assert np.min(gap) > STOP_DISTANCE
  assert np.mean(trace.speed[settled]) >= settled_lead_speed - 1.5
  assert np.mean(gap[settled]) <= desired_gap + 20.0
  assert not trace.fcw.any()
  assert trace.solver_failures == 0


def test_acceleration_output_remains_inside_stock_limits():
  trace = _run(
    duration=12.0, controller_enabled=True, profile=AccelProfile.sport, lead_relevancy=False,
    speed=0.0, v_cruise=30.0, actuator_delay=0.15, actuator_lag=0.20,
  )
  stock_max = np.asarray([get_max_accel(speed) for speed in trace.speed])
  assert np.all(trace.a_target >= ACCEL_MIN - 1e-9)
  assert np.all(trace.a_target <= stock_max + 0.06)
  assert trace.stock_bounds_valid.all()
  assert trace.solver_failures == 0
