#!/usr/bin/env python3
import math
import os
import time
import numpy as np
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
      'pandaStates',
      'carState'
    ])
    self.pm = messaging.PubMaster(['parkingEvent'])

    # State
    self.parking_mode_active = False
    self.is_calibrating = False
    self.calibration_data = []
    self.mean_accel = None
    self.cov_inv_accel = None

    # Config
    self.MAHALANOBIS_THRESHOLD = 15.0  # Statistical distance threshold for shock detection
    self.CALIBRATION_SAMPLES = 100     # 10 seconds at 10Hz to calibrate baseline vibrations
    self.PRESERVE_BEFORE = 2           # Preserve 2 segments before shock (2 × 60s = 2min)
    self.PRESERVE_AFTER = 4            # Preserve 4 segments after shock (4 × 60s = 4min)
    self.LOW_VOLTAGE_THRESHOLD = 11.8  # Shutdown if battery < 11.8V
    self.MAX_PARKING_DURATION_SEC = 12 * 3600  # 12 hours max parking duration

    self.parking_start_time = 0
    self.rk = Ratekeeper(10)

  def is_parked(self) -> bool:
    if not self.sm.valid['pandaStates']:
      return False

    # Check ignition is off
    ignition_off = all(not ps.ignitionLine for ps in self.sm['pandaStates'])

    # Check vehicle is not moving (speed < 0.5 m/s ~= 1.8 km/h)
    standstill = True
    if self.sm.valid['carState']:
      standstill = self.sm['carState'].vEgo < 0.5

    return ignition_off and standstill

  def calibrate(self):
    if len(self.calibration_data) < self.CALIBRATION_SAMPLES:
      return

    data = np.array(self.calibration_data)
    self.mean_accel = np.mean(data, axis=0)

    try:
      cov = np.cov(data, rowvar=False)
      self.cov_inv_accel = np.linalg.inv(cov)
      cloudlog.info(f"Parking mode calibrated. Mean: {self.mean_accel}, Covariance: {cov}")
    except np.linalg.LinAlgError:
      # Covariance matrix is singular, use a default identity matrix
      cloudlog.warning("Singular covariance matrix, using identity.")
      self.cov_inv_accel = np.identity(3)

    self.is_calibrating = False
    self.calibration_data = [] # Clear data after calibration

  def detect_shock_mahalanobis(self) -> tuple[bool, float]:
    if self.mean_accel is None or self.cov_inv_accel is None or not self.sm.valid['accelerometer']:
      return False, 0.0

    current_accel = np.array(self.sm['accelerometer'].acceleration.v)
    diff = current_accel - self.mean_accel

    # Mahalanobis distance squared: D² = (x - μ)ᵀ Σ⁻¹ (x - μ)
    mahal_dist_sq = diff.T @ self.cov_inv_accel @ diff

    is_shock = mahal_dist_sq > self.MAHALANOBIS_THRESHOLD
    return is_shock, math.sqrt(mahal_dist_sq)

  def check_battery_voltage(self) -> float:
    if not self.sm.valid['deviceState']:
      return 13.0  # Default safe value

    return float(self.sm['deviceState'].batteryVoltage)

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
      cloudlog.info("Entering parking mode, starting calibration...")
      self.parking_mode_active = True
      self.is_calibrating = True
      self.calibration_data = []
      self.parking_start_time = time.monotonic()
      self.params.put_bool("ParkingModeActive", True)
    elif (not is_parked or not enable_param) and self.parking_mode_active:
      cloudlog.info("Exiting parking mode")
      self.parking_mode_active = False
      self.is_calibrating = False
      self.params.put_bool("ParkingModeActive", False)

    # Logique principale du mode parking
    if self.parking_mode_active:
      # Vérification batterie et durée
      if self.should_shutdown():
        cloudlog.warning("Parking mode shutdown triggered")
        self.parking_mode_active = False
        self.params.put_bool("ParkingModeActive", False)
        self.params.put_bool("DoShutdown", True)
        return

      # Phase de calibration
      if self.is_calibrating:
        if self.sm.valid['accelerometer']:
          self.calibration_data.append(self.sm['accelerometer'].acceleration.v)
        if len(self.calibration_data) >= self.CALIBRATION_SAMPLES:
          self.calibrate()
        return

      # Détection de chocs (après calibration)
      shock, magnitude = self.detect_shock_mahalanobis()
      if shock:
        current_time = int(self.sm['deviceState'].wallTimeNanos / 1e9)
        cloudlog.event("parking_shock_detected", magnitude=magnitude, timestamp=current_time)
        cloudlog.warning(f"Parking Mode: Impact detected! Magnitude (Mahalanobis): {magnitude:.2f} at {current_time}")

        self.mark_current_segment_for_preservation()

        # Store shock info for UI and settings display
        self.params.put("LastParkingShockTime", str(current_time))
        self.params.put("LastParkingShockMagnitude", str(magnitude))

        # Envoyer événement
        msg = messaging.new_message('parkingEvent')
        msg.valid = True
        msg.parkingEvent.shockDetected = True
        msg.parkingEvent.magnitude = magnitude
        msg.parkingEvent.timestamp = self.sm['deviceState'].wallTimeNanos
        self.pm.send('parkingEvent', msg)


def main() -> None:
  monitor = ParkingMonitor()
  cloudlog.info("parking_monitor started")

  while True:
    monitor.step()
    monitor.rk.keep_time()


if __name__ == "__main__":
  main()
