"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections import deque
import math
from typing import Any

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState


LEAD_DEPARTURE_MIN_SPEED = 0.3
LEAD_DEPARTURE_CONFIRM_FRAMES = 3
LEAD_DEPARTURE_MIN_DISTANCE = 0.03
LEAD_DEPARTURE_MAX_EGO_SPEED = 0.3

MpcPlanSource = log.LongitudinalPlan.LongitudinalPlanSource


class LeadDepartureController:
  def __init__(self, enabled: bool):
    self.enabled = enabled
    self._track_id: int | None = None
    self._distances: deque[float] = deque(maxlen=LEAD_DEPARTURE_CONFIRM_FRAMES)
    self._active = False

  @property
  def active(self) -> bool:
    return self._active

  def reset(self) -> None:
    self._track_id = None
    self._distances.clear()
    self._active = False

  @staticmethod
  def _selected_lead(radar_state: Any, source: Any) -> Any | None:
    if source == MpcPlanSource.lead0:
      return radar_state.leadOne
    if source == MpcPlanSource.lead1:
      return radar_state.leadTwo
    return None

  @staticmethod
  def _radar_has_errors(radar_state: Any) -> bool:
    errors = radar_state.radarErrors
    return errors.canError or errors.radarFault or errors.wrongConfig or errors.radarUnavailableTemporary

  def update(self, sm: Any, source: Any, a_target: float, should_stop: bool, reset: bool, radar_valid: bool) -> bool:
    CS = sm['carState']
    CC = sm['carControl']
    controls_state = sm['controlsState']
    radar_state = sm['radarState']

    blocked = (
      not self.enabled
      or reset
      or not CC.longActive
      or CC.cruiseControl.override
      or CS.gasPressed
      or CS.brakePressed
      or controls_state.forceDecel
      or controls_state.longControlState == LongCtrlState.off
      or not radar_valid
      or self._radar_has_errors(radar_state)
    )
    if blocked or not math.isfinite(CS.vEgo) or CS.vEgo >= LEAD_DEPARTURE_MAX_EGO_SPEED or not math.isfinite(a_target):
      self.reset()
      return should_stop

    lead = self._selected_lead(radar_state, source)
    lead_valid = (
      lead is not None
      and lead.present
      and lead.radar
      and lead.radarTrackId >= 0
      and all(math.isfinite(value) for value in (lead.dRel, lead.vLeadK, lead.vRel))
      and lead.dRel > 0.0
      and lead.vLeadK >= LEAD_DEPARTURE_MIN_SPEED
      and lead.vRel >= LEAD_DEPARTURE_MIN_SPEED
      and a_target >= 0.0
    )
    if not lead_valid:
      self.reset()
      return should_stop

    track_id = int(lead.radarTrackId)
    if self._active:
      if track_id != self._track_id:
        self.reset()
        return should_stop
      return False

    if not should_stop:
      self.reset()
      return False

    if controls_state.longControlState != LongCtrlState.stopping:
      self.reset()
      return should_stop

    if track_id != self._track_id:
      self._track_id = track_id
      self._distances.clear()
    self._distances.append(float(lead.dRel))

    if len(self._distances) == LEAD_DEPARTURE_CONFIRM_FRAMES and self._distances[-1] - self._distances[0] >= LEAD_DEPARTURE_MIN_DISTANCE:
      self._active = True
      return False

    return should_stop
