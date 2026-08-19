"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from contextlib import ExitStack
from types import SimpleNamespace
from unittest import mock

import numpy as np

from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller import mpc_comfort_controller as comfort
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelProfile
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.mpc_comfort_controller import MpcComfortController
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, MpcPlanSource
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PlantSP, PRIUS_TSS2_ROUTE_MODEL


class TestMpcComfortController(OpenpilotTestCase):
  def setUp(self):
    self.controller = MpcComfortController()
    self.times = np.array([0.0, 0.5, 2.5])
    self.risk_horizon = np.array([0.0, -0.5, -2.0])
    self.a_min = -1.0

  def activate(self, a_target: float = 0.0) -> float:
    self.assertEqual(self.controller.update(a_target, self.risk_horizon, self.times, True, self.a_min), a_target)
    return self.controller.update(a_target, self.risk_horizon, self.times, True, self.a_min)

  def test_preview_brake_jerk_and_profile_limit(self):
    output = self.activate()
    self.assertAlmostEqual(output, -comfort._BRAKE_JERK * DT_MDL)

    outputs = [output]
    while outputs[-1] > self.a_min:
      outputs.append(self.controller.update(0.0, self.risk_horizon, self.times, True, self.a_min))

    brake_step = comfort._BRAKE_JERK * DT_MDL
    assert all(next_a - a >= -brake_step - 1e-9 for a, next_a in zip(outputs, outputs[1:], strict=False))
    self.assertEqual(outputs[-1], self.a_min)
    assert self.controller.active

  def test_falling_raw_target_blocks_activation(self):
    self.assertEqual(self.controller.update(0.0, self.risk_horizon, self.times, True, self.a_min), 0.0)
    raw_target = -(comfort._ACTIVATION_JERK + 0.1) * DT_MDL
    self.assertEqual(self.controller.update(raw_target, self.risk_horizon, self.times, True, self.a_min), raw_target)
    assert not self.controller.active

    self.assertEqual(self.controller.update(raw_target, self.risk_horizon, self.times, True, self.a_min), raw_target)
    self.assertLess(self.controller.update(raw_target, self.risk_horizon, self.times, True, self.a_min), raw_target)

  def test_raw_emergency_wins_and_clears_state(self):
    self.activate()
    self.assertEqual(self.controller.update(-3.5, self.risk_horizon, self.times, True, self.a_min), -3.5)
    assert not self.controller.active
    self.assertEqual(self.controller.update(0.2, np.zeros(3), self.times, True, self.a_min), 0.2)

  def test_transient_preview_does_not_activate(self):
    for horizon in (self.risk_horizon, np.zeros(3)) * 4:
      self.assertEqual(self.controller.update(0.0, horizon, self.times, True, self.a_min), 0.0)
      assert not self.controller.active

  def test_lead_dropout_holds_then_releases_at_bounded_jerk(self):
    self.activate()
    for _ in range(20):
      self.controller.update(0.0, self.risk_horizon, self.times, True, self.a_min)

    start = self.controller.update(0.0, np.zeros(3), self.times, False, self.a_min)
    hold_frames = round(comfort._LEAD_LOSS_HOLD_TIME / DT_MDL)
    held = [start]
    for _ in range(hold_frames - 1):
      held.append(self.controller.update(0.0, np.zeros(3), self.times, False, self.a_min))
    assert all(a == start for a in held)

    released = [held[-1]]
    while self.controller.active:
      released.append(self.controller.update(0.0, np.zeros(3), self.times, False, self.a_min))
    release_step = comfort._RELEASE_JERK * DT_MDL
    assert all(0.0 <= next_a - a <= release_step + 1e-9 for a, next_a in zip(released, released[1:], strict=False))
    self.assertEqual(released[-1], 0.0)

  def test_active_preview_releases_at_bounded_jerk(self):
    self.activate()
    for _ in range(20):
      self.controller.update(0.5, self.risk_horizon, self.times, True, self.a_min)

    milder_horizon = np.array([0.0, -0.2, -0.2])
    previous = self.controller.update(0.5, self.risk_horizon, self.times, True, self.a_min)
    for _ in range(round(comfort._LEAD_LOSS_HOLD_TIME / DT_MDL)):
      self.assertEqual(self.controller.update(0.5, milder_horizon, self.times, True, self.a_min), previous)
    output = self.controller.update(0.5, milder_horizon, self.times, True, self.a_min)
    self.assertAlmostEqual(output - previous, comfort._RELEASE_JERK * DT_MDL)

  def test_alternating_preview_does_not_reverse_jerk(self):
    self.activate(0.5)
    outputs = []
    for frame in range(20):
      horizon = self.risk_horizon if frame % 2 == 0 else np.zeros(3)
      outputs.append(self.controller.update(0.5, horizon, self.times, True, self.a_min))

    assert np.all(np.diff(outputs) <= 1e-9)

  def test_reset_and_invalid_horizon_return_raw(self):
    self.activate()
    self.assertEqual(self.controller.update(0.4, self.risk_horizon, self.times, True, self.a_min, reset=True), 0.4)
    self.assertEqual(self.controller.update(0.2, np.array([0.0, np.nan, np.inf]), self.times, True, self.a_min), 0.2)
    assert not self.controller.active

  def test_current_state_anchor_is_excluded(self):
    horizon = np.array([-2.0, 0.0, 0.0])
    self.assertEqual(self.controller.update(0.0, horizon, self.times, True, self.a_min), 0.0)
    self.assertEqual(self.controller.update(0.0, horizon, self.times, True, self.a_min), 0.0)
    assert not self.controller.active

  def test_output_never_weakens_raw_target(self):
    for a_target, horizon in ((0.2, self.risk_horizon), (-0.2, np.zeros(3)), (-3.5, self.risk_horizon)):
      self.assertLessEqual(self.controller.update(a_target, horizon, self.times, True, self.a_min), a_target)


