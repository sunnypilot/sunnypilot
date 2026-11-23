"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import math
import time
from collections import deque

import numpy as np

import openpilot.cereal.messaging as messaging
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.common.transformations.orientation import rot_from_euler

EARTH_RADIUS = 6378137.0
GPS_LATENCY = {'gpsLocation': 0.630, 'gpsLocationExternal': 0.095}  # s, empirical fix latency per receiver
RESET_DISTANCE = 100.0  # m
MAX_REJECTS = 5
MAX_POS_STD = 50.0  # m
MIN_BEARING_SPEED = 5.0  # m/s
MAX_BEARING_ACCURACY = 10.0  # deg
GPS_TIMEOUT = 2.0  # s
SEED_INTERVAL = 60.0  # s


def wrap(a: float) -> float:
  return (a + math.pi) % (2 * math.pi) - math.pi


class GpsFuser:
  def __init__(self):
    self.t: float | None = None
    self.lat = self.lon = self.heading = math.nan
    self.pos_var = self.heading_var = math.inf
    self.history: deque = deque(maxlen=40)
    self.rejects = 0

  @property
  def initialized(self) -> bool:
    return math.isfinite(self.lat)

  @property
  def valid(self) -> bool:
    return self.initialized and math.isfinite(self.heading) and self.pos_var < MAX_POS_STD ** 2

  def _move(self, north: float, east: float) -> None:
    self.lat += math.degrees(north / EARTH_RADIUS)
    self.lon += math.degrees(east / (EARTH_RADIUS * math.cos(math.radians(self.lat))))

  @staticmethod
  def _offset(lat: float, lon: float, ref_lat: float, ref_lon: float) -> tuple[float, float]:
    north = math.radians(lat - ref_lat) * EARTH_RADIUS
    east = math.radians(lon - ref_lon) * EARTH_RADIUS * math.cos(math.radians(ref_lat))
    return north, east

  def _state_at(self, t: float) -> tuple[float, float, float]:
    for ht, lat, lon, heading in reversed(self.history):
      if ht <= t:
        return lat, lon, heading
    return self.lat, self.lon, self.heading

  def predict(self, t: float, speed: float, yaw_rate: float) -> None:
    dt = 0.0 if self.t is None else t - self.t
    self.t = t
    if not 0.0 < dt < 1.0 or not self.initialized:
      return
    if math.isfinite(self.heading):
      self.heading = (self.heading + yaw_rate * dt) % (2 * math.pi)
      self._move(speed * dt * math.cos(self.heading), speed * dt * math.sin(self.heading))
    # dead reckoning error grows with distance driven (speed scale and heading error), not as a random walk
    drift = (0.03 + math.sqrt(min(self.heading_var, 1.0))) * abs(speed) * dt
    self.pos_var = (math.sqrt(self.pos_var) + drift) ** 2 + 0.01 * dt
    self.heading_var += 1e-5 * dt
    self.history.append((t, self.lat, self.lon, self.heading))

  def update_gps(self, t: float, gps, latency: float) -> None:
    # qcom reports no horizontal accuracy
    accuracy = gps.horizontalAccuracy if gps.horizontalAccuracy > 0 else math.sqrt(3) * gps.verticalAccuracy
    if not gps.hasFix or not 0 < accuracy < 1500 or gps.speedAccuracy <= 0:
      return
    if abs(gps.latitude) > 90 or abs(gps.longitude) > 180:
      return

    then_lat, then_lon, then_heading = self._state_at(t - latency)
    moved = self._offset(self.lat, self.lon, then_lat, then_lon) if self.initialized else (0.0, 0.0)
    bearing = math.radians(gps.bearingDeg)
    bearing_ok = gps.speed > MIN_BEARING_SPEED and 0 < gps.bearingAccuracyDeg < MAX_BEARING_ACCURACY
    pos_r = accuracy ** 2

    innov = self._offset(gps.latitude, gps.longitude, then_lat, then_lon) if self.initialized else (math.inf, math.inf)
    dist = math.hypot(*innov)
    if not self.initialized or dist > RESET_DISTANCE or self.rejects >= MAX_REJECTS:
      self.lat, self.lon = gps.latitude, gps.longitude
      self._move(*moved)
      self.pos_var = pos_r
      self.rejects = 0
      self.history.clear()
      if bearing_ok:
        self.heading, self.heading_var = bearing, math.radians(gps.bearingAccuracyDeg) ** 2
      return

    s = self.pos_var + pos_r
    if dist ** 2 > 9.0 * s and dist > 10.0:
      self.rejects += 1
      return
    self.rejects = 0
    k = self.pos_var / s
    lat0, lon0 = self.lat, self.lon
    self._move(k * innov[0], k * innov[1])
    dlat, dlon = self.lat - lat0, self.lon - lon0
    self.history = deque(((ht, lat + dlat, lon + dlon, h) for ht, lat, lon, h in self.history), maxlen=self.history.maxlen)
    self.pos_var *= 1 - k

    if bearing_ok:
      head_r = math.radians(gps.bearingAccuracyDeg) ** 2
      if not math.isfinite(self.heading):
        self.heading, self.heading_var = bearing, head_r
      else:
        kh = self.heading_var / (self.heading_var + head_r)
        self.heading = (self.heading + kh * wrap(bearing - then_heading)) % (2 * math.pi)
        self.heading_var *= 1 - kh


