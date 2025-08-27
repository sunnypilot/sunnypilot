"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
from abc import abstractmethod, ABC

from cereal import messaging
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.sunnypilot.navd.helpers import Coordinate, coordinate_from_param


class BaseMapData(ABC):
  def __init__(self):
    self.params = Params()

    self.gps_location_service = get_gps_location_service(self.params)
    self.sm = messaging.SubMaster(['livePose', 'carControl'] + [self.gps_location_service])
    self.pm = messaging.PubMaster(['liveMapDataSP'])

    self.last_position = coordinate_from_param("LastGPSPosition", self.params)
    self.last_altitude = None

  @abstractmethod
  def update_location(self) -> None:
    pass

  @abstractmethod
  def get_current_speed_limit(self) -> float:
    pass

  @abstractmethod
  def get_next_speed_limit_and_distance(self) -> tuple[float, float]:
    pass

  @abstractmethod
  def get_current_road_name(self) -> str:
    pass

  def get_current_location(self) -> None:
    gps = self.sm[self.gps_location_service]

    # ignore the message if the fix is invalid
    gps_ok = self.sm.updated[self.gps_location_service] or (time.monotonic() - self.sm.logMonoTime[self.gps_location_service] / 1e9) > 2.0
    if not gps_ok and self.sm['livePose'].inputsOK:
      return None

    # livePose has these data, but aren't on cereal
    self.last_position = Coordinate(gps.latitude, gps.longitude)
    self.last_altitude = gps.altitude

  def publish(self) -> None:
    speed_limit = self.get_current_speed_limit()
    next_speed_limit, next_speed_limit_distance = self.get_next_speed_limit_and_distance()

    mapd_sp_send = messaging.new_message('liveMapDataSP')
    mapd_sp_send.valid = self.sm.all_checks(service_list=[self.gps_location_service, 'livePose'])
    live_map_data = mapd_sp_send.liveMapDataSP

    live_map_data.speedLimitValid = bool(speed_limit > 0)
    live_map_data.speedLimit = speed_limit
    live_map_data.speedLimitAheadValid = bool(next_speed_limit > 0)
    live_map_data.speedLimitAhead = next_speed_limit
    live_map_data.speedLimitAheadDistance = next_speed_limit_distance
    live_map_data.roadName = self.get_current_road_name()

    self.pm.send('liveMapDataSP', mapd_sp_send)

  def tick(self) -> None:
    self.sm.update()
    self.get_current_location()
    self.update_location()
    self.publish()
