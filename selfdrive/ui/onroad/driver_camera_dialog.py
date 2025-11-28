import numpy as np
import math
import time
import pyray as rl
from msgq.visionipc import VisionStreamType
from openpilot.selfdrive.ui.onroad.cameraview import CameraView
from openpilot.selfdrive.ui.ui_state import ui_state, device
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.lib.multilang import tr


# ============================================================
#  EXACT SAME DRIVER MONITORING ICON USED IN onroad (TIZI)
# ============================================================

class TiziDriverStateRenderer(Widget):
  BASE_SIZE = int(60 * 2.5)
  LINES_ANGLE_INCREMENT = 5
  LINES_STALE_ANGLES = 3.0

  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, self.BASE_SIZE, self.BASE_SIZE))

    self._confirm_angles = {}
    self._lines = False
    self._confirm_mode = False

    # load textures
    self._dm_person = gui_app.texture(
      "icons_mici/onroad/driver_monitoring/dm_person.png",
      self._rect.width, self._rect.height
    )
    self._dm_cone = gui_app.texture(
      "icons_mici/onroad/driver_monitoring/dm_cone.png",
      self._rect.width, self._rect.height
    )
    center_size = round(36 / self.BASE_SIZE * self._rect.width)
    self._dm_center = gui_app.texture(
      "icons_mici/onroad/driver_monitoring/dm_center.png",
      center_size, center_size
    )
    background_size = round(52 / self.BASE_SIZE * self._rect.width)
    self._dm_background = gui_app.texture(
      "icons_mici/onroad/driver_monitoring/dm_background.png",
      background_size, background_size
    )

    # filters
    self._fade_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps)
    self._yaw_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps, initialized=False)
    self._pitch_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps, initialized=False)
    self._rotation_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps, initialized=False)
    self._looking_center_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)

    assert 360 % self.LINES_ANGLE_INCREMENT == 0
    self._head_angles = {
      i * self.LINES_ANGLE_INCREMENT: FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)
      for i in range(360 // self.LINES_ANGLE_INCREMENT)
    }

    # state
    self._is_active = False
    self._face_detected = False
    self._looking_center = False
    self._force_active = False
    self._should_draw = True
    self._is_rhd = False

  # ----------------------------------------------------------
  # INTERNAL STATE UPDATES
  # ----------------------------------------------------------
  def _update_state(self):
    sm = ui_state.sm
    dm_state = sm["driverMonitoringState"]

    self._is_active = dm_state.isActiveMode
    self._is_rhd = dm_state.isRHD
    self._face_detected = dm_state.faceDetected

    driverstate = sm["driverStateV2"]
    driver_data = driverstate.rightDriverData if self._is_rhd else driverstate.leftDriverData
    driver_orient = driver_data.faceOrientation

    if len(driver_orient) != 3:
      return

    pitch, yaw, roll = driver_orient

    pitch = self._pitch_filter.update(pitch)
    yaw = self._yaw_filter.update(yaw)

    # looking center logic
    if abs(pitch) < math.radians(3) and abs(yaw) < math.radians(3):
      self._looking_center = True
    elif abs(pitch) > math.radians(6) or abs(yaw) > math.radians(6):
      self._looking_center = False

    self._looking_center_filter.update(1 if self._looking_center else 0)

    rotation = math.degrees(math.atan2(pitch, yaw))
    angle_diff = ((rotation - self._rotation_filter.x + 180) % 360) - 180
    self._rotation_filter.update(self._rotation_filter.x + angle_diff)

    # appearance fade
    if not self._should_draw:
      self._fade_filter.update(0.0)
    elif not self._is_active:
      self._fade_filter.update(0.35)
    else:
      self._fade_filter.update(1.0)

  # ----------------------------------------------------------
  # DRAWING
  # ----------------------------------------------------------
  def _render(self, _):
    rl.draw_texture(
      self._dm_background,
      int(self._rect.x + (self._rect.width - self._dm_background.width) / 2),
      int(self._rect.y + (self._rect.height - self._dm_background.height) / 2),
      rl.Color(255, 255, 255, int(255 * self._fade_filter.x)),
    )

    rl.draw_texture(
      self._dm_person,
      int(self._rect.x),
      int(self._rect.y),
      rl.Color(255, 255, 255, int(255 * 0.9 * self._fade_filter.x)),
    )

    # highlight/center icon
    rl.draw_texture(
      self._dm_center,
      int(self._rect.x + (self._rect.width - self._dm_center.width) / 2),
      int(self._rect.y + (self._rect.height - self._dm_center.height) / 2),
      rl.Color(
        255,
        255,
        255,
        int(255 * self._fade_filter.x * self._looking_center_filter.x),
      ),
    )