def main():
  params = Params()
  gps_service = get_gps_location_service(params)
  latency = GPS_LATENCY[gps_service]
  sm = messaging.SubMaster(['deviceMotion', 'carState', 'extrinsicsCalibration', gps_service], poll='deviceMotion')
  pm = messaging.PubMaster(['gpsLocationSP'])
  fuser = GpsFuser()
  calib_from_device = np.eye(3)
  last_seed = 0.0

  while True:
    sm.update()
    t = sm.logMonoTime['deviceMotion'] * 1e-9

    rpy = list(sm['extrinsicsCalibration'].rpyCalib)
    if sm.updated['extrinsicsCalibration'] and len(rpy) == 3:
      calib_from_device = rot_from_euler(rpy).T

    gps = sm[gps_service]
    gps_t = sm.logMonoTime[gps_service] * 1e-9
    if sm.updated[gps_service] and sm.valid[gps_service]:
      fuser.update_gps(gps_t, gps, latency)

    if sm.valid['deviceMotion']:
      w = sm['deviceMotion'].angularVelocityDevice
      yaw_rate = float((calib_from_device @ np.array([w.x, w.y, w.z]))[2])
      fuser.predict(t, sm['carState'].vEgo, yaw_rate)

    gps_ok = gps.hasFix and t - gps_t < GPS_TIMEOUT
    msg = messaging.new_message('gpsLocationSP', valid=fuser.valid or gps_ok)
    out = msg.gpsLocationSP
    out.gpsOK = gps_ok
    out.fused = fuser.valid
    if fuser.valid:
      out.hasFix = True
      out.latitude, out.longitude = fuser.lat, fuser.lon
      out.bearingDeg = math.degrees(fuser.heading) % 360
      out.bearingAccuracyDeg = math.degrees(math.sqrt(fuser.heading_var))
      out.horizontalAccuracy = math.sqrt(fuser.pos_var)
      out.speed = sm['carState'].vEgo
    elif gps_ok:
      out.hasFix = True
      out.latitude, out.longitude = gps.latitude, gps.longitude
      out.bearingDeg, out.bearingAccuracyDeg = gps.bearingDeg, gps.bearingAccuracyDeg
      out.horizontalAccuracy, out.speed = gps.horizontalAccuracy, gps.speed
    pm.send('gpsLocationSP', msg)

    if fuser.valid and time.monotonic() - last_seed > SEED_INTERVAL:
      params.put("LastGPSPositionFused", json.dumps({"latitude": fuser.lat, "longitude": fuser.lon}))
      last_seed = time.monotonic()


if __name__ == "__main__":
  main()
