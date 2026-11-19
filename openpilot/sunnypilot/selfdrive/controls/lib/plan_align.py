"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Plan-Aligned Braking (alpha).

Models that output both a plan (modelV2.velocity / position) and a learned action head (modelV2.action.desiredAcceleration)
can disagree: when decelerating hard, the action head commands less braking than the plan implies. With no lead car the e2e
candidate is the only braking source in the planner's min(mpc, cruise, e2e), so the shortfall reaches the car as creeping
toward stops and overshooting red lights, worse at higher speed (decel needed for a fixed stopping distance scales with v^2).

This pulls the e2e accel toward the stronger of
  a_plan : accel implied by the plan's speed change over HORIZON seconds
  a_stop : constant decel needed to stop at the stop point the plan itself predicts (-v^2 / 2d)
Only ever toward HARDER braking, only while the action accel is already braking, never with a lead, and floored.

Gate: Custom (non-Default) models only, same condition as Blendful / sunnylink `custom_model_active`.
"""
import numpy as np

from openpilot.cereal import custom
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants

PARAM = "PlanAlignBraking"

BETA = 0.7          # 0 = off, 1 = follow the plan fully
HORIZON = 1.0       # s, plan lookahead for a_plan
FLOOR = -3.0        # m/s^2, never push the aligned command below this (stock ACCEL_MIN is -3.5)
STOP_V = 0.3        # m/s, plan speed below this counts as "stopped"
MIN_V = 2.0         # m/s, ignore the stop-point term below this speed
MIN_DIST = 3.0      # m, avoid blow-up when the predicted stop point is very close
TAU = 0.5           # s, smoothing of the stop-point term
RAMP = 0.3          # m/s^2, correction fades in as the action accel goes from 0 to -RAMP (no effect while cruising/accelerating)
PARAM_CHECK_FRAMES = int(1.0 / DT_MDL)


class PlanAlignBraking:
  def __init__(self):
    self.params = Params()
    self.enabled = False
    self._frame = 0
    self.a_stop_f = FirstOrderFilter(0.0, TAU, DT_MDL)
    self._read_params()

  def _read_params(self) -> None:
    # runner the manager launches; Default (stock) model is excluded
    custom_model = self.params.get("ModelRunnerTypeCache") == custom.ModelManagerSP.Runner.tinygrad
    self.enabled = bool(custom_model and self.params.get_bool(PARAM))

  def update_params(self) -> None:
    if self._frame % PARAM_CHECK_FRAMES == 0:
      self._read_params()
    self._frame += 1

  def update(self, model_msg, a_action: float, has_lead: bool) -> float:
    self.update_params()
    if not self.enabled:
      self.a_stop_f.x = 0.0
      return a_action

    t = ModelConstants.T_IDXS
    v = np.array(model_msg.velocity.x)
    x = np.array(model_msg.position.x)
    if len(v) != len(t) or len(x) != len(t):
      self.a_stop_f.x = 0.0
      return a_action

    a_plan = (np.interp(HORIZON, t, v) - v[0]) / HORIZON
    a_stop = 0.0
    if v[0] > MIN_V:
      idx = np.flatnonzero(v < STOP_V)
      if idx.size:
        a_stop = -v[0] ** 2 / (2.0 * max(x[idx[0]], MIN_DIST))
    a_stop = self.a_stop_f.update(a_stop)

    if has_lead:
      return a_action

    a_tgt = min(a_plan, a_stop)
    w = float(np.clip(-a_action / RAMP, 0.0, 1.0))
    a_out = a_action + BETA * w * min(a_tgt - a_action, 0.0)
    return float(max(a_out, min(a_action, FLOOR)))
