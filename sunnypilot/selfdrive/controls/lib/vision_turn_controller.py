import numpy as np
import time
import math

from cereal import custom
from openpilot.common.params import Params
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N

VisionTurnSpeedControlState = custom.LongitudinalPlanSP.VisionTurnSpeedControl.VisionTurnSpeedControlState

TRAJECTORY_SIZE = 33

_MIN_V = 20 * CV.KPH_TO_MS  # Do not operate under 20 km/h

_ENTERING_PRED_LAT_ACC_TH = 1.6  # Predicted Lat Acc threshold to trigger entering turn state.
_ABORT_ENTERING_PRED_LAT_ACC_TH = 1.1  # Predicted Lat Acc threshold to abort entering state if speed drops.

_TURNING_LAT_ACC_TH = 1.9  # Lat Acc threshold to trigger turning state.

_LEAVING_LAT_ACC_TH = 1.3  # Lat Acc threshold to trigger leaving turn state.
_FINISH_LAT_ACC_TH = 1.1  # Lat Acc threshold to trigger the end of the turn cycle.

_EVAL_STEP = 5.  # mts. Resolution of the curvature evaluation.
_EVAL_START = 20.  # mts. Distance ahead where to start evaluating vision curvature.
_EVAL_LENGTH = 150.  # mts. Distance ahead where to stop evaluating vision curvature.
_EVAL_RANGE = np.arange(_EVAL_START, _EVAL_LENGTH, _EVAL_STEP)

_A_LAT_REG_MAX = 3.  # Maximum lateral acceleration

_NO_OVERSHOOT_TIME_HORIZON = 4.  # s. Time to use for velocity desired based on a_target when not overshooting.

# Lookup table for the minimum smooth deceleration during the ENTERING state
# depending on the actual maximum absolute lateral acceleration predicted on the turn ahead.
_ENTERING_SMOOTH_DECEL_V = [-0.1, -0.6, -0.8]  # min decel value allowed on ENTERING state
_ENTERING_SMOOTH_DECEL_BP = [1.5, 2.5, 4.]  # absolute value of lat acc ahead

# Lookup table for the acceleration for the TURNING state
# depending on the current lateral acceleration of the vehicle.
_TURNING_ACC_V = [0.5, -0.15, -0.45, -0.6]  # acc value
_TURNING_ACC_BP = [1.5, 2., 3., 4.]  # absolute value of current lat acc

_LEAVING_ACC = 0.5  # Conformable acceleration to regain speed while leaving a turn.

_MIN_LANE_PROB = 0.6  # Minimum lanes probability to allow curvature prediction based on lanes.

_DEBUG = True


def _debug(msg):
  if not _DEBUG:
    return
  print(msg)


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


def _description_for_state(turn_controller_state):
  if turn_controller_state == VisionTurnSpeedControlState.disabled:
    return 'DISABLED'
  if turn_controller_state == VisionTurnSpeedControlState.entering:
    return 'ENTERING'
  if turn_controller_state == VisionTurnSpeedControlState.turning:
    return 'TURNING'
  if turn_controller_state == VisionTurnSpeedControlState.leaving:
    return 'LEAVING'
  return NotImplementedError("v-tsc: state not supported")


