"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import numpy as np

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL


CURVE_OUTWARD_DEADZONE = 0.0005  # 1/m
CURVE_OUTWARD_SPEED_BP = [30.0, 40.0, 50.0, 60.0, 70.0, 90.0, 100.0, 120.0]  # km/h
# Conservative, outward-only schedule: no added steering at low speed; fades to 15.5% less curvature at highway speed.
CURVE_OUTWARD_FRACTION = [0.0, 0.0, 0.04, 0.07, 0.09, 0.155, 0.155, 0.155]

LANE_CENTER_MIN_SPEED = 8.0  # m/s
LANE_CENTER_FADE_SPEED_BP = [19.4, 22.2]  # m/s (70-80 km/h)
LANE_CENTER_MIN_LINE_PROB = 0.5
LANE_CENTER_WIDTH_PROB = 0.6
LANE_CENTER_WIDTH_RANGE = (2.6, 4.6)  # m
LANE_CENTER_WIDTH_TOL = 0.7  # m
LANE_CENTER_FIT_RANGE = 12.0  # m
LANE_CENTER_FILTER_TAU = 0.5  # s
LANE_CENTER_WIDTH_TAU = 3.0  # s
LANE_CENTER_DEADBAND = 0.03  # m
LANE_CENTER_KP = 0.25  # m/s^2 per metre of offset
LANE_CENTER_KD = 0.8  # m/s^2 per m/s of lateral motion
LANE_CENTER_KI = 0.02  # m/s^2 per metre-second
LANE_CENTER_I_LIMIT = 0.15  # m/s^2
LANE_CENTER_MAX_LAT_ACCEL = 0.3  # m/s^2
LANE_CENTER_MAX_CURV = 2.5e-3  # 1/m
LANE_CENTER_MAX_JERK = 0.25  # m/s^3


def apply_curve_outward_bias(desired_curvature: float, v_ego: float) -> float:
  """Reduce high-speed turn curvature slightly to counter a path that cuts inside the lane."""
  if not math.isfinite(desired_curvature) or not math.isfinite(v_ego):
    return desired_curvature
  speed_kph = v_ego * 3.6
  fraction = float(np.interp(speed_kph, CURVE_OUTWARD_SPEED_BP, CURVE_OUTWARD_FRACTION))
  if abs(desired_curvature) <= CURVE_OUTWARD_DEADZONE:
    return desired_curvature
  return desired_curvature * (1.0 - fraction)


