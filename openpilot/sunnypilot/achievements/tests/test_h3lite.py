"""
h3lite must give the same cell ids as Uber's H3, because the site and the
server use h3-js and h3-pg on the ids the car sends. The vectors below come
from h3-py 4.1.2; with h3 installed, the last test also compares random points.
"""
import random

import pytest

from openpilot.sunnypilot.achievements import h3lite

RESOLUTIONS = (0, 4, 6, 9, 15)
CELLS = [
  (40.0334, -83.1588, ("802bfffffffffff", "842a90bffffffff", "862a90b4fffffff", "892a90b4917ffff", "8f2a90b4915d388")),
  (37.7749, -122.4194, ("8029fffffffffff", "8428309ffffffff", "86283082fffffff", "89283082803ffff", "8f283082800b390")),
  (51.5007, -0.1246, ("8019fffffffffff", "84194adffffffff", "86194ad17ffffff", "89194ad14c3ffff", "8f194ad14c254d3")),
  (-33.8688, 151.2093, ("80bffffffffffff", "84be0e3ffffffff", "86be0e35fffffff", "89be0e35cbbffff", "8fbe0e35cbad0a8")),
  (35.6762, 139.6503, ("802ffffffffffff", "842f5a3ffffffff", "862f5a367ffffff", "892f5a363bbffff", "8f2f5a363ba005a")),
  (64.8378, -147.7164, ("800dfffffffffff", "840d5a9ffffffff", "860d5a9afffffff", "890d5a9add3ffff", "8f0d5a9add25781")),
  (-54.8019, -68.303, ("80dffffffffffff", "84df451ffffffff", "86df45177ffffff", "89df4517557ffff", "8fdf45175542186")),
  (0.0, 0.0, ("8075fffffffffff", "84754a9ffffffff", "86754e64fffffff", "89754e64993ffff", "8f754e64992d6d8")),
  (89.9, 45.0, ("8001fffffffffff", "8403263ffffffff", "86032630fffffff", "89032630ac3ffff", "8f032630ac0311a")),
  (-89.9, -45.0, ("80f3fffffffffff", "84f2939ffffffff", "86f2938efffffff", "89f2938ec7bffff", "8ff2938ec78c80e")),
  (52.0, 179.999, ("8017fffffffffff", "841659bffffffff", "861659aefffffff", "891659acc9bffff", "8f1659acc9ad193")),
  (-16.5, -179.999, ("809bfffffffffff", "849b5ddffffffff", "869b5dc57ffffff", "899b5dc5597ffff", "8f9b5dc5596a500")),
  (-28.18676, -125.6943, ("80b1fffffffffff", "84b1713ffffffff", "86b171247ffffff", "89b1712423bffff", "8fb171242396a80")),
  (24.14952, -153.92294, ("805dfffffffffff", "845d35bffffffff", "865d35b0fffffff", "895d35b0b23ffff", "8f5d35b0b200c24")),
  (5.74112, -48.35199, ("805ffffffffffff", "845fa25ffffffff", "865fa248fffffff", "895fa248b23ffff", "8f5fa248b218936")),
  (-70.72017, 2.67686, ("80e7fffffffffff", "84e749dffffffff", "86e749c47ffffff", "89e749c44c3ffff", "8fe749c44c216ec")),
  (-74.00069, -23.88755, ("80effffffffffff", "84ee139ffffffff", "86ee13967ffffff", "89ee1396293ffff", "8fee139629208d2")),
  (-68.82313, -147.34332, ("80e3fffffffffff", "84e334dffffffff", "86e334c9fffffff", "89e334c983bffff", "8fe334c9839a3b1")),
  (-12.07693, 117.66676, ("8095fffffffffff", "849581dffffffff", "869581d97ffffff", "899581d9487ffff", "8f9581d9486a96e")),
  (-60.19169, -99.63397, ("80e9fffffffffff", "84e95c1ffffffff", "86e95c107ffffff", "89e95c1000bffff", "8fe95c1000b639c")),
]
PARENTS = [
  ("8f2a90b4915d388", ("802bfffffffffff", "842a90bffffffff", "862a90b4fffffff", "892a90b4917ffff", "8f2a90b4915d388")),
  ("8f283082800b390", ("8029fffffffffff", "8428309ffffffff", "86283082fffffff", "89283082803ffff", "8f283082800b390")),
  ("8f194ad14c254d3", ("8019fffffffffff", "84194adffffffff", "86194ad17ffffff", "89194ad14c3ffff", "8f194ad14c254d3")),
  ("8fbe0e35cbad0a8", ("80bffffffffffff", "84be0e3ffffffff", "86be0e35fffffff", "89be0e35cbbffff", "8fbe0e35cbad0a8")),
  ("8f2f5a363ba005a", ("802ffffffffffff", "842f5a3ffffffff", "862f5a367ffffff", "892f5a363bbffff", "8f2f5a363ba005a")),
  ("8f0d5a9add25781", ("800dfffffffffff", "840d5a9ffffffff", "860d5a9afffffff", "890d5a9add3ffff", "8f0d5a9add25781")),
  ("8fdf45175542186", ("80dffffffffffff", "84df451ffffffff", "86df45177ffffff", "89df4517557ffff", "8fdf45175542186")),
  ("8f754e64992d6d8", ("8075fffffffffff", "84754e7ffffffff", "86754e64fffffff", "89754e64993ffff", "8f754e64992d6d8")),
  ("8f032630ac0311a", ("8003fffffffffff", "8403263ffffffff", "86032630fffffff", "89032630ac3ffff", "8f032630ac0311a")),
  ("8ff2938ec78c80e", ("80f3fffffffffff", "84f2939ffffffff", "86f2938efffffff", "89f2938ec7bffff", "8ff2938ec78c80e")),
  ("8f1659acc9ad193", ("8017fffffffffff", "841659bffffffff", "861659acfffffff", "891659acc9bffff", "8f1659acc9ad193")),
  ("8f9b5dc5596a500", ("809bfffffffffff", "849b5ddffffffff", "869b5dc57ffffff", "899b5dc5597ffff", "8f9b5dc5596a500")),
  ("8fb171242396a80", ("80b1fffffffffff", "84b1713ffffffff", "86b171247ffffff", "89b1712423bffff", "8fb171242396a80")),
  ("8f5d35b0b200c24", ("805dfffffffffff", "845d35bffffffff", "865d35b0fffffff", "895d35b0b23ffff", "8f5d35b0b200c24")),
  ("8f5fa248b218936", ("805ffffffffffff", "845fa25ffffffff", "865fa248fffffff", "895fa248b23ffff", "8f5fa248b218936")),
  ("8fe749c44c216ec", ("80e7fffffffffff", "84e749dffffffff", "86e749c47ffffff", "89e749c44c3ffff", "8fe749c44c216ec")),
  ("8fee139629208d2", ("80effffffffffff", "84ee139ffffffff", "86ee13967ffffff", "89ee1396293ffff", "8fee139629208d2")),
  ("8fe334c9839a3b1", ("80e3fffffffffff", "84e334dffffffff", "86e334c9fffffff", "89e334c983bffff", "8fe334c9839a3b1")),
  ("8f9581d9486a96e", ("8095fffffffffff", "849581dffffffff", "869581d97ffffff", "899581d9487ffff", "8f9581d9486a96e")),
  ("8fe95c1000b639c", ("80e9fffffffffff", "84e95c1ffffffff", "86e95c107ffffff", "89e95c1000bffff", "8fe95c1000b639c")),
  ("8f2a90b4915d388", ("802bfffffffffff", "842a90bffffffff", "862a90b4fffffff", "892a90b4917ffff", "8f2a90b4915d388")),
]
CENTERS = [
  ("862a90b4fffffff", 40.05041861648768, -83.181315523919),
  ("842a90bffffffff", 40.08105106496825, -83.41180170584032),
  ("864c00007ffffff", 23.71792527122296, -67.13232636643565),
  ("8f2a90b4915d388", 40.03339893697043, -83.1588004749386),
  ("8001fffffffffff", 79.24239850975903, 38.02340700796989),
]
DISKS = {
  "862a90b4fffffff": ['862a90a67ffffff', '862a90b47ffffff', '862a90b4fffffff', '862a90b5fffffff', '862a90b6fffffff', '862a95697ffffff', '862a956b7ffffff'],
  # a pentagon: 5 neighbors
  "864c00007ffffff": [
    '864c00007ffffff',
    '864c00017ffffff',
    '864c0001fffffff',
    '864c00027ffffff',
    '864c0002fffffff',
    '864c00037ffffff',
  ],
}


