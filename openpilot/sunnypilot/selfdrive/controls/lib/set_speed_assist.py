"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

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

MIN_SPEED = 5.  # m/s, stop-and-go stays with the model
FULL_SPEED = 8.  # m/s
GAIN_BP = [-0.3, -0.1]  # m/s^2, the model's accel or its plan's mean accel
HORIZON = ModelConstants.T_IDXS[-1]  # s
LEAD_TTC_BP = [15., 25.]  # s
FADE_LAT_ACC_BP = [0.6, 1.0]  # m/s^2
LIFT_FALL = 2.4  # m/s^3
REENGAGE_JERK = 0.3  # m/s^3
FADE_JERK = 0.3  # m/s^3
MIN_GAP = 0.05  # m/s^2
# max approach accel by speed, gentler than the cruise planner's
APPROACH_BP = [0., 4., 9., 14., 18., 25.]  # m/s
APPROACH_V = [1.5, 1.75, 1.45, 1.05, 0.85, 0.65]  # m/s^2
APPROACH_JERK = 0.065  # m/s^3


def approach_ceiling(v_ego: float, personality) -> float:
  # the table is standard, other personalities shift it by Acceleration Boost's step
  step = get_boost_max(personality) - get_boost_max(log.LongitudinalPersonality.standard)
  return float(np.interp(v_ego, APPROACH_BP, APPROACH_V) + step)


def approach_accel(v_ego: float, v_target: float, personality) -> float:
  # eases off at APPROACH_JERK into v_target, then follows the gap itself, which goes negative past it
  gap = v_target - v_ego
  return min(math.sqrt(2. * APPROACH_JERK * max(gap, 0.)), gap, approach_ceiling(v_ego, personality))


def planned_slowdown(v_ego: float, plan_v: np.ndarray, lead) -> float:
  drop = v_ego - float(np.min(plan_v))
  # the plan often shows no slowdown yet for a far closing lead
  if lead.present and math.isfinite(lead.vRel) and math.isfinite(lead.dRel) and lead.vRel < 0.:
    ttc = max(lead.dRel, 0.) / -lead.vRel
    drop = max(drop, -lead.vRel * float(np.interp(ttc, LEAD_TTC_BP, [1., 0.])))
  return drop


class SetSpeedAssist:
  """Lifts the model's accel toward the lead and cruise planners' while the model isn't slowing down. Never lowers it."""
  def __init__(self):
    # local import, longitudinal_planner imports this module
    from openpilot.selfdrive.controls.lib.longitudinal_planner import J_CRUISE_BP, J_CRUISE_VALS
    self.rise_bp, self.rise_vals = J_CRUISE_BP, J_CRUISE_VALS

    self.params = Params()
    self.frame = -1
    self.enabled = self.params.get_bool("SetSpeedAssist")
    self._reset()

  def _reset(self) -> None:
    self.active = False
    self.gain = self.fade = self.authority = self.lift = 0.
    self._fresh = True  # the first fade isn't rate limited

  def update_params(self) -> None:
    self.frame += 1
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("SetSpeedAssist")

  def update(self, sm: messaging.SubMaster, a_model: float, a_floor: float, reset_state: bool) -> float:
    # switched off, the lift still eases out
    if reset_state or (not self.enabled and self.lift == 0.):
      self._reset()
      return a_model

    md = sm['modelV2']
    v_ego = sm['carState'].vEgo
    vel = np.asarray(md.velocity.x)
    yaw_rate = np.asarray(md.orientationRate.z)
    curvature_now = sm['controlsState'].curvature
    if not (len(vel) == len(yaw_rate) == ModelConstants.IDX_N and
            np.isfinite(np.concatenate([vel, yaw_rate, [v_ego, a_model, a_floor, curvature_now]])).all()):
      self._reset()
      return a_model

    # sharpest bend now or along the model's path, at the current speed
    curvature = max(abs(curvature_now), np.max(np.abs(yaw_rate) / np.maximum(vel, 1.)))
    lat_acc = curvature * v_ego ** 2
    gap = max(0., a_floor - a_model)
    # authority steps scale with 1 / gap, so flicker in the gain or fade adds a bounded jerk to the lift
    step = DT_MDL / max(gap, MIN_GAP)

    # fades as the model slows or plans to, so a gentle coast toward a stop still lets go
    plan_gain = np.interp(-planned_slowdown(v_ego, vel, sm['radarState'].leadOne) / HORIZON, GAIN_BP, [0., 1.])
    self.gain = min(np.interp(a_model, GAIN_BP, [0., 1.]), plan_gain) * np.interp(v_ego, [MIN_SPEED, FULL_SPEED], [0., 1.])
    fade = np.interp(lat_acc, FADE_LAT_ACC_BP, [1., 0.])
    self.fade = fade if self._fresh else np.clip(fade, self.fade - FADE_JERK * step, self.fade + FADE_JERK * step)
    self._fresh = False
    self.active = self.enabled and md.meta.laneChangeState == LaneChangeState.off

    authority = self.gain * self.fade if self.active else 0.
    self.authority = min(authority, self.authority + REENGAGE_JERK * step)
    target = self.authority * gap
    rise = np.interp(v_ego, self.rise_bp, self.rise_vals)
    # at gain 0 the lift may drop in one frame, so the model's braking isn't delayed
    fall = max(LIFT_FALL * DT_MDL, (1. - self.gain) * self.lift)
    self.lift = rate_limit(target, self.lift, -fall, rise * DT_MDL)
    return a_model + self.lift
