"""Authoritative assisted-driving distance and milestone tracking."""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from openpilot.common.params import Params


METERS_PER_MILE = 1609.344
METERS_PER_KILOMETER = 1000.0
MAX_SAMPLE_INTERVAL_SECONDS = 0.5
PERSIST_INTERVAL_NS = 10_000_000_000
STATE_VERSION = 1
STATE_PARAM = "AssistedDrivingMilestoneState"
LAST_DRIVE_SUMMARY_PARAM = "LastDriveAssistedDrivingSummary"


class AssistCategory(StrEnum):
  MADS = "mads"
  FULL_ASSIST = "fullAssist"


class MilestoneUnit(StrEnum):
  IMPERIAL = "imperial"
  METRIC = "metric"


@dataclass(frozen=True)
class MilestoneEvent:
  event_id: int
  category: AssistCategory
  distance_meters: float
  previous_distance_meters: float
  unit: MilestoneUnit


@dataclass(frozen=True)
class MilestoneSnapshot:
  distances_meters: dict[AssistCategory, float]
  drive_start_distances_meters: dict[AssistCategory, float]
  next_event_id: int
  next_summary_id: int
  unit: MilestoneUnit
  active_drive_id: str


def assist_category(lat_active: bool, long_active: bool) -> AssistCategory | None:
  if not lat_active:
    return None
  return AssistCategory.FULL_ASSIST if long_active else AssistCategory.MADS


def _meters_per_unit(unit: MilestoneUnit) -> float:
  return METERS_PER_KILOMETER if unit == MilestoneUnit.METRIC else METERS_PER_MILE


def _next_ladder_value(value: float) -> float:
  value = max(0.0, value)
  magnitude = 10.0 ** math.floor(math.log10(max(1.0, value)))
  for multiplier in (1.0, 2.0, 5.0):
    candidate = multiplier * magnitude
    if candidate > value + 1e-9:
      return candidate
  return 10.0 * magnitude


def _previous_ladder_value(value: float) -> float:
  if value <= 1.0:
    return 0.0
  magnitude = 10.0 ** math.floor(math.log10(value))
  normalized = value / magnitude
  if normalized <= 1.0 + 1e-9:
    return 5.0 * magnitude / 10.0
  if normalized <= 2.0 + 1e-9:
    return magnitude
  return 2.0 * magnitude


def next_milestone_meters(distance_meters: float, unit: MilestoneUnit) -> float:
  meters_per_unit = _meters_per_unit(unit)
  return _next_ladder_value(distance_meters / meters_per_unit) * meters_per_unit


class MilestoneStore:
  def __init__(self, params: Params | None = None):
    self._params = params or Params()

  def load(self) -> MilestoneSnapshot:
    raw = self._params.get(STATE_PARAM, return_default=True)
    raw = raw if isinstance(raw, dict) else {}
    raw_distances = raw.get("distancesMeters", {})
    raw_distances = raw_distances if isinstance(raw_distances, dict) else {}
    try:
      unit = MilestoneUnit(raw.get("unit", MilestoneUnit.IMPERIAL))
    except ValueError:
      unit = MilestoneUnit.IMPERIAL

    def distance(category: AssistCategory) -> float:
      try:
        return max(0.0, float(raw_distances.get(category.value, 0.0)))
      except (TypeError, ValueError):
        return 0.0

    distances = {category: distance(category) for category in AssistCategory}
    raw_drive_start = raw.get("driveStartDistancesMeters", {})
    raw_drive_start = raw_drive_start if isinstance(raw_drive_start, dict) else {}

    def drive_start_distance(category: AssistCategory) -> float:
      try:
        return max(0.0, min(float(raw_drive_start.get(category.value, distances[category])), distances[category]))
      except (TypeError, ValueError):
        return distances[category]

    try:
      next_event_id = max(1, int(raw.get("nextEventId", 1)))
    except (TypeError, ValueError):
      next_event_id = 1
    try:
      next_summary_id = max(1, int(raw.get("nextSummaryId", 1)))
    except (TypeError, ValueError):
      next_summary_id = 1

    return MilestoneSnapshot(
      distances_meters=distances,
      drive_start_distances_meters={category: drive_start_distance(category) for category in AssistCategory},
      next_event_id=next_event_id,
      next_summary_id=next_summary_id,
      unit=unit,
      active_drive_id=str(raw.get("activeDriveId", "")),
    )

  def save(self, snapshot: MilestoneSnapshot, block: bool = False) -> None:
    if block:
      self._params.flush()
    self._params.put(STATE_PARAM, {
      "version": STATE_VERSION,
      "distancesMeters": {category.value: max(0.0, snapshot.distances_meters.get(category, 0.0)) for category in AssistCategory},
      "driveStartDistancesMeters": {
        category.value: max(0.0, snapshot.drive_start_distances_meters.get(category, 0.0)) for category in AssistCategory
      },
      "nextEventId": max(1, snapshot.next_event_id),
      "nextSummaryId": max(1, snapshot.next_summary_id),
      "unit": snapshot.unit.value,
      "activeDriveId": snapshot.active_drive_id,
    }, block=block)

  def save_drive_summary(self, summary_id: int, distances_meters: Mapping[AssistCategory, float], unit: MilestoneUnit) -> None:
    self._params.put(LAST_DRIVE_SUMMARY_PARAM, {
      "version": STATE_VERSION,
      "id": summary_id,
      "distancesMeters": {category.value: max(0.0, distances_meters.get(category, 0.0)) for category in AssistCategory},
      "unit": unit.value,
    }, block=True)


