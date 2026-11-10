#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Builds regions.json.gz, the table the car uses to turn a map tile into a home
region code. Dev tool only: it is not run on the car.

  pip install h3 shapely
  curl -LO https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson
  python openpilot/sunnypilot/achievements/tools/build_regions.py \
    ne_10m_admin_1_states_provinces.geojson openpilot/sunnypilot/achievements/regions.json.gz

Rules:
- Region codes are ISO 3166-2 (US-OH) in the countries in SUBDIVISIONS, and the
  ISO 3166-1 country code (GB) everywhere else.
- A resolution-6 tile (about 6 km) belongs to the region its center is in.
  Coastal tiles whose center is in the water go to the region whose coastline
  passes through them most.
- Stored as the majority region of each resolution-4 cell ("regions") plus the
  resolution-6 tiles that differ from it ("exceptions"), each compacted. That
  keeps 6 km accuracy at borders in about 200 KB.

Boundaries: Natural Earth 1:10m admin 1, public domain.
"""
import collections
import gzip
import json
import re
import sys

import h3
from shapely.geometry import box, shape

SUBDIVISIONS = {"US", "CA", "MX", "BR", "AU", "DE"}
TILE_RES = 6
BASE_RES = 4
CUT_DEG = 10.0  # H3 can't fill huge polygons at resolution 6, so cut them into squares first
ISO_3166_2 = re.compile(r"^[A-Z]{2}-[A-Z0-9]{1,3}$")


def region_code(props: dict) -> str | None:
  country = props.get("iso_a2") or ""
  if not re.fullmatch(r"[A-Z]{2}", country):
    return None
  code = props.get("iso_3166_2") or ""
  if country in SUBDIVISIONS and ISO_3166_2.match(code):
    return code
  return country


def pieces(geom: dict):
  """Polygon rings, as (lng, lat) lists, of the geometry cut into CUT_DEG squares."""
  g = shape(geom)
  if not g.is_valid:
    g = g.buffer(0)
  minx, miny, maxx, maxy = g.bounds
  x = minx
  while x < maxx:
    y = miny
    while y < maxy:
      part = g.intersection(box(x, y, x + CUT_DEG, y + CUT_DEG))
      for poly in getattr(part, "geoms", [part]):
        if poly.geom_type == "Polygon" and not poly.is_empty:
          yield [list(poly.exterior.coords)] + [list(r.coords) for r in poly.interiors]
      y += CUT_DEG
    x += CUT_DEG


def outer_rings(geom: dict):
  polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
  for rings in polys:
    yield rings[0]


def winner(counter: collections.Counter) -> str:
  return max(sorted(counter), key=lambda k: counter[k])


def main(src: str, dst: str) -> None:
  features = json.load(open(src))["features"]
  by_center: dict[str, str] = {}
  by_coast: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
  for n, f in enumerate(features):
    code = region_code(f["properties"])
    if code is None or f["geometry"] is None:
      continue
    for rings in pieces(f["geometry"]):
      outer, holes = rings[0], rings[1:]
      poly = h3.LatLngPoly([(lat, lng) for lng, lat in outer], *[[(lat, lng) for lng, lat in r] for r in holes])
      for cell in h3.polygon_to_cells(poly, TILE_RES):
        by_center[cell] = code
    for ring in outer_rings(f["geometry"]):
      for lng, lat in ring:
        by_coast[h3.latlng_to_cell(lat, lng, TILE_RES)][code] += 1
    if n % 500 == 0:
      print(f"{n}/{len(features)} boundaries", file=sys.stderr)

  tiles = dict(by_center)
  for cell, votes in by_coast.items():
    tiles.setdefault(cell, winner(votes))

  base_votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
  for cell, code in tiles.items():
    base_votes[h3.cell_to_parent(cell, BASE_RES)][code] += 1
  base = {cell: winner(votes) for cell, votes in base_votes.items()}

  regions: dict[str, list[str]] = collections.defaultdict(list)
  for cell, code in base.items():
    regions[code].append(cell)
  exceptions: dict[str, list[str]] = collections.defaultdict(list)
  for cell, code in tiles.items():
    if base[h3.cell_to_parent(cell, BASE_RES)] != code:
      exceptions[code].append(cell)

  data = {
    "v": 1,
    "source": "Natural Earth 1:10m admin 1 (public domain); built by tools/build_regions.py",
    "subdivisions": sorted(SUBDIVISIONS),
    "tile_res": TILE_RES,
    "base_res": BASE_RES,
    "regions": {k: sorted(h3.compact_cells(v)) for k, v in sorted(regions.items())},
    "exceptions": {k: sorted(h3.compact_cells(v)) for k, v in sorted(exceptions.items())},
  }
  raw = json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
  with gzip.GzipFile(dst, "wb", mtime=0) as out:
    out.write(raw)
  n_regions = sum(map(len, data["regions"].values()))
  n_exceptions = sum(map(len, data["exceptions"].values()))
  print(f"{len(tiles)} tiles, {len(data['regions'])} regions, {n_regions} base cells, {n_exceptions} exceptions", file=sys.stderr)


if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
