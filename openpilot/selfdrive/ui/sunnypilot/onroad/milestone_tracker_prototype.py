"""Persistent assisted-distance milestone tracking."""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from openpilot.common.params import Params


METERS_PER_MILE = 1609.344
MAX_SAMPLE_INTERVAL_SECONDS = 0.5
MILESTONE_EVENT_PAYLOAD = b"sunnypilot-milestone-v1"


class AssistCategory(StrEnum):
  MADS = "mads"
  FULL_ASSIST = "full_assist"


PARAM_KEYS = {
  AssistCategory.MADS: "MadsDrivenDistanceMeters",
  AssistCategory.FULL_ASSIST: "FullAssistDrivenDistanceMeters",
}


def assist_category(lat_active: bool, long_active: bool) -> AssistCategory | None:
  if not lat_active:
    return None
  return AssistCategory.FULL_ASSIST if long_active else AssistCategory.MADS


def next_milestone_miles(distance_miles: float) -> float:
  """Return the next value in the 1, 2, 5 × 10ⁿ milestone ladder."""
  distance_miles = max(0.0, distance_miles)
  magnitude = 10.0 ** math.floor(math.log10(max(1.0, distance_miles)))
  for multiplier in (1.0, 2.0, 5.0):
    candidate = multiplier * magnitude
    if candidate > distance_miles + 1e-9:
      return candidate
  return 10.0 * magnitude


def previous_milestone_miles(milestone_miles: float) -> float:
  if milestone_miles <= 1.0:
    return 0.0
  magnitude = 10.0 ** math.floor(math.log10(milestone_miles))
  normalized = milestone_miles / magnitude
  if normalized <= 1.0 + 1e-9:
    return 5.0 * magnitude / 10.0
  if normalized <= 2.0 + 1e-9:
    return magnitude
  return 2.0 * magnitude


@dataclass(frozen=True)
class DistanceMilestone:
  category: AssistCategory
  distance_meters: float
  previous_distance_meters: float

  @property
  def distance_miles(self) -> float:
    return self.distance_meters / METERS_PER_MILE

  @property
  def previous_distance_miles(self) -> float:
    return self.previous_distance_meters / METERS_PER_MILE


class MilestoneStore:
  def __init__(self, params: Params | None = None):
    self._params = params or Params()

  def load(self) -> dict[AssistCategory, float]:
    return {
      category: max(0.0, self._params.get(key, return_default=True) or 0.0)
      for category, key in PARAM_KEYS.items()
    }

  def save(self, distances_meters: Mapping[AssistCategory, float]) -> None:
    for category, key in PARAM_KEYS.items():
      self._params.put(key, max(0.0, distances_meters.get(category, 0.0)))

  def reset(self) -> dict[AssistCategory, float]:
    distances = dict.fromkeys(AssistCategory, 0.0)
    self.save(distances)
    return distances


class AssistedDistanceMilestoneTracker:
  def __init__(self, initial_distances_meters: Mapping[AssistCategory, float] | None = None):
    initial_distances_meters = initial_distances_meters or {}
    self._distance_meters = {
      category: max(0.0, initial_distances_meters.get(category, 0.0))
      for category in AssistCategory
    }
    self._next_milestone_meters = {
      category: next_milestone_miles(distance / METERS_PER_MILE) * METERS_PER_MILE
      for category, distance in self._distance_meters.items()
    }
    self.reset_sampling()

  def reset_sampling(self) -> None:
    self._last_timestamp_ns: int | None = None
    self._last_speed_mps = 0.0
    self._last_category: AssistCategory | None = None

  def distance_meters(self, category: AssistCategory) -> float:
    return self._distance_meters[category]

  def distances_meters(self) -> dict[AssistCategory, float]:
    return self._distance_meters.copy()

  def update(self, timestamp_ns: int, speed_mps: float, category: AssistCategory | None) -> list[DistanceMilestone]:
    milestones: list[DistanceMilestone] = []
    speed_mps = max(0.0, speed_mps)

    if self._last_timestamp_ns is not None and timestamp_ns != self._last_timestamp_ns:
      dt = (timestamp_ns - self._last_timestamp_ns) / 1e9
      if 0 < dt <= MAX_SAMPLE_INTERVAL_SECONDS and self._last_category is not None:
        delta_meters = (self._last_speed_mps + speed_mps) / 2.0 * dt
        active_category = self._last_category
        self._distance_meters[active_category] += delta_meters

        next_milestone = self._next_milestone_meters[active_category]
        while self._distance_meters[active_category] >= next_milestone:
          milestone_miles = next_milestone / METERS_PER_MILE
          milestones.append(DistanceMilestone(
            active_category,
            next_milestone,
            previous_milestone_miles(milestone_miles) * METERS_PER_MILE,
          ))
          next_milestone = next_milestone_miles(milestone_miles) * METERS_PER_MILE
        self._next_milestone_meters[active_category] = next_milestone

    self._last_timestamp_ns = timestamp_ns
    self._last_speed_mps = speed_mps
    self._last_category = category
    return milestones
