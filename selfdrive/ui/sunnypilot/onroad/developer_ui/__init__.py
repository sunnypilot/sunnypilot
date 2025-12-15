"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import DeveloperUiElements, UiElement
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


class DeveloperUiRenderer(Widget):
  DEV_UI_OFF = 0
  DEV_UI_RIGHT = 1
  DEV_UI_BOTTOM = 2
  DEV_UI_BOTH = 3

  def __init__(self):
    super().__init__()
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self.dev_ui_mode = self.DEV_UI_OFF

    self.elements = DeveloperUiElements()

  def _update_state(self) -> None:
    self.dev_ui_mode = ui_state.developer_ui

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
    x = int(rect.x + rect.width - container_width - UI_BORDER_SIZE * 2)
    y = int(rect.y + UI_BORDER_SIZE * 1.5)

    elements = [
      self.elements.get_d_rel(lead_status, lead_d_rel),
      self.elements.get_v_rel(lead_status, lead_v_rel, ui_state.is_metric),
      self.elements.get_steering_angle_deg(angle_steers, lat_active, steer_override),
    ]
    if controls_state.lateralControlState.which() == 'torqueState':
      roll = sm['liveParameters'].roll if sm.valid['liveParameters'] else 0.0
      curvature = controls_state.curvature
      desired_curvature = controls_state.desiredCurvature
      v_ego = car_state.vEgo

      elements.append(self.elements.get_desired_lateral_accel(
        desired_curvature, v_ego, roll, lat_active, steer_override
      ))
      elements.append(self.elements.get_actual_lateral_accel(
        curvature, v_ego, roll, lat_active, steer_override
      ))
    else:
      steer_angle_desired = controls_state.lateralControlState.angleState.steeringAngleDeg
      elements.append(self.elements.get_desired_steering_angle_deg(
        lat_active, steer_angle_desired, angle_steers
      ))

    current_y = y
    for element in elements:
      current_y += self._draw_right_dev_ui_element(x, current_y, element)

  def _draw_right_dev_ui_element(self, x: int, y: int, element: UiElement) -> int:
    x += 0
    y += 230
    container_width = 184
    label_size = 28
    value_size = 60
    unit_size = 28
    label_width = measure_text_cached(self._font_bold, element.label, label_size, 0).x
    centered_label_x = x + (container_width - label_width) / 2
    rl.draw_text_ex(self._font_bold, element.label, rl.Vector2(centered_label_x, y), label_size, 0, rl.WHITE)

    y += 45
    value_width = measure_text_cached(self._font_bold, element.value, value_size, 0).x
    centered_value_x = x + (container_width - value_width) / 2
    rl.draw_text_ex(self._font_bold, element.value, rl.Vector2(centered_value_x, y), value_size, 0, element.color)

    if element.units:
      units_height = measure_text_cached(self._font_bold, element.units, unit_size, 0).x

      units_x = x + container_width - 10
      units_y = y + (value_size / 2) + (units_height / 2)

      rl.draw_text_pro(self._font_bold, element.units, rl.Vector2(units_x, units_y), rl.Vector2(0, 0), -90.0, unit_size, 0, rl.WHITE)

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
      self.elements.get_a_ego(a_ego),
      self.elements.get_v_ego_lead(lead_status, lead_v_rel, v_ego, ui_state.is_metric),
    ]

    # Add torque-specific elements if using torque control
    if sm['controlsState'].lateralControlState.which() == 'torqueState':
      if sm.valid['liveTorqueParameters']:
        ltp = sm['liveTorqueParameters']
        elements.extend([
          self.elements.get_friction_coefficient(
            ltp.frictionCoefficientFiltered, ltp.liveValid
          ),
          self.elements.get_lat_accel_factor(
            ltp.latAccelFactorFiltered, ltp.liveValid
          ),
        ])
    else:
      # Non-torque: show steering torque and GPS data
      steering_torque_eps = car_state.steeringTorqueEps
      elements.append(self.elements.get_steering_torque_eps(steering_torque_eps))

      if sm.valid['gpsLocationExternal']:
        gps_data = sm['gpsLocationExternal']
        elements.append(self.elements.get_bearing_deg(
          gps_data.bearingAccuracyDeg, gps_data.bearingDeg
        ))
      elif sm.valid['gpsLocation']:
        gps_data = sm['gpsLocation']
        elements.append(self.elements.get_bearing_deg(
          gps_data.bearingAccuracyDeg, gps_data.bearingDeg
        ))

    # Add altitude if GPS available
    if sm.valid['gpsLocationExternal']:
      gps_data = sm['gpsLocationExternal']
      elements.append(self.elements.get_altitude(gps_data.horizontalAccuracy, gps_data.altitude))
    elif sm.valid['gpsLocation']:
      gps_data = sm['gpsLocation']
      elements.append(self.elements.get_altitude(1.0, gps_data.altitude))

    current_x = int(rect.x + 90)
    center_y = y + bar_height // 2
    for element in elements:
      current_x += self._draw_bottom_dev_ui_element(current_x, center_y, element)

  def _draw_bottom_dev_ui_element(self, x: int, y: int, element: UiElement) -> int:
    font_size = 38

    label_text = f"{element.label} "
    label_width = measure_text_cached(self._font_bold, label_text, font_size, 0).x
    rl.draw_text_ex(self._font_bold, label_text, rl.Vector2(x, y - font_size // 2), font_size, 0, rl.WHITE)

    value_width = measure_text_cached(self._font_bold, element.value, font_size, 0).x
    rl.draw_text_ex(self._font_bold, element.value, rl.Vector2(x + label_width + 10, y - font_size // 2), font_size, 0, element.color)

    if element.units:
      rl.draw_text_ex(self._font_bold, element.units, rl.Vector2(x + label_width + value_width + 20, y - font_size // 2), font_size, 0, rl.WHITE)

    return 400
