"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The achievement catalog. Pure Python on purpose: the UI, achievementsd and the
tests all load it, and none of them should need cereal or the Params library to
read a list of goals.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

CATALOG_PATH = Path(__file__).with_name("catalog.json")
SINGLE = "single"
KM_TO_MI = 0.621371


@dataclass(frozen=True)
class Tier:
  tier: str
  threshold: float


@dataclass(frozen=True)
class Achievement:
  id: str
  name: str
  description: str
  metric: str
  unit: str
  tiers: tuple[Tier, ...]

  def unlock_id(self, tier: Tier) -> str:
    """The id an unlock is stored and shared under: `odometer.silver`, or just `first_light`."""
    return self.id if tier.tier == SINGLE else f"{self.id}.{tier.tier}"

  @property
  def tiered(self) -> bool:
    return not (len(self.tiers) == 1 and self.tiers[0].tier == SINGLE)


@dataclass(frozen=True)
class Catalog:
  version: int
  achievements: tuple[Achievement, ...]

  @property
  def metrics(self) -> set[str]:
    return {a.metric for a in self.achievements}

  def all_unlock_ids(self) -> list[str]:
    return [a.unlock_id(t) for a in self.achievements for t in a.tiers]


def parse_catalog(data: dict) -> Catalog:
  achievements = []
  seen: set[str] = set()
  for raw in data["achievements"]:
    tiers = tuple(Tier(str(t["tier"]), float(t["threshold"])) for t in raw["tiers"])
    if not tiers:
      raise ValueError(f"achievement {raw['id']} has no tiers")
    if any(b.threshold <= a.threshold for a, b in zip(tiers, tiers[1:], strict=False)):
      raise ValueError(f"achievement {raw['id']} tiers must increase")
    if raw["id"] in seen:
      raise ValueError(f"duplicate achievement id {raw['id']}")
    seen.add(raw["id"])
    achievements.append(Achievement(raw["id"], raw["name"], raw["description"], raw["metric"], raw.get("unit", ""), tiers))
  return Catalog(int(data["version"]), tuple(achievements))


@cache
def load_catalog(path: str = str(CATALOG_PATH)) -> Catalog:
  with open(path) as f:
    return parse_catalog(json.load(f))


# --- display helpers, shared by both device UIs ---

def _fmt_number(value: float) -> str:
  if value >= 100 or value == int(value):
    return f"{int(value):,}"
  return f"{value:.1f}"


def format_amount(value: float, unit: str, is_metric: bool = True) -> str:
  if unit == "km" and not is_metric:
    value, unit = value * KM_TO_MI, "mi"
  if not unit:
    return _fmt_number(value)
  return f"{_fmt_number(value)} {unit}"


@dataclass(frozen=True)
class AchievementStatus:
  achievement: Achievement
  reached: Tier | None   # highest tier unlocked, None if locked
  next: Tier | None      # next tier to unlock, None when all are done
  value: float

  @property
  def done(self) -> bool:
    return self.next is None

  def summary(self, is_metric: bool = True) -> str:
    """One short line: `silver · 1,240 / 10,000 km`, `locked · 3 / 7 days`, `gold · done`."""
    a = self.achievement
    if self.next is None:
      return f"{self.reached.tier} · done" if a.tiered and self.reached else "done"
    label = self.reached.tier if self.reached else "locked"
    if not a.unit:  # a yes/no achievement, like turning on sunnylink
      return label
    return f"{label} · {format_progress(self.value, self.next.threshold, a.unit, is_metric)}"


def format_progress(value: float, goal: float, unit: str, is_metric: bool = True) -> str:
  if unit == "km" and not is_metric:
    value, goal, unit = value * KM_TO_MI, goal * KM_TO_MI, "mi"
  return f"{_fmt_number(min(value, goal))} / {_fmt_number(goal)} {unit}"


def statuses(catalog: Catalog, metrics: dict[str, float], unlocked: dict[str, str]) -> list[AchievementStatus]:
  out = []
  for a in catalog.achievements:
    reached = None
    nxt = None
    for t in a.tiers:
      if a.unlock_id(t) in unlocked:
        reached = t
      elif nxt is None:
        nxt = t
    out.append(AchievementStatus(a, reached, nxt, float(metrics.get(a.metric, 0.0))))
  return out
