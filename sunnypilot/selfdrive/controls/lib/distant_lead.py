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

# 1s was too long: ghost tracks with smaller dRel blocked real leads for ~1s.
_RELEASE_SECONDS = 0.25
_RELEASE_FRAMES = max(1, int(round(_RELEASE_SECONDS / DT_MDL)))

_MIN_FORWARD_SPEED = 1.0  # m/s
_MIN_DREL = 2.0           # m
_MIN_V_EGO = 4.0          # m/s

_CLOSE_DREL_MAX = 25.0    # m
_CLOSE_CONFIRM_FRAMES = max(1, int(round(0.5 / DT_MDL)))
_CLOSE_HOLDOVER_FRAMES = max(1, int(round(2.0 / DT_MDL)))
_CLOSE_OVERRIDE_DREL = 25.0  # m


class DistantLeadDetector:
  def __init__(self) -> None:
    self._streak: dict[int, int] = {}
    self._release: dict[int, int] = {}

    self._close_tid: int | None = None
    self._close_streak: int = 0
    self._close_holdover: int = 0

  def detect(self, tracks: dict, model_data: capnp._DynamicStructReader, v_ego: float = 0.0,
             lead_one_drel: float = 0.0, lead_one_status: bool = False):
    if v_ego < _MIN_V_EGO:
      self._streak = {}
      self._release = {}
      self._close_tid = None
      self._close_streak = 0
      self._close_holdover = 0
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
        next_release[tid] = _RELEASE_FRAMES
      elif qualifies and in_holdover:
        next_release[tid] = _RELEASE_FRAMES
        promoted = True
      elif not qualifies and in_holdover:
        next_release[tid] = self._release[tid] - 1
        promoted = True

      if promoted:
        if chosen is None or track.dRel < chosen.dRel:
          chosen = track

    self._streak = next_streak
    self._release = next_release

    if self._close_tid is not None and self._close_tid in tracks:
      if tracks[self._close_tid].dRel < _CLOSE_DREL_MAX:
        self._close_streak += 1
        self._close_holdover = _CLOSE_HOLDOVER_FRAMES
      else:
        self._close_streak = 0
        self._close_holdover = max(0, self._close_holdover - 1)
    else:
      self._close_streak = 0
      self._close_holdover = max(0, self._close_holdover - 1)

    for tid, track in tracks.items():
      if track.dRel < _CLOSE_DREL_MAX and tid in next_streak and next_streak[tid] >= _CLOSE_CONFIRM_FRAMES:
        if self._close_tid != tid:
          self._close_tid = tid
          self._close_streak = next_streak[tid]
          self._close_holdover = _CLOSE_HOLDOVER_FRAMES
        break

    if self._close_holdover > 0 and self._close_tid is not None and self._close_tid in tracks:
      if not lead_one_status or lead_one_drel > _CLOSE_OVERRIDE_DREL:
        return tracks[self._close_tid]

    return chosen
