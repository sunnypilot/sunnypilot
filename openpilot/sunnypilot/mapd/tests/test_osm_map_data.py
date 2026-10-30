"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import math
import platform

import openpilot.cereal.messaging as messaging
from openpilot.cereal import log
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.mapd.live_map_data.osm_map_data import OsmMapData


class TestOsmMapData(OpenpilotTestCase):
  """The mapd binary reads its position from the memory params as JSON, so mapd_manager has to feed it."""

  LATITUDE = 32.875134
  LONGITUDE = -117.209777
  ALTITUDE = 42.0
  BEARING = 90.0

  def setup_method(self):
    self.mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else Params()
    self.mem_params.remove("LastGPSPosition")
    self.map_data = OsmMapData()
    self.pm = messaging.PubMaster(['liveLocationKalman'])

  def location_message(self, status: log.LiveLocationKalman.Status, position_valid: bool):
    msg = messaging.new_message('liveLocationKalman', valid=True)
    location = msg.liveLocationKalman
    location.status = status
    location.positionGeodetic = {'value': [self.LATITUDE, self.LONGITUDE, self.ALTITUDE], 'valid': position_valid}
    location.calibratedOrientationNED = {'value': [0.0, 0.0, math.radians(self.BEARING)], 'valid': True}
    return msg

  def send_location(self, status: log.LiveLocationKalman.Status, position_valid: bool) -> None:
    # the first exchange synchronizes the PUB/SUB connection, the second one is actually received
    self.pm.send('liveLocationKalman', self.location_message(status, position_valid))
    self.map_data.sm.update(1000)
    self.pm.send('liveLocationKalman', self.location_message(status, position_valid))
    self.map_data.sm.update(1000)

  def read_position(self) -> dict:
    value = self.mem_params.get("LastGPSPosition")
    self.assertIsNotNone(value, "LastGPSPosition was not written for mapd")
    return json.loads(value)

  def test_writes_position_for_mapd(self):
    self.send_location(log.LiveLocationKalman.Status.valid, True)
    self.map_data.tick()

    position = self.read_position()
    self.assertAlmostEqual(position['latitude'], self.LATITUDE, delta=1e-6)
    self.assertAlmostEqual(position['longitude'], self.LONGITUDE, delta=1e-6)
    self.assertAlmostEqual(position['bearing'], self.BEARING, delta=1e-6)

  def test_invalid_localizer_keeps_last_known_position(self):
    self.send_location(log.LiveLocationKalman.Status.valid, True)
    self.map_data.tick()

    self.send_location(log.LiveLocationKalman.Status.uninitialized, False)
    self.map_data.tick()

    position = self.read_position()
    self.assertAlmostEqual(position['latitude'], self.LATITUDE, delta=1e-6)
    self.assertAlmostEqual(position['longitude'], self.LONGITUDE, delta=1e-6)
