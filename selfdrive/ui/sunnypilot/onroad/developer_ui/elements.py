from abc import ABC, abstractmethod
import pyray as rl
from dataclasses import dataclass

from openpilot.common.constants import CV


@dataclass
class UiElement:
  value: str
  label: str
  units: str
  color: rl.Color


class BaseUiElement(ABC):
  @abstractmethod
  def update(self, sm, is_metric: bool) -> UiElement:
    pass


class RelDistElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    lead_one = sm['radarState'].leadOne
    lead_status = lead_one.status
    lead_d_rel = lead_one.dRel

    value = f"{lead_d_rel:.0f}" if lead_status else "-"
    color = rl.WHITE

    if lead_status:
      if lead_d_rel < 5:
        color = rl.RED
      elif lead_d_rel < 15:
        color = rl.Color(255, 188, 0, 255)  # Orange

    return UiElement(value, "REL DIST", "m", color)


class RelSpeedElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    lead_one = sm['radarState'].leadOne
    lead_status = lead_one.status
    lead_v_rel = lead_one.vRel

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


class SteeringAngleElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    car_state = sm['carState']
    angle_steers = car_state.steeringAngleDeg
    lat_active = sm['carControl'].latActive
    steer_override = car_state.steeringPressed

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


class DesiredSteeringAngleElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    car_state = sm['carState']
    controls_state = sm['controlsState']
    lat_active = sm['carControl'].latActive
    angle_steers = car_state.steeringAngleDeg
    steer_angle_desired = controls_state.lateralControlState.angleState.steeringAngleDeg

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


class ActualLateralAccelElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    controls_state = sm['controlsState']
    curvature = controls_state.curvature
    v_ego = sm['carState'].vEgo
    roll = sm['liveParameters'].roll if sm.valid['liveParameters'] else 0.0
    lat_active = sm['carControl'].latActive
    steer_override = sm['carState'].steeringPressed

    actual_lat_accel = (curvature * v_ego ** 2) - (roll * 9.81)
    value = f"{actual_lat_accel:.2f}"

    if lat_active:
      color = rl.Color(145, 155, 149, 255) if steer_override else rl.Color(0, 255, 0, 255)
    else:
      color = rl.WHITE

    return UiElement(value, "ACTUAL L.A.", "m/s²", color)


class DesiredLateralAccelElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    controls_state = sm['controlsState']
    desired_curvature = controls_state.desiredCurvature
    v_ego = sm['carState'].vEgo
    roll = sm['liveParameters'].roll if sm.valid['liveParameters'] else 0.0
    lat_active = sm['carControl'].latActive
    steer_override = sm['carState'].steeringPressed

    desired_lat_accel = (desired_curvature * v_ego ** 2) - (roll * 9.81)
    value = f"{desired_lat_accel:.2f}" if lat_active else "-"

    if lat_active:
      color = rl.Color(145, 155, 149, 255) if steer_override else rl.Color(0, 255, 0, 255)
    else:
      color = rl.WHITE

    return UiElement(value, "DESIRED L.A.", "m/s²", color)


class MemoryUsageElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    # Not currently used in the main UI but kept for completeness
    # This might require passing memory usage explicitly if it's not in SM
    # For now, we'll return a placeholder or need to find where it comes from.
    # The original method took `memory_usage_percent: int`.
    # Since we don't have it in SM easily (maybe deviceState?), we might need to skip or fake it.
    # Assuming it's passed or available.
    return UiElement("-", "RAM", "", rl.WHITE)


class AEgoElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    a_ego = sm['carState'].aEgo
    value = f"{a_ego:.1f}"
    return UiElement(value, "ACC.", "m/s²", rl.WHITE)


class LeadSpeedElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    radar_state = sm['radarState']
    lead_one = radar_state.leadOne
    lead_status = lead_one.status
    lead_v_rel = lead_one.vRel
    v_ego = sm['carState'].vEgo

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


class FrictionCoefficientElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    ltp = sm['liveTorqueParameters']
    friction_coef = ltp.frictionCoefficientFiltered
    live_valid = ltp.liveValid

    value = f"{friction_coef:.3f}"
    color = rl.Color(0, 255, 0, 255) if live_valid else rl.WHITE
    return UiElement(value, "FRIC.", "", color)


class LatAccelFactorElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    ltp = sm['liveTorqueParameters']
    lat_accel_factor = ltp.latAccelFactorFiltered
    live_valid = ltp.liveValid

    value = f"{lat_accel_factor:.3f}"
    color = rl.Color(0, 255, 0, 255) if live_valid else rl.WHITE
    return UiElement(value, "L.A.F.", "", color)


class SteeringTorqueEpsElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    steering_torque_eps = sm['carState'].steeringTorqueEps
    value = f"{abs(steering_torque_eps):.1f}"
    return UiElement(value, "E.T.", "N·dm", rl.WHITE)


class BearingDegElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    if sm.valid['gpsLocationExternal']:
        gps_data = sm['gpsLocationExternal']
    elif sm.valid['gpsLocation']:
        gps_data = sm['gpsLocation']
    else:
        return UiElement("OFF | -", "B.D.", "", rl.WHITE)

    bearing_accuracy_deg = gps_data.bearingAccuracyDeg
    bearing_deg = gps_data.bearingDeg

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


class AltitudeElement(BaseUiElement):
  def update(self, sm, is_metric: bool) -> UiElement:
    gps_accuracy = 0.0
    altitude = 0.0
    if sm.valid['gpsLocationExternal']:
      gps_data = sm['gpsLocationExternal']
      gps_accuracy = gps_data.horizontalAccuracy
      altitude = gps_data.altitude
    elif sm.valid['gpsLocation']:
      gps_data = sm['gpsLocation']
      gps_accuracy = 1.0 # Simulate valid for legacy check
      altitude = gps_data.altitude

    value = f"{altitude:.1f}" if gps_accuracy != 0.0 else "-"
    return UiElement(value, "ALT.", "m", rl.WHITE)
