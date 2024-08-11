import math
from abc import abstractmethod, ABC

from cereal import custom, messaging
from openpilot.selfdrive.navd.helpers import Coordinate
from openpilot.selfdrive.sunnypilot.live_map_data import get_debug


class BaseMapData(ABC):
  def __init__(self):
    self._last_gps: Coordinate | None = None
    self._gps_sock = None
    self._data_type = custom.LiveMapDataSP.DataType.default
    self._sub_master = messaging.SubMaster(['liveLocationKalman', 'carControl'])
    self._pub_master = messaging.PubMaster(['liveMapDataSP'])

  @abstractmethod
  def update_location(self, current_location: Coordinate):
    pass

  @abstractmethod
  def get_current_speed_limit(self) -> float:
    pass

  @abstractmethod
  def get_next_speed_limit_and_distance(self) -> (float, float):
    pass

  @abstractmethod
  def get_current_road_name(self) -> str:
    pass

  def _is_gps_data_valid(self) -> bool:
    all_sock_alive = self._sub_master.all_alive(service_list=[self._gps_sock])
    all_sock_valid = self._sub_master.all_valid(service_list=[self._gps_sock])
    return all_sock_alive and all_sock_valid

  def get_current_location(self) -> Coordinate | None:
    self._gps_sock = "liveLocationKalman"
    if not self._sub_master.updated[self._gps_sock] or not self._sub_master.valid[self._gps_sock]:
      return None

    _last_gps = self._sub_master[self._gps_sock]
    # ignore the message if the fix is invalid
    if not _last_gps.positionGeodetic.valid:
      return None

    kalman_bearing_deg = math.degrees(_last_gps.calibratedOrientationNED.value[2])
    kalman_speed = _last_gps.velocityCalibrated.value[2]
    kalman_latitude = _last_gps.positionGeodetic.value[0];
    kalman_longitude = _last_gps.positionGeodetic.value[1]

    result = Coordinate(kalman_latitude, kalman_longitude)
    result.annotations['unixTimestampMillis'] = _last_gps.unixTimestampMillis
    result.annotations['speed'] = kalman_speed
    result.annotations['bearingDeg'] = kalman_bearing_deg
    result.annotations['accuracy'] = 1  # Hardcoded since liveLocationKalman does not report this.
    result.annotations['bearingAccuracyDeg'] = 1.  # you'll need to assign this if available

    return result

  def get_live_map_data_sp(self, speed_limit, next_speed_limit, next_speed_limit_distance, current_road_name):
    last_gps = self.get_current_location()
    map_data_msg = messaging.new_message('liveMapDataSP')
    map_data_msg.valid = self._is_gps_data_valid()

    live_map_data = map_data_msg.liveMapDataSP
    if last_gps:
      live_map_data.lastGpsTimestamp = last_gps.annotations.get('unixTimestampMillis', 0)
      live_map_data.lastGpsLatitude = last_gps.latitude
      live_map_data.lastGpsLongitude = last_gps.longitude
      live_map_data.lastGpsSpeed = last_gps.annotations.get('speed', 0)
      live_map_data.lastGpsBearingDeg = last_gps.annotations.get('bearingDeg', 0)
      live_map_data.lastGpsAccuracy = last_gps.annotations.get('accuracy', 0)
      live_map_data.lastGpsBearingAccuracyDeg = last_gps.annotations.get('bearingAccuracyDeg', 0)

    live_map_data.speedLimitValid = bool(speed_limit > 0)
    live_map_data.speedLimit = speed_limit
    live_map_data.speedLimitAheadValid = bool(next_speed_limit > 0)
    live_map_data.speedLimitAhead = float(next_speed_limit)
    live_map_data.speedLimitAheadDistance = float(next_speed_limit_distance)
    live_map_data.currentRoadName = str(current_road_name)
    live_map_data.dataType = self._data_type

    return map_data_msg

  def publish(self):
    speed_limit = self.get_current_speed_limit()
    current_road_name = self.get_current_road_name()
    next_speed_limit, next_speed_limit_distance = self.get_next_speed_limit_and_distance()

    live_map_data_sp = self.get_live_map_data_sp(
      speed_limit,
      next_speed_limit,
      next_speed_limit_distance,
      current_road_name
    )

    self._pub_master.send('liveMapDataSP', live_map_data_sp)
    get_debug(f"SRC: [{self.__class__.__name__}] | SLC: [{speed_limit}] | NSL: [{next_speed_limit}] | NSLD: [{next_speed_limit_distance}] | CRN: [{current_road_name}] | GPS: [{self._last_gps}] Annotations: [{', '.join(f'{key}: {value}' for key, value in self._last_gps.annotations.items()) if self._last_gps else []}]")

  def tick(self):
    self._sub_master.update()
    self._last_gps = self.get_current_location()
    self.update_location(self._last_gps)
    self.publish()
