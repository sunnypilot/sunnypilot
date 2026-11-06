"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from enum import IntEnum

import numpy as np
import raylib_nb as rl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui.elements import (
  UiElement, RelDistElement, RelSpeedElement, SteeringAngleElement,
  DesiredLateralAccelElement, ActualLateralAccelElement, DesiredSteeringAngleElement,
  AEgoElement, LeadSpeedElement, FrictionCoefficientElement, LatAccelFactorElement,
  SteeringTorqueEpsElement, BearingDegElement, AltitudeElement, DesiredSteeringPIDElement
)
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


RIGHT_UNIT_SIZE = 28
RIGHT_UNITS = ("m", "km/h", "mph", "m/s^2")


def load_text_texture(font: rl.Font, text: str, font_size: int) -> rl.Texture:
  """Rasterize white text into a texture, so it can be drawn rotated with draw_texture_pro."""
  size = measure_text_cached(font, text, font_size)
  width, height = math.ceil(size.x), math.ceil(size.y)
  target = rl.load_render_texture(width, height)
  rl.begin_texture_mode(target)
  rl.clear_background(rl.BLANK)
  rl.draw_text_ex(font, text, rl.Vector2(0, 0), font_size, 0, rl.WHITE)
  rl.end_texture_mode()

  image = rl.load_image_from_texture(target.texture)
  pixels = np.frombuffer(image.to_bytes(width * height * 4), dtype=np.uint8).reshape(height, width, 4)
  rl.unload_image(image)
  rl.unload_render_texture(target)

  # Blending onto a transparent target leaves the coverage in rgb and squares the alpha; rebuild straight alpha.
  # Render textures are stored bottom-up, so flip the rows.
  rgba = np.full((height, width, 4), 255, dtype=np.uint8)
  rgba[..., 3] = pixels[::-1, :, 0]
  texture = rl.load_texture_from_image(rl.Image(rgba, width, height, 1, rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8))
  rl.set_texture_filter(texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
  rl.set_texture_wrap(texture, rl.TextureWrap.TEXTURE_WRAP_CLAMP)
  return texture


def get_bottom_dev_ui_offset():
  if ui_state.developer_ui in (DeveloperUiState.BOTTOM, DeveloperUiState.BOTH):
    return 60
  return 0


class DeveloperUiState(IntEnum):
  OFF = 0
  BOTTOM = 1
  RIGHT = 2
  BOTH = 3


class DeveloperUiRenderer(Widget):
  def __init__(self):
    super().__init__()
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)
    self._font_semi_bold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self.dev_ui_mode = DeveloperUiState.OFF
    # rotated units (raylib_nb has no draw_text_pro), built outside the frame since onroad renders inside a scissor
    self._unit_textures = {unit: load_text_texture(self._font_bold, unit, RIGHT_UNIT_SIZE) for unit in RIGHT_UNITS}

    self.rel_dist_elem = RelDistElement()
    self.rel_speed_elem = RelSpeedElement()
    self.steering_angle_elem = SteeringAngleElement()
    self.desired_lat_accel_elem = DesiredLateralAccelElement()
    self.actual_lat_accel_elem = ActualLateralAccelElement()
    self.desired_steer_elem = DesiredSteeringAngleElement()
    self.desired_pid_steer_elem = DesiredSteeringPIDElement()
    self.a_ego_elem = AEgoElement()
    self.lead_speed_elem = LeadSpeedElement()
    self.friction_elem = FrictionCoefficientElement()
    self.lat_accel_factor_elem = LatAccelFactorElement()
    self.steering_torque_elem = SteeringTorqueEpsElement()
    self.bearing_elem = BearingDegElement()
    self.altitude_elem = AltitudeElement()

  def _update_state(self) -> None:
    self.dev_ui_mode = ui_state.developer_ui

  def _render(self, rect: rl.Rectangle) -> None:
    if self.dev_ui_mode == DeveloperUiState.OFF:
      return

    sm = ui_state.sm
    if sm.recv_frame["carState"] < ui_state.started_frame:
      return

    if self.dev_ui_mode == DeveloperUiState.BOTTOM:
      self._draw_bottom_dev_ui(rect)
    elif self.dev_ui_mode == DeveloperUiState.RIGHT:
      self._draw_right_dev_ui(rect)
    elif self.dev_ui_mode == DeveloperUiState.BOTH:
      self._draw_right_dev_ui(rect)
      self._draw_bottom_dev_ui(rect)

  def _draw_right_dev_ui(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm
    controls_state = sm['controlsState']

    UI_BORDER_SIZE = 20
    container_width = 184
    x = int(rect.x + rect.width - container_width - UI_BORDER_SIZE * 2)
    y = int(rect.y + UI_BORDER_SIZE * 1.5)

    elements = [
      self.rel_dist_elem.update(sm, ui_state.is_metric),
      self.rel_speed_elem.update(sm, ui_state.is_metric),
      self.steering_angle_elem.update(sm, ui_state.is_metric),
    ]
    if controls_state.lateralControlState.which() == 'torqueState':
      elements.append(self.desired_lat_accel_elem.update(sm, ui_state.is_metric))
    elif controls_state.lateralControlState.which() == 'angleState':
      elements.append(self.desired_steer_elem.update(sm, ui_state.is_metric))
    elif controls_state.lateralControlState.which() == 'pidState':
      elements.append(self.desired_pid_steer_elem.update(sm, ui_state.is_metric))

    elements.append(self.actual_lat_accel_elem.update(sm, ui_state.is_metric))

    current_y = y
    for element in elements:
      current_y += self._draw_right_dev_ui_element(x, current_y, element)

  def _draw_right_dev_ui_element(self, x: int, y: int, element: UiElement) -> int:
    x += 0
    y += 230
    container_width = 184
    label_size = 28
    value_size = 60
    label_width = measure_text_cached(self._font_bold, element.label, label_size, 0).x
    centered_label_x = x + (container_width - label_width) / 2
    rl.draw_text_ex(self._font_bold, element.label, rl.Vector2(centered_label_x, y), label_size, 0, rl.WHITE)

    y += 45
    value_width = measure_text_cached(self._font_bold, element.value, value_size, 0).x
    centered_value_x = x + (container_width - value_width) / 2
    rl.draw_text_ex(self._font_bold, element.value, rl.Vector2(centered_value_x, y), value_size, 0, element.color)

    if element.unit:
      unit_texture = self._unit_textures[element.unit]
      units_x = x + container_width
      units_y = y + (value_size / 2) + (unit_texture.width / 2)
      src = rl.Rectangle(0, 0, unit_texture.width, unit_texture.height)
      dst = rl.Rectangle(units_x, units_y, unit_texture.width, unit_texture.height)
      rl.draw_texture_pro(unit_texture, src, dst, rl.Vector2(0, 0), -90.0, rl.WHITE)

    return 130

  def _draw_bottom_dev_ui(self, rect: rl.Rectangle) -> None:
    sm = ui_state.sm
    bar_height = 61
    y = int(rect.y + rect.height - bar_height)

    rl.draw_rectangle(int(rect.x), y, int(rect.width), bar_height,
                      rl.Color(0, 0, 0, 100))

    elements = [
      self.a_ego_elem.update(sm, ui_state.is_metric),
      self.lead_speed_elem.update(sm, ui_state.is_metric),
    ]

    # Add torque-specific elements if using torque control
    if sm['controlsState'].lateralControlState.which() == 'torqueState':
      override_active = ui_state.enforce_torque_control and ui_state.custom_torque_params and ui_state.torque_override_enabled
      if sm.valid['lateralTorqueParameters'] or override_active:
        elements.extend([
          self.friction_elem.update(sm, ui_state.is_metric),
          self.lat_accel_factor_elem.update(sm, ui_state.is_metric),
        ])
    else:
      # Non-torque: show steering torque and GPS data
      elements.append(self.steering_torque_elem.update(sm, ui_state.is_metric))

      if sm.valid['gpsLocationExternal'] or sm.valid['gpsLocation']:
        elements.append(self.bearing_elem.update(sm, ui_state.is_metric))

    # Add altitude if GPS available
    if sm.valid['gpsLocationExternal'] or sm.valid['gpsLocation']:
      elements.append(self.altitude_elem.update(sm, ui_state.is_metric))

    if not elements:
      return

    font_size = 38
    element_widths = []
    for element in elements:
      element.measure(self._font_bold, font_size)
      element_widths.append(element.total_width)

    total_element_width = sum(element_widths)
    num_gaps = len(elements) + 1
    available_width = rect.width
    gap_width = (available_width - total_element_width) / num_gaps

    center_y = y + bar_height // 2
    current_x = rect.x + gap_width

    for i, element in enumerate(elements):
      element_center_x = int(current_x + element_widths[i] / 2)
      self._draw_bottom_dev_ui_element(element_center_x, center_y, element)
      current_x += element_widths[i] + gap_width

  def _draw_bottom_dev_ui_element(self, center_x: int, y: int, element: UiElement) -> None:
    font_size = 38
    start_x = center_x - element.total_width / 2

    rl.draw_text_ex(self._font_bold, element.label_text, rl.Vector2(start_x, y - font_size // 2), font_size, 0, rl.WHITE)
    rl.draw_text_ex(self._font_bold, element.val_text, rl.Vector2(start_x + element.label_width, y - font_size // 2), font_size, 0, element.color)

    if element.unit:
      rl.draw_text_ex(self._font_bold, element.unit_text, rl.Vector2(start_x + element.label_width + element.val_width, y - font_size // 2),
                      font_size, 0, rl.WHITE)
