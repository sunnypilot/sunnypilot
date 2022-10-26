import math

from cereal import car
from common.conversions import Conversions as CV
from common.numpy_fast import clip, interp
from common.params import Params
from common.realtime import DT_MDL
from selfdrive.modeld.constants import T_IDXS

# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
V_CRUISE_MAX = 145  # kph
V_CRUISE_MIN = 8  # kph
V_CRUISE_MIN_HONDA = 5  # kph
V_CRUISE_DELTA_HONDA = 5
V_CRUISE_ENABLE_MIN_MPH = 32  # kph
V_CRUISE_ENABLE_MIN_KPH = 30  # kph
V_CRUISE_INITIAL = 255  # kph

MIN_SPEED = 1.0
LAT_MPC_N = 16
LON_MPC_N = 32
CONTROL_N = 17
CAR_ROTATION_RADIUS = 0.0

# EU guidelines
MAX_LATERAL_JERK = 5.0

ButtonType = car.CarState.ButtonEvent.Type
CRUISE_LONG_PRESS = 50
CRUISE_NEAREST_FUNC = {
  ButtonType.accelCruise: math.ceil,
  ButtonType.decelCruise: math.floor,
}
CRUISE_INTERVAL_SIGN = {
  ButtonType.accelCruise: +1,
  ButtonType.decelCruise: -1,
}


# Constants for Limit controllers.
LIMIT_ADAPT_ACC = -1.  # m/s^2 Ideal acceleration for the adapting (braking) phase when approaching speed limits.
LIMIT_MIN_ACC = -1.5  # m/s^2 Maximum deceleration allowed for limit controllers to provide.
LIMIT_MAX_ACC = 1.0   # m/s^2 Maximum acelration allowed for limit controllers to provide while active.
LIMIT_MIN_SPEED = 8.33  # m/s, Minimum speed limit to provide as solution on limit controllers.
LIMIT_SPEED_OFFSET_TH = -1.  # m/s Maximum offset between speed limit and current speed for adapting state.
LIMIT_MAX_MAP_DATA_AGE = 10.  # s Maximum time to hold to map data, then consider it invalid inside limits controllers.


def apply_deadzone(error, deadzone):
  if error > deadzone:
    error -= deadzone
  elif error < - deadzone:
    error += deadzone
  else:
    error = 0.
  return error


def rate_limit(new_value, last_value, dw_step, up_step):
  return clip(new_value, last_value + dw_step, last_value + up_step)


def update_v_cruise(v_cruise_kph, v_ego, gas_pressed, buttonEvents, button_timers, enabled, metric):
  # handle button presses. TODO: this should be in state_control, but a decelCruise press
  # would have the effect of both enabling and changing speed is checked after the state transition
  reverse_acc_change = Params().get_bool("ReverseAccChange")
  if not enabled:
    return v_cruise_kph

  long_press = False
  button_type = None

  # should be CV.MPH_TO_KPH, but this causes rounding errors
  v_cruise_delta = 1. if metric else 1.6
  v_cruise_delta_multiplier = 10 if metric else 5

  for b in buttonEvents:
    if b.type.raw in button_timers and not b.pressed:
      if button_timers[b.type.raw] > CRUISE_LONG_PRESS:
        return v_cruise_kph  # end long press
      button_type = b.type.raw
      break
  else:
    for k in button_timers.keys():
      if button_timers[k] and button_timers[k] % CRUISE_LONG_PRESS == 0:
        button_type = k
        long_press = True
        break

  if button_type:
    if reverse_acc_change:
      v_cruise_delta = v_cruise_delta * (1 if long_press else v_cruise_delta_multiplier)
      if not long_press and v_cruise_kph % v_cruise_delta != 0: # partial interval
        v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](v_cruise_kph / v_cruise_delta) * v_cruise_delta
      else:
        v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]
    else:
      v_cruise_delta = v_cruise_delta * (v_cruise_delta_multiplier if long_press else 1)
      if long_press and v_cruise_kph % v_cruise_delta != 0:  # partial interval
        v_cruise_kph = CRUISE_NEAREST_FUNC[button_type](v_cruise_kph / v_cruise_delta) * v_cruise_delta
      else:
        v_cruise_kph += v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if gas_pressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      v_cruise_kph = max(v_cruise_kph, v_ego * CV.MS_TO_KPH)

    v_cruise_kph = clip(round(v_cruise_kph, 1), V_CRUISE_MIN, V_CRUISE_MAX)

  return v_cruise_kph


