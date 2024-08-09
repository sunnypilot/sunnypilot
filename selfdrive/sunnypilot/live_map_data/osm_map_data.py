import json
import platform

from openpilot.common.params_pyx import Params
from openpilot.selfdrive.navd.helpers import Coordinate
from openpilot.selfdrive.sunnypilot.live_map_data import DataType
from openpilot.selfdrive.sunnypilot.live_map_data.base_map_data import BaseMapData


class OsmMapData(BaseMapData):
  def __init__(self):
    super().__init__()
    self.last_gps = Coordinate(0.0, 0.0)
    self.params = Params()
    self.mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else self.params
    self.data_type = DataType.offline

  def update_location(self, current_location):
    self.last_gps = current_location
    if not self.last_gps:
      return

    last_gps_position_for_osm = {
      "latitude": self.last_gps.latitude,
      "longitude": self.last_gps.longitude,
      "bearing": self.last_gps.annotations.get("bearingDeg", 0)
    }
    self.mem_params.put("LastGPSPosition", json.dumps(last_gps_position_for_osm))

  def get_current_speed_limit(self):
    speed_limit = self.mem_params.get("MapSpeedLimit", encoding='utf8')
    return float(speed_limit) if speed_limit else 0.0

  def get_current_road_name(self):
    current_road_name = self.mem_params.get("RoadName", encoding='utf8')
    return current_road_name if current_road_name else ""

  def get_next_speed_limit_and_distance(self):
    next_speed_limit_section_str = self.mem_params.get("NextMapSpeedLimit", encoding='utf8')
    next_speed_limit_section = json.loads(next_speed_limit_section_str) if next_speed_limit_section_str else {}
    next_speed_limit = next_speed_limit_section.get('speedlimit', 0.0)
    next_speed_limit_latitude = next_speed_limit_section.get('latitude')
    next_speed_limit_longitude = next_speed_limit_section.get('longitude')
    next_speed_limit_distance = 0

    if next_speed_limit_latitude and next_speed_limit_longitude:
      next_speed_limit_coordinates = Coordinate(next_speed_limit_latitude, next_speed_limit_longitude)
      next_speed_limit_distance = (self.last_gps or Coordinate(0, 0)).distance_to(next_speed_limit_coordinates)

    return next_speed_limit, next_speed_limit_distance