@pytest.mark.parametrize("lat,lng,expected", CELLS)
def test_latlng_to_cell(lat, lng, expected):
  for res, want in zip(RESOLUTIONS, expected, strict=True):
    assert h3lite.cell_to_str(h3lite.latlng_to_cell(lat, lng, res)) == want


@pytest.mark.parametrize("cell,expected", PARENTS)
def test_cell_to_parent(cell, expected):
  # a parent isn't always the cell that holds the same point: H3 children stick out a little
  for res, want in zip(RESOLUTIONS, expected, strict=True):
    assert h3lite.cell_to_str(h3lite.cell_to_parent(h3lite.str_to_cell(cell), res)) == want
    assert h3lite.get_resolution(h3lite.str_to_cell(want)) == res


@pytest.mark.parametrize("cell,lat,lng", CENTERS)
def test_cell_to_latlng(cell, lat, lng):
  got = h3lite.cell_to_latlng(h3lite.str_to_cell(cell))
  assert got == pytest.approx((lat, lng), abs=1e-9)


@pytest.mark.parametrize("cell,expected", DISKS.items())
def test_grid_disk1(cell, expected):
  got = {h3lite.cell_to_str(c) for c in h3lite.grid_disk1(h3lite.str_to_cell(cell))}
  assert got == set(expected)


def test_bad_input():
  with pytest.raises(ValueError):
    h3lite.latlng_to_cell(40.0, -83.0, 16)
  with pytest.raises(ValueError):
    h3lite.latlng_to_cell(float("nan"), -83.0, 6)
  with pytest.raises(ValueError):
    h3lite.cell_to_parent(h3lite.str_to_cell("862a90b4fffffff"), 7)


def test_matches_h3_on_random_points():
  h3 = pytest.importorskip("h3")
  rnd = random.Random(0)
  for _ in range(1500):
    lat, lng = rnd.uniform(-90, 90), rnd.uniform(-180, 180)
    for res in range(16):
      want = h3.latlng_to_cell(lat, lng, res)
      cell = h3lite.latlng_to_cell(lat, lng, res)
      assert h3lite.cell_to_str(cell) == want
      assert h3lite.cell_to_latlng(cell) == pytest.approx(h3.cell_to_latlng(want), abs=1e-9)
    want_disk = {h3.str_to_int(c) for c in h3.grid_disk(h3.latlng_to_cell(lat, lng, 6), 1)}
    assert h3lite.grid_disk1(h3lite.latlng_to_cell(lat, lng, 6)) == want_disk
