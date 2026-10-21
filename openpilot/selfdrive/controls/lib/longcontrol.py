import numpy as np
from opendbc.car.structs import car
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.common.pid import PIDController
from openpilot.selfdrive.modeld.constants import ModelConstants

CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]

LongCtrlState = car.CarControl.Actuators.LongControlState

STOPPING_JERK_MIN = 0.3  # m/s^3
STOPPING_JERK_MAX = 2.0  # m/s^3
STOPPING_HOLD_SPEED = 0.05  # m/s, below this ramp into the standstill hold
STOPPING_HOLD_JERK = 1.0  # m/s^3, command ramp rate for the standstill hold
STOPPING_EXIT_FRAMES = 15  # 0.15 s at 100 Hz, debounce should_stop at standstill


def long_control_state_trans(CP_SP, active, long_control_state,
                             should_stop, brake_pressed, cruise_standstill):
  # Gas Interceptor
  cruise_standstill = cruise_standstill and not CP_SP.enableGasInterceptor

  starting_condition = (not should_stop and
                        not cruise_standstill and
                        not brake_pressed)

  if not active:
    long_control_state = LongCtrlState.off

  else:
    if long_control_state == LongCtrlState.off:
      if not starting_condition:
        long_control_state = LongCtrlState.stopping
      else:
        long_control_state = LongCtrlState.pid

    elif long_control_state == LongCtrlState.stopping:
      if starting_condition:
        long_control_state = LongCtrlState.pid

    elif long_control_state == LongCtrlState.pid:
      if should_stop:
        long_control_state = LongCtrlState.stopping

  return long_control_state

class LongControl:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.long_control_state = LongCtrlState.off
    self.pid = PIDController(0.0, (CP.longitudinalTuning.kiBP, CP.longitudinalTuning.kiV),
                             rate=1 / DT_CTRL)
    self.last_output_accel = 0.0
    self.stopping_jerk = STOPPING_JERK_MIN
    self.stopping_exit_frames = 0

  def reset(self):
    self.pid.reset()

  def _stopping_accel(self, v_ego, standstill):
    v_ego = max(float(v_ego), 0.0)
    if standstill or v_ego < STOPPING_HOLD_SPEED:
      goal = float(self.CP.stopAccel)
      jerk = STOPPING_HOLD_JERK
    else:
      taper = -np.sqrt(2.0 * self.stopping_jerk * v_ego)
      goal = max(self.last_output_accel, taper) if self.last_output_accel < 0.0 else taper
      jerk = self.stopping_jerk

    output_accel = np.clip(min(goal, 0.0), self.last_output_accel - jerk * DT_CTRL,
                           self.last_output_accel + jerk * DT_CTRL)
    return float(output_accel)

  def update(self, active, CS, a_target, should_stop, accel_limits):
    """Update longitudinal control. This updates the state machine and runs a PID loop"""
    self.pid.neg_limit = accel_limits[0]
    self.pid.pos_limit = accel_limits[1]

    if self.long_control_state == LongCtrlState.stopping and not should_stop:
      self.stopping_exit_frames += 1
    else:
      self.stopping_exit_frames = 0
    should_stop_trans = should_stop or (self.long_control_state == LongCtrlState.stopping and
                                        self.stopping_exit_frames < STOPPING_EXIT_FRAMES)

    prev_state = self.long_control_state
    self.long_control_state = long_control_state_trans(self.CP_SP, active, self.long_control_state,
                                                       should_stop_trans, CS.brakePressed,
                                                       CS.cruiseState.standstill)

    if self.long_control_state == LongCtrlState.stopping and prev_state != LongCtrlState.stopping:
      entry_v = max(float(CS.vEgo), STOPPING_HOLD_SPEED)
      entry_a = min(float(self.last_output_accel), 0.0)
      if entry_a == 0.0:
        entry_a = min(float(a_target), 0.0)
      self.stopping_jerk = float(np.clip(entry_a ** 2 / (2.0 * entry_v),
                                         STOPPING_JERK_MIN, STOPPING_JERK_MAX))

    if self.long_control_state == LongCtrlState.off:
      self.reset()
      output_accel = 0.

    elif self.long_control_state == LongCtrlState.stopping:
      output_accel = self._stopping_accel(CS.vEgo, CS.standstill)
      self.reset()

    else:  # LongCtrlState.pid
      error = a_target - CS.aEgo
      output_accel = self.pid.update(error, speed=CS.vEgo,
                                     feedforward=a_target)

    self.last_output_accel = np.clip(output_accel, accel_limits[0], accel_limits[1])
    return self.last_output_accel
