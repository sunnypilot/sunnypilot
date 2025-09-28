#!/usr/bin/env python3
import math
import os
import time
import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths
from openpilot.system.loggerd.xattr_cache import setxattr


class ParkingMonitor:
  def __init__(self):
    self.params = Params()
    self.sm = messaging.SubMaster([
      'accelerometer',
      'deviceState',
      'pandaStates'
    ])
    self.pm = messaging.PubMaster(['parkingEvent'])

    # State
    self.parking_mode_active = False
    self.shock_detected = False
    self.preserve_countdown = 0

    # Config
    self.SHOCK_THRESHOLD_G = 2.0
    self.PRESERVE_BEFORE = 2
    self.PRESERVE_AFTER = 4
    self.LOW_VOLTAGE_THRESHOLD = 11.8
    self.MAX_PARKING_DURATION_SEC = 12 * 3600  # 12 hours

    self.parking_start_time = 0
    self.rk = Ratekeeper(10)

  def is_parked(self) -> bool:
    if not self.sm.valid['pandaStates']:
      return False
    return all(not ps.ignitionLine for ps in self.sm['pandaStates'])

  def detect_shock(self) -> tuple[bool, float]:
    if not self.sm.valid['accelerometer']:
      return False, 0.0

    accel = self.sm['accelerometer'].acceleration
    magnitude_ms2 = math.sqrt(accel.v[0]**2 + accel.v[1]**2 + accel.v[2]**2)
    magnitude_g = magnitude_ms2 / 9.81

    return magnitude_g > self.SHOCK_THRESHOLD_G, magnitude_g

  def check_battery_voltage(self) -> float:
    if not self.sm.valid['deviceState']:
      return 13.0  # Default safe value

    return self.sm['deviceState'].batteryVoltage

  def should_shutdown(self) -> bool:
    voltage = self.check_battery_voltage()
    if voltage < self.LOW_VOLTAGE_THRESHOLD:
      cloudlog.warning(f"Low voltage detected: {voltage:.2f}V")
      return True

    parking_duration = time.monotonic() - self.parking_start_time
    if parking_duration > self.MAX_PARKING_DURATION_SEC:
      cloudlog.warning(f"Max parking duration exceeded: {parking_duration/3600:.1f}h")
      return True

    return False

  def mark_current_segment_for_preservation(self):
    current_route = self.params.get("CurrentRoute", encoding='utf-8')
    if not current_route:
      return

    log_root = Paths.log_root()
    route_path = os.path.join(log_root, current_route)
    if not os.path.exists(route_path):
      return

    # Marquer le segment courant avec l'attribut preserve
    try:
      setxattr(route_path, 'user.preserve', b'1')
      cloudlog.info(f"Marked segment for preservation: {current_route}")
    except OSError as e:
      cloudlog.error(f"Failed to mark segment: {e}")

  def step(self):
    self.sm.update()

    is_parked = self.is_parked()
    enable_param = self.params.get_bool("EnableParkingMode")

    # Activation/désactivation parking mode
    if is_parked and enable_param and not self.parking_mode_active:
      cloudlog.info("Entering parking mode")
      self.parking_mode_active = True
      self.parking_start_time = time.monotonic()
      self.params.put_bool("ParkingModeActive", True)
    elif (not is_parked or not enable_param) and self.parking_mode_active:
      cloudlog.info("Exiting parking mode")
      self.parking_mode_active = False
      self.params.put_bool("ParkingModeActive", False)

    # Vérification batterie et durée
    if self.parking_mode_active and self.should_shutdown():
      cloudlog.warning("Parking mode shutdown triggered")
      self.parking_mode_active = False
      self.params.put_bool("ParkingModeActive", False)
      self.params.put_bool("DoShutdown", True)

    # Détection chocs si en parking mode
    if self.parking_mode_active:
      shock, magnitude = self.detect_shock()
      if shock:
        cloudlog.warning(f"Shock detected: {magnitude:.2f}g")
        self.shock_detected = True
        self.preserve_countdown = self.PRESERVE_AFTER
        self.mark_current_segment_for_preservation()

        # Envoyer événement
        msg = messaging.new_message('parkingEvent')
        msg.valid = True
        msg.parkingEvent.shockDetected = True
        msg.parkingEvent.magnitude = magnitude
        msg.parkingEvent.timestamp = int(time.monotonic() * 1e9)
        self.pm.send('parkingEvent', msg)


def main() -> None:
  monitor = ParkingMonitor()
  cloudlog.info("parking_monitor started")

  while True:
    monitor.step()
    monitor.rk.keep_time()


if __name__ == "__main__":
  main()