class TestInheritedMpcComfortHook(OpenpilotTestCase):
  def setUp(self):
    self.planner = object.__new__(LongitudinalPlannerSP)
    self.planner.mpc_comfort_controller = MpcComfortController()
    self.planner.mpc = SimpleNamespace(source=MpcPlanSource.lead1)
    self.times = np.array([0.0, 0.5, 2.5])
    self.horizon = np.array([0.0, -0.5, -2.0])
    self.a_min = -1.0

  @staticmethod
  def make_sm(v_ego: float = 10.0):
    return {
      'radarState': SimpleNamespace(leadOne=SimpleNamespace(present=False), leadTwo=SimpleNamespace(present=True)),
      'carControl': SimpleNamespace(cruiseControl=SimpleNamespace(override=False)),
      'carState': SimpleNamespace(standstill=False, vEgo=v_ego),
    }

  def test_lead_two_uses_inherited_hook(self):
    sm = self.make_sm()
    self.assertEqual(self.planner.update_mpc_comfort(sm, 0.0, self.horizon, self.times, False, self.a_min), 0.0)
    self.assertLess(self.planner.update_mpc_comfort(sm, 0.0, self.horizon, self.times, False, self.a_min), 0.0)

  def test_non_lead_source_is_ignored(self):
    self.planner.mpc.source = MpcPlanSource.cruise
    for _ in range(3):
      self.assertEqual(self.planner.update_mpc_comfort(self.make_sm(), 0.0, self.horizon, self.times, False, self.a_min), 0.0)
    assert not self.planner.mpc_comfort_controller.active

  def test_disabled_controller_is_exact_stock(self):
    self.planner.mpc_comfort_controller.update(0.0, self.horizon, self.times, True, self.a_min)
    self.planner.mpc_comfort_controller.update(0.0, self.horizon, self.times, True, self.a_min)

    self.assertEqual(self.planner.update_mpc_comfort(self.make_sm(), 0.2, self.horizon, self.times, False, None), 0.2)
    assert not self.planner.mpc_comfort_controller.active

  def test_stop_region_remains_raw(self):
    self.assertEqual(self.planner.update_mpc_comfort(self.make_sm(0.29), 0.2, self.horizon, self.times, False, self.a_min), 0.2)
    assert not self.planner.mpc_comfort_controller.active

    sm = self.make_sm(0.3)
    self.assertEqual(self.planner.update_mpc_comfort(sm, 0.2, self.horizon, self.times, False, self.a_min), 0.2)
    self.assertLess(self.planner.update_mpc_comfort(sm, 0.2, self.horizon, self.times, False, self.a_min), 0.2)


