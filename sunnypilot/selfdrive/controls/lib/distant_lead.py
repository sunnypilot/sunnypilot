"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from dataclasses import dataclass

import capnp
import numpy as np

from openpilot.common.realtime import DT_MDL


CONFIRM_FRAMES = max(1, int(round(0.5 / DT_MDL)))
RELEASE_FRAMES = max(1, int(round(0.25 / DT_MDL)))

MIN_FORWARD_SPEED = 1.0
MIN_DREL          = 2.0
MIN_V_EGO         = 4.0

CLOSE_DREL_MAX        = 25.0
CLOSE_CONFIRM_FRAMES  = max(1, int(round(0.5 / DT_MDL)))
CLOSE_HOLDOVER_FRAMES = max(1, int(round(2.0 / DT_MDL)))
CLOSE_OVERRIDE_DREL   = 25.0

# Hold the last selected (chosen or override) Track across short radar
# dropouts so a 1-3 frame absence does not collapse the override and force
# lead_one back to vision-only or to a freshly initialized track on the
# radard side. Python keeps the Track object alive via reference even after
# radard pops it from its own dict; we keep reading its last Kalman state.
SELECT_HOLDOVER_FRAMES = max(1, int(round(0.15 / DT_MDL)))

# Bias the chosen track's aLeadTau using the model's predicted lead acceleration
# horizon (modelV2.leadsV3[0].a[1]). When a[1] agrees with a[0] in direction and
# magnitude, nudge the FirstOrderFilter so MPC's extrapolate_lead persists
# (sustained brake) or decays (spurious brake). Ambiguous frames return None and
# the heuristic tau stays in place — safe by construction.
_MODEL_TAU_MIN_PROB  = 0.5
_MODEL_TAU_BRAKE_A   = -0.5
_MODEL_TAU_SUSTAINED = 0.5  # small tau = accel persists in MPC horizon
_MODEL_TAU_SPURIOUS  = 3.0  # large tau = accel decays fast


def _model_lead_tau(lead_msg) -> float | None:
  if lead_msg.prob < _MODEL_TAU_MIN_PROB or len(lead_msg.a) < 2:
    return None
  a0 = float(lead_msg.a[0])
  a1 = float(lead_msg.a[1])
  if a0 > _MODEL_TAU_BRAKE_A:
    return None
  if a1 < 0.5 * a0:
    return _MODEL_TAU_SUSTAINED
  if a1 > 0.1 * a0:
    return _MODEL_TAU_SPURIOUS
  return None


@dataclass
class CloseLead:
  tid: int | None = None
  streak: int = 0
  holdover: int = 0

  def reset(self) -> None:
    self.tid = None
    self.streak = 0
    self.holdover = 0

  def decay(self) -> None:
    self.streak = 0
    self.holdover = max(0, self.holdover - 1)

  def alive(self) -> bool:
    return self.holdover > 0 and self.tid is not None


def _in_lane(track, left_x, left_y, right_x, right_y) -> bool:
  return bool(np.interp(track.dRel, left_x, left_y) < -track.yRel < np.interp(track.dRel, right_x, right_y))


class DistantLeadDetector:
  def __init__(self) -> None:
    self._streak: dict[int, int] = {}
    self._release: dict[int, int] = {}
    self._close = CloseLead()
    self._last_selected = None
    self._absent_count = 0

  def detect(self, tracks: dict, model_data: capnp._DynamicStructReader, v_ego: float = 0.0,
             lead_one_drel: float = 0.0, lead_one_status: bool = False):
    if v_ego < MIN_V_EGO:
      self._streak.clear()
      self._release.clear()
      self._close.reset()
      self._last_selected = None
      self._absent_count = 0
      return None

    horizon = model_data.position.x[-1]
    left_x  = model_data.laneLines[1].x
    left_y  = model_data.laneLines[1].y
    right_x = model_data.laneLines[2].x
    right_y = model_data.laneLines[2].y

    chosen = self._promote_distant(tracks, horizon, left_x, left_y, right_x, right_y)
    self._update_close(tracks, left_x, left_y, right_x, right_y)

    override = self._close_override(tracks, left_x, left_y, right_x, right_y,
                                    lead_one_drel, lead_one_status)
    selected = override if override is not None else chosen

    if selected is not None:
      self._last_selected = selected
      self._absent_count = 0
    elif self._last_selected is not None:
      self._absent_count += 1
      if self._absent_count > SELECT_HOLDOVER_FRAMES:
        self._last_selected = None
        self._absent_count = 0
      else:
        selected = self._last_selected

    if selected is not None and len(model_data.leadsV3):
      model_tau = _model_lead_tau(model_data.leadsV3[0])
      if model_tau is not None:
        selected.aLeadTau.update(model_tau)
    return selected

  def _promote_distant(self, tracks: dict, horizon: float,
                       left_x, left_y, right_x, right_y):
    next_streak: dict[int, int] = {}
    next_release: dict[int, int] = {}
    chosen = None

    for tid, track in tracks.items():
      qualifies = (
        track.vLeadK > MIN_FORWARD_SPEED
        and MIN_DREL < track.dRel < horizon
        and _in_lane(track, left_x, left_y, right_x, right_y)
      )

      streak = self._streak.get(tid, 0) + 1 if qualifies else 0
      next_streak[tid] = streak

      promoted = streak >= CONFIRM_FRAMES
      in_holdover = self._release.get(tid, 0) > 0

      if promoted and qualifies:
        next_release[tid] = RELEASE_FRAMES
      elif qualifies and in_holdover:
        next_release[tid] = RELEASE_FRAMES
        promoted = True
      elif not qualifies and in_holdover:
        next_release[tid] = self._release[tid] - 1
        promoted = True

      if promoted and (chosen is None or track.dRel < chosen.dRel):
        chosen = track

    self._streak = next_streak
    self._release = next_release
    return chosen

  def _update_close(self, tracks: dict, left_x, left_y, right_x, right_y) -> None:
    if self._close.tid is not None and self._close.tid in tracks:
      ct = tracks[self._close.tid]
      if ct.dRel < CLOSE_DREL_MAX and _in_lane(ct, left_x, left_y, right_x, right_y):
        self._close.streak += 1
        self._close.holdover = CLOSE_HOLDOVER_FRAMES
      else:
        self._close.decay()
    else:
      self._close.decay()

    for tid, track in tracks.items():
      if (track.dRel < CLOSE_DREL_MAX
          and self._streak.get(tid, 0) >= CLOSE_CONFIRM_FRAMES
          and self._close.tid != tid):
        self._close.tid = tid
        self._close.streak = self._streak[tid]
        self._close.holdover = CLOSE_HOLDOVER_FRAMES
        break

  def _close_override(self, tracks: dict, left_x, left_y, right_x, right_y,
                      lead_one_drel: float, lead_one_status: bool):
    if not self._close.alive():
      return None
    if self._close.tid not in tracks:
      return None
    ct = tracks[self._close.tid]
    if not _in_lane(ct, left_x, left_y, right_x, right_y):
      return None
    if not lead_one_status or lead_one_drel > CLOSE_OVERRIDE_DREL:
      return ct
    return None
