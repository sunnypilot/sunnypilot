import time
import numpy as np
import pyray as rl
from cereal import log, messaging
from msgq.visionipc import VisionStreamType
from openpilot.selfdrive.ui import UI_BORDER_SIZE
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.selfdrive.ui.onroad.alert_renderer import AlertRenderer
from openpilot.system.ui.widgets import Widget
from openpilot.common.filter_simple import FirstOrderFilter
import math

# Driver monitoring alert size enum
AlertSize = log.SelfdriveState.AlertSize
from openpilot.selfdrive.ui.onroad.hud_renderer import HudRenderer
from openpilot.selfdrive.ui.onroad.model_renderer import ModelRenderer
from openpilot.selfdrive.ui.onroad.cameraview import CameraView
from openpilot.system.ui.lib.application import gui_app
from openpilot.common.transformations.camera import DEVICE_CAMERAS, DeviceCameraConfig, view_frame_from_device_frame
from openpilot.common.transformations.orientation import rot_from_euler
from openpilot.selfdrive.ui.layouts.sidebar import SIDEBAR_WIDTH

OpState = log.SelfdriveState.OpenpilotState
CALIBRATED = log.LiveCalibrationData.Status.calibrated
ROAD_CAM = VisionStreamType.VISION_STREAM_ROAD
WIDE_CAM = VisionStreamType.VISION_STREAM_WIDE_ROAD
DEFAULT_DEVICE_CAMERA = DEVICE_CAMERAS["tici", "ar0231"]

BORDER_COLORS = {
  UIStatus.DISENGAGED: rl.Color(0x12, 0x28, 0x39, 0xFF),  # Blue for disengaged state
  UIStatus.OVERRIDE: rl.Color(0x89, 0x92, 0x8D, 0xFF),  # Gray for override state
  UIStatus.ENGAGED: rl.Color(0x16, 0x7F, 0x40, 0xFF),  # Green for engaged state
}

WIDE_CAM_MAX_SPEED = 10.0  # m/s (22 mph)
ROAD_CAM_MIN_SPEED = 15.0  # m/s (34 mph)
INF_POINT = np.array([1000.0, 0.0, 0.0])


