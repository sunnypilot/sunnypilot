"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from dataclasses import dataclass

from openpilot.common.constants import CV


@dataclass
class UiElement:
  value: str
  label: str
  units: str
  color: rl.Color


class DeveloperUi:
  @staticmethod
  def get_d_rel(lead_status: bool, lead_d_rel: float) -> UiElement:
    value = f"{lead_d_rel:.0f}" if lead_status else "-"
    color = rl.WHITE

    if lead_status:
      if lead_d_rel < 5:
        color = rl.RED
      elif lead_d_rel < 15:
        color = rl.Color(255, 188, 0, 255)  # Orange

    return UiElement(value, "REL DIST", "m", color)

  @staticmethod
  def get_v_rel(lead_status: bool, lead_v_rel: float, is_metric: bool) -> UiElement:
    """Relative velocity"""
    speed_unit = "km/h" if is_metric else "mph"
    conversion = CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH
    value = f"{lead_v_rel * conversion:.0f}" if lead_status else "-"
    color = rl.WHITE

    if lead_status:
      if lead_v_rel < -4.4704:
        color = rl.RED
      elif lead_v_rel < 0:
        color = rl.Color(255, 188, 0, 255)  # Orange

    return UiElement(value, "REL SPEED", speed_unit, color)

  @staticmethod
  def get_steering_angle_deg(angle_steers: float, lat_active: bool, steer_override: bool) -> UiElement:
    """Real steering angle (degrees)."""
    value = f"{angle_steers:.1f}°"

    if lat_active:
      color = rl.Color(145, 155, 149, 255) if steer_override else rl.Color(0, 255, 0, 255)
    else:
      color = rl.WHITE

    if abs(angle_steers) > 180:
      color = rl.RED
    elif abs(angle_steers) > 90:
      color = rl.Color(255, 188, 0, 255)

    return UiElement(value, "REAL STEER", "", color)

  @staticmethod
  def get_desired_steering_angle_deg(lat_active: bool, steer_angle_desired: float,
                                     angle_steers: float) -> UiElement:
    """Desired steering angle"""
    value = f"{steer_angle_desired:.1f}°" if lat_active else "-"
    color = rl.WHITE

    if lat_active:
      if abs(angle_steers) > 180:
        color = rl.RED
      elif abs(angle_steers) > 90:
        color = rl.Color(255, 188, 0, 255)
      else:
        color = rl.Color(0, 255, 0, 255)

    return UiElement(value, "DESIRED STEER", "", color)

  @staticmethod
  def get_actual_lateral_accel(curvature: float, v_ego: float, roll: float,
                               lat_active: bool, steer_override: bool) -> UiElement:
    """Actual lateral acceleration (roll compensated)"""
    actual_lat_accel = (curvature * v_ego ** 2) - (roll * 9.81)
    value = f"{actual_lat_accel:.2f}"

    if lat_active:
      color = rl.Color(145, 155, 149, 255) if steer_override else rl.Color(0, 255, 0, 255)
    else:
      color = rl.WHITE

    return UiElement(value, "ACTUAL L.A.", "m/s²", color)

  @staticmethod
  def get_desired_lateral_accel(desired_curvature: float, v_ego: float, roll: float,
                                lat_active: bool, steer_override: bool) -> UiElement:
    """Desired lateral acceleration"""
    desired_lat_accel = (desired_curvature * v_ego ** 2) - (roll * 9.81)
    value = f"{desired_lat_accel:.2f}" if lat_active else "-"

    if lat_active:
      color = rl.Color(145, 155, 149, 255) if steer_override else rl.Color(0, 255, 0, 255)
    else:
      color = rl.WHITE

    return UiElement(value, "DESIRED L.A.", "m/s²", color)

  @staticmethod
  def get_memory_usage_percent(memory_usage_percent: int) -> UiElement:
    """RAM"""
    value = f"{memory_usage_percent}%"
    color = rl.Color(255, 188, 0, 255) if memory_usage_percent > 85 else rl.WHITE
    return UiElement(value, "RAM", "", color)

  @staticmethod
  def get_a_ego(a_ego: float) -> UiElement:
    """current acceleration (m/s²)."""
    value = f"{a_ego:.1f}"
    return UiElement(value, "ACC.", "m/s²", rl.WHITE)

  @staticmethod
  def get_v_ego_lead(lead_status: bool, lead_v_rel: float, v_ego: float, is_metric: bool) -> UiElement:
    """Lead vehicle absolute speed."""
    speed_unit = "km/h" if is_metric else "mph"
    conversion = CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH
    value = f"{(lead_v_rel + v_ego) * conversion:.0f}" if lead_status else "-"
    color = rl.WHITE

    if lead_status:
      if lead_v_rel < -4.4704:
        color = rl.RED
      elif lead_v_rel < 0:
        color = rl.Color(255, 188, 0, 255)

    return UiElement(value, "L.S.", speed_unit, color)

  @staticmethod
  def get_friction_coefficient(friction_coef: float, live_valid: bool) -> UiElement:
    """Friction coefficient from torqued."""
    value = f"{friction_coef:.3f}"
    color = rl.Color(0, 255, 0, 255) if live_valid else rl.WHITE
    return UiElement(value, "FRIC.", "", color)

  @staticmethod
  def get_lat_accel_factor(lat_accel_factor: float, live_valid: bool) -> UiElement:
    """Lateral acceleration factor from torqued."""
    value = f"{lat_accel_factor:.3f}"
    color = rl.Color(0, 255, 0, 255) if live_valid else rl.WHITE
    return UiElement(value, "L.A.F.", "", color)

  @staticmethod
  def get_steering_torque_eps(steering_torque_eps: float) -> UiElement:
    """Steering torque from car EPS (Newton decimeters)."""
    value = f"{abs(steering_torque_eps):.1f}"
    return UiElement(value, "E.T.", "N·dm", rl.WHITE)

  @staticmethod
  def get_bearing_deg(bearing_accuracy_deg: float, bearing_deg: float) -> UiElement:
    """Bearing degree and direction (compass)."""
    if bearing_accuracy_deg != 180.0:
      value = f"{bearing_deg:.0f}°"
      if (337.5 <= bearing_deg <= 360) or (0 <= bearing_deg <= 22.5):
        dir_value = "N"
      elif 22.5 < bearing_deg < 67.5:
        dir_value = "NE"
      elif 67.5 <= bearing_deg <= 112.5:
        dir_value = "E"
      elif 112.5 < bearing_deg < 157.5:
        dir_value = "SE"
      elif 157.5 <= bearing_deg <= 202.5:
        dir_value = "S"
      elif 202.5 < bearing_deg < 247.5:
        dir_value = "SW"
      elif 247.5 <= bearing_deg <= 292.5:
        dir_value = "W"
      else:  # 292.5 < bearing_deg < 337.5
        dir_value = "NW"
    else:
      value = "-"
      dir_value = "OFF"

    return UiElement(f"{dir_value} | {value}", "B.D.", "", rl.WHITE)

  @staticmethod
  def get_altitude(gps_accuracy: float, altitude: float) -> UiElement:
    """Altitude"""
    value = f"{altitude:.1f}" if gps_accuracy != 0.0 else "-"
    return UiElement(value, "ALT.", "m", rl.WHITE)
