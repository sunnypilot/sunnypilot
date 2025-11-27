import pyray as rl
from dataclasses import dataclass
from typing import Optional
from openpilot.common.constants import CV
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.widgets import Widget


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


class DeveloperUiRenderer(Widget):
  DEV_UI_OFF = 0
  DEV_UI_RIGHT = 1
  DEV_UI_BOTTOM = 2
  DEV_UI_BOTH = 3

  def __init__(self):
    super().__init__()
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self.dev_ui_mode = self.DEV_UI_RIGHT

  def _update_state(self) -> None:
    pass

  def _render(self, rect: rl.Rectangle) -> None:
    if self.dev_ui_mode == self.DEV_UI_OFF:
      return

    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    if self.dev_ui_mode == self.DEV_UI_RIGHT:
      self._draw_right_dev_ui(rect)
    elif self.dev_ui_mode == self.DEV_UI_BOTTOM:
      self._draw_bottom_dev_ui(rect)
    elif self.dev_ui_mode == self.DEV_UI_BOTH:
      self._draw_right_dev_ui(rect)
      self._draw_bottom_dev_ui(rect)

  def _draw_right_dev_ui(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm
    car_state = sm['carState']
    controls_state = sm['controlsState']
    radar_state = sm['radarState']
    lead_one = radar_state.leadOne
    lead_status = lead_one.status
    lead_d_rel = lead_one.dRel
    lead_v_rel = lead_one.vRel

    angle_steers = car_state.steeringAngleDeg
    lat_active = sm['carControl'].latActive
    steer_override = car_state.steeringPressed

    UI_BORDER_SIZE = 20
    container_width = 184
    container_height = 170
    x = int(rect.x + rect.width - container_width - UI_BORDER_SIZE * 2)
    y = int(rect.y + UI_BORDER_SIZE * 1.5)

    elements = [
      DeveloperUi.get_d_rel(lead_status, lead_d_rel),
      DeveloperUi.get_v_rel(lead_status, lead_v_rel, ui_state.is_metric),
      DeveloperUi.get_steering_angle_deg(angle_steers, lat_active, steer_override),
    ]
    if controls_state.lateralControlState.which() == 'torqueState':
      roll = sm['liveParameters'].roll if sm.valid['liveParameters'] else 0.0
      curvature = controls_state.curvature
      desired_curvature = controls_state.desiredCurvature
      v_ego = car_state.vEgo

      elements.append(DeveloperUi.get_desired_lateral_accel(
        desired_curvature, v_ego, roll, lat_active, steer_override
      ))
      elements.append(DeveloperUi.get_actual_lateral_accel(
        curvature, v_ego, roll, lat_active, steer_override
      ))
    else:
      steer_angle_desired = controls_state.lateralControlState.angleState.steeringAngleDeg
      elements.append(DeveloperUi.get_desired_steering_angle_deg(
        lat_active, steer_angle_desired, angle_steers
      ))

    current_y = y
    for element in elements:
      current_y += self._draw_right_dev_ui_element(x, current_y, element)

  def _draw_right_dev_ui_element(self, x: int, y: int, element: UiElement) -> int:
    x += 0
    y += 230

    label_size = 28
    rl.draw_text_ex(self._font_bold, element.label,
                    rl.Vector2(x, y), label_size, 0, rl.WHITE)

    y += 65
    value_size = 60
    rl.draw_text_ex(self._font_bold, element.value,
                    rl.Vector2(x, y), value_size, 0, element.color)

    if element.units:
      x += 120
      y -= 25
      # Note-SP: Raylib doesn't have native text rotation, so we'll draw it horizontally
      # For true rotation, you'd need to render to a texture first which I do not know
      unit_size = 28
      rl.draw_text_ex(self._font_bold, element.units,
                      rl.Vector2(x, y), unit_size, 0, rl.WHITE)

    return 130

  def _draw_bottom_dev_ui(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm
    car_state = sm['carState']
    radar_state = sm['radarState']
    lead_one = radar_state.leadOne
    lead_status = lead_one.status
    lead_v_rel = lead_one.vRel
    v_ego = car_state.vEgo
    a_ego = car_state.aEgo
    bar_height = 61
    y = int(rect.y + rect.height - bar_height)

    rl.draw_rectangle(int(rect.x), y, int(rect.width), bar_height,
                      rl.Color(0, 0, 0, 100))

    elements = [
      DeveloperUi.get_a_ego(a_ego),
      DeveloperUi.get_v_ego_lead(lead_status, lead_v_rel, v_ego, ui_state.is_metric),
    ]

    # Add torque-specific elements if using torque control
    if sm['controlsState'].lateralControlState.which() == 'torqueState':
      if sm.valid['liveTorqueParameters']:
        ltp = sm['liveTorqueParameters']
        elements.extend([
          DeveloperUi.get_friction_coefficient(
            ltp.frictionCoefficientFiltered, ltp.liveValid
          ),
          DeveloperUi.get_lat_accel_factor(
            ltp.latAccelFactorFiltered, ltp.liveValid
          ),
        ])
    else:
      # Non-torque: show steering torque and GPS data
      steering_torque_eps = car_state.steeringTorqueEps
      elements.append(DeveloperUi.get_steering_torque_eps(steering_torque_eps))

      if sm.valid['gpsLocationExternal']:
        gps_data = sm['gpsLocationExternal']
        elements.append(DeveloperUi.get_bearing_deg(
          gps_data.bearingAccuracyDeg, gps_data.bearingDeg
        ))
      elif sm.valid['gpsLocation']:
        gps_data = sm['gpsLocation']
        elements.append(DeveloperUi.get_bearing_deg(
          gps_data.bearingAccuracyDeg, gps_data.bearingDeg
        ))

    # Add altitude if GPS available
    if sm.valid['gpsLocationExternal']:
      gps_data = sm['gpsLocationExternal']
      elements.append(DeveloperUi.get_altitude(gps_data.horizontalAccuracy, gps_data.altitude))
    elif sm.valid['gpsLocation']:
      gps_data = sm['gpsLocation']
      elements.append(DeveloperUi.get_altitude(1.0, gps_data.altitude))

    current_x = int(rect.x + 90)
    center_y = y + bar_height // 2
    for element in elements:
      current_x += self._draw_bottom_dev_ui_element(current_x, center_y, element)

  def _draw_bottom_dev_ui_element(self, x: int, y: int, element: UiElement) -> int:
    font_size = 38

    label_text = f"{element.label} "
    value_text = element.value
    units_text = element.units

    rl.draw_text_ex(self._font_bold, label_text,
                    rl.Vector2(x, y - font_size // 2), font_size, 0, rl.WHITE)

    label_width = len(label_text) * font_size * 0.5

    rl.draw_text_ex(self._font_bold, value_text,
                    rl.Vector2(x + label_width + 10, y - font_size // 2),
                    font_size, 0, element.color)

    value_width = len(value_text) * font_size * 0.6

    if units_text:
      rl.draw_text_ex(self._font_bold, units_text,
                      rl.Vector2(x + label_width + value_width + 20, y - font_size // 2),
                      font_size, 0, rl.WHITE)

    return 400
