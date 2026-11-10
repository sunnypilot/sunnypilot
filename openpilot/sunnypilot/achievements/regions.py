"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Home region lookup: map tile -> region code (US-OH, CA-ON, or a country code
like GB), from the table in regions.json.gz. Works offline on the car; no
geocoding service is ever called. See tools/build_regions.py for how the table
is made.
"""
from __future__ import annotations

import gzip
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from openpilot.sunnypilot.achievements import h3lite

TABLE_PATH = Path(__file__).parent / "regions.json.gz"


class RegionTable:
  def __init__(self, path: Path = TABLE_PATH):
    with gzip.open(path, "rt") as f:
      data = json.load(f)
    self.tile_res: int = data["tile_res"]
    self.base_res: int = data["base_res"]
    self.codes: list[str] = sorted(set(data["regions"]) | set(data["exceptions"]))
    index = {c: i for i, c in enumerate(self.codes)}
    self._base = self._arrays(data["regions"], index)
    self._exceptions = self._arrays(data["exceptions"], index)

  @staticmethod
  def _arrays(groups: dict[str, list[str]], index: dict[str, int]) -> tuple[np.ndarray, np.ndarray]:
    pairs = sorted((int(cell, 16), index[code]) for code, cells in groups.items() for cell in cells)
    keys = np.array([p[0] for p in pairs], dtype=np.int64)
    vals = np.array([p[1] for p in pairs], dtype=np.uint16)
    return keys, vals

  @staticmethod
  def _find(arrays: tuple[np.ndarray, np.ndarray], cell: int) -> int | None:
    keys, vals = arrays
    i = int(np.searchsorted(keys, cell))
    if i < len(keys) and int(keys[i]) == cell:
      return int(vals[i])
    return None

  def lookup_cell(self, cell: int) -> str | None:
    """Region for a tile at tile_res (or finer). None at sea or off the map."""
    res = h3lite.get_resolution(cell)
    if res > self.tile_res:
      cell, res = h3lite.cell_to_parent(cell, self.tile_res), self.tile_res
    for table, top in ((self._exceptions, res), (self._base, min(res, self.base_res))):
      for r in range(top, -1, -1):
        hit = self._find(table, h3lite.cell_to_parent(cell, r))
        if hit is not None:
          return self.codes[hit]
    return None

  def lookup(self, lat: float, lng: float) -> str | None:
    return self.lookup_cell(h3lite.latlng_to_cell(lat, lng, self.tile_res))


@lru_cache(maxsize=1)
def table() -> RegionTable:
  return RegionTable()


def country_of(region: str) -> str:
  return region.split("-", 1)[0]