class AssistedDrivingMilestones:
  """Tracks, persists, and emits milestones through one small interface."""

  def __init__(self, store: MilestoneStore | None = None):
    self._store = store or MilestoneStore()
    snapshot = self._store.load()
    self._distances_meters = snapshot.distances_meters
    self._drive_start_distances_meters = snapshot.drive_start_distances_meters
    self._next_event_id = snapshot.next_event_id
    self._next_summary_id = snapshot.next_summary_id
    self._unit = snapshot.unit
    self._active_drive_id = snapshot.active_drive_id
    self._next_milestone_meters = {
      category: next_milestone_meters(distance, self._unit)
      for category, distance in self._distances_meters.items()
    }
    self._last_timestamp_ns: int | None = None
    self._last_persist_timestamp_ns: int | None = None
    self._last_speed_mps = 0.0
    self._last_category: AssistCategory | None = None
    self._enabled = False
    self._closed = False

  def snapshot(self) -> MilestoneSnapshot:
    return MilestoneSnapshot(
      self._distances_meters.copy(),
      self._drive_start_distances_meters.copy(),
      self._next_event_id,
      self._next_summary_id,
      self._unit,
      self._active_drive_id,
    )

  def set_drive_id(self, drive_id: str) -> None:
    if not drive_id or drive_id == self._active_drive_id:
      return
    self._active_drive_id = drive_id
    self._drive_start_distances_meters = self._distances_meters.copy()
    self._persist()

  def update(self, timestamp_ns: int, speed_mps: float, *, lat_active: bool, long_active: bool,
             is_metric: bool, enabled: bool) -> MilestoneEvent | None:
    self._enabled = enabled
    unit = MilestoneUnit.METRIC if is_metric else MilestoneUnit.IMPERIAL
    if unit != self._unit:
      self._unit = unit
      self._next_milestone_meters = {
        category: next_milestone_meters(distance, unit)
        for category, distance in self._distances_meters.items()
      }

    speed_mps = max(0.0, speed_mps)
    category = assist_category(lat_active, long_active) if enabled else None
    event = None

    if self._last_timestamp_ns is not None and timestamp_ns != self._last_timestamp_ns:
      dt = (timestamp_ns - self._last_timestamp_ns) / 1e9
      if 0 < dt <= MAX_SAMPLE_INTERVAL_SECONDS and self._last_category is not None:
        active_category = self._last_category
        self._distances_meters[active_category] += (self._last_speed_mps + speed_mps) / 2.0 * dt
        threshold_meters = self._next_milestone_meters[active_category]
        if self._distances_meters[active_category] >= threshold_meters:
          meters_per_unit = _meters_per_unit(self._unit)
          threshold_units = threshold_meters / meters_per_unit
          event = MilestoneEvent(
            event_id=self._next_event_id,
            category=active_category,
            distance_meters=threshold_meters,
            previous_distance_meters=_previous_ladder_value(threshold_units) * meters_per_unit,
            unit=self._unit,
          )
          self._next_event_id += 1
          self._next_milestone_meters[active_category] = next_milestone_meters(threshold_meters, self._unit)
          self._persist(timestamp_ns=timestamp_ns)

    self._last_timestamp_ns = timestamp_ns
    self._last_speed_mps = speed_mps
    self._last_category = category

    if self._last_persist_timestamp_ns is None:
      self._last_persist_timestamp_ns = timestamp_ns
    elif timestamp_ns - self._last_persist_timestamp_ns >= PERSIST_INTERVAL_NS:
      self._persist(timestamp_ns=timestamp_ns)

    return event

  def close(self) -> None:
    if self._closed:
      return
    self._closed = True
    drive_distances = {
      category: self._distances_meters[category] - self._drive_start_distances_meters[category]
      for category in AssistCategory
    }
    summary_id = self._next_summary_id
    self._next_summary_id += 1
    self._persist(block=True)
    if self._enabled:
      self._store.save_drive_summary(summary_id, drive_distances, self._unit)

  def _persist(self, block: bool = False, timestamp_ns: int | None = None) -> None:
    self._store.save(self.snapshot(), block=block)
    self._last_persist_timestamp_ns = self._last_timestamp_ns if timestamp_ns is None else timestamp_ns
