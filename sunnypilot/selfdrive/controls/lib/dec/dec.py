# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Version = 2025-1-18

import numpy as np

from cereal import messaging
from opendbc.car import structs
from numpy import interp
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants

# d-e2e, from modeldata.h
TRAJECTORY_SIZE = 33
SET_MODE_TIMEOUT = 10


class KalmanFilter:
  """
  Simple one-dimensional Kalman filter implementation with forgetting factor.
  - x: state estimate
  - P: error covariance
  - R: measurement error (uncertainty in measurements)
  - Q: process noise (uncertainty in system dynamics)
  - alpha: forgetting factor (1.0 = no forgetting, >1.0 = forget old data faster)
  - window_size_equivalent: approx window size this filter behavior matches
  """
  def __init__(self, initial_value=0, initial_estimate_error=1.0, measurement_noise=0.1,
               process_noise=0.01, alpha=1.0, window_size_equivalent=None):
    # State estimate
    self.x = initial_value
    # Error covariance
    self.P = initial_estimate_error
    # Measurement noise
    self.R = measurement_noise
    # Process noise
    self.Q = process_noise
    # Forgetting factor (>1.0 means forget old data faster)
    self.alpha = alpha
    # Whether the filter has been initialized with data
    self.initialized = False
    # History of most recent measurements for debugging and adaptive behavior
    self.history = []
    self.max_history = 10
    # For diagnostic purposes
    self.window_size_equivalent = window_size_equivalent

  def add_data(self, measurement):
    # Keep track of some history for debugging
    if len(self.history) >= self.max_history:
      self.history.pop(0)
    self.history.append(measurement)

    if not self.initialized:
      self.x = measurement
      self.initialized = True
      return

    # Prediction step (state extrapolation)
    # x = x (no system dynamics in this simple implementation)
    # Error covariance extrapolation with forgetting factor
    self.P = self.alpha * self.P + self.Q

    # Update step
    # Compute Kalman gain
    K = self.P / (self.P + self.R)
    # Update state estimate with measurement
    self.x = self.x + K * (measurement - self.x)
    # Update error covariance
    self.P = (1 - K) * self.P

  def get_value(self):
    return self.x if self.initialized else None

  def get_recent_trend(self):
    """Return the trend from recent data, -1 (decreasing), 0 (stable), 1 (increasing)"""
    if len(self.history) < 3:
      return 0

    # Simple trend detector based on recent history
    recent = self.history[-3:]
    if recent[2] > recent[0] + 0.05:  # Increasing with threshold
      return 1
    elif recent[0] > recent[2] + 0.05:  # Decreasing with threshold
      return -1
    return 0

  def reset_data(self):
    self.initialized = False
    self.history = []