class LaneCentering:
  """Small, capped curvature correction from reliable lane-line geometry."""

  def __init__(self, dt: float = DT_CTRL):
    self.dt = dt
    self.offset_filter = FirstOrderFilter(0.0, LANE_CENTER_FILTER_TAU, dt)
    self.heading_filter = FirstOrderFilter(0.0, LANE_CENTER_FILTER_TAU, dt)
    self.width_filter = FirstOrderFilter(0.0, LANE_CENTER_WIDTH_TAU, dt)
    self.integral = 0.0
    self.correction = 0.0
    self.valid = False

  def measure(self, model_v2) -> tuple[float, float] | None:
    """Return lane-centre offset and heading; positive values mean the car is left of lane centre."""
    if model_v2 is None:
      return None

    lines = model_v2.laneLines
    probs = model_v2.laneLineProbs
    if len(lines) < 3 or len(probs) < 3 or len(lines[1].x) < 4 or len(lines[1].y) < 4 or len(lines[2].y) < 4:
      return None
    if min(probs[1], probs[2]) < LANE_CENTER_MIN_LINE_PROB:
      return None

    yl = np.asarray(lines[1].y, dtype=float)
    yr = np.asarray(lines[2].y, dtype=float)
    x = np.asarray(lines[1].x, dtype=float)
    width = float(yr[0] - yl[0])
    if not LANE_CENTER_WIDTH_RANGE[0] <= width <= LANE_CENTER_WIDTH_RANGE[1]:
      return None
    if self.width_filter.x > 0.0 and abs(width - self.width_filter.x) > LANE_CENTER_WIDTH_TOL:
      return None
    if min(probs[1], probs[2]) >= LANE_CENTER_WIDTH_PROB:
      if self.width_filter.x > 0.0:
        self.width_filter.update(width)
      else:
        self.width_filter.x = width

    n = int(np.sum(x <= LANE_CENTER_FIT_RANGE))
    if n < 4:
      return None
    centre = (yl[:n] + yr[:n]) / 2.0  # model lateral y is positive to the right
    if not np.all(np.isfinite(x[:n])) or not np.all(np.isfinite(centre)):
      return None
    try:
      _, slope, offset_right = np.polyfit(x[:n], centre, 2)
    except (np.linalg.LinAlgError, ValueError):
      return None
    if not math.isfinite(offset_right) or not math.isfinite(slope):
      return None
    return float(offset_right), float(math.atan(slope))

  def update(self, model_v2, v_ego: float, active: bool, steering_pressed: bool) -> float:
    lane_change = model_v2 is not None and model_v2.meta.laneChangeState != 0
    usable = active and not steering_pressed and not lane_change and v_ego > LANE_CENTER_MIN_SPEED
    measurement = self.measure(model_v2) if usable else None
    step = LANE_CENTER_MAX_JERK / max(v_ego, LANE_CENTER_MIN_SPEED) ** 2 * self.dt

    if measurement is None:
      self.offset_filter.x = 0.0
      self.heading_filter.x = 0.0
      self.integral = 0.0
      self.valid = False
      self.correction = float(np.clip(0.0, self.correction - step, self.correction + step))
      return self.correction

    self.valid = True
    offset_right, heading_left = measurement
    offset_left = self.offset_filter.update(offset_right)
    heading_left = self.heading_filter.update(heading_left)
    # Model y is positive right: positive centre y means the car is left of centre.
    error = offset_left - float(np.clip(offset_left, -LANE_CENTER_DEADBAND, LANE_CENTER_DEADBAND))
    lateral_speed_left = v_ego * math.sin(heading_left)
    self.integral = float(np.clip(self.integral + LANE_CENTER_KI * error * self.dt,
                                  -LANE_CENTER_I_LIMIT, LANE_CENTER_I_LIMIT))
    lateral_accel = LANE_CENTER_KP * error + LANE_CENTER_KD * lateral_speed_left + self.integral
    lateral_accel = float(np.clip(lateral_accel, -LANE_CENTER_MAX_LAT_ACCEL, LANE_CENTER_MAX_LAT_ACCEL))
    target = float(np.clip(lateral_accel / max(v_ego, LANE_CENTER_MIN_SPEED) ** 2,
                           -LANE_CENTER_MAX_CURV, LANE_CENTER_MAX_CURV))
    target *= float(np.interp(v_ego, LANE_CENTER_FADE_SPEED_BP, [0.0, 1.0]))
    self.correction = float(np.clip(target, self.correction - step, self.correction + step))
    return self.correction


class LateralLaneAssist:
  """Per-setting opt-in wrapper for torque-controller-only lane corrections."""

  def __init__(self, dt: float = DT_CTRL, params: Params | None = None):
    params = params or Params()
    self.curve_bias_enabled = params.get_bool("LateralCurveCuttingCorrection")
    self.lane_centering_enabled = params.get_bool("LateralLaneCentering")
    self.lane_centering = LaneCentering(dt)

  def update(self, desired_curvature: float, v_ego: float, active: bool, steering_pressed: bool, model_v2) -> float:
    lane_change = model_v2 is not None and model_v2.meta.laneChangeState != 0
    if self.curve_bias_enabled and active and not steering_pressed and not lane_change:
      desired_curvature = apply_curve_outward_bias(desired_curvature, v_ego)
    if self.lane_centering_enabled:
      desired_curvature += self.lane_centering.update(model_v2, v_ego, active, steering_pressed)
    return desired_curvature
