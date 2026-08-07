"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import gc

import numpy as np

from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanSource
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.vision_controller import _A_LAT_REG_MAX
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PlantSP as Plant


def _run_constant_curve(*, scc_enabled: bool, cruise: float, duration: float = 70.) -> dict[str, np.ndarray]:
  gc.collect()
  curvature = 0.005
  plant = Plant(lead_relevancy=False, speed=30., actuator_delay=0.15, actuator_lag=0.20)
  planner = plant.planner
  planner.accel_controller.enabled = False
  planner.accel_controller.update_params = lambda: None
  planner.dec._enabled = False
  planner.dec._read_params = lambda: None
  planner.scc.map.enabled = False
  planner.scc.map.update_params = lambda: None
  planner.scc.vision.enabled = scc_enabled
  planner.scc.vision._update_params = lambda: None

  if scc_enabled:
    original_update_calculations = planner.scc.vision._update_calculations

    def inject_constant_curvature(sm):
      velocities = np.asarray(sm['modelV2'].velocity.x, dtype=float)
      sm['modelV2'].orientationRate.z = (curvature * velocities).tolist()
      sm['controlsState'].curvature = curvature
      original_update_calculations(sm)

    planner.scc.vision._update_calculations = inject_constant_curvature

  original_update = planner.update

  def enable_longitudinal(sm):
    sm['carControl'].enabled = True
    sm['carControl'].longActive = True
    original_update(sm)

  planner.update = enable_longitudinal
  rows = []
  while plant.current_time < duration:
    output = plant.step(v_cruise=cruise)
    rows.append((
      plant.current_time, output['speed'], planner.mpc.last_solution_status, output['should_stop'],
      planner.scc.vision.is_active, planner.source == LongitudinalPlanSource.sccVision,
      planner.scc.vision.output_v_target,
    ))

  data = np.asarray(rows, dtype=float)
  gc.collect()
  return {
    'time': data[:, 0], 'speed': data[:, 1], 'solver_status': data[:, 2], 'should_stop': data[:, 3],
    'active': data[:, 4], 'scc_source': data[:, 5], 'target': data[:, 6],
  }


def test_constant_curve_recovers_like_stock_speed_cap():
  target = (_A_LAT_REG_MAX / 0.005) ** 0.5
  scc = _run_constant_curve(scc_enabled=True, cruise=30.)
  stock = _run_constant_curve(scc_enabled=False, cruise=target)
  scc_final = scc['speed'][scc['time'] >= 60.]
  stock_final = stock['speed'][stock['time'] >= 60.]

  assert not scc['solver_status'].any()
  assert not stock['solver_status'].any()
  assert not scc['should_stop'].any()
  assert np.all(scc['active'][scc['time'] >= 60.])
  assert np.all(scc['scc_source'][scc['time'] >= 60.])
  assert np.allclose(scc['target'][scc['time'] >= 60.], target)
  assert scc_final.min() >= target - 1.
  assert abs(scc_final.mean() - stock_final.mean()) < 0.5
  assert abs(scc_final.min() - stock_final.min()) < 1.
  assert abs(scc_final.max() - stock_final.max()) < 1.
