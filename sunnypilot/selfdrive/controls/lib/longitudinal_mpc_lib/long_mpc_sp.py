"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
from cereal import log
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import (
  LongitudinalMpc, LongitudinalPlanSource,
  COMFORT_BRAKE, STOP_DISTANCE,
  get_safe_obstacle_distance, get_stopped_equivalence_factor, get_T_FOLLOW,
  T_IDXS, T_DIFFS, N, COST_E_DIM, LEAD_DANGER_FACTOR,
  CRUISE_MIN_ACCEL, CRUISE_MAX_ACCEL,
  MPC_SOURCES, FCW_IDXS, CRASH_DISTANCE,
)
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

# Velocity threshold below which a lead is considered "stopped"
STOPPED_LEAD_V_THRESHOLD = 0.5  # m/s

# Extra distance subtracted from obstacle position for stopped leads (personality-dependent).
# This makes the MPC think the obstacle is closer, so the ego vehicle stops further away.
EXTRA_STOP_DISTANCE = {
  log.LongitudinalPersonality.relaxed: 4.0,
  log.LongitudinalPersonality.standard: 3.0,
  log.LongitudinalPersonality.aggressive: 1.0,
}

# Reduced comfort brake for stopped lead approach (personality-dependent).
# Lower value = system assumes it brakes less effectively = starts braking earlier.
APPROACH_COMFORT_BRAKE = {
  log.LongitudinalPersonality.relaxed: 1.8,
  log.LongitudinalPersonality.standard: 2.0,
  log.LongitudinalPersonality.aggressive: 2.3,
}


def get_stopped_equivalence_factor_sp(v_lead, comfort_brake):
  """Same as upstream but with parameterized comfort brake."""
  return (v_lead ** 2) / (2 * comfort_brake)


class LongitudinalMpcSP(LongitudinalMpc):
  def __init__(self, dt=DT_MDL):
    super().__init__(dt=dt)
    self.params_reader = Params()
    self.sp_frame = 0
    self.improved_stopped_approach = self.params_reader.get_bool("ImprovedStoppedApproach")

  def _update_params(self):
    if self.sp_frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.improved_stopped_approach = self.params_reader.get_bool("ImprovedStoppedApproach")

  def update(self, radarstate, v_cruise, personality=log.LongitudinalPersonality.standard):
    self.sp_frame += 1
    self._update_params()

    if not self.improved_stopped_approach:
      super().update(radarstate, v_cruise, personality)
      return

    t_follow = get_T_FOLLOW(personality)
    v_ego = self.x0[1]
    self.status = radarstate.leadOne.status or radarstate.leadTwo.status

    lead_xv_0 = self.process_lead(radarstate.leadOne)
    lead_xv_1 = self.process_lead(radarstate.leadTwo)

    # Check if leads are stopped/nearly stopped
    lead_0_stopped = radarstate.leadOne.status and radarstate.leadOne.vLead < STOPPED_LEAD_V_THRESHOLD
    lead_1_stopped = radarstate.leadTwo.status and radarstate.leadTwo.vLead < STOPPED_LEAD_V_THRESHOLD

    extra_stop = EXTRA_STOP_DISTANCE.get(personality, 3.0)
    approach_brake = APPROACH_COMFORT_BRAKE.get(personality, 2.0)

    # For stopped leads: use softer comfort brake (earlier braking) and add extra stop buffer
    if lead_0_stopped:
      lead_0_obstacle = lead_xv_0[:, 0] + get_stopped_equivalence_factor_sp(lead_xv_0[:, 1], approach_brake) - extra_stop
    else:
      lead_0_obstacle = lead_xv_0[:, 0] + get_stopped_equivalence_factor(lead_xv_0[:, 1])

    if lead_1_stopped:
      lead_1_obstacle = lead_xv_1[:, 0] + get_stopped_equivalence_factor_sp(lead_xv_1[:, 1], approach_brake) - extra_stop
    else:
      lead_1_obstacle = lead_xv_1[:, 0] + get_stopped_equivalence_factor(lead_xv_1[:, 1])

    # Cruise obstacle (unchanged from upstream)
    v_lower = v_ego + (T_IDXS * CRUISE_MIN_ACCEL * 1.05)
    v_upper = v_ego + (T_IDXS * CRUISE_MAX_ACCEL * 1.05)
    v_cruise_clipped = np.clip(v_cruise * np.ones(N + 1), v_lower, v_upper)
    cruise_obstacle = np.cumsum(T_DIFFS * v_cruise_clipped) + get_safe_obstacle_distance(v_cruise_clipped, t_follow)

    x_obstacles = np.column_stack([lead_0_obstacle, lead_1_obstacle, cruise_obstacle])
    self.source = MPC_SOURCES[np.argmin(x_obstacles[0])]

    self.yref[:, :] = 0.0
    for i in range(N):
      self.solver.set(i, "yref", self.yref[i])
    self.solver.set(N, "yref", self.yref[N][:COST_E_DIM])

    self.params[:, 0] = ACCEL_MIN
    self.params[:, 1] = ACCEL_MAX
    self.params[:, 2] = np.min(x_obstacles, axis=1)
    self.params[:, 3] = np.copy(self.a_prev)
    self.params[:, 4] = t_follow
    self.params[:, 5] = LEAD_DANGER_FACTOR

    self.run()
    if (np.any(lead_xv_0[FCW_IDXS, 0] - self.x_sol[FCW_IDXS, 0] < CRASH_DISTANCE) and
            radarstate.leadOne.modelProb > 0.9):
      self.crash_cnt += 1
    else:
      self.crash_cnt = 0
