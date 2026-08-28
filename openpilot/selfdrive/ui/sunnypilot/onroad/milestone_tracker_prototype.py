"""PROTOTYPE: per-drive assisted-distance milestone tracking."""

from dataclasses import dataclass
from enum import StrEnum


METERS_PER_MILE = 1609.344
TEST_MILESTONE_MILES = 0.5
MAX_SAMPLE_INTERVAL_SECONDS = 0.5


class AssistCategory(StrEnum):
  MADS = "mads"
  FULL_ASSIST = "full_assist"


def assist_category(lat_active: bool, long_active: bool) -> AssistCategory | None:
  if not lat_active:
    return None
  return AssistCategory.FULL_ASSIST if long_active else AssistCategory.MADS


@dataclass(frozen=True)
class DistanceMilestone:
  category: AssistCategory
  distance_meters: float

  @property
  def distance_miles(self) -> float:
    return self.distance_meters / METERS_PER_MILE


class PerDriveMilestoneTracker:
  def __init__(self, milestone_meters: float = TEST_MILESTONE_MILES * METERS_PER_MILE):
    if milestone_meters <= 0:
      raise ValueError("milestone distance must be positive")
    self.milestone_meters = milestone_meters
    self.reset()

  def reset(self) -> None:
    self._distance_meters = dict.fromkeys(AssistCategory, 0.0)
    self._next_milestone_meters = dict.fromkeys(AssistCategory, self.milestone_meters)
    self._last_timestamp_ns: int | None = None
    self._last_speed_mps = 0.0
    self._last_category: AssistCategory | None = None

  def distance_meters(self, category: AssistCategory) -> float:
    return self._distance_meters[category]

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
          milestones.append(DistanceMilestone(active_category, next_milestone))
          next_milestone += self.milestone_meters
        self._next_milestone_meters[active_category] = next_milestone

    self._last_timestamp_ns = timestamp_ns
    self._last_speed_mps = speed_mps
    self._last_category = category
    return milestones