class DynamicExperimentalController:
  def __init__(self, CP: structs.CarParams, mpc, params=None):
    self._CP = CP
    self._mpc = mpc
    self._params = params or Params()
    self._enabled: bool = self._params.get_bool("DynamicExperimentalControl")
    self._active: bool = False
    self._mode: str = 'acc'
    self._frame: int = 0
    self._urgency = 0.0

    # Using Kalman filters for improved filtering

    # Lead vehicle tracking - calibrated to match LEAD_WINDOW_SIZE=7
    self._lead_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=1.0,
      measurement_noise=0.25,  # Higher value -> more smoothing
      process_noise=0.08,      # Lower value -> more stable tracking
      alpha=1.03,              # Slight forgetting factor
      window_size_equivalent=WMACConstants.LEAD_WINDOW_SIZE
    )
    self._has_lead_filtered = False
    self._has_lead_filtered_prev = False

    # Slow down detection - calibrated to match SLOW_DOWN_WINDOW_SIZE=4
    self._slow_down_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=1.0,
      measurement_noise=0.4,   # Higher because we want smoother transitions
      process_noise=0.15,      # Balance responsiveness and stability
      alpha=1.05,              # Moderate forgetting factor for quick adaptation
      window_size_equivalent=WMACConstants.SLOW_DOWN_WINDOW_SIZE
    )
    self._has_slow_down: bool = False

    # Slowness detection - calibrated to match SLOWNESS_WINDOW_SIZE=10
    self._slowness_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=1.0,
      measurement_noise=0.18,  # Lower for faster response
      process_noise=0.08,      # Balanced for stability in speed measurements
      alpha=1.02,              # Slight forgetting factor
      window_size_equivalent=WMACConstants.SLOWNESS_WINDOW_SIZE
    )
    self._has_slowness: bool = False

    # For tracking lead vehicle distance
    self._lead_dist_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=5.0,  # Higher initial uncertainty
      measurement_noise=0.3,
      process_noise=2.0,           # Higher because distance can change rapidly
      alpha=1.1                    # Forget old distance measurements faster
    )
    self._lead_dist = 0.0

    # For tracking lead vehicle relative velocity
    self._lead_vel_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=2.0,
      measurement_noise=0.2,
      process_noise=1.0,           # Higher for velocity changes
      alpha=1.2                    # Forget old velocity measurements faster
    )
    self._lead_rel_vel = 0.0

    # Acceleration filter to detect rapid deceleration of lead
    self._lead_accel_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=1.0,
      measurement_noise=0.3,
      process_noise=2.0,           # Higher for acceleration changes
      alpha=1.3                    # Forget old acceleration data quickly
    )
    self._lead_accel = 0.0
    self._prev_lead_vel = 0.0

    # Trajectory curvature detection for curves
    self._curvature_filter = KalmanFilter(
      initial_value=0,
      initial_estimate_error=1.0,
      measurement_noise=0.4,
      process_noise=0.1,
      alpha=1.05
    )
    self._curvature = 0.0
    self._high_curvature = False

    self._v_ego_kph = 0.
    self._v_cruise_kph = 0.
    self._has_standstill = False
    self._set_mode_timeout = 0

  def _read_params(self) -> None:
    if self._frame % int(1. / DT_MDL) == 0:
      self._enabled = self._params.get_bool("DynamicExperimentalControl")

  def mode(self) -> str:
    return str(self._mode)

  def enabled(self) -> bool:
    return self._enabled

  def active(self) -> bool:
    return self._active

  def _update_calculations(self, sm: messaging.SubMaster) -> None:
    car_state = sm['carState']
    lead_one = sm['radarState'].leadOne
    md = sm['modelV2']

    self._v_ego_kph = car_state.vEgo * 3.6
    self._v_cruise_kph = car_state.vCruise
    self._has_standstill = car_state.standstill

    # Lead detection with Kalman filtering
    self._lead_filter.add_data(float(lead_one.status))
    lead_filtered_value = self._lead_filter.get_value() or 0.0
    self._has_lead_filtered = lead_filtered_value > WMACConstants.LEAD_PROB

    # Track lead vehicle parameters if present
    if lead_one.status:
      # Track lead distance
      self._lead_dist_filter.add_data(lead_one.dRel)
      self._lead_dist = self._lead_dist_filter.get_value() or 0.0

      # Track lead relative velocity
      self._lead_vel_filter.add_data(lead_one.vRel)
      current_vel = self._lead_vel_filter.get_value() or 0.0
      self._lead_rel_vel = current_vel

      # Calculate lead acceleration from velocity changes
      if self._prev_lead_vel != 0:
        accel = (current_vel - self._prev_lead_vel) / DT_MDL
        self._lead_accel_filter.add_data(accel)
        self._lead_accel = self._lead_accel_filter.get_value() or 0.0
      self._prev_lead_vel = current_vel

    # Calculate path curvature as a measure of how curvy the road ahead is
    if len(md.position.x) == len(md.position.y) == TRAJECTORY_SIZE:
      # Simple curvature calculation using the trajectory points
      # Using points at indices that allow seeing further ahead
      idx1, idx2, idx3 = 5, 15, 25  # Sample at different distances ahead

      if idx3 < TRAJECTORY_SIZE:
        try:
          # Calculate vectors between points
          v1x = md.position.x[idx2] - md.position.x[idx1]
          v1y = md.position.y[idx2] - md.position.y[idx1]
          v2x = md.position.x[idx3] - md.position.x[idx2]
          v2y = md.position.y[idx3] - md.position.y[idx2]

          # Calculate vector magnitudes
          mag1 = (v1x**2 + v1y**2)**0.5
          mag2 = (v2x**2 + v2y**2)**0.5

          if mag1 > 0.1 and mag2 > 0.1:  # Avoid division by near-zero
            # Calculate the dot product
            dot_product = v1x * v2x + v1y * v2y
            # Calculate the cosine of the angle
            cos_angle = dot_product / (mag1 * mag2)
            cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
            # Calculate the angle
            angle = np.arccos(cos_angle)
            # Normalize by the distance to get a curvature measure
            curvature = angle / ((mag1 + mag2) / 2)

            self._curvature_filter.add_data(curvature)
            self._curvature = self._curvature_filter.get_value() or 0.0
            self._high_curvature = self._curvature > 0.05  # Threshold for high curvature
        except Exception:
          pass  # Safely handle any numerical issues

    # Slow down detection
    slow_down_threshold = float(
      interp(self._v_ego_kph, WMACConstants.SLOW_DOWN_BP, WMACConstants.SLOW_DOWN_DIST)
    )

    curv_score = np.clip(self._curvature / 0.1, 0.0, 1.0)
    endpt_score = 0.0
    if len(md.orientation.x) == len(md.position.x) == TRAJECTORY_SIZE:
      endpoint_x = md.position.x[TRAJECTORY_SIZE - 1]
      endpt_score = np.clip((slow_down_threshold - endpoint_x) / 10.0, 0.0, 1.0)

    # Combine urgency from curvature + endpoint
    urgency = max(curv_score, endpt_score)

    # Apply Kalman filtering to slow down detection
    self._slow_down_filter.add_data(urgency)
    urgency_filtered = self._slow_down_filter.get_value() or 0.0

    # Final decision using probabilistic threshold
    self._has_slow_down = urgency_filtered > WMACConstants.SLOW_DOWN_PROB

    # use it for debug
    self._urgency = urgency_filtered


    # Slowness detection with Kalman filtering
    if not self._has_standstill:
      self._slowness_filter.add_data(float(self._v_ego_kph <= (self._v_cruise_kph * WMACConstants.SLOWNESS_CRUISE_OFFSET)))
      slowness_filtered_value = self._slowness_filter.get_value() or 0.0
      self._has_slowness = slowness_filtered_value > WMACConstants.SLOWNESS_PROB

    # Keep prev value for lead filtered
    self._has_lead_filtered_prev = self._has_lead_filtered

  def _radarless_mode(self) -> None:
    # Enhanced radarless mode implementation

    # When standstill: blended
    if self._has_standstill:
      self._set_mode('blended')
      return

    # When detecting slow down scenario: blended
    if self._has_slow_down:
      self._set_mode('blended')
      return

    # When high curvature is detected: use blended for better curve handling
    if self._high_curvature and self._v_ego_kph > 45.0:
      self._set_mode('blended')
      return

    # Car driving at speed lower than set speed: acc
    if self._has_slowness:
      self._set_mode('acc')
      return

    # Default to acc mode
    self._set_mode('acc')

  def _radar_mode(self) -> None:
    # Enhanced radar mode with lead distance and acceleration consideration

    # Advanced radar mode decision logic
    if self._has_lead_filtered:
      # Lead vehicle detected
      #  if self._has_standstill:
      #    # Vehicle is stopped
      #    self._set_mode('blended')
      #    return

      # Check for rapid deceleration of lead vehicle
      #  if self._lead_accel < -2.0:
      # Lead is braking hard, use blended mode for better response
      #    self._set_mode('blended')
      #    return

      # Check distance-based conditions
      #  if self._lead_dist < 30.0:
      # Lead is closer than 30m
      #    if self._lead_rel_vel < -1.0:
      # Lead is getting closer, use blended for more responsive braking
      #      self._set_mode('blended')
      #      return

      # Lead is close but not getting closer significantly
      # Use acc for smooth following
      #    self._set_mode('acc')
      #    return
      #  else:
      # Lead is far away, use normal acc behavior
      self._set_mode('acc')
      return

    # When detecting slow down scenario or high curvature: blended
    if self._has_slow_down:
      self._set_mode('blended')
      return

    # When standstill: blended
    if self._has_standstill:
      self._set_mode('blended')
      return

    # When high curvature is detected: use blended for better curve handling
    if self._high_curvature and self._v_ego_kph > 50.0:
      self._set_mode('blended')
      return

    # Car driving at speed lower than set speed: acc
    if self._has_slowness:
      self._set_mode('acc')
      return

    # Default to acc mode
    self._set_mode('acc')

  def _set_mode(self, mode: str) -> None:
    if self._set_mode_timeout == 0:
      self._mode = mode
      if mode == 'blended':
        self._set_mode_timeout = SET_MODE_TIMEOUT

    if self._set_mode_timeout > 0:
      self._set_mode_timeout -= 1

  def update(self, sm: messaging.SubMaster) -> None:
    self._read_params()
    self._update_calculations(sm)

    if self._CP.radarUnavailable:
      self._radarless_mode()
    else:
      self._radar_mode()

    self._active = sm['selfdriveState'].experimentalMode and self._enabled
    self._frame += 1