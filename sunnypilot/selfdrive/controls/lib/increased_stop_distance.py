"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Increased Stop Distance: stop further behind a stopped lead vehicle, and
further from stops the model plans to hold (red lights).

Two mechanisms share the IncreasedStoppedDistance param (meters):

- Lead stops (radard): the reported lead distance is reduced by the offset,
  faded back out as the lead gets up to speed so normal following distance
  is unaffected. Works in both chill and end-to-end mode.

- Model-held stops (planner, end-to-end mode): when the model's trajectory
  ends at ~zero velocity (it plans to remain stopped, e.g. a red light),
  brake toward a point short of its predicted stop point, and hold there
  instead of creeping forward. Only ever adds braking, never reduces it.
  Stops the model plans to proceed through shortly (stop signs) are left
  untouched: forcing an early stop makes the model treat the stop as
  completed and roll through the sign itself (confirmed in road testing).
"""
import numpy as np

from opendbc.car.interfaces import ACCEL_MIN
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

# Fade the offset back out as the lead gets up to speed
STOPPED_DISTANCE_FADE_BP = [0., 3.]  # m/s, lead speed
MIN_ADJUSTED_D_REL = 1.0  # m

E2E_STOP_PLAN_VEL_THRESHOLD = 1.0  # m/s, model plan ending below this implies a held stop
E2E_STOP_MIN_BRAKING = -0.1  # m/s^2, only deepen braking the model has already started
E2E_STOP_MIN_DIST = 2.0  # m, never target a stop point closer than this
E2E_STOP_HOLD_MAX_V = 0.5  # m/s, below this the car is considered stopped
E2E_STOP_HOLD_BUFFER = 2.0  # m, hold until the model's stop point moves beyond offset + buffer


class IncreasedStopDistance:
  def __init__(self):
    self.params = Params()
    self.frame = 0
    self.distance = 0.
    self.read_params()

  def read_params(self) -> None:
    self.distance = float(self.params.get("IncreasedStoppedDistance", return_default=True))

  def update(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.read_params()
    self.frame += 1

  def apply_lead(self, lead_dict: dict) -> dict:
    if self.distance <= 0. or not lead_dict.get('status', False):
      return lead_dict

    offset = self.distance * float(np.interp(lead_dict['vLead'], STOPPED_DISTANCE_FADE_BP, [1., 0.]))
    lead_dict['dRel'] = min(lead_dict['dRel'], max(lead_dict['dRel'] - offset, MIN_ADJUSTED_D_REL))
    return lead_dict

  def adjust_e2e_stop(self, a_target: float, should_stop: bool, v_ego: float, model_msg) -> tuple[float, bool]:
    if self.distance <= 0.:
      return a_target, should_stop

    x = model_msg.position.x
    v = model_msg.velocity.x
    if len(x) != ModelConstants.IDX_N or len(v) != ModelConstants.IDX_N:
      return a_target, should_stop

    # only stops the model plans to hold (red lights) can be shifted
    if float(v[-1]) > E2E_STOP_PLAN_VEL_THRESHOLD:
      return a_target, should_stop

    stop_distance = float(x[-1])

    if v_ego < E2E_STOP_HOLD_MAX_V:
      # stopped short of the model's stop point: hold instead of creeping up to it
      if stop_distance <= self.distance + E2E_STOP_HOLD_BUFFER:
        should_stop = True
    elif a_target < E2E_STOP_MIN_BRAKING:
      # deepen braking that has already started, targeting a stop short of the model's stop point
      adjusted_distance = max(stop_distance - self.distance, E2E_STOP_MIN_DIST)
      a_required = max(-(v_ego ** 2) / (2 * adjusted_distance), ACCEL_MIN)
      if a_required < a_target:
        a_target = float(a_required)

    return a_target, should_stop