# ============================================================
#   DRIVER CAMERA WINDOW USING SAME DM ICON
# ============================================================

class DriverCameraDialog(CameraView):
  def __init__(self):
    super().__init__("camerad", VisionStreamType.VISION_STREAM_DRIVER)

    self.driver_state_renderer = TiziDriverStateRenderer()

    device.add_interactive_timeout_callback(self.stop_dmonitoringmodeld)
    ui_state.params.put_bool("IsDriverViewEnabled", True)

  def stop_dmonitoringmodeld(self):
    ui_state.params.put_bool("IsDriverViewEnabled", False)
    gui_app.set_modal_overlay(None)

  def _handle_mouse_release(self, _):
    super()._handle_mouse_release(_)
    self.stop_dmonitoringmodeld()

  # ------------------------------------------------------------
  # RENDER
  # ------------------------------------------------------------
  def _render(self, rect):
    super()._render(rect)

    if not self.frame:
      gui_label(
        rect,
        tr("camera starting"),
        font_size=100,
        font_weight=FontWeight.BOLD,
        alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
      )
      return -1

    # your face detection box
    self._draw_face_detection(rect)

    # the iconic new DM widget (position unchanged)
    self.driver_state_renderer.render(rect)

    return -1

  # ------------------------------------------------------------
  # FACE BOX DRAW
  # ------------------------------------------------------------
  def _draw_face_detection(self, rect: rl.Rectangle) -> None:
    driver_state = ui_state.sm["driverStateV2"]
    is_rhd = driver_state.wheelOnRightProb > 0.5
    driver_data = driver_state.rightDriverData if is_rhd else driver_state.leftDriverData

    if not (driver_data.faceProb > 0.7):
      return

    face_x, face_y = driver_data.facePosition
    face_std = max(driver_data.faceOrientationStd[0], driver_data.faceOrientationStd[1])

    alpha = 0.7
    if face_std > 0.15:
      alpha = max(0.7 - (face_std - 0.15) * 3.5, 0.0)

    fbox_x = int(1080.0 - 1714.0 * face_x)
    fbox_y = int(-135.0 + (504.0 + abs(face_x) * 112.0) + (1205.0 - abs(face_x) * 724.0) * face_y)
    box_size = 220

    line_color = rl.Color(255, 255, 255, int(alpha * 255))
    rl.draw_rectangle_rounded_lines_ex(
      rl.Rectangle(fbox_x - box_size / 2, fbox_y - box_size / 2, box_size, box_size),
      35.0 / box_size / 2, 10, 10, line_color
    )

  # ------------------------------------------------------------
  # FRAME MATRIX SAME AS BEFORE
  # ------------------------------------------------------------
  def _calc_frame_matrix(self, rect: rl.Rectangle) -> np.ndarray:
    driver_view_ratio = 2.0

    if self.frame:
      stream_width, stream_height = self.frame.width, self.frame.height
    else:
      stream_width, stream_height = 1928, 1208

    yscale = stream_height * driver_view_ratio / stream_width
    xscale = yscale * rect.height / rect.width * stream_width / stream_height

    return np.array([
      [xscale, 0.0, 0.0],
      [0.0, yscale, 0.0],
      [0.0, 0.0, 1.0]
    ])


if __name__ == "__main__":
  gui_app.init_window("Driver Camera View")
  driver_camera_view = DriverCameraDialog()
  try:
    for _ in gui_app.render():
      ui_state.update()
      driver_camera_view.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
  finally:
    driver_camera_view.close()