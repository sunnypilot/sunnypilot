"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections.abc import Callable

import numpy as np

from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.drive_helpers import should_stop
from openpilot.selfdrive.controls.lib.longitudinal_planner import A_CRUISE_MAX_BP, J_CRUISE_VALS, get_cruise_accel
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalPlanSource, T_IDXS as T_IDXS_MPC
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import (
  AccelController, AccelProfile, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES,
)
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PRIUS_TSS2_ROUTE_MODEL, PlantSP


class CarParams:
  steerRatio = 15.0
  wheelbase = 2.7


def _set_mpc_acceleration(plant: PlantSP, acceleration: float = 2.0) -> None:
  def update(_radar_state, **_kwargs):
    mpc = plant.planner.mpc
    mpc.source = LongitudinalPlanSource.lead0
    mpc.v_solution[:] = mpc.x0[1] + acceleration * T_IDXS_MPC
    mpc.a_solution.fill(acceleration)
    mpc.j_solution.fill(0.0)

  plant.planner.mpc.update = update


def run_profile(profile: int, *, enabled: bool = True, speed: float = 0.0, v_cruise: float = 30.0,
                v_cruise_fn: Callable[[int], float] | None = None, e2e: bool = False, steps: int = 120,
                speed_noise: float = 0.0, seed: int = 0):
  params = Params()
  params.put_bool("AccelPersonalityEnabled", enabled, block=True)
  params.put("AccelPersonality", profile, block=True)
  controller = AccelController()
  rng = np.random.default_rng(seed)

  accel = 0.0
  rows = []
  for frame in range(steps):
    target_speed = v_cruise if v_cruise_fn is None else v_cruise_fn(frame)
    measured = speed + (float(rng.normal(0.0, speed_noise)) if speed_noise else 0.0)
    accel = get_cruise_accel(e2e, target_speed, measured, accel, 0.0, CarParams(), DT_MDL, 2.0, True)
    accel = controller.limit_accel(accel, measured)
    speed = max(0.0, speed + accel * DT_MDL)
    rows.append((speed, accel, should_stop(speed, accel)))
  return rows


def run_vehicle_profile(profile: int, duration: float = 80.0, enabled: bool = True, speed: float = 0.0,
                        v_cruise_fn: Callable[[float], float] | None = None):
  params = Params()
  params.put_bool("AccelPersonalityEnabled", enabled, block=True)
  params.put("AccelPersonality", profile, block=True)

  plant = PlantSP(speed=speed, actuator_model=PRIUS_TSS2_ROUTE_MODEL, run_long_control=True)
  _set_mpc_acceleration(plant)
  rows = []
  while plant.current_time < duration:
    v_cruise = 25.0 if v_cruise_fn is None else v_cruise_fn(plant.current_time)
    result = plant.step(v_cruise=v_cruise)
    rows.append((plant.current_time, result["speed"], result["a_target"], result["actuator_command"], result["acceleration"]))
  return np.asarray(rows)