def _run_closed_loop(comfort_enabled, speed, gap, cruise, duration, lead_speed):
  plant = PlantSP(lead_relevancy=True, speed=speed, distance_lead=gap, actuator_model=PRIUS_TSS2_ROUTE_MODEL, run_long_control=True)
  plant.v_lead_prev = lead_speed(0.0)
  planner = plant.planner
  planner.accel_controller._enabled = True
  planner.accel_controller._profile = AccelProfile.eco
  planner.dec._enabled = False
  solver_failures = 0

  with ExitStack() as patches:
    patches.enter_context(mock.patch.object(planner.accel_controller, "update", return_value=None))
    patches.enter_context(mock.patch.object(planner.dec, "_read_params", return_value=None))

    if not comfort_enabled:

      def bypass_comfort(_sm, a_target, *_args):
        planner.mpc_comfort_controller.reset()
        return a_target

      patches.enter_context(mock.patch.object(planner, "update_mpc_comfort", side_effect=bypass_comfort))

    original_reset = planner.mpc.reset

    def count_reset(*args, **kwargs):
      nonlocal solver_failures
      solver_failures += int(planner.mpc.solution_status != 0)
      return original_reset(*args, **kwargs)

    patches.enter_context(mock.patch.object(planner.mpc, "reset", side_effect=count_reset))
    rows = []
    for _ in range(round(duration / DT_MDL)):
      current_time = plant.current_time
      v_lead = lead_speed(current_time)
      result = plant.step(v_lead=v_lead, v_cruise=cruise)
      current_gap = result["distance_lead"] - result["distance"]
      closing_speed = max(result["speed"] - v_lead, 0.0)
      rows.append(
        (
          current_time,
          result["a_target"],
          result["actuator_command"],
          result["realized_acceleration"],
          result["speed"],
          current_gap,
          current_gap / closing_speed if closing_speed > 0.01 else np.inf,
          planner.mpc_comfort_controller.active,
          result["fcw"],
        )
      )

  data = np.asarray(rows, dtype=float)
  return {
    "time": data[:, 0],
    "target": data[:, 1],
    "command": data[:, 2],
    "accel": data[:, 3],
    "speed": data[:, 4],
    "gap": data[:, 5],
    "ttc": data[:, 6],
    "active": data[:, 7].astype(bool),
    "fcw": data[:, 8].astype(bool),
    "solver_failures": solver_failures,
  }


def _sustained_onset(times, values, threshold=-0.2):
  for frame in range(len(values) - 1):
    if values[frame] <= threshold and values[frame + 1] <= threshold:
      return times[frame]
  return None


def _command_switches(command, deadband=0.05):
  states = np.where(command < -deadband, -1, np.where(command > deadband, 1, 0))
  states = states[states != 0]
  return int(np.count_nonzero(states[1:] != states[:-1]))


class TestMpcComfortClosedLoop(OpenpilotTestCase):
  def test_closing_lead_brakes_earlier_and_more_smoothly(self):
    def lead_speed(t):
      return 10.0 - 1.5 * np.clip(t - 0.75, 0.0, 3.0)

    stock = _run_closed_loop(False, 12.0, 45.0, 20.0, 7.0, lead_speed)
    enabled = _run_closed_loop(True, 12.0, 45.0, 20.0, 7.0, lead_speed)

    assert stock["solver_failures"] == enabled["solver_failures"] == 0
    assert not stock["fcw"].any() and not enabled["fcw"].any()
    assert enabled["active"].any()

    stock_target_onset = _sustained_onset(stock["time"], stock["target"])
    enabled_target_onset = _sustained_onset(enabled["time"], enabled["target"])
    stock_accel_onset = _sustained_onset(stock["time"], stock["accel"])
    enabled_accel_onset = _sustained_onset(enabled["time"], enabled["accel"])
    assert None not in (stock_target_onset, enabled_target_onset, stock_accel_onset, enabled_accel_onset)
    assert enabled_target_onset <= stock_target_onset - 1.5
    assert enabled_accel_onset <= stock_accel_onset - 1.5

    stock_target_jerk = np.diff(stock["target"]) / DT_MDL
    enabled_target_jerk = np.diff(enabled["target"]) / DT_MDL
    stock_accel_jerk = np.diff(stock["accel"]) / DT_MDL
    enabled_accel_jerk = np.diff(enabled["accel"]) / DT_MDL
    assert enabled_target_jerk.min() >= stock_target_jerk.min()
    assert enabled_target_jerk.max() <= stock_target_jerk.max()
    assert enabled_accel_jerk.min() >= stock_accel_jerk.min()
    assert enabled_accel_jerk.max() <= stock_accel_jerk.max()
    assert np.percentile(np.abs(enabled_accel_jerk), 95) <= np.percentile(np.abs(stock_accel_jerk), 95)
    assert enabled["accel"].min() >= stock["accel"].min() + 0.5
    assert enabled["gap"].min() >= stock["gap"].min()
    assert enabled["ttc"].min() >= stock["ttc"].min()
    assert _command_switches(enabled["command"]) <= _command_switches(stock["command"])

  def test_hard_lead_brake_remains_stock(self):
    def lead_speed(t):
      return 22.0 - 4.0 * np.clip(t - 3.0, 0.0, 1.0)

    stock = _run_closed_loop(False, 22.0, 60.0, 27.0, 10.0, lead_speed)
    enabled = _run_closed_loop(True, 22.0, 60.0, 27.0, 10.0, lead_speed)

    assert stock["solver_failures"] == enabled["solver_failures"] == 0
    assert not stock["fcw"].any() and not enabled["fcw"].any()
    assert not enabled["active"].any()
    for key in ("target", "command", "accel", "speed", "gap"):
      np.testing.assert_array_equal(enabled[key], stock[key])
