"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

# Asymmetric speed-scaled curvature rate limit, mirroring apply_std_steer_angle_limits
# used by angle-control cars. Tuned from Toyota LTA (wheelbase 2.7m, steerRatio 14)
# converted to curvature space. Wind-up (|curv| increasing) limited tighter than unwind.
_RATE_BP = [5.0, 25.0]                       # m/s
_WIND_UP_RATE = [0.000139, 0.0000693]        # 1/m per DT_CTRL frame (100 Hz)
_UNWIND_RATE = [0.00060, 0.00030]            # 1/m per DT_CTRL frame (100 Hz) - loose toward 0 for fast unwind


def angle_like_clip_curvature(v_ego: float, prev_curvature: float, new_curvature: float) -> float:
  is_winding = abs(new_curvature) > abs(prev_curvature)
  rate_v = _WIND_UP_RATE if is_winding else _UNWIND_RATE
  rate = float(np.interp(v_ego, _RATE_BP, rate_v))
  return float(np.clip(new_curvature, prev_curvature - rate, prev_curvature + rate))


class CurvaturePreFilteredLatControl:
  """Wraps a LatControl so the commanded desired_curvature gets an asymmetric
  speed-scaled rate-limit applied before it reaches the inner controller.
  Mimics what angle-control cars do natively. All other attribute access
  delegates to the wrapped controller."""

  def __init__(self, inner):
    self._inner = inner
    self._prev_curvature: float | None = None

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature,
             calibrated_pose, curvature_limited, lat_delay):
    if self._prev_curvature is None:
      filtered = desired_curvature
    else:
      filtered = angle_like_clip_curvature(CS.vEgo, self._prev_curvature, desired_curvature)
    self._prev_curvature = filtered
    return self._inner.update(active, CS, VM, params, steer_limited_by_safety, filtered,
                              calibrated_pose, curvature_limited, lat_delay)

  def reset(self):
    self._prev_curvature = None
    self._inner.reset()
    ext = getattr(self._inner, 'extension', None)
    if ext is not None and hasattr(ext, 'reset_state'):
      ext.reset_state()

  def __getattr__(self, name):
    return getattr(self._inner, name)
