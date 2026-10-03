"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

ONSET_T_BP = [0.0, 0.15, 0.6]  # s
ONSET_V_BP = [11.1, 16.7]  # m/s
ONSET_T1_V = [0.1, 0.1]
ONSET_T3_V = [0.4, 0.4]
ONSET_J_DOWN = [1.0, 1.0, 4.0]  # m/s^3
HARD_BRAKE_ACCEL = -2.0
URGENT_T = 0.1  # s
URGENT_J = 1.0  # m/s^3
URGENT_T_RAMP = 0.1  # s


class BrakeOnsetShaper:
  def __init__(self, dt: float, stock_down_jerk: float):
    self.dt = dt
    self.stock_down_jerk = stock_down_jerk
    self.t_onset = 0.0

  def reset(self) -> None:
    self.t_onset = 0.0

  @staticmethod
  def schedule_t(v_ego: float) -> list[float]:
    t1 = float(np.interp(v_ego, ONSET_V_BP, ONSET_T1_V))
    t3 = float(np.interp(v_ego, ONSET_V_BP, ONSET_T3_V))
    return [0.0, t1, t3]

  def down_step(self, accel_request: float, prev_accel: float, bypass: bool = False, v_ego: float = 30.0,
                urgent: bool = False) -> float:
    if bypass:
      self.t_onset = 0.0
      return -self.stock_down_jerk * self.dt

    if urgent:
      t_bp, j_bp = [0.0, URGENT_T, URGENT_T + max(URGENT_T_RAMP, self.dt)], [URGENT_J, URGENT_J, self.stock_down_jerk]
    else:
      t_bp, j_bp = self.schedule_t(v_ego), ONSET_J_DOWN
    gentlest_step = -ONSET_J_DOWN[0] * self.dt
    onset = (accel_request - prev_accel) < gentlest_step - 1e-9
    if onset:
      j_down = float(np.interp(self.t_onset, t_bp, j_bp))
      self.t_onset = min(self.t_onset + self.dt, t_bp[-1])
    else:
      j_down = self.stock_down_jerk
      self.t_onset = max(self.t_onset - self.dt, 0.0)
    return -min(j_down, self.stock_down_jerk) * self.dt

  def is_urgent(self, accel_request: float, fcw: bool) -> bool:
    return fcw or accel_request < HARD_BRAKE_ACCEL

ENGAGE_T_BP = [0.0, 0.1, 0.6]  # s
ENGAGE_J_UP = [0.25, 0.6, 4.0]  # m/s^3


class EngageOnsetShaper:
  def __init__(self, dt: float, stock_up_jerk: float):
    self.dt = dt
    self.stock_up_jerk = stock_up_jerk
    self.t_engaged: float | None = None

  def reset(self) -> None:
    self.t_engaged = None

  @property
  def in_engage_window(self) -> bool:
    return self.t_engaged is None or self.t_engaged < ENGAGE_T_BP[-1]

  def up_step(self, active: bool) -> float:
    if not active:
      self.t_engaged = None
      return self.stock_up_jerk * self.dt
    if self.t_engaged is None:
      self.t_engaged = 0.0
    else:
      self.t_engaged += self.dt
    if self.t_engaged >= ENGAGE_T_BP[-1]:
      return self.stock_up_jerk * self.dt
    j_up = float(np.interp(self.t_engaged, ENGAGE_T_BP, ENGAGE_J_UP))
    return min(j_up, self.stock_up_jerk) * self.dt