def update_v_cruise_honda(v_cruise_kph, buttonEvents, enabled, cur_time, accel_pressed, decel_pressed,
                          accel_pressed_last, decel_pressed_last, fastMode):

  reverse_acc_change = Params().get_bool("ReverseAccChange")
  if enabled:
    if accel_pressed:
      if (cur_time-accel_pressed_last) >= 1 or (fastMode and (cur_time-accel_pressed_last) >= 0.5):
        if reverse_acc_change:
          v_cruise_kph += 1
        else:
          v_cruise_kph += V_CRUISE_DELTA_HONDA - (v_cruise_kph % V_CRUISE_DELTA_HONDA)
    elif decel_pressed:
      if (cur_time-decel_pressed_last) >= 1 or (fastMode and (cur_time-decel_pressed_last) >= 0.5):
        if reverse_acc_change:
          v_cruise_kph -= 1
        else:
          v_cruise_kph -= V_CRUISE_DELTA_HONDA - ((V_CRUISE_DELTA_HONDA - v_cruise_kph) % V_CRUISE_DELTA_HONDA)
    else:
      for b in buttonEvents:
        if not b.pressed:
          if b.type == car.CarState.ButtonEvent.Type.accelCruise:
            if not fastMode:
              if reverse_acc_change:
                v_cruise_kph += V_CRUISE_DELTA_HONDA - (v_cruise_kph % V_CRUISE_DELTA_HONDA)
              else:
                v_cruise_kph += 1
          elif b.type == car.CarState.ButtonEvent.Type.decelCruise:
            if not fastMode:
              if reverse_acc_change:
                v_cruise_kph -= V_CRUISE_DELTA_HONDA - ((V_CRUISE_DELTA_HONDA - v_cruise_kph) % V_CRUISE_DELTA_HONDA)
              else:
                v_cruise_kph -= 1
    v_cruise_kph = clip(v_cruise_kph, V_CRUISE_MIN_HONDA, V_CRUISE_MAX)

  return v_cruise_kph


def initialize_v_cruise(v_ego, buttonEvents, v_cruise_last, metric):
  for b in buttonEvents:
    # 250kph or above probably means we never had a set speed
    if b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) and v_cruise_last < 250:
      return v_cruise_last

  return int(round(clip(v_ego * CV.MS_TO_KPH, V_CRUISE_ENABLE_MIN_KPH if metric else V_CRUISE_ENABLE_MIN_MPH, V_CRUISE_MAX)))


def get_lag_adjusted_curvature(CP, v_ego, psis, curvatures, curvature_rates):
  if len(psis) != CONTROL_N:
    psis = [0.0]*CONTROL_N
    curvatures = [0.0]*CONTROL_N
    curvature_rates = [0.0]*CONTROL_N
  v_ego = max(MIN_SPEED, v_ego)

  # TODO this needs more thought, use .2s extra for now to estimate other delays
  delay = CP.steerActuatorDelay + .2

  # MPC can plan to turn the wheel and turn back before t_delay. This means
  # in high delay cases some corrections never even get commanded. So just use
  # psi to calculate a simple linearization of desired curvature
  current_curvature_desired = curvatures[0]
  psi = interp(delay, T_IDXS[:CONTROL_N], psis)
  average_curvature_desired = psi / (v_ego * delay)
  desired_curvature = 2 * average_curvature_desired - current_curvature_desired

  # This is the "desired rate of the setpoint" not an actual desired rate
  desired_curvature_rate = curvature_rates[0]
  max_curvature_rate = MAX_LATERAL_JERK / (v_ego**2) # inexact calculation, check https://github.com/commaai/openpilot/pull/24755
  safe_desired_curvature_rate = clip(desired_curvature_rate,
                                     -max_curvature_rate,
                                     max_curvature_rate)
  safe_desired_curvature = clip(desired_curvature,
                                current_curvature_desired - max_curvature_rate * DT_MDL,
                                current_curvature_desired + max_curvature_rate * DT_MDL)

  return safe_desired_curvature, safe_desired_curvature_rate
