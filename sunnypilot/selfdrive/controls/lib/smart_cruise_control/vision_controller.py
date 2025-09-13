"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
import math

from cereal import custom
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

VisionState = custom.LongitudinalPlanSP.SmartCruiseControl.VisionState

ACTIVE_STATES = [VisionState.entering, VisionState.turning, VisionState.leaving]

TRAJECTORY_SIZE = 33

_MIN_V = 20 * CV.KPH_TO_MS  # Do not operate under 20 km/h

_ENTERING_PRED_LAT_ACC_TH = 1.3  # Predicted Lat Acc threshold to trigger entering turn state.
_ABORT_ENTERING_PRED_LAT_ACC_TH = 1.1  # Predicted Lat Acc threshold to abort entering state if speed drops.

_TURNING_LAT_ACC_TH = 1.6  # Lat Acc threshold to trigger turning state.

_LEAVING_LAT_ACC_TH = 1.3  # Lat Acc threshold to trigger leaving turn state.
_FINISH_LAT_ACC_TH = 1.1  # Lat Acc threshold to trigger the end of the turn cycle.

_EVAL_STEP = 5.  # mts. Resolution of the curvature evaluation.
_EVAL_START = 20.  # mts. Distance ahead where to start evaluating vision curvature.
_EVAL_LENGTH = 150.  # mts. Distance ahead where to stop evaluating vision curvature.
_EVAL_RANGE = np.arange(_EVAL_START, _EVAL_LENGTH, _EVAL_STEP)

_A_LAT_REG_MAX = 2.  # Maximum lateral acceleration

_NO_OVERSHOOT_TIME_HORIZON = 4.  # s. Time to use for velocity desired based on a_target when not overshooting.

# Lookup table for the minimum smooth deceleration during the ENTERING state
# depending on the actual maximum absolute lateral acceleration predicted on the turn ahead.
_ENTERING_SMOOTH_DECEL_V = [-0.2, -1.]  # min decel value allowed on ENTERING state
_ENTERING_SMOOTH_DECEL_BP = [1.3, 3.]  # absolute value of lat acc ahead

# Lookup table for the acceleration for the TURNING state
# depending on the current lateral acceleration of the vehicle.
_TURNING_ACC_V = [0.5, 0., -0.4]  # acc value
_TURNING_ACC_BP = [1.5, 2.3, 3.]  # absolute value of current lat acc

_LEAVING_ACC = 0.5  # Conformable acceleration to regain speed while leaving a turn.

_MIN_LANE_PROB = 0.6  # Minimum lanes probability to allow curvature prediction based on lanes.


def eval_curvature(poly, x_vals):
  """
  This function returns a vector with the curvature based on a path defined by `poly`
  evaluated on distance vector `x_vals`
  """

  # https://en.wikipedia.org/wiki/Curvature# Local_expressions
  def curvature(x):
    a = abs(2 * poly[1] + 6 * poly[0] * x) / (1 + (3 * poly[0] * x ** 2 + 2 * poly[1] * x + poly[2]) ** 2) ** 1.5
    return a

  return np.vectorize(curvature)(x_vals)


def eval_lat_acc(v_ego, x_curv):
  """
  This function returns a vector with the lateral acceleration based
  for the provided speed `v_ego` evaluated over curvature vector `x_curv`
  """

  def lat_acc(curv):
    a = v_ego ** 2 * curv
    return a

  return np.vectorize(lat_acc)(x_curv)


