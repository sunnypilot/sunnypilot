"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import gc
from contextlib import ExitStack
from unittest import mock

import numpy as np

from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.test.longitudinal_maneuvers.plant import Plant
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanSource
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.vision_controller import _A_LAT_REG_MAX


def _run_constant_curve(*, scc_enabled: bool, cruise: float, duration: float = 70.0) -> dict[str, np.ndarray]:
  gc.collect()
  curvature = 0.005
  plant = Plant(lead_relevancy=False, speed=30.0)
  planner = plant.planner
  planner.dec._enabled = False
  planner.scc.map.enabled = False
  planner.scc.vision.enabled = scc_enabled
  solver_failures = 0

  with ExitStack() as patches:
    patches.enter_context(mock.patch.object(planner.dec, "_read_params", return_value=None))
    patches.enter_context(mock.patch.object(planner.scc.map, "update_params", return_value=None))
    patches.enter_context(mock.patch.object(planner.scc.vision, "_update_params", return_value=None))

    original_mpc_reset = planner.mpc.reset

    def record_mpc_reset(*args, **kwargs):
      nonlocal solver_failures
      solver_failures += int(planner.mpc.solution_status != 0)
      return original_mpc_reset(*args, **kwargs)

    patches.enter_context(mock.patch.object(planner.mpc, "reset", side_effect=record_mpc_reset))

    if scc_enabled:
      original_update_calculations = planner.scc.vision._update_calculations

      def inject_constant_curvature(sm):
        velocities = np.asarray(sm['modelV2'].velocity.x, dtype=float)
        sm['modelV2'].orientationRate.z = (curvature * velocities).tolist()
        sm['controlsState'].curvature = curvature
        original_update_calculations(sm)

      patches.enter_context(mock.patch.object(planner.scc.vision, "_update_calculations", side_effect=inject_constant_curvature))

    original_update = planner.update

    def enable_longitudinal(sm):
      sm['carControl'].enabled = True
      sm['carControl'].longActive = True
      original_update(sm)

    patches.enter_context(mock.patch.object(planner, "update", side_effect=enable_longitudinal))
    rows = []
    while plant.current_time < duration:
      output = plant.step(v_cruise=cruise)
      rows.append(
        (
          plant.current_time,
          output['speed'],
          output['should_stop'],
          planner.scc.vision.is_active,
          planner.source == LongitudinalPlanSource.sccVision,
          planner.scc.vision.output_v_target,
        )
      )

  data = np.asarray(rows, dtype=float)
  gc.collect()
  return {
    'time': data[:, 0],
    'speed': data[:, 1],
    'should_stop': data[:, 2],
    'active': data[:, 3],
    'scc_source': data[:, 4],
    'target': data[:, 5],
    'solver_failures': np.asarray(solver_failures),
  }


class TestVisionControllerClosedLoop(OpenpilotTestCase):
  def test_constant_curve_recovers_like_stock_speed_cap(self):
    target = (_A_LAT_REG_MAX / 0.005) ** 0.5
    scc = _run_constant_curve(scc_enabled=True, cruise=30.0)
    stock = _run_constant_curve(scc_enabled=False, cruise=target)
    scc_final = scc['speed'][scc['time'] >= 60.0]
    stock_final = stock['speed'][stock['time'] >= 60.0]

    # The generated solver can report platform-specific failures for the
    # synthetic no-lead plant. The feature must not make that stock baseline
    # worse; requiring an absolute zero would hide a harness difference as a
    # controller regression.
    assert scc['solver_failures'] <= stock['solver_failures']
    assert not scc['should_stop'].any()
    assert np.all(scc['active'][scc['time'] >= 60.0])
    assert np.all(scc['scc_source'][scc['time'] >= 60.0])
    assert np.allclose(scc['target'][scc['time'] >= 60.0], target)
    assert scc_final.min() >= target - 1.0
    assert abs(scc_final.mean() - stock_final.mean()) < 0.5
    assert abs(scc_final.min() - stock_final.min()) < 1.0
    assert abs(scc_final.max() - stock_final.max()) < 1.0
