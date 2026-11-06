"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

import openpilot.cereal.messaging as messaging
from opendbc.car import rate_limit
from openpilot.cereal import log
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import get_boost_max

LaneChangeState = log.LaneChangeState

MIN_SPEED = 5.  # m/s. No assist below this, so stop-and-go stays with the model.
FULL_SPEED = 8.  # m/s. Full assist from this speed up.
GAIN_BP = [-0.3, -0.1]  # Model accel over which the assist fades out as the model slows down.
FADE_LAT_ACC_BP = [0.6, 1.0]  # Lat acc of the sharpest bend ahead over which the assist fades out.
LIFT_FALL = 2.4  # m/s^3. The slowest the lift eases off, e.g. on a lane change or a bend.
# Stock ACC approach to the target speed, gentler than the cruise planner's: max accel by speed,
# scaled by the shortfall.
APPROACH_BP = [0., 4., 9., 14., 18., 25.]  # m/s
APPROACH_V = [1.5, 1.75, 1.45, 1.05, 0.85, 0.65]  # m/s^2
APPROACH_GAP_BP = [0., 1., 3., 5., 10.]  # m/s below the target speed
APPROACH_GAP_FRACTION = [0.38, 0.47, 0.57, 0.72, 1.]


def approach_accel(v_ego: float, v_target: float, personality) -> float:
  """Max floor accel while closing on v_target. The table is Standard; the other personalities move
  it by Acceleration Boost's step between them."""
  step = get_boost_max(personality) - get_boost_max(log.LongitudinalPersonality.standard)
  ceiling = np.interp(v_ego, APPROACH_BP, APPROACH_V) + step
  return float(ceiling * np.interp(v_target - v_ego, APPROACH_GAP_BP, APPROACH_GAP_FRACTION))


class SetSpeedAssist:
  """
  The driving model doesn't know the set speed, so it often drives below it, or further back from
  a lead than the personality's gap. This adds acceleration to the model's, up to what the lead and
  cruise planners would do, while the model isn't slowing down. It never takes any away.
  """
  def __init__(self):
    # the assist builds at the cruise planner's jerk; imported here because longitudinal_planner imports this module
    from openpilot.selfdrive.controls.lib.longitudinal_planner import J_CRUISE_BP, J_CRUISE_VALS
    self.rise_bp, self.rise_vals = J_CRUISE_BP, J_CRUISE_VALS

    self.params = Params()
    self.frame = -1
    self.enabled = self.params.get_bool("SetSpeedAssist")
    self.active = False
    self.gain = 0.
    self.fade = 0.
    self.lift = 0.

  def update_params(self) -> None:
    """Read the param. Called before the planner decides whether Acceleration Boost may run."""
    self.frame += 1
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("SetSpeedAssist")

  def update(self, sm: messaging.SubMaster, a_model: float, a_floor: float, reset_state: bool) -> float:
    """Return the model's accel plus the assist. a_floor is the lower of the lead and cruise accels and the approach pace."""
    self.active = False
    self.gain = self.fade = 0.
    # when switched off, the lift eases out before the assist stops
    if reset_state or (not self.enabled and self.lift == 0.):
      self.lift = 0.
      return a_model

    md = sm['modelV2']
    v_ego = sm['carState'].vEgo
    vel = np.asarray(md.velocity.x)
    yaw_rate = np.asarray(md.orientationRate.z)
    curvature_now = sm['controlsState'].curvature
    if not (len(vel) == len(yaw_rate) == ModelConstants.IDX_N and
            np.isfinite(np.concatenate([vel, yaw_rate, [v_ego, a_model, a_floor, curvature_now]])).all()):
      self.lift = 0.
      return a_model

    # sharpest bend now or along the model's path, at the current speed
    curvature = max(abs(curvature_now), np.max(np.abs(yaw_rate) / np.maximum(vel, 1.)))
    lat_acc = curvature * v_ego ** 2

    self.gain = np.interp(a_model, GAIN_BP, [0., 1.]) * np.interp(v_ego, [MIN_SPEED, FULL_SPEED], [0., 1.])
    self.fade = np.interp(lat_acc, FADE_LAT_ACC_BP, [1., 0.])
    self.active = self.enabled and md.meta.laneChangeState == LaneChangeState.off

    target = self.gain * self.fade * max(0., a_floor - a_model) if self.active else 0.
    rise = np.interp(v_ego, self.rise_bp, self.rise_vals)
    # Normally the lift eases off at LIFT_FALL. When the model starts to brake the gain drops, and
    # the lift may drop with it in one frame, so at gain 0 the model's braking is not delayed.
    fall = max(LIFT_FALL * DT_MDL, (1. - self.gain) * self.lift)
    self.lift = rate_limit(target, self.lift, -fall, rise * DT_MDL)
    return a_model + self.lift
