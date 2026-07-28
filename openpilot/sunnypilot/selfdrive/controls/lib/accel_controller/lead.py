"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math
from typing import NamedTuple

import numpy as np

from cereal import log
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import (
  LongitudinalMpc, LongitudinalPlanSource, STOP_DISTANCE, T_IDXS, get_T_FOLLOW, get_stopped_equivalence_factor,
)
from openpilot.selfdrive.controls.radard import _LEAD_ACCEL_TAU
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  COMFORT_DECEL, MAX_LEAD_ACCEL_TAU, MIN_LEAD_SPEED, STOP_GAP_RESERVE, STOP_GAP_RESERVE_DECEL_BP,
  STOP_GAP_RESERVE_LEAD_SPEED, STOPPED_LEAD_SPEED, sanitize_profile,
)


class LeadPlan(NamedTuple):
  cap: float = math.inf
  selected_lead: int = -1
  selected_lead_track_id: int = -1
  selected_lead_speed: float = math.inf
  selected_lead_accel: float = 0.0
  departure_lead_index: int = -1
  departure_lead_speed: float = math.inf
  departure_cap: float = math.inf
  departure_lead_speeds: tuple[float, float] = (math.inf, math.inf)
  departure_lead_distances: tuple[float, float] = (-math.inf, -math.inf)
  departure_lead_track_ids: tuple[int, int] = (-1, -1)
  departure_lead_separations: tuple[float, float] = (-math.inf, -math.inf)
  usable_gap: float = math.inf
  closing_speed: float = 0.0
  required_decel: float = 0.0
  has_nearly_stopped_lead: bool = False
  lead_status: bool = False


def is_lead_source(source) -> bool:
  return source in (LongitudinalPlanSource.lead0, LongitudinalPlanSource.lead1)


def has_radar_lead(radar_state) -> bool:
  return bool(radar_state.leadOne.status or radar_state.leadTwo.status)


def _project_ego(v_ego: float, a_ego: float, delay: float) -> tuple[float, float]:
  if a_ego < 0.0:
    stop_time = -v_ego / a_ego if v_ego > 0.0 else 0.0
    if stop_time <= delay:
      distance = -v_ego**2 / (2.0 * a_ego) if v_ego > 0.0 else 0.0
      return distance, 0.0
  return max(v_ego * delay + 0.5 * a_ego * delay**2, 0.0), max(v_ego + a_ego * delay, 0.0)


def _lead_values(lead) -> tuple[float, float, float, float] | None:
  if not lead.status:
    return None
  d_rel, v_lead = float(lead.dRel), float(lead.vLeadK)
  if not math.isfinite(d_rel) or d_rel < 0.0 or not math.isfinite(v_lead) or v_lead < MIN_LEAD_SPEED:
    return None

  a_lead = float(lead.aLeadK)
  if not math.isfinite(a_lead):
    a_lead = 0.0
  a_lead_tau = float(lead.aLeadTau)
  if not math.isfinite(a_lead_tau) or not 0.0 < a_lead_tau <= MAX_LEAD_ACCEL_TAU:
    a_lead_tau = _LEAD_ACCEL_TAU
  return d_rel, max(v_lead, 0.0), float(np.clip(a_lead, -10.0, 5.0)), a_lead_tau