class TestAccelControllerClosedLoop(OpenpilotTestCase):
  def test_profiles_are_immediate_smooth_and_clearly_distinct(self):
    traces = {profile: run_vehicle_profile(profile) for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)}
    stock = run_vehicle_profile(AccelProfile.normal, enabled=False)

    def crossing(trace, speed):
      return float(trace[np.flatnonzero(trace[:, 1] >= speed)[0], 0])

    time_to_20 = {profile: crossing(trace, 20.0 * CV.MPH_TO_MS) for profile, trace in traces.items()}
    time_to_50 = {profile: crossing(trace, 50.0 * CV.MPH_TO_MS) for profile, trace in traces.items()}
    first_motion = {profile: int(np.flatnonzero(trace[:, 1] > 0.01)[0]) for profile, trace in traces.items()}

    self.assertEqual(len(set(first_motion.values())), 1)
    self.assertTrue(all(trace[0, 2] > 0.0 and trace[1, 3] > 0.0 for trace in traces.values()))
    self.assertLess(time_to_20[AccelProfile.eco], 8.0)
    self.assertLess(time_to_50[AccelProfile.eco], 27.0)
    self.assertGreaterEqual(time_to_20[AccelProfile.eco] - time_to_20[AccelProfile.normal], 0.5)
    self.assertGreaterEqual(time_to_20[AccelProfile.normal] - time_to_20[AccelProfile.sport], 0.5)
    self.assertGreaterEqual(time_to_50[AccelProfile.eco] - time_to_50[AccelProfile.normal], 2.0)
    self.assertGreaterEqual(time_to_50[AccelProfile.normal] - time_to_50[AccelProfile.sport], 3.0)

    stock_peak_jerk = float(np.max(np.abs(np.diff(stock[:, 3])) / DT_MDL))
    for profile, trace in traces.items():
      command_jerk = np.abs(np.diff(trace[:, 3])) / DT_MDL
      self.assertLessEqual(float(np.max(command_jerk)), stock_peak_jerk + 1e-9, profile)

      settled = np.flatnonzero(trace[:, 1] >= 25.0 - 0.15)
      self.assertGreater(len(settled), 0)
      settled_trace = trace[settled[0]:]
      self.assertGreaterEqual(float(np.min(settled_trace[:, 3])), -0.05)
      self.assertLessEqual(float(np.max(trace[:, 1])), 25.0 + 1e-9)

  def test_blended_positive_model_request_uses_profile_cruise_cap(self):
    params = Params()
    params.put_bool("DynamicExperimentalControl", False, block=True)
    params.put_bool("AccelPersonalityEnabled", True, block=True)
    params.put("AccelPersonality", AccelProfile.eco, block=True)

    def request_acceleration(_current_time: float, _speed: float, _acceleration: float) -> tuple[float, bool]:
      return 2.0, False

    plant = PlantSP(speed=15.0, e2e=True, model_action_fn=request_acceleration)
    _set_mpc_acceleration(plant)
    results = [plant.step(v_cruise=35.0) for _ in range(20)]
    settled = results[-1]
    eco_limit = float(np.interp(settled["published_v_ego"], MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.eco]))

    self.assertTrue(settled["controller_active"])
    self.assertEqual(settled["mpc_source"], LongitudinalPlanSource.cruise)
    self.assertAlmostEqual(settled["a_target"], eco_limit, delta=0.01)
    self.assertLess(settled["a_target"], settled["model_action"]["desiredAcceleration"])

  def test_normal_launch_is_faster_than_eco(self):
    eco = run_profile(AccelProfile.eco, speed=4.0, steps=120)
    normal = run_profile(AccelProfile.normal, speed=4.0, steps=120)
    self.assertGreater(normal[-1][0], eco[-1][0])

  def test_zero_speed_stop_request_is_unchanged(self):
    for e2e in (False, True):
      stock = run_profile(AccelProfile.normal, enabled=False, speed=20.0, v_cruise=0.0, e2e=e2e, steps=100)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
        self.assertEqual(run_profile(profile, speed=20.0, v_cruise=0.0, e2e=e2e, steps=100), stock)

  def test_cruise_decel_remains_stock_for_all_profiles(self):
    target = 25.0 - 5.0 * CV.MPH_TO_MS
    stock = np.asarray(run_profile(AccelProfile.normal, enabled=False, speed=25.0, v_cruise=target, steps=300))

    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      trace = np.asarray(run_profile(profile, speed=25.0, v_cruise=target, steps=300))
      np.testing.assert_array_equal(trace, stock)

  def test_cruise_decel_stays_stock_through_actuator(self):
    target = 25.0 - 5.0 * CV.MPH_TO_MS

    def cruise_target(current_time: float) -> float:
      return 25.0 if current_time < 2.0 else target

    stock = run_vehicle_profile(AccelProfile.normal, duration=12.0, enabled=False, speed=25.0, v_cruise_fn=cruise_target)
    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      trace = run_vehicle_profile(profile, duration=12.0, speed=25.0, v_cruise_fn=cruise_target)
      np.testing.assert_array_equal(trace, stock)

  def test_blended_launch_respects_profiles(self):
    traces = {
      profile: run_profile(profile, v_cruise=8.0, e2e=True, steps=180)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    time_to_five = {
      profile: next(frame for frame, row in enumerate(rows) if row[0] >= 5.0) * DT_MDL
      for profile, rows in traces.items()
    }

    self.assertLess(time_to_five[AccelProfile.sport], time_to_five[AccelProfile.normal])
    self.assertLess(time_to_five[AccelProfile.normal], time_to_five[AccelProfile.eco])

  def test_launch_ordering_without_departure_delay(self):
    stock = run_profile(AccelProfile.normal, enabled=False, v_cruise=8.0, steps=160)
    traces = {
      profile: run_profile(profile, v_cruise=8.0, steps=160)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    first_motion = {
      profile: next(frame for frame, row in enumerate(rows) if row[0] > 0.01)
      for profile, rows in traces.items()
    }
    time_to_five = {
      profile: next(frame for frame, row in enumerate(rows) if row[0] >= 5.0) * DT_MDL
      for profile, rows in traces.items()
    }
    stock_first_motion = next(frame for frame, row in enumerate(stock) if row[0] > 0.01)

    self.assertEqual(len(set(first_motion.values())), 1)
    self.assertTrue(all(frame == stock_first_motion for frame in first_motion.values()))
    self.assertGreaterEqual(time_to_five[AccelProfile.eco] - time_to_five[AccelProfile.normal], 0.1)
    self.assertGreaterEqual(time_to_five[AccelProfile.normal] - time_to_five[AccelProfile.sport], 0.1)

  def test_road_speed_catchup_stays_useful(self):
    traces = {
      profile: run_profile(profile, speed=20.0, v_cruise=30.0, steps=100)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    gains = {profile: rows[-1][0] - 20.0 for profile, rows in traces.items()}
    self.assertGreater(gains[AccelProfile.normal] - gains[AccelProfile.eco], 0.05)
    self.assertGreater(gains[AccelProfile.sport] - gains[AccelProfile.normal], 0.1)

  def test_full_catchup_trace_respects_stock_jerk(self):
    for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport):
      rows = run_profile(profile, v_cruise=30.0, steps=300)
      previous_speed = 0.0
      previous_accel = 0.0
      for speed, accel, _should_stop in rows:
        jerk_step = float(np.interp(previous_speed, A_CRUISE_MAX_BP, J_CRUISE_VALS)) * DT_MDL
        self.assertLessEqual(abs(accel - previous_accel), jerk_step + 1e-12)
        previous_speed = speed
        previous_accel = accel

  def test_stop_release_frame_is_profile_independent(self):
    def target_speed(frame: int) -> float:
      return 0.0 if frame < 20 else 8.0

    traces = {
      profile: run_profile(profile, v_cruise_fn=target_speed, steps=80)
      for profile in (AccelProfile.eco, AccelProfile.normal, AccelProfile.sport)
    }
    release_frames = {
      profile: next(frame for frame, row in enumerate(rows) if frame >= 20 and not row[2])
      for profile, rows in traces.items()
    }
    stock = run_profile(AccelProfile.normal, enabled=False, v_cruise_fn=target_speed, steps=80)
    stock_release_frame = next(frame for frame, row in enumerate(stock) if frame >= 20 and not row[2])
    self.assertEqual(len(set(release_frames.values())), 1)
    self.assertTrue(all(frame == stock_release_frame for frame in release_frames.values()))
