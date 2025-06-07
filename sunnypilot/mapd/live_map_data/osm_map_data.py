import json
import platform

from openpilot.common.params import Params
from openpilot.sunnypilot.navd.helpers import Coordinate
from openpilot.sunnypilot.mapd.live_map_data.base_map_data import BaseMapData


class OsmMapData(BaseMapData):
  def __init__(self):
    super().__init__()
    self.params = Params()
    self.mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else self.params

  def update_location(self, current_location: Coordinate | None) -> None:
    if not current_location:
      return

    last_gps_position_for_osm = {
      "latitude": current_location.latitude,
      "longitude": current_location.longitude,
      "bearing": current_location.annotations.get("bearingDeg", 0)
    }
    self.mem_params.put("LastGPSPosition", json.dumps(last_gps_position_for_osm))

  def get_current_speed_limit(self) -> float:
    return float(self.mem_params.get("MapSpeedLimit", encoding='utf8') or 0.0)

  def get_current_road_name(self) -> str:
    return self.mem_params.get("RoadName", encoding='utf8') or ""

  def get_next_speed_limit_and_distance(self, current_location: Coordinate | None) -> tuple[float, float]:
    next_speed_limit_section_str = self.mem_params.get("NextMapSpeedLimit", encoding='utf8')
    next_speed_limit_section = json.loads(next_speed_limit_section_str) if next_speed_limit_section_str else {}
    next_speed_limit = next_speed_limit_section.get('speedlimit', 0.0)
    next_speed_limit_latitude = next_speed_limit_section.get('latitude')
    next_speed_limit_longitude = next_speed_limit_section.get('longitude')
    next_speed_limit_distance = 0.0

    if next_speed_limit_latitude and next_speed_limit_longitude:
      next_speed_limit_coordinates = Coordinate(next_speed_limit_latitude, next_speed_limit_longitude)
      next_speed_limit_distance = (current_location or Coordinate(0, 0)).distance_to(next_speed_limit_coordinates)

    return next_speed_limit, next_speed_limit_distance