def calculate_lead_plan(radar_state, v_ego: float, a_ego: float, delay: float, profile: int,
                        follow_personality=log.LongitudinalPersonality.standard) -> LeadPlan:
  if not all(math.isfinite(value) for value in (v_ego, a_ego, delay)) or v_ego < 0.0 or delay < 0.0:
    return LeadPlan()

  leads = (radar_state.leadOne, radar_state.leadTwo)
  lead_status = any(lead.status for lead in leads)
  t_follow = get_T_FOLLOW(follow_personality)
  if not math.isfinite(t_follow) or t_follow < 0.0:
    return LeadPlan(lead_status=lead_status)

  profile = sanitize_profile(profile)
  x_ego, v_ego_delay = _project_ego(v_ego, a_ego, delay)
  comfort_decel = COMFORT_DECEL[profile]
  candidates: list[LeadPlan] = []
  departure_candidates: list[tuple[float, int]] = []
  departure_speeds = [math.inf, math.inf]
  departure_distances = [-math.inf, -math.inf]
  departure_track_ids = [-1, -1]
  departure_separations = [-math.inf, -math.inf]
  departure_caps = [math.inf, math.inf]

  for lead_index, lead in enumerate(leads):
    values = _lead_values(lead)
    if values is None:
      continue

    d_rel, v_lead, a_lead, a_lead_tau = values
    lead_xv = LongitudinalMpc.extrapolate_lead(d_rel, v_lead, a_lead, a_lead_tau)
    x_lead = float(np.interp(delay, T_IDXS, lead_xv[:, 0]))
    v_lead_delay = float(np.interp(delay, T_IDXS, lead_xv[:, 1]))
    safety_gap = max(x_lead - x_ego - STOP_DISTANCE - t_follow * v_lead_delay, 0.0)
    closing_speed = max(v_ego_delay - v_lead_delay, 0.0)
    required_decel = 0.0 if closing_speed == 0.0 else math.inf if safety_gap == 0.0 else closing_speed**2 / (2.0 * safety_gap)
    reserve = float(np.interp(v_lead_delay, (0.0, STOP_GAP_RESERVE_LEAD_SPEED), (STOP_GAP_RESERVE, 0.0)))
    reserve_scale = float(np.interp(required_decel, STOP_GAP_RESERVE_DECEL_BP, (1.0, 0.0)))
    usable_gap = max(safety_gap - reserve * reserve_scale, 0.0)
    cap = v_lead_delay + math.sqrt(2.0 * comfort_decel * usable_gap)
    departure_cap = v_lead_delay + math.sqrt(2.0 * comfort_decel * safety_gap)
    separation = x_lead - x_ego
    departure_distance = x_lead + float(get_stopped_equivalence_factor(v_lead_delay))

    finite_values = (x_lead, v_lead_delay, safety_gap, usable_gap, closing_speed, cap, departure_cap, departure_distance)
    if (not all(math.isfinite(value) and value >= 0.0 for value in finite_values) or math.isnan(required_decel)
        or required_decel < 0.0 or not math.isfinite(separation)):
      continue

    track_id = max(int(lead.radarTrackId), -1) if math.isfinite(lead.radarTrackId) else -1
    candidates.append(LeadPlan(
      cap=cap, selected_lead=lead_index, selected_lead_track_id=track_id, selected_lead_speed=v_lead_delay, selected_lead_accel=a_lead,
      usable_gap=usable_gap, closing_speed=closing_speed, required_decel=required_decel, lead_status=lead_status,
    ))
    departure_candidates.append((departure_distance, lead_index))
    departure_speeds[lead_index] = v_lead_delay
    departure_distances[lead_index] = d_rel
    departure_track_ids[lead_index] = track_id
    departure_separations[lead_index] = separation
    departure_caps[lead_index] = departure_cap

  if not candidates:
    return LeadPlan(lead_status=lead_status)

  selected = min(candidates, key=lambda candidate: candidate.cap)
  departure_lead_index = min(departure_candidates, key=lambda candidate: candidate[0])[1]
  departure_lead_speed = departure_speeds[departure_lead_index]
  return selected._replace(
    departure_lead_index=departure_lead_index, departure_lead_speed=departure_lead_speed,
    departure_cap=departure_caps[departure_lead_index], departure_lead_speeds=tuple(departure_speeds),
    departure_lead_distances=tuple(departure_distances), departure_lead_track_ids=tuple(departure_track_ids),
    departure_lead_separations=tuple(departure_separations), has_nearly_stopped_lead=departure_lead_speed < STOPPED_LEAD_SPEED,
  )
