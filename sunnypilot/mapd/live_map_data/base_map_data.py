import time
from abc import abstractmethod, ABC

from cereal import custom, messaging
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.sunnypilot.navd.helpers import Coordinate
from openpilot.sunnypilot.mapd.live_map_data import get_debug


class BaseMapData(ABC):
  def __init__(self):
    self.params = Params()
    self._last_gps: Coordinate | None = None
    self._gps_location_service = get_gps_location_service(self.params)
    self._gps_packets = [self._gps_location_service]
    self._data_type = custom.LiveMapDataSP.DataType.default
    self._sm = messaging.SubMaster(['livePose', 'carControl'] + self._gps_packets)
    self._pm = messaging.PubMaster(['liveMapDataSP'])

  @abstractmethod
  def update_location(self, current_location: Coordinate):
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

  def _is_gps_data_valid(self) -> bool:
    all_sock_alive = self._sm.all_alive(service_list=[self._gps_location_service])
    all_sock_valid = self._sm.all_valid(service_list=[self._gps_location_service])
    return bool(all_sock_alive and all_sock_valid)

  def get_current_location(self) -> Coordinate | None:
    if not self._sm.updated[self._gps_location_service] or not self._sm.valid[self._gps_location_service]:
      return None

    _last_gps = self._sm[self._gps_location_service]

    # ignore the message if the fix is invalid
    gps_ok = self._sm.updated[self._gps_location_service] or (time.monotonic() - self._sm.logMonoTime[self._gps_location_service] / 1e9) > 2.0
    if not gps_ok and self._sm['livePose'].inputsOK:
      return None

    result = Coordinate(_last_gps.latitude, _last_gps.longitude)
    result.annotations['unixTimestampMillis'] = _last_gps.unixTimestampMillis
    result.annotations['speed'] = _last_gps.speed
    result.annotations['bearingDeg'] = _last_gps.bearingDeg
    result.annotations['accuracy'] = 1  # Hardcoded for now
    result.annotations['bearingAccuracyDeg'] = _last_gps.bearingAccuracyDeg

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

    self._pm.send('liveMapDataSP', live_map_data_sp)
    get_debug(f"SRC: [{self.__class__.__name__}] | SLC: [{speed_limit}] | NSL: [{next_speed_limit}] | " +
              f"NSLD: [{next_speed_limit_distance}] | CRN: [{current_road_name}] | GPS: [{self._last_gps}] " +
              f"Annotations: [{', '.join(f'{key}: {value}' for key, value in self._last_gps.annotations.items()) if self._last_gps else []}]")

  def tick(self):
    self._sm.update()
    self._last_gps = self.get_current_location()
    self.update_location(self._last_gps)
    self.publish()
