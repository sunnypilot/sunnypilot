"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.common.realtime import DT_MDL

_BRAKE_JERK = 1.4
_RELEASE_JERK = 0.8
_ACTIVATION_JERK = 1.2
_ACTIVATION_DELTA = 0.15
_LEAD_LOSS_HOLD_TIME = 0.2
_PREVIEW_START_TIME = 0.5
_CONFIRMATION_FRAMES = 2


class MpcComfortController:
  def __init__(self, dt: float = DT_MDL):
    self.dt = dt
    self._a_target: float | None = None
    self._last_raw_target: float | None = None
    self._confirmation_frames = 0
    self._hold_frames = 0

  @property
  def active(self) -> bool:
    return self._a_target is not None

  def reset(self) -> None:
    self._a_target = None
    self._last_raw_target = None
    self._confirmation_frames = 0
    self._hold_frames = 0

  def update(self, a_target: float, a_trajectory, t_idxs, lead_present: bool, a_min: float, reset: bool = False) -> float:
    if reset:
      self.reset()
      return a_target

    a_trajectory = np.asarray(a_trajectory, dtype=float)
    t_idxs = np.asarray(t_idxs, dtype=float)
    if (
      len(a_trajectory) != len(t_idxs)
      or not np.isfinite(a_target)
      or not np.isfinite(a_min)
      or not np.all(np.isfinite(a_trajectory))
      or not np.all(np.isfinite(t_idxs))
    ):
      self.reset()
      return a_target

    future_a = a_trajectory[t_idxs >= _PREVIEW_START_TIME]
    if len(future_a) == 0:
      self.reset()
      return a_target

    previous_raw_target = self._last_raw_target
    self._last_raw_target = a_target
    preview_a = max(float(np.min(future_a)), a_min)
    preview_requested = lead_present and preview_a < a_target - _ACTIVATION_DELTA

    if self._a_target is None:
      raw_target_falling = previous_raw_target is not None and a_target - previous_raw_target < -_ACTIVATION_JERK * self.dt
      if raw_target_falling:
        self._confirmation_frames = 0
        return a_target

      self._confirmation_frames = self._confirmation_frames + 1 if preview_requested else 0
      if self._confirmation_frames < _CONFIRMATION_FRAMES:
        return a_target
      self._a_target = a_target

    # Never delay braking requested by MPC.
    if a_target < self._a_target:
      self.reset()
      return a_target

    if preview_requested and preview_a <= self._a_target:
      self._hold_frames = round(_LEAD_LOSS_HOLD_TIME / self.dt)
      self._a_target = max(preview_a, self._a_target - _BRAKE_JERK * self.dt)
    elif self._hold_frames > 0:
      self._hold_frames -= 1
    else:
      release_target = preview_a if preview_requested else a_target
      self._a_target = min(release_target, self._a_target + _RELEASE_JERK * self.dt)

    if self._a_target >= a_target:
      self.reset()
      return a_target

    return self._a_target
