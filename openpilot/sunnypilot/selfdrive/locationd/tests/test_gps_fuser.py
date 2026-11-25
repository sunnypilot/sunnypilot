"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from types import SimpleNamespace

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.locationd.gps_fuser import EARTH_RADIUS, GPS_LATENCY, GpsFuser

LAT0, LON0 = 39.0, -77.0
LATENCY = GPS_LATENCY['gpsLocation']


def fix(north, east, speed=30.0, bearing=90.0, h_acc=0.0, v_acc=1.5):
  return SimpleNamespace(latitude=LAT0 + math.degrees(north / EARTH_RADIUS),
                         longitude=LON0 + math.degrees(east / (EARTH_RADIUS * math.cos(math.radians(LAT0)))),
                         speed=speed, bearingDeg=bearing, horizontalAccuracy=h_acc, verticalAccuracy=v_acc,
                         speedAccuracy=0.3, bearingAccuracyDeg=0.5, hasFix=True)


def position(f: GpsFuser) -> tuple[float, float]:
  north = math.radians(f.lat - LAT0) * EARTH_RADIUS
  east = math.radians(f.lon - LON0) * EARTH_RADIUS * math.cos(math.radians(LAT0))
  return north, east


class TestGpsFuser(OpenpilotTestCase):
  def drive(self, f, seconds, speed=30.0, start=0.0, gps=lambda t, true_east: fix(0.0, true_east)):
    t = start
    while t < start + seconds:
      t = round(t + 0.05, 2)
      f.predict(t, speed, 0.0)
      if abs(t - round(t)) < 1e-6:
        f.update_gps(t, gps(t, speed * (t - LATENCY)), LATENCY)
    return t

  def test_compensates_latency(self):
    f = GpsFuser()
    t = self.drive(f, 30)
    self.assertTrue(f.valid)
    north, east = position(f)
    self.assertAlmostEqual(east, 30.0 * t, delta=3.0)
    self.assertAlmostEqual(north, 0.0, delta=1.0)

  def test_rejects_single_jump(self):
    f = GpsFuser()
    t = self.drive(f, 20)
    f.predict(t + 0.05, 30.0, 0.0)
    f.update_gps(t + 0.05, fix(40.0, 30.0 * (t + 0.05 - LATENCY)), LATENCY)
    self.assertAlmostEqual(position(f)[0], 0.0, delta=2.0)

  def test_follows_persistent_offset(self):
    f = GpsFuser()
    t = self.drive(f, 20)
    self.drive(f, 10, start=t, gps=lambda _, e: fix(150.0, e))
    self.assertAlmostEqual(position(f)[0], 150.0, delta=3.0)

  def test_ignores_bearing_when_slow(self):
    f = GpsFuser()
    t = self.drive(f, 20)
    self.drive(f, 5, speed=1.0, start=t, gps=lambda _, e: fix(0.0, e, speed=1.0, bearing=270.0))
    self.assertAlmostEqual(math.degrees(f.heading), 90.0, delta=1.0)

  def test_invalid_after_long_outage(self):
    f = GpsFuser()
    t = self.drive(f, 20)
    self.drive(f, 120, start=t, gps=lambda _, e: SimpleNamespace(hasFix=False, horizontalAccuracy=0.0, verticalAccuracy=0.0,
                                                                  speedAccuracy=0.0, latitude=0.0, longitude=0.0))
    self.assertFalse(f.valid)

