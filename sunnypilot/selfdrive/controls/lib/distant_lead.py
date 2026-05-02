"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
import capnp

from openpilot.common.realtime import DT_MDL

_CONFIRM_SECONDS = 0.5
_CONFIRM_FRAMES = max(1, int(round(_CONFIRM_SECONDS / DT_MDL)))

# Hold a promoted track for 0.25s after it stops qualifying just enough to
# absorb single-frame lane-line jitter without blocking new lead detection.
# 1s was too long: ghost tracks with smaller dRel blocked real leads for ~1s.
_RELEASE_SECONDS = 0.25
_RELEASE_FRAMES = max(1, int(round(_RELEASE_SECONDS / DT_MDL)))

_MIN_FORWARD_SPEED = 1.0  # m/s — discard stationary or wrong-way radar returns
_MIN_DREL = 2.0           # m — tracks closer than this are almost always glitches
_MIN_V_EGO = 4.0          # m/s — disable at very low speed where radar clutter peaks


class DistantLeadDetector:
  def __init__(self) -> None:
    self._streak: dict[int, int] = {}
    self._release: dict[int, int] = {}  # countdown frames before dropping a promoted track

  def detect(self, tracks: dict, model_data: capnp._DynamicStructReader, v_ego: float = 0.0):
    if v_ego < _MIN_V_EGO:
      self._streak = {}
      self._release = {}
      return None

    horizon = model_data.position.x[-1]
    left_x = model_data.laneLines[1].x
    left_y = model_data.laneLines[1].y
    right_x = model_data.laneLines[2].x
    right_y = model_data.laneLines[2].y

    next_streak: dict[int, int] = {}
    next_release: dict[int, int] = {}
    chosen = None

    for tid, track in tracks.items():
      in_lane = np.interp(track.dRel, left_x, left_y) < -track.yRel < np.interp(track.dRel, right_x, right_y)
      qualifies = track.vLeadK > _MIN_FORWARD_SPEED and _MIN_DREL < track.dRel < horizon and in_lane

      streak = self._streak.get(tid, 0) + 1 if qualifies else 0
      next_streak[tid] = streak

      promoted = streak >= _CONFIRM_FRAMES
      in_holdover = self._release.get(tid, 0) > 0

      if promoted and qualifies:
        # Fully promoted and still qualifying — refresh holdover window
        next_release[tid] = _RELEASE_FRAMES
      elif qualifies and in_holdover:
        # Re-qualifies during holdover — restore immediately, no need to rebuild streak
        next_release[tid] = _RELEASE_FRAMES
        promoted = True
      elif not qualifies and in_holdover:
        # Was promoted, briefly disqualified — decrement holdover countdown
        next_release[tid] = self._release[tid] - 1
        promoted = True

      if promoted:
        if chosen is None or track.dRel < chosen.dRel:
          chosen = track

    self._streak = next_streak
    self._release = next_release
    return chosen
