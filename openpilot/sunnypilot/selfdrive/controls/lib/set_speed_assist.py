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

MIN_SPEED = 5.  # m/s. No assist below this, so stop-and-go stays with the model.
FULL_SPEED = 8.  # m/s. Full assist from this speed up.
GAIN_BP = [-0.3, -0.1]  # Model accel over which the assist fades out as the model slows down.
# A slowdown the model plans fades the assist out the same way, read as a mean decel over its plan:
# 1-3 m/s of drop, above the ~1 m/s its far end flickers on a straight road. A closing lead counts
# too, since the lead planner still accelerates while it is far and the plan often shows no slowdown
# yet: in full under 15 s to contact, not at all past 25 s.
HORIZON = ModelConstants.T_IDXS[-1]  # s
LEAD_TTC_BP = [15., 25.]  # s
FADE_LAT_ACC_BP = [0.6, 1.0]  # Lat acc of the sharpest bend ahead over which the assist fades out.
LIFT_FALL = 2.4  # m/s^3. The slowest the lift eases off, e.g. on a lane change or a bend.
# The lift heads for authority * gap, with authority = gain * fade and gap = floor - model accel. The
# gain and fade are read each frame from inputs that flicker (the path's bends, the model's wander),
# and a flicker times the gap came out as jerk. So the authority re-engages at most REENGAGE_JERK /
# gap a second and the fade moves at most FADE_JERK / gap either way, which bounds their share of
# the lift's jerk. Letting go for the model (the gain, a lane change) is still at once.
REENGAGE_JERK = 0.3  # m/s^3
FADE_JERK = 0.3  # m/s^3
MIN_GAP = 0.05  # m/s^2. Only bounds the step when the model is at the floor.
# Stock ACC approach to the target speed, gentler than the cruise planner's: max accel by speed.
APPROACH_BP = [0., 4., 9., 14., 18., 25.]  # m/s
APPROACH_V = [1.5, 1.75, 1.45, 1.05, 0.85, 0.65]  # m/s^2
# Under that ceiling, the accel that eases off at this jerk and reaches the target with none left.
APPROACH_JERK = 0.065  # m/s^3


def approach_ceiling(v_ego: float, personality) -> float:
  """The most the approach asks for at v_ego, a long way under the target. The table is Standard;
  the other personalities move it by Acceleration Boost's step between them."""
  step = get_boost_max(personality) - get_boost_max(log.LongitudinalPersonality.standard)
  return float(np.interp(v_ego, APPROACH_BP, APPROACH_V) + step)


def approach_accel(v_ego: float, v_target: float, personality) -> float:
  """Max floor accel while closing on v_target, sqrt(2 * jerk * gap) up to the ceiling. Within
  2 * APPROACH_JERK of the target it is the gap itself, a 1 s line that goes negative over the
  target, so the floor settles on it without relying on the cruise candidate."""
  gap = v_target - v_ego
  return min(math.sqrt(2. * APPROACH_JERK * max(gap, 0.)), gap, approach_ceiling(v_ego, personality))


def planned_slowdown(v_ego: float, plan_v: np.ndarray, lead) -> float:
  """m/s the model plans to shed: down to its plan's lowest speed, or a closing lead's closing speed
  as it nears contact."""
  drop = v_ego - float(np.min(plan_v))
  if lead.present and math.isfinite(lead.vRel) and math.isfinite(lead.dRel) and lead.vRel < 0.:
    ttc = max(lead.dRel, 0.) / -lead.vRel
    drop = max(drop, -lead.vRel * float(np.interp(ttc, LEAD_TTC_BP, [1., 0.])))
  return drop


class SetSpeedAssist:
  """
  The driving model doesn't know the set speed, so it often drives below it, or further back from
  a lead than the personality's gap. This adds acceleration to the model's, up to what the lead and
  cruise planners would do, while the model isn't slowing down or planning to. It never takes any away.
  """
  def __init__(self):
    # the assist builds at the cruise planner's jerk; imported here because longitudinal_planner imports this module
    from openpilot.selfdrive.controls.lib.longitudinal_planner import J_CRUISE_BP, J_CRUISE_VALS
    self.rise_bp, self.rise_vals = J_CRUISE_BP, J_CRUISE_VALS

    self.params = Params()
    self.frame = -1
    self.enabled = self.params.get_bool("SetSpeedAssist")
    self._reset()

  def _reset(self) -> None:
    self.active = False
    self.gain = self.fade = self.authority = self.lift = 0.
    self._fresh = True  # the fade starts from the road as it is, with nothing to smooth yet

  def update_params(self) -> None:
    """Read the param. Called before the planner decides whether Acceleration Boost may run."""
    self.frame += 1
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("SetSpeedAssist")

  def update(self, sm: messaging.SubMaster, a_model: float, a_floor: float, reset_state: bool) -> float:
    """Return the model's accel plus the assist. a_floor is the lower of the lead and cruise accels and the approach pace."""
    # when switched off, the lift eases out before the assist stops
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
    step = DT_MDL / max(gap, MIN_GAP)  # times a jerk budget, the most the authority moves this frame

    # the model's decision, now and over its plan: a gentle coast toward a stop still lets go
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
    # Normally the lift eases off at LIFT_FALL. When the model starts to brake the gain drops, and
    # the lift may drop with it in one frame, so at gain 0 the model's braking is not delayed.
    fall = max(LIFT_FALL * DT_MDL, (1. - self.gain) * self.lift)
    self.lift = rate_limit(target, self.lift, -fall, rise * DT_MDL)
    return a_model + self.lift