class VisionTurnController:
  def __init__(self, CP):
    self._params = Params()
    self._CP = CP
    self._op_enabled = False
    self._gas_pressed = False
    self._is_enabled = self._params.get_bool("VisionTurnSpeedControl")
    self._last_params_update = 0.
    self._v_cruise_setpoint = 0.
    self._v_ego = 0.
    self._a_ego = 0.
    self._a_target = 0.
    self._v_overshoot = 0.
    self._state = VisionTurnSpeedControlState.disabled

    self._reset()

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    if value != self._state:
      _debug(f'TVC: TurnVisionController state: {_description_for_state(value)}')
      if value == VisionTurnSpeedControlState.disabled:
        self._reset()
    self._state = value

  @property
  def a_target(self):
    return self._a_target if self.is_active else self._a_ego

  @property
  def v_turn(self):
    if not self.is_active:
      return self._v_cruise_setpoint
    return self._v_overshoot if self._lat_acc_overshoot_ahead \
      else self._v_ego + self._a_target * _NO_OVERSHOOT_TIME_HORIZON

  @property
  def current_lat_acc(self):
    return self._current_lat_acc

  @property
  def max_pred_lat_acc(self):
    return self._max_pred_lat_acc

  @property
  def is_active(self):
    return self._state != VisionTurnSpeedControlState.disabled

  def _reset(self):
    self._current_lat_acc = 0.
    self._max_v_for_current_curvature = 0.
    self._max_pred_lat_acc = 0.
    self._v_overshoot_distance = 200.
    self._lat_acc_overshoot_ahead = False

  def _update_params(self):
    tm = time.time()
    if tm > self._last_params_update + 5.0:
      self._is_enabled = self._params.get_bool("VisionTurnSpeedControl")
      self._last_params_update = tm

  def _update_calculations(self, sm):
    # Get path polynomial approximation for curvature estimation from model data.
    path_poly = None
    model_data = sm['modelV2'] if sm.valid.get('modelV2', False) else None
    lat_planner_data = sm['lateralPlan'] if sm.valid.get('lateralPlan', False) else None

    # 1. When the probability of lanes is good enough, compute polynomial from lanes as they are way more stable
    # on current mode than a driving path.
    if model_data is not None and len(model_data.laneLines) == 4 and len(model_data.laneLines[0].t) == TRAJECTORY_SIZE:
      ll_x = model_data.laneLines[1].x  # left and right ll x is the same
      lll_y = np.array(model_data.laneLines[1].y)
      rll_y = np.array(model_data.laneLines[2].y)
      l_prob = model_data.laneLineProbs[1]
      r_prob = model_data.laneLineProbs[2]
      lll_std = model_data.laneLineStds[1]
      rll_std = model_data.laneLineStds[2]

      # Reduce reliance on lanelines that are too far apart or will be in a few seconds
      width_pts = rll_y - lll_y
      prob_mods = []
      for t_check in [0.0, 1.5, 3.0]:
        width_at_t = np.interp(t_check * (self._v_ego + 7), ll_x, width_pts)
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

    # 2. If not polynomially derived from lanes, then derive it from a driving path as provided by `lateralPlanner`.
    if path_poly is None and lat_planner_data is not None and len(lat_planner_data.psis) == CONTROL_N \
       and lat_planner_data.dPathPoints[0] > 0:
      yData = list(lat_planner_data.dPathPoints)
      path_poly = np.polyfit(lat_planner_data.psis, yData[0:CONTROL_N], 3)

    # 3. If no polynomial derived from lanes or driving path, then provide a straight line poly.
    if path_poly is None:
      path_poly = np.array([0., 0., 0., 0.])

    current_curvature = abs(
      sm['carState'].steeringAngleDeg * CV.DEG_TO_RAD / (self._CP.steerRatio * self._CP.wheelbase))
    self._current_lat_acc = current_curvature * self._v_ego ** 2
    self._max_v_for_current_curvature = math.sqrt(_A_LAT_REG_MAX / current_curvature) if current_curvature > 0 \
        else V_CRUISE_MAX * CV.KPH_TO_MS

    pred_curvatures = eval_curvature(path_poly, _EVAL_RANGE)
    max_pred_curvature = np.amax(pred_curvatures)
    self._max_pred_lat_acc = self._v_ego ** 2 * max_pred_curvature

    max_curvature_for_vego = _A_LAT_REG_MAX / max(self._v_ego, 0.1) ** 2
    lat_acc_overshoot_idxs = np.nonzero(pred_curvatures >= max_curvature_for_vego)[0]
    self._lat_acc_overshoot_ahead = len(lat_acc_overshoot_idxs) > 0

    if self._lat_acc_overshoot_ahead:
      self._v_overshoot = min(math.sqrt(_A_LAT_REG_MAX / max_pred_curvature), self._v_cruise_setpoint)
      self._v_overshoot_distance = max(float(lat_acc_overshoot_idxs[0] * _EVAL_STEP + _EVAL_START), _EVAL_STEP)
      _debug(f'TVC: High LatAcc. Dist: {self._v_overshoot_distance:.2f}, v: {self._v_overshoot * CV.MS_TO_KPH:.2f}')

  def _state_transition(self):
    # In any case, if a system is disabled or the feature is disabled or gas is pressed, disable.
    if not self._op_enabled or not self._is_enabled or self._gas_pressed:
      self.state = VisionTurnSpeedControlState.disabled
      return

    # DISABLED
    if self.state == VisionTurnSpeedControlState.disabled:
      # Do not enter a turn control cycle if the speed is low.
      if self._v_ego <= _MIN_V:
        pass
      # If significant lateral acceleration is predicted ahead, then move to Entering turn state.
      elif self._max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.entering
    # ENTERING
    elif self.state == VisionTurnSpeedControlState.entering:
      # Transition to Turning if current lateral acceleration is over the threshold.
      if self._current_lat_acc >= _TURNING_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.turning
      # Abort if the predicted lateral acceleration drops
      elif self._max_pred_lat_acc < _ABORT_ENTERING_PRED_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.disabled
    # TURNING
    elif self.state == VisionTurnSpeedControlState.turning:
      # Transition to Leaving if current lateral acceleration drops below a threshold.
      if self._current_lat_acc <= _LEAVING_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.leaving
    # LEAVING
    elif self.state == VisionTurnSpeedControlState.leaving:
      # Transition back to Turning if current lateral acceleration goes back over the threshold.
      if self._current_lat_acc >= _TURNING_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.turning
      # Finish if current lateral acceleration goes below a threshold.
      elif self._current_lat_acc < _FINISH_LAT_ACC_TH:
        self.state = VisionTurnSpeedControlState.disabled

  def _update_solution(self):
    # DISABLED
    if self.state == VisionTurnSpeedControlState.disabled:
      # when not overshooting, calculate v_turn as the speed at the prediction horizon when following
      # the smooth deceleration.
      a_target = self._a_ego
    # ENTERING
    elif self.state == VisionTurnSpeedControlState.entering:
      # when not overshooting, target a smooth deceleration in preparation for a sharp turn to come.
      a_target = np.interp(self._max_pred_lat_acc, _ENTERING_SMOOTH_DECEL_BP, _ENTERING_SMOOTH_DECEL_V)
      if self._lat_acc_overshoot_ahead:
        # when overshooting, target the acceleration needed to achieve the overshoot speed at
        # the required distance
        a_target = min((self._v_overshoot ** 2 - self._v_ego ** 2) / (2 * self._v_overshoot_distance), a_target)
      _debug(f'TVC Entering: Overshooting: {self._lat_acc_overshoot_ahead}')
      _debug(f'    Decel: {a_target:.2f}, target v: {self.v_turn * CV.MS_TO_KPH}')
    # TURNING
    elif self.state == VisionTurnSpeedControlState.turning:
      # When turning, we provide a target acceleration that is comfortable for the lateral acceleration felt.
      a_target = np.interp(self._current_lat_acc, _TURNING_ACC_BP, _TURNING_ACC_V)
    # LEAVING
    elif self.state == VisionTurnSpeedControlState.leaving:
      # When leaving, we provide a comfortable acceleration to regain speed.
      a_target = _LEAVING_ACC

    # update solution values.
    self._a_target = a_target

  def update(self, sm, enabled, v_ego, a_ego, v_cruise_setpoint):
    self._op_enabled = enabled
    self._gas_pressed = sm['carState'].gasPressed
    self._v_ego = v_ego
    self._a_ego = a_ego
    self._v_cruise_setpoint = v_cruise_setpoint

    self._update_params()
    self._update_calculations(sm)
    self._state_transition()
    self._update_solution()