class SmartCruiseControlVision:
  v_target: float = 0
  a_target: float = 0.
  v_ego: float = 0.
  a_ego: float = 0.
  v_overshoot: float = 0.
  output_v_target: float = V_CRUISE_UNSET
  output_a_target: float = 0.

  def __init__(self, CP):
    self._params = Params()
    self.CP = CP
    self.frame = -1
    self.long_active = False
    self.enabled = self._params.get_bool("SmartCruiseControlVision")
    self.v_cruise_setpoint = 0.
    self.max_v_for_current_curvature = 0.
    self.lat_acc_overshoot_ahead = 0.
    self.v_overshoot_distance = 200.

    self.state = VisionState.disabled
    self.current_lat_acc = 0.
    self.max_pred_lat_acc = 0.

    self.reset()

  def get_a_target_from_control(self) -> float:
    if self.is_active:
      return self.a_target

    return self.a_ego

  def get_v_target_from_control(self) -> float:
    if self.is_active:
      if self.lat_acc_overshoot_ahead:
        return self.v_overshoot
      return self.v_ego + self.a_target * _NO_OVERSHOOT_TIME_HORIZON

    return V_CRUISE_UNSET

  @property
  def is_active(self):
    return self.state != VisionState.disabled

  def reset(self):
    self.current_lat_acc = 0.
    self.max_v_for_current_curvature = 0.
    self.max_pred_lat_acc = 0.
    self.v_overshoot_distance = 200.
    self.lat_acc_overshoot_ahead = False

  def _update_params(self):
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self._params.get_bool("SmartCruiseControlVision")

  def _update_calculations(self, sm):
    # Get path polynomial approximation for curvature estimation from model data.
    path_poly = None

    # 1. When the probability of lanes is good enough, compute polynomial from lanes as they are way more stable
    # on current mode than a driving path.
    model_v2 = sm['modelV2']
    model_valid = model_v2 is not None and len(model_v2.orientation.x) >= CONTROL_N
    if model_valid and len(model_v2.laneLines) == 4 and len(model_v2.laneLines[0].t) == TRAJECTORY_SIZE:
      ll_x = model_v2.laneLines[1].x  # left and right ll x is the same
      lll_y = np.array(model_v2.laneLines[1].y)
      rll_y = np.array(model_v2.laneLines[2].y)
      l_prob = model_v2.laneLineProbs[1]
      r_prob = model_v2.laneLineProbs[2]
      lll_std = model_v2.laneLineStds[1]
      rll_std = model_v2.laneLineStds[2]

      # Reduce reliance on lanelines that are too far apart or will be in a few seconds
      width_pts = rll_y - lll_y
      prob_mods = []
      for t_check in [0.0, 1.5, 3.0]:
        width_at_t = np.interp(t_check * (self.v_ego + 7), ll_x, width_pts)
        prob_mods.append(np.interp(width_at_t, [4.0, 5.0], [1.0, 0.0]))
      mod = min(prob_mods)
      l_prob *= mod
      r_prob *= mod

      # Reduce reliance on uncertain lanelines
      l_std_mod = np.interp(lll_std, [.15, .3], [1.0, 0.0])
      r_std_mod = np.interp(rll_std, [.15, .3], [1.0, 0.0])
      l_prob *= l_std_mod
      r_prob *= r_std_mod

      # Find a path from lanes as the average center lane only if min probability on both lanes is above a threshold.
      if l_prob > _MIN_LANE_PROB and r_prob > _MIN_LANE_PROB:
        c_y = width_pts / 2 + lll_y
        path_poly = np.polyfit(ll_x, c_y, 3)

    # TODO-SP: uncomment this once we reintroduce models with lateralPlanner
    # 2. If not polynomially derived from lanes, then derive it from a driving path as provided by `lateralPlanner`.
    # lateral_plan = sm['lateralPlan']
    # lateral_plan_valid = lateral_plan is not None and len(lateral_plan.psis) >= CONTROL_N
    # if path_poly is None and lateral_plan_valid and len(lateral_plan.psis) == CONTROL_N \
    #    and lateral_plan.dPathPoints[0] > 0:
    #   yData = list(lateral_plan.dPathPoints)
    #   path_poly = np.polyfit(lateral_plan.psis, yData[0:CONTROL_N], 3)

    # 3. If no polynomial derived from lanes or driving path, then provide a straight line poly.
    if path_poly is None:
      path_poly = np.array([0., 0., 0., 0.])

    current_curvature = abs(sm['carState'].steeringAngleDeg * CV.DEG_TO_RAD / (self.CP.steerRatio * self.CP.wheelbase))
    self.current_lat_acc = current_curvature * self.v_ego ** 2
    self.max_v_for_current_curvature = math.sqrt(_A_LAT_REG_MAX / current_curvature) if current_curvature > 0 else \
                                       V_CRUISE_MAX * CV.KPH_TO_MS

    pred_curvatures = eval_curvature(path_poly, _EVAL_RANGE)
    max_pred_curvature = np.amax(pred_curvatures)
    self.max_pred_lat_acc = self.v_ego ** 2 * max_pred_curvature

    max_curvature_for_vego = _A_LAT_REG_MAX / max(self.v_ego, 0.1) ** 2
    lat_acc_overshoot_idxs = np.nonzero(pred_curvatures >= max_curvature_for_vego)[0]
    self.lat_acc_overshoot_ahead = len(lat_acc_overshoot_idxs) > 0

    if self.lat_acc_overshoot_ahead:
      self.v_overshoot = min(math.sqrt(_A_LAT_REG_MAX / max_pred_curvature), self.v_cruise_setpoint)
      self.v_overshoot_distance = max(float(lat_acc_overshoot_idxs[0] * _EVAL_STEP + _EVAL_START), _EVAL_STEP)

  def _update_state_machine(self):
    # ENABLED, ENTERING, TURNING, LEAVING
    if self.state != VisionState.disabled:
      # longitudinal and feature disable always have priority in a non-disabled state
      if not self.long_active or not self.enabled:
        self.state = VisionState.disabled

      else:
        # ENABLED
        if self.state == VisionState.enabled:
          # Do not enter a turn control cycle if the speed is low.
          if self.v_ego <= _MIN_V:
            pass
          # If significant lateral acceleration is predicted ahead, then move to Entering turn state.
          elif self.max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH:
            self.state = VisionState.entering

        # ENTERING
        elif self.state == VisionState.entering:
          # Transition to Turning if current lateral acceleration is over the threshold.
          if self.current_lat_acc >= _TURNING_LAT_ACC_TH:
            self.state = VisionState.turning
          # Abort if the predicted lateral acceleration drops
          elif self.max_pred_lat_acc < _ABORT_ENTERING_PRED_LAT_ACC_TH:
            self.state = VisionState.enabled

        # TURNING
        elif self.state == VisionState.turning:
          # Transition to Leaving if current lateral acceleration drops below a threshold.
          if self.current_lat_acc <= _LEAVING_LAT_ACC_TH:
            self.state = VisionState.leaving

        # LEAVING
        elif self.state == VisionState.leaving:
          # Transition back to Turning if current lateral acceleration goes back over the threshold.
          if self.current_lat_acc >= _TURNING_LAT_ACC_TH:
            self.state = VisionState.turning
          # Finish if current lateral acceleration goes below a threshold.
          elif self.current_lat_acc < _FINISH_LAT_ACC_TH:
            self.state = VisionState.enabled

    # DISABLED
    elif self.state == VisionState.disabled:
      if self.long_active and self.enabled:
        self.state = VisionState.enabled

  def _update_solution(self):
    # DISABLED, ENABLED
    if self.state not in [ACTIVE_STATES]:
      # when not overshooting, calculate v_turn as the speed at the prediction horizon when following
      # the smooth deceleration.
      a_target = self.a_ego
    # ENTERING
    elif self.state == VisionState.entering:
      # when not overshooting, target a smooth deceleration in preparation for a sharp turn to come.
      a_target = np.interp(self.max_pred_lat_acc, _ENTERING_SMOOTH_DECEL_BP, _ENTERING_SMOOTH_DECEL_V)
      if self.lat_acc_overshoot_ahead:
        # when overshooting, target the acceleration needed to achieve the overshoot speed at
        # the required distance
        a_target = min((self.v_overshoot ** 2 - self.v_ego ** 2) / (2 * self.v_overshoot_distance), a_target)
    # TURNING
    elif self.state == VisionState.turning:
      # When turning, we provide a target acceleration that is comfortable for the lateral acceleration felt.
      a_target = np.interp(self.current_lat_acc, _TURNING_ACC_BP, _TURNING_ACC_V)
    # LEAVING
    elif self.state == VisionState.leaving:
      # When leaving, we provide a comfortable acceleration to regain speed.
      a_target = _LEAVING_ACC
    else:
      raise NotImplementedError(f"SCC-V state not supported: {self.state}")

    self.a_target = a_target

  def update(self, sm, long_active, v_ego, a_ego, v_cruise_setpoint):
    self.long_active = long_active
    self.v_ego = v_ego
    self.a_ego = a_ego
    self.v_cruise_setpoint = v_cruise_setpoint

    self._update_params()
    self._update_calculations(sm)
    self._update_state_machine()
    self._update_solution()

    self.frame += 1

    self.output_v_target = self.get_v_target_from_control()
    self.output_a_target = self.get_a_target_from_control()
