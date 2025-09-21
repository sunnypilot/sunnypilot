#!/usr/bin/env python3
"""
Standalone GPS Localizer
Processes GPS data independently from livePose, providing filtered GPS position/velocity
"""

import json
import numpy as np
from typing import Optional
from collections import deque

import cereal.messaging as messaging
from cereal import log
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.common.realtime import config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.common.transformations.coordinates import LocalCoord, geodetic2ecef, ecef2geodetic

# GPS constants
GPS_UBLOX_SENSOR_TIME_OFFSET = 0.050  # s
GPS_QCOM_SENSOR_TIME_OFFSET = 0.630  # s
GPS_VARIANCE_FACTOR_UBLOX = 10.0
GPS_VARIANCE_FACTOR_QCOM = 5.0
GPS_HORIZONTAL_ACCURACY_THRESHOLD = 50.0  # m
GPS_VERTICAL_ACCURACY_THRESHOLD = 100.0  # m
GPS_SPEED_ACCURACY_THRESHOLD = 10.0  # m/s
GPS_SANITY_CHECK_MAX_HORIZONTAL = 200.0  # m/s
GPS_SANITY_CHECK_MAX_VERTICAL = 150.0  # m/s
GPS_RESET_THRESHOLD_HORIZONTAL = 20.0  # m
GPS_RESET_THRESHOLD_VERTICAL = 10.0  # m
GPS_FAKE_OBSERVATION_INTERVAL = 0.1  # s
GPS_SAVE_POSITION_INTERVAL = 60.0  # s


class SimpleGPSKalman:
  """Simplified Kalman filter for GPS position/velocity tracking"""

  def __init__(self):
    # Initial state: approximate ECEF position for San Francisco area
    self.x = np.array([
      -2.71e6,  # x ECEF
      -4.26e6,  # y ECEF
      3.88e6,  # z ECEF
      0.0,  # vx
      0.0,  # vy
      0.0  # vz
    ])

    # Initial covariance
    self.P = np.diag([
      100 ** 2, 100 ** 2, 100 ** 2,  # Position uncertainty
      10 ** 2, 10 ** 2, 10 ** 2  # Velocity uncertainty
    ])

    # Process noise
    self.Q = np.diag([
      0.1 ** 2, 0.1 ** 2, 0.1 ** 2,  # Position process noise
      1.0 ** 2, 1.0 ** 2, 1.0 ** 2  # Velocity process noise
    ])

    self.filter_time = 0.0
    self.initialized = False

  def predict(self, t: float):
    """Predict step of Kalman filter"""
    if not self.initialized:
      self.filter_time = t
      self.initialized = True
      return

    dt = t - self.filter_time
    if dt <= 0:
      return

    # State transition matrix
    F = np.eye(6)
    F[0:3, 3:6] = np.eye(3) * dt

    # Predict state
    self.x = F @ self.x

    # Predict covariance
    self.P = F @ self.P @ F.T + self.Q * dt

    self.filter_time = t

  def update_position(self, z: np.ndarray, R: np.ndarray):
    """Update with position measurement"""
    # Measurement matrix for position
    H = np.zeros((3, 6))
    H[0:3, 0:3] = np.eye(3)

    # Innovation
    y = z - H @ self.x

    # Innovation covariance
    S = H @ self.P @ H.T + R

    # Kalman gain
    K = self.P @ H.T @ np.linalg.inv(S)

    # Update state and covariance
    self.x = self.x + K @ y
    self.P = (np.eye(6) - K @ H) @ self.P

    return y  # Return innovation for error tracking

  def update_velocity(self, z: np.ndarray, R: np.ndarray):
    """Update with velocity measurement"""
    # Measurement matrix for velocity
    H = np.zeros((3, 6))
    H[0:3, 3:6] = np.eye(3)

    # Innovation
    y = z - H @ self.x

    # Innovation covariance
    S = H @ self.P @ H.T + R

    # Kalman gain
    K = self.P @ H.T @ np.linalg.inv(S)

    # Update state and covariance
    self.x = self.x + K @ y
    self.P = (np.eye(6) - K @ H) @ self.P

    return y  # Return innovation for error tracking

  def reset(self, pos: np.ndarray, vel: np.ndarray, pos_var: np.ndarray, vel_var: np.ndarray):
    """Reset filter state"""
    self.x[0:3] = pos
    self.x[3:6] = vel
    self.P = np.diag(np.concatenate([pos_var, vel_var]))