class AugmentedRoadView(CameraView):
  def __init__(self, stream_type: VisionStreamType = VisionStreamType.VISION_STREAM_ROAD):
    super().__init__("camerad", stream_type)
    self._set_placeholder_color(BORDER_COLORS[UIStatus.DISENGAGED])

    self.device_camera: DeviceCameraConfig | None = None
    self.view_from_calib = view_frame_from_device_frame.copy()
    self.view_from_wide_calib = view_frame_from_device_frame.copy()

    self._matrix_cache_key = (0, 0.0, 0.0, stream_type)
    self._cached_matrix: np.ndarray | None = None
    self._content_rect = rl.Rectangle()

    self.model_renderer = ModelRenderer()
    self._hud_renderer = HudRenderer()
    self.alert_renderer = AlertRenderer()
    self._settings_cb = None
    self._settings_icon = gui_app.texture("icons_mici/settings.png", 110, 110)
    self._settings_rect = rl.Rectangle()

    # Inline Tizi DriverStateRenderer (ported from Mici) scaled up for Tizi
    # This avoids relying on the external mici module so we consume fewer Copilot requests.
    class TiziDriverStateRenderer(Widget):
      BASE_SIZE = int(60 * 2.5)
      LINES_ANGLE_INCREMENT = 5
      LINES_STALE_ANGLES = 3.0  # seconds

      def __init__(self, lines: bool = False, confirm_mode: bool = False, confirm_callback=None):
        super().__init__()
        self.set_rect(rl.Rectangle(0, 0, self.BASE_SIZE, self.BASE_SIZE))
        self._lines = lines or confirm_mode

        self._confirm_mode = confirm_mode
        self._confirm_callback = confirm_callback
        self._confirm_angles = {}

        assert 360 % self.LINES_ANGLE_INCREMENT == 0
        self._head_angles = {
          i * self.LINES_ANGLE_INCREMENT: FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)
          for i in range(360 // self.LINES_ANGLE_INCREMENT)
        }

        self._is_active = False
        self._is_rhd = False
        self._face_detected = False
        self._should_draw = False
        self._force_active = False
        self._looking_center = False

        self._fade_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps)
        self._pitch_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps, initialized=False)
        self._yaw_filter = FirstOrderFilter(0.0, 0.05, 1 / gui_app.target_fps, initialized=False)
        self._rotation_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps, initialized=False)
        self._looking_center_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)

        # Load icons/textures
        self.load_icons()

      def load_icons(self):
        self._dm_person = gui_app.texture(
          "icons_mici/onroad/driver_monitoring/dm_person.png", self._rect.width, self._rect.height
        )
        self._dm_cone = gui_app.texture(
          "icons_mici/onroad/driver_monitoring/dm_cone.png", self._rect.width, self._rect.height
        )
        center_size = round(36 / self.BASE_SIZE * self._rect.width)
        self._dm_center = gui_app.texture(
          "icons_mici/onroad/driver_monitoring/dm_center.png", center_size, center_size
        )
        background_size = round(52 / self.BASE_SIZE * self._rect.width)
        self._dm_background = gui_app.texture(
          "icons_mici/onroad/driver_monitoring/dm_background.png", background_size, background_size
        )

      def set_should_draw(self, should_draw: bool):
        self._should_draw = should_draw

      @property
      def should_draw(self):
        return (
          self._should_draw
          and ui_state.sm["selfdriveState"].alertSize == AlertSize.none
          and ui_state.sm.recv_frame["driverStateV2"] > ui_state.started_frame
        )

      def set_force_active(self, force_active: bool):
        self._force_active = force_active

      @property
      def effective_active(self) -> bool:
        return bool(self._force_active or self._is_active)

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

        if self.effective_active:
          source_rect = rl.Rectangle(0, 0, self._dm_cone.width, self._dm_cone.height)
          dest_rect = rl.Rectangle(
            self._rect.x + self._rect.width / 2,
            self._rect.y + self._rect.height / 2,
            self._dm_cone.width,
            self._dm_cone.height,
          )

          if not self._lines:
            rl.draw_texture_pro(
              self._dm_cone,
              source_rect,
              dest_rect,
              rl.Vector2(dest_rect.width / 2, dest_rect.height / 2),
              self._rotation_filter.x - 90,
              rl.Color(
                255,
                255,
                255,
                int(255 * self._fade_filter.x * (1 - self._looking_center_filter.x)),
              ),
            )

            rl.draw_texture_ex(
              self._dm_center,
              (
                int(self._rect.x + (self._rect.width - self._dm_center.width) / 2),
                int(self._rect.y + (self._rect.height - self._dm_center.height) / 2),
              ),
              0,
              1.0,
              rl.Color(
                255,
                255,
                255,
                int(255 * self._fade_filter.x * self._looking_center_filter.x),
              ),
            )

          else:
            now = rl.get_time()
            self._confirm_angles = {
              angle: t for angle, t in self._confirm_angles.items() if now - t < self.LINES_STALE_ANGLES
            }

            looking_center = self._looking_center_filter.x > 0.2
            for angle, f in self._head_angles.items():
              dst_from_current = ((angle - self._rotation_filter.x) % 360) - 180
              target = 1.0 if abs(dst_from_current) <= self.LINES_ANGLE_INCREMENT * 5 else 0.0
              if not self._face_detected:
                target = 0.0

              if self._confirm_mode:
                if target > 0 and not looking_center:
                  self._confirm_angles[angle] = now

                if angle in self._confirm_angles and target == 0:
                  target = 0.65

              if self._looking_center:
                target = np.interp(self._looking_center_filter.x, [0.0, 1.0], [target, 0.45])

              f.update(target)
              self._draw_line(angle, f, self._looking_center and angle not in self._confirm_angles)

            if self._confirm_mode:
              if len(self._confirm_angles) >= 360 // self.LINES_ANGLE_INCREMENT:
                self._confirm_angles = {}
                if self._confirm_callback is not None:
                  self._confirm_callback()

      def _draw_line(self, angle: int, f: FirstOrderFilter, grey: bool):
        line_length = self._rect.width / 6
        line_length = round(np.interp(f.x, [0.0, 1.0], [0, line_length]))
        line_offset = self._rect.width / 2 - line_length * 2
        center_x = self._rect.x + self._rect.width / 2
        center_y = self._rect.y + self._rect.height / 2
        start_x = center_x + (line_offset + line_length) * math.cos(math.radians(angle))
        start_y = center_y + (line_offset + line_length) * math.sin(math.radians(angle))
        end_x = start_x + line_length * math.cos(math.radians(angle))
        end_y = start_y + line_length * math.sin(math.radians(angle))
        color = rl.Color(0, 255, 64, 255)

        if grey:
          color = rl.Color(166, 166, 166, 255)

        if f.x > 0.01:
          rl.draw_line_ex((start_x, start_y), (end_x, end_y), 12, color)

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

        if abs(pitch) < math.radians(3) and abs(yaw) < math.radians(3):
          self._looking_center = True
        elif abs(pitch) > math.radians(6) or abs(yaw) > math.radians(6):
          self._looking_center = False
        self._looking_center_filter.update(1 if self._looking_center else 0)

        rotation = math.degrees(math.atan2(pitch, yaw))
        angle_diff = rotation - self._rotation_filter.x
        angle_diff = ((angle_diff + 180) % 360) - 180
        self._rotation_filter.update(self._rotation_filter.x + angle_diff)

        if not self.should_draw:
          self._fade_filter.update(0.0)
        elif not self.effective_active:
          self._fade_filter.update(0.35)
        else:
          self._fade_filter.update(1.0)

    self.driver_state_renderer = TiziDriverStateRenderer()

    # debug
    self._pm = messaging.PubMaster(['uiDebug'])

  def set_settings_callback(self, cb):
    self._settings_cb = cb

  def _render(self, rect):
    # Only render when system is started to avoid invalid data access
    start_draw = time.monotonic()
    if not ui_state.started:
      return

    self._switch_stream_if_needed(ui_state.sm)

    # Update calibration before rendering
    self._update_calibration()

    # Create inner content area with border padding
    self._content_rect = rl.Rectangle(
      rect.x + UI_BORDER_SIZE,
      rect.y + UI_BORDER_SIZE,
      rect.width - 2 * UI_BORDER_SIZE,
      rect.height - 2 * UI_BORDER_SIZE,
    )

    # Enable scissor mode to clip all rendering within content rectangle boundaries
    # This creates a rendering viewport that prevents graphics from drawing outside the border
    rl.begin_scissor_mode(
      int(self._content_rect.x),
      int(self._content_rect.y),
      int(self._content_rect.width),
      int(self._content_rect.height),
    )

    # Render the base camera view
    super()._render(rect)

    # Draw all UI overlays
    self.model_renderer.render(self._content_rect)
    self._hud_renderer.render(self._content_rect)
    self.alert_renderer.render(self._content_rect)
    self._render_settings_icon()

    # Determine whether to show driver monitoring (match Mici logic).
    # HudRenderer no longer exposes `drawing_top_icons()` in the Tizi HUD,
    # so omit that check here to avoid crashes. If top icons need to suppress
    # the dmoji in future, reintroduce a HUD API and gate this accordingly.
    should_draw_dmoji = (
      ui_state.is_onroad()
      and (ui_state.status != UIStatus.DISENGAGED or ui_state.always_on_dm)
    )
    try:
      self.driver_state_renderer.set_should_draw(should_draw_dmoji)

      # Position DM in the BOTTOM-LEFT of the content rect.
      # Use the widget's own height so it sits just above the bottom border.
      dm_rect = self.driver_state_renderer._rect
      self.driver_state_renderer.set_position(
        self._content_rect.x + 16,
        self._content_rect.y + self._content_rect.height - dm_rect.height - 16,
      )
    except Exception:
      pass

    # Render without passing `self._content_rect` to preserve the widget's own rect/size
    self.driver_state_renderer.render()

    # Custom UI extension point - add custom overlays here
    # Use self._content_rect for positioning within camera bounds

    # End clipping region
    rl.end_scissor_mode()

    # Draw colored border based on driving state
    self._draw_border(rect)

    # publish uiDebug
    msg = messaging.new_message('uiDebug')
    msg.uiDebug.drawTimeMillis = (time.monotonic() - start_draw) * 1000
    self._pm.send('uiDebug', msg)

  def _handle_mouse_press(self, _):
    # Swallow clicks on settings icon
    mouse_pos = rl.get_mouse_position()
    if rl.check_collision_point_rec(mouse_pos, self._settings_rect):
      return

    if not self._hud_renderer.user_interacting() and self._click_callback is not None:
      self._click_callback()

  def _handle_mouse_release(self, _):
    mouse_pos = rl.get_mouse_position()
    if rl.check_collision_point_rec(mouse_pos, self._settings_rect):
      if self._settings_cb is not None:
        self._settings_cb()
      return

  def _draw_border(self, rect: rl.Rectangle):
    rl.draw_rectangle_lines_ex(rect, UI_BORDER_SIZE, rl.BLACK)
    border_roundness = 0.12
    border_color = BORDER_COLORS.get(ui_state.status, BORDER_COLORS[UIStatus.DISENGAGED])
    border_rect = rl.Rectangle(
      rect.x + UI_BORDER_SIZE,
      rect.y + UI_BORDER_SIZE,
      rect.width - 2 * UI_BORDER_SIZE,
      rect.height - 2 * UI_BORDER_SIZE,
    )
    rl.draw_rectangle_rounded_lines_ex(
      border_rect, border_roundness, 10, UI_BORDER_SIZE, border_color
    )

  def _render_settings_icon(self):
    if self._settings_icon is None:
      return
    margin = 18
    scale = 1.15
    w = self._settings_icon.width * scale
    h = self._settings_icon.height * scale
    x = self._content_rect.x + margin
    y = self._content_rect.y + margin
    self._settings_rect = rl.Rectangle(x, y, w, h)
    rl.draw_texture_ex(self._settings_icon, (int(x), int(y)), 0, scale, rl.Color(255, 255, 255, 235))

  def _switch_stream_if_needed(self, sm):
    if sm['selfdriveState'].experimentalMode and WIDE_CAM in self.available_streams:
      v_ego = sm['carState'].vEgo
      if v_ego < WIDE_CAM_MAX_SPEED:
        target = WIDE_CAM
      elif v_ego > ROAD_CAM_MIN_SPEED:
        target = ROAD_CAM
      else:
        # Hysteresis zone - keep current stream
        target = self.stream_type
    else:
      target = ROAD_CAM

    if self.stream_type != target:
      self.switch_stream(target)

  def _update_calibration(self):
    # Update device camera if not already set
    sm = ui_state.sm
    if not self.device_camera and sm.seen['roadCameraState'] and sm.seen['deviceState']:
      self.device_camera = DEVICE_CAMERAS[
        (str(sm['deviceState'].deviceType), str(sm['roadCameraState'].sensor))
      ]

    # Check if live calibration data is available and valid
    if not (sm.updated["liveCalibration"] and sm.valid['liveCalibration']):
      return

    calib = sm['liveCalibration']
    if len(calib.rpyCalib) != 3 or calib.calStatus != CALIBRATED:
      return

    # Update view_from_calib matrix
    device_from_calib = rot_from_euler(calib.rpyCalib)
    self.view_from_calib = view_frame_from_device_frame @ device_from_calib

    # Update wide calibration if available
    if hasattr(calib, 'wideFromDeviceEuler') and len(calib.wideFromDeviceEuler) == 3:
      wide_from_device = rot_from_euler(calib.wideFromDeviceEuler)
      self.view_from_wide_calib = (
        view_frame_from_device_frame @ wide_from_device @ device_from_calib
      )

  def _calc_frame_matrix(self, rect: rl.Rectangle) -> np.ndarray:
    # Check if we can use cached matrix
    cache_key = (
      ui_state.sm.recv_frame['liveCalibration'],
      self._content_rect.width,
      self._content_rect.height,
      self.stream_type,
    )
    if cache_key == self._matrix_cache_key and self._cached_matrix is not None:
      return self._cached_matrix

    # Get camera configuration
    device_camera = self.device_camera or DEFAULT_DEVICE_CAMERA
    is_wide_camera = self.stream_type == WIDE_CAM
    intrinsic = device_camera.ecam.intrinsics if is_wide_camera else device_camera.fcam.intrinsics
    calibration = self.view_from_wide_calib if is_wide_camera else self.view_from_calib
    zoom = 2.0 if is_wide_camera else 1.1

    # Calculate transforms for vanishing point
    calib_transform = intrinsic @ calibration
    kep = calib_transform @ INF_POINT

    # Calculate center points and dimensions
    x, y = self._content_rect.x, self._content_rect.y
    w, h = self._content_rect.width, self._content_rect.height
    cx, cy = intrinsic[0, 2], intrinsic[1, 2]

    # Calculate max allowed offsets with margins
    margin = 5
    max_x_offset = cx * zoom - w / 2 - margin
    max_y_offset = cy * zoom - h / 2 - margin

    # Calculate and clamp offsets to prevent out-of-bounds issues
    try:
      if abs(kep[2]) > 1e-6:
        x_offset = np.clip((kep[0] / kep[2] - cx) * zoom, -max_x_offset, max_x_offset)
        y_offset = np.clip((kep[1] / kep[2] - cy) * zoom, -max_y_offset, max_y_offset)
      else:
        x_offset, y_offset = 0, 0
    except (ZeroDivisionError, OverflowError):
      x_offset, y_offset = 0, 0

    # Cache the computed transformation matrix to avoid recalculations
    self._matrix_cache_key = cache_key
    self._cached_matrix = np.array(
      [
        [zoom * 2 * cx / w, 0, -x_offset / w * 2],
        [0, zoom * 2 * cy / h, -y_offset / h * 2],
        [0, 0, 1.0],
      ]
    )

    video_transform = np.array(
      [
        [zoom, 0.0, (w / 2 + x - x_offset) - (cx * zoom)],
        [0.0, zoom, (h / 2 + y - y_offset) - (cy * zoom)],
        [0.0, 0.0, 1.0],
      ]
    )
    self.model_renderer.set_transform(video_transform @ calib_transform)

    return self._cached_matrix


if __name__ == "__main__":
  gui_app.init_window("OnRoad Camera View")
  road_camera_view = AugmentedRoadView(ROAD_CAM)
  print("***press space to switch camera view***")
  try:
    for _ in gui_app.render():
      ui_state.update()
      if rl.is_key_released(rl.KeyboardKey.KEY_SPACE):
        if WIDE_CAM in road_camera_view.available_streams:
          stream = ROAD_CAM if road_camera_view.stream_type == WIDE_CAM else WIDE_CAM
          road_camera_view.switch_stream(stream)
      road_camera_view.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
  finally:
    road_camera_view.close()