class GPSLocalizer:
  def __init__(self, params: Params):
    self.params = params
    self.kf = SimpleGPSKalman()

    # GPS state
    self.last_gps_msg: Optional[log.Event] = None
    self.last_gps_time = 0.0
    self.gps_valid = False
    self.gps_ok = False
    self.last_fake_gps_time = 0.0
    self.last_position_save_time = 0.0

    # GPS source configuration
    self.gps_location_service = get_gps_location_service(params)
    self.using_ublox = (self.gps_location_service == "gpsLocationExternal")

    if self.using_ublox:
      self.gps_sensor_time_offset = GPS_UBLOX_SENSOR_TIME_OFFSET
      self.gps_variance_factor = GPS_VARIANCE_FACTOR_UBLOX
    else:
      self.gps_sensor_time_offset = GPS_QCOM_SENSOR_TIME_OFFSET
      self.gps_variance_factor = GPS_VARIANCE_FACTOR_QCOM

    # Coordinate converter
    self.converter: Optional[LocalCoord] = None

    # GPS history for sanity checking
    self.gps_history = deque(maxlen=10)

    cloudlog.info(f"GPS Localizer initialized with {self.gps_location_service}")

  @staticmethod
  def validate_gps(gps) -> bool:
    """Validate GPS data quality"""
    # Check fix status
    if gps.flags == 0:
      return False

    # Check accuracy thresholds
    if (gps.horizontalAccuracy > GPS_HORIZONTAL_ACCURACY_THRESHOLD or
          gps.verticalAccuracy > GPS_VERTICAL_ACCURACY_THRESHOLD or
          gps.speedAccuracy > GPS_SPEED_ACCURACY_THRESHOLD):
      return False

    return True

  def sanity_check_gps(self, gps, ecef_pos: np.ndarray) -> bool:
    """Check for unrealistic GPS changes"""
    if not self.gps_history:
      return True

    last_entry = self.gps_history[-1]
    dt = (gps.unixTimestampMillis - last_entry['timestamp']) * 1e-3

    if dt <= 0:
      return False

    # Check for unrealistic position changes
    last_ecef = last_entry['ecef_pos']
    horizontal_change = np.linalg.norm(ecef_pos[:2] - last_ecef[:2]) / dt
    vertical_change = abs(ecef_pos[2] - last_ecef[2]) / dt

    if (horizontal_change > GPS_SANITY_CHECK_MAX_HORIZONTAL or
          vertical_change > GPS_SANITY_CHECK_MAX_VERTICAL):
      cloudlog.warning(f"GPS sanity check failed: horizontal {horizontal_change:.1f} m/s, "
                       f"vertical {vertical_change:.1f} m/s")
      return False

    return True

  def handle_gps(self, t: float, gps_msg: log.Event):
    """Process GPS message"""
    gps = gps_msg.gpsLocationExternal if self.using_ublox else gps_msg.gpsLocation

    # Validate GPS data
    if not self.validate_gps(gps):
      self.gps_valid = False
      return

    # Convert to ECEF
    geodetic_pos = [gps.latitude, gps.longitude, gps.altitude]
    ecef_pos = np.array(geodetic2ecef(geodetic_pos))

    # Sanity check
    if not self.sanity_check_gps(gps, ecef_pos):
      self.gps_valid = False
      return

    # Initialize converter if needed
    if self.converter is None:
      self.converter = LocalCoord.from_geodetic(geodetic_pos)
      # Reset Kalman filter to GPS position
      ecef_vel = self.converter.ned2ecef_matrix @ np.array([gps.vNED[0], gps.vNED[1], gps.vNED[2]])
      pos_var = np.array([
        (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
        (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
        (gps.verticalAccuracy * self.gps_variance_factor) ** 2
      ])
      vel_var = np.array([
        (gps.speedAccuracy * self.gps_variance_factor) ** 2,
        (gps.speedAccuracy * self.gps_variance_factor) ** 2,
        (gps.speedAccuracy * self.gps_variance_factor) ** 2
      ])
      self.kf.reset(ecef_pos, ecef_vel, pos_var, vel_var)

    # Convert NED velocity to ECEF
    ned_vel = np.array([gps.vNED[0], gps.vNED[1], gps.vNED[2]])
    ecef_vel = self.converter.ned2ecef_matrix @ ned_vel

    # Kalman filter predict
    sensor_time = t - self.gps_sensor_time_offset
    self.kf.predict(sensor_time)

    # Position measurement update
    R_pos = np.diag([
      (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
      (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
      (gps.verticalAccuracy * self.gps_variance_factor) ** 2
    ])
    pos_innovation = self.kf.update_position(ecef_pos, R_pos)

    # Velocity measurement update
    R_vel = np.diag([
      (gps.speedAccuracy * self.gps_variance_factor) ** 2,
      (gps.speedAccuracy * self.gps_variance_factor) ** 2,
      (gps.speedAccuracy * self.gps_variance_factor) ** 2
    ])
    vel_innovation = self.kf.update_velocity(ecef_vel, R_vel)

    # Check if we need to reset due to large errors
    position_error = np.linalg.norm(pos_innovation[:2])
    vertical_error = abs(pos_innovation[2])

    if (position_error > GPS_RESET_THRESHOLD_HORIZONTAL or
          vertical_error > GPS_RESET_THRESHOLD_VERTICAL):
      cloudlog.info(f"GPS reset: horizontal error {position_error:.1f}m, "
                    f"vertical error {vertical_error:.1f}m")
      pos_var = np.array([
        (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
        (gps.horizontalAccuracy * self.gps_variance_factor) ** 2,
        (gps.verticalAccuracy * self.gps_variance_factor) ** 2
      ])
      vel_var = np.array([
        (gps.speedAccuracy * self.gps_variance_factor) ** 2,
        (gps.speedAccuracy * self.gps_variance_factor) ** 2,
        (gps.speedAccuracy * self.gps_variance_factor) ** 2
      ])
      self.kf.reset(ecef_pos, ecef_vel, pos_var, vel_var)

    # Update state
    self.gps_valid = True
    self.gps_ok = True
    self.last_gps_msg = gps_msg
    self.last_gps_time = t

    # Add to history
    self.gps_history.append({
      'timestamp': gps.unixTimestampMillis,
      'ecef_pos': ecef_pos.copy()
    })

    # Save LastGPSPosition periodically
    if t - self.last_position_save_time > GPS_SAVE_POSITION_INTERVAL:
      self.save_last_gps_position(gps)
      self.last_position_save_time = t

  def handle_fake_gps(self, t: float):
    """Generate fake GPS observation to prevent covariance explosion"""
    if self.gps_valid or not self.kf.initialized:
      return

    # Only add fake observations periodically
    if t - self.last_fake_gps_time < GPS_FAKE_OBSERVATION_INTERVAL:
      return

    self.kf.predict(t)

    # Fake position observation with large uncertainty
    R_pos = np.diag([1000 ** 2, 1000 ** 2, 1000 ** 2])
    self.kf.update_position(self.kf.x[0:3], R_pos)

    # Fake velocity observation to prevent drift
    R_vel = np.diag([10 ** 2, 10 ** 2, 10 ** 2])
    self.kf.update_velocity(self.kf.x[3:6], R_vel)

    self.last_fake_gps_time = t

  def save_last_gps_position(self, gps):
    """Save last valid GPS position to params"""
    try:
      last_gps_position = {
        "latitude": gps.latitude,
        "longitude": gps.longitude,
        "altitude": gps.altitude,
        "unixTimestampMillis": gps.unixTimestampMillis
      }
      self.params.put("LastGPSPosition", json.dumps(last_gps_position))
    except Exception as e:
      cloudlog.error(f"Failed to save LastGPSPosition: {e}")

  def get_message(self):
    """Build gpsLocationProcessed message"""
    if not self.kf.initialized:
      return None

    msg = messaging.new_message('gpsLocationProcessed')
    gps_proc = msg.gpsLocationProcessed

    # Convert ECEF to geodetic
    ecef_pos = self.kf.x[0:3]
    geodetic = ecef2geodetic(ecef_pos)

    gps_proc.latitude = geodetic[0]
    gps_proc.longitude = geodetic[1]
    gps_proc.altitude = geodetic[2]

    # ECEF position and velocity
    gps_proc.ecefX = ecef_pos[0]
    gps_proc.ecefY = ecef_pos[1]
    gps_proc.ecefZ = ecef_pos[2]

    ecef_vel = self.kf.x[3:6]
    gps_proc.ecefVx = ecef_vel[0]
    gps_proc.ecefVy = ecef_vel[1]
    gps_proc.ecefVz = ecef_vel[2]

    # Convert velocity to NED if converter available
    if self.converter is not None:
      ned_vel = self.converter.ecef2ned_matrix @ ecef_vel
      gps_proc.vNED = ned_vel.tolist()
    else:
      gps_proc.vNED = [0.0, 0.0, 0.0]

    # Uncertainties from covariance
    pos_std = np.sqrt(np.diag(self.kf.P[0:3, 0:3]))
    vel_std = np.sqrt(np.diag(self.kf.P[3:6, 3:6]))

    gps_proc.horizontalAccuracy = float(np.linalg.norm(pos_std[:2]))
    gps_proc.verticalAccuracy = float(pos_std[2])
    gps_proc.speedAccuracy = float(np.linalg.norm(vel_std))

    gps_proc.valid = self.gps_ok
    gps_proc.source = 'ublox' if self.using_ublox else 'qcom'

    return msg

  def run(self):
    """Main loop for GPS localizer"""
    config_realtime_process(5, priority=3)

    sm = messaging.SubMaster([self.gps_location_service])
    pm = messaging.PubMaster(['gpsLocationProcessed'])

    cloudlog.info("GPS Localizer started")

    while True:
      sm.update(timeout=100)

      # Current time
      t = sm.logMonoTime[self.gps_location_service] * 1e-9 if sm.updated[self.gps_location_service] else 0

      # Process GPS message
      if sm.updated[self.gps_location_service]:
        self.handle_gps(t, sm[self.gps_location_service])

      # Add fake GPS if needed
      if t > 0:
        self.handle_fake_gps(t)

      # Publish processed GPS
      msg = self.get_message()
      if msg is not None:
        pm.send('gpsLocationProcessed', msg)


def main():
  params = Params()
  localizer = GPSLocalizer(params)
  localizer.run()


if __name__ == "__main__":
  main()
