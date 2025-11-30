import os
import threading
import json
import pyray as rl
from enum import IntEnum
from collections.abc import Callable

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.time_helpers import system_time_valid
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigMultiOptionDialog, BigDialog, BigConfirmationDialogV2
from openpilot.selfdrive.ui.mici.widgets.pairing_dialog import PairingDialog
from openpilot.selfdrive.ui.mici.onroad.driver_camera_dialog import DriverCameraDialog
from openpilot.selfdrive.ui.mici.layouts.onboarding import TrainingGuide
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos, MouseEvent
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget, NavWidget
from openpilot.system.ui.widgets.slider import SmallSlider
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.label import MiciLabel
from openpilot.system.ui.widgets.html_render import HtmlModal, HtmlRenderer
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID


class MiciFccModal(NavWidget):
  BACK_TOUCH_AREA_PERCENTAGE = 0.1

  def __init__(self, file_path: str | None = None, text: str | None = None):
    super().__init__()
    self.set_back_callback(lambda: gui_app.set_modal_overlay(None))
    self._content = HtmlRenderer(file_path=file_path, text=text)
    self._scroll_panel = GuiScrollPanel2(horizontal=False)
    self._fcc_logo = gui_app.texture("icons_mici/settings/device/fcc_logo.png", 76, 64)

  def _render(self, rect: rl.Rectangle):
    content_height = self._content.get_total_height(int(rect.width))
    content_height += self._fcc_logo.height + 20

    scroll_content_rect = rl.Rectangle(rect.x, rect.y, rect.width, content_height)
    scroll_offset = self._scroll_panel.update(rect, scroll_content_rect.height)

    fcc_pos = rl.Vector2(rect.x + 20, rect.y + 20 + scroll_offset)

    scroll_content_rect.y += scroll_offset + self._fcc_logo.height + 20
    self._content.render(scroll_content_rect)

    rl.draw_texture_ex(self._fcc_logo, fcc_pos, 0.0, 1.0, rl.WHITE)

    return -1


def _engaged_confirmation_callback(callback: Callable, action_text: str):
  if not ui_state.engaged:
    def confirm_callback():
      # Check engaged again in case it changed while the dialog was open
      if not ui_state.engaged:
        callback()

    red = False
    if action_text == "power off":
      icon = "icons_mici/settings/device/power.png"
      red = True
    elif action_text == "reboot":
      icon = "icons_mici/settings/device/reboot.png"
    elif action_text == "reset":
      icon = "icons_mici/settings/device/lkas.png"
    elif action_text == "uninstall":
      icon = "icons_mici/settings/device/uninstall.png"
    else:
      # TODO: check
      icon = "icons_mici/settings/comma_icon.png"

    dlg: BigConfirmationDialogV2 | BigDialog = BigConfirmationDialogV2(f"slide to\n{action_text.lower()}", icon, red=red,
                                                                       exit_on_confirm=action_text == "reset",
                                                                       confirm_callback=confirm_callback)
    gui_app.set_modal_overlay(dlg)
  else:
    dlg = BigDialog(f"Disengage to {action_text}", "")
    gui_app.set_modal_overlay(dlg)


class RebootSlider(SmallSlider):
  HORIZONTAL_PADDING = 12

  def __init__(self, confirm_callback: Callable | None = None):
    self._icon = gui_app.texture("icons_mici/settings/device/reboot.png", 140, 140)
    super().__init__("slide to\nreboot", confirm_callback=confirm_callback)
    self._label.font_size = 64
    self._label.line_height = 0.9

  def _load_assets(self):
    self.set_rect(rl.Rectangle(0, 0, 760 + self.HORIZONTAL_PADDING * 2, 230))

    self._bg_txt = gui_app.texture("icons_mici/buttons/slider_bg.png", 760, 230, keep_aspect_ratio=False)
    self._circle_bg_txt = gui_app.texture("icons_mici/buttons/button_circle.png", 240, 240, keep_aspect_ratio=False)
    self._circle_arrow_txt = self._icon


class RebootConfirmScreen(NavWidget):
  EXIT_THRESHOLD = 0.02

  def __init__(self, confirm_callback: Callable | None = None, dismiss_callback: Callable | None = None):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))

    self._confirm_callback = confirm_callback
    self._dismiss_callback = dismiss_callback

    self._back_texture = gui_app.texture("icons_mici/setup/back_new.png", 96, 96)
    self._back_rect = rl.Rectangle(0, 0, 0, 0)
    self._slider = RebootSlider(confirm_callback=self._on_confirm)

    self._anim = FirstOrderFilter(0.0, 0.16, 1 / gui_app.target_fps)
    self._anim_target = 1.0
    self._anim_value = 0.0
    self._closing = False

    self.set_back_callback(self._on_back)

  def _on_confirm(self):
    if self._confirm_callback:
      self._confirm_callback()
    self._start_close()

  def _on_back(self):
    self._start_close()

  def _start_close(self):
    self._anim_target = 0.0
    self._closing = True
    self._slider.reset()

  def _handle_mouse_event(self, mouse_event: MouseEvent) -> None:
    super()._handle_mouse_event(mouse_event)
    if self._closing:
      return

    if mouse_event.left_released and rl.check_collision_point_rec(mouse_event.pos, self._back_rect):
      self._on_back()
      return

    self._slider.handle_mouse_event(mouse_event)

  def _update_state(self):
    super()._update_state()
    self._anim_value = self._anim.update(self._anim_target)
    self._slider.set_opacity(self._anim_value)

    if self._closing and self._anim_value <= self.EXIT_THRESHOLD:
      if self._dismiss_callback:
        self._dismiss_callback()
      gui_app.set_modal_overlay(None)

  def _render(self, rect: rl.Rectangle):
    ease = self._anim_value * self._anim_value * (3 - 2 * self._anim_value)
    slide_offset = (1.0 - ease) * rect.width * 0.18

    # back button
    back_pos = rl.Vector2(rect.x + 30 + slide_offset, rect.y + 30)
    back_color = rl.Color(255, 255, 255, int(255 * ease))
    rl.draw_texture_ex(self._back_texture, back_pos, 0.0, 1.0, back_color)
    self._back_rect = rl.Rectangle(back_pos.x, back_pos.y, self._back_texture.width, self._back_texture.height)

    # slider
    slider_rect = rl.Rectangle(
      rect.x + slide_offset + (rect.width - self._slider._rect.width) / 2,
      rect.y + rect.height * 0.52 - self._slider._rect.height / 2,
      self._slider._rect.width,
      self._slider._rect.height,
    )
    self._slider.set_rect(slider_rect)
    self._slider.render(slider_rect)
    return -1


class DeviceInfoLayoutMici(Widget):
  def __init__(self):
    super().__init__()

    self.set_rect(rl.Rectangle(0, 0, 360, 180))

    params = Params()
    header_color = rl.Color(255, 255, 255, int(255 * 0.9))
    subheader_color = rl.Color(255, 255, 255, int(255 * 0.9 * 0.65))
    max_width = int(self._rect.width - 20)
    self._dongle_id_label = MiciLabel("device ID", 48, width=max_width, color=header_color, font_weight=FontWeight.DISPLAY)
    self._dongle_id_text_label = MiciLabel(params.get("DongleId") or 'N/A', 32, width=max_width, color=subheader_color, font_weight=FontWeight.ROMAN)

    self._serial_number_label = MiciLabel("serial", 48, color=header_color, font_weight=FontWeight.DISPLAY)
    self._serial_number_text_label = MiciLabel(params.get("HardwareSerial") or 'N/A', 32, width=max_width, color=subheader_color, font_weight=FontWeight.ROMAN)

  def _render(self, _):
    self._dongle_id_label.set_position(self._rect.x + 20, self._rect.y - 10)
    self._dongle_id_label.render()

    self._dongle_id_text_label.set_position(self._rect.x + 20, self._rect.y + 68 - 25)
    self._dongle_id_text_label.render()

    self._serial_number_label.set_position(self._rect.x + 20, self._rect.y + 114 - 30)
    self._serial_number_label.render()

    self._serial_number_text_label.set_position(self._rect.x + 20, self._rect.y + 161 - 25)
    self._serial_number_text_label.render()


class UpdaterState(IntEnum):
  IDLE = 0
  WAITING_FOR_UPDATER = 1
  UPDATER_RESPONDING = 2


class PairBigButton(BigButton):
  def __init__(self):
    super().__init__("pair", "stable.konik.ai", "icons_mici/settings/comma_icon.png")

  def _update_state(self):
    if ui_state.prime_state.is_paired():
      self.set_text("paired")
    else:
      self.set_text("pair")
      self.set_value("stable.konik.ai")

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    # TODO: show ad dialog when clicked if not prime
    if ui_state.prime_state.is_paired():
      return
    dlg: BigDialog | PairingDialog
    if not system_time_valid():
      dlg = BigDialog(tr("Please connect to Wi-Fi to complete initial pairing"), "")
    elif UNREGISTERED_DONGLE_ID == (ui_state.params.get("DongleId") or UNREGISTERED_DONGLE_ID):
      dlg = BigDialog(tr("Device must be registered with the konik.ai backend to pair"), "")
    else:
      dlg = PairingDialog()
    gui_app.set_modal_overlay(dlg)


UPDATER_TIMEOUT = 10.0  # seconds to wait for updater to respond


class UpdateOpenpilotBigButton(BigButton):
  def __init__(self):
    self._txt_update_icon = gui_app.texture("icons_mici/settings/device/update.png", 64, 64)
    self._txt_reboot_icon = gui_app.texture("icons_mici/settings/device/reboot.png", 64, 64)
    self._txt_up_to_date_icon = gui_app.texture("icons_mici/settings/device/up_to_date.png", 64, 64)
    super().__init__("update hoofpilot", "", self._txt_update_icon)

    self._waiting_for_updater_t: float | None = None
    self._hide_value_t: float | None = None
    self._state: UpdaterState = UpdaterState.IDLE

    ui_state.add_offroad_transition_callback(self.offroad_transition)

  def offroad_transition(self):
    if ui_state.is_offroad():
      self.set_enabled(True)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if not system_time_valid():
      dlg = BigDialog(tr("Please connect to Wi-Fi to update"), "")
      gui_app.set_modal_overlay(dlg)
      return

    self.set_enabled(False)
    self._state = UpdaterState.WAITING_FOR_UPDATER
    self.set_icon(self._txt_update_icon)

    def run():
      if self.get_value() == "download update":
        os.system("pkill -SIGHUP -f system.updated.updated")
      elif self.get_value() == "update now":
        ui_state.params.put_bool("DoReboot", True)
      else:
        os.system("pkill -SIGUSR1 -f system.updated.updated")

    threading.Thread(target=run, daemon=True).start()

  def set_value(self, value: str):
    super().set_value(value)
    if value:
      self.set_text("")
    else:
      self.set_text("update hoofpilot")

  def _update_state(self):
    if ui_state.started:
      self.set_enabled(False)
      return

    updater_state = ui_state.params.get("UpdaterState") or ""
    failed_count = ui_state.params.get("UpdateFailedCount")
    failed = False if failed_count is None else int(failed_count) > 0

    if ui_state.params.get_bool("UpdateAvailable"):
      self.set_rotate_icon(False)
      self.set_enabled(True)
      if self.get_value() != "update now":
        self.set_value("update now")
        self.set_icon(self._txt_reboot_icon)

    elif self._state == UpdaterState.WAITING_FOR_UPDATER:
      self.set_rotate_icon(True)
      if updater_state != "idle":
        self._state = UpdaterState.UPDATER_RESPONDING

      # Recover from updater not responding (time invalid shortly after boot)
      if self._waiting_for_updater_t is None:
        self._waiting_for_updater_t = rl.get_time()

      if self._waiting_for_updater_t is not None and rl.get_time() - self._waiting_for_updater_t > UPDATER_TIMEOUT:
        self.set_rotate_icon(False)
        self.set_value("updater failed to respond")
        self._state = UpdaterState.IDLE
        self._hide_value_t = rl.get_time()

    elif self._state == UpdaterState.UPDATER_RESPONDING:
      if updater_state == "idle":
        self.set_rotate_icon(False)
        self._state = UpdaterState.IDLE
        self._hide_value_t = rl.get_time()
      else:
        if self.get_value() != updater_state:
          self.set_value(updater_state)

    elif self._state == UpdaterState.IDLE:
      self.set_rotate_icon(False)
      if failed:
        if self.get_value() != "failed to update":
          self.set_value("failed to update")

      elif ui_state.params.get_bool("UpdaterFetchAvailable"):
        self.set_enabled(True)
        if self.get_value() != "download update":
          self.set_value("download update")

      elif self._hide_value_t is not None:
        self.set_enabled(True)
        if self.get_value() == "checking...":
          self.set_value("up to date")
          self.set_icon(self._txt_up_to_date_icon)

        # Hide previous text after short amount of time (up to date or failed)
        if rl.get_time() - self._hide_value_t > 3.0:
          self._hide_value_t = None
          self.set_value("")
          self.set_icon(self._txt_update_icon)
      else:
        if self.get_value() != "":
          self.set_value("")

    if self._state != UpdaterState.WAITING_FOR_UPDATER:
      self._waiting_for_updater_t = None


class DeviceLayoutMici(NavWidget):
  def __init__(self, back_callback: Callable):
    super().__init__()

    self._fcc_dialog: HtmlModal | None = None
    self._driver_camera: DriverCameraDialog | None = None
    self._training_guide: TrainingGuide | None = None
    self._reboot_overlay: RebootConfirmScreen | None = None

    def reset_calibration_callback():
      params = ui_state.params
      params.remove("CalibrationParams")
      params.remove("LiveTorqueParameters")
      params.remove("LiveParameters")
      params.remove("LiveParametersV2")
      params.remove("LiveDelay")
      params.put_bool("OnroadCycleRequested", True)

    def uninstall_openpilot_callback():
      ui_state.params.put_bool("DoUninstall", True)

    reset_calibration_btn = BigButton("reset calibration", "", "icons_mici/settings/device/lkas.png")
    reset_calibration_btn.set_click_callback(lambda: _engaged_confirmation_callback(reset_calibration_callback, "reset"))

    uninstall_openpilot_btn = BigButton("uninstall hoofpilot", "", "icons_mici/settings/device/uninstall.png")
    uninstall_openpilot_btn.set_click_callback(lambda: _engaged_confirmation_callback(uninstall_openpilot_callback, "uninstall"))

    reboot_btn = BigCircleButton("icons_mici/settings/device/reboot.png", red=False)
    reboot_btn.set_click_callback(self._show_reboot_slider)

    self._load_languages()

    def language_callback():
      def selected_language_callback():
        selected_language = dlg.get_selected_option()
        ui_state.params.put("LanguageSetting", self._languages[selected_language])

      current_language_name = ui_state.params.get("LanguageSetting")
      current_language = next(name for name, lang in self._languages.items() if lang == current_language_name)

      dlg = BigMultiOptionDialog(list(self._languages), default=current_language, right_btn_callback=selected_language_callback)
      gui_app.set_modal_overlay(dlg)

    # lang_button = BigButton("change language", "", "icons_mici/settings/device/language.png")
    # lang_button.set_click_callback(language_callback)

    regulatory_btn = BigButton("regulatory info", "", "icons_mici/settings/device/info.png")
    regulatory_btn.set_click_callback(self._on_regulatory)

    driver_cam_btn = BigButton("driver camera preview", "", "icons_mici/settings/device/cameras.png")
    driver_cam_btn.set_click_callback(self._show_driver_camera)
    driver_cam_btn.set_enabled(lambda: ui_state.is_offroad())

    review_training_guide_btn = BigButton("review training guide", "", "icons_mici/settings/device/info.png")
    review_training_guide_btn.set_click_callback(self._on_review_training_guide)
    review_training_guide_btn.set_enabled(lambda: ui_state.is_offroad())

    self._scroller = Scroller([
      DeviceInfoLayoutMici(),
      UpdateOpenpilotBigButton(),
      PairBigButton(),
      review_training_guide_btn,
      driver_cam_btn,
      # lang_button,
      reset_calibration_btn,
      uninstall_openpilot_btn,
      regulatory_btn,
      reboot_btn,
    ], snap_items=False)

    # Set up back navigation
    self.set_back_callback(back_callback)

  def _show_reboot_slider(self):
    if ui_state.engaged:
      dlg = BigDialog(tr("Disengage to reboot"), "")
      gui_app.set_modal_overlay(dlg)
      return

    def on_confirm():
      ui_state.params.put_bool("DoReboot", True)

    def on_dismiss():
      self._reboot_overlay = None

    if self._reboot_overlay is None:
      self._reboot_overlay = RebootConfirmScreen(confirm_callback=on_confirm, dismiss_callback=on_dismiss)

    gui_app.set_modal_overlay(self._reboot_overlay, callback=lambda result: on_dismiss())

  def _on_regulatory(self):
    if not self._fcc_dialog:
      self._fcc_dialog = MiciFccModal(os.path.join(BASEDIR, "selfdrive/assets/offroad/mici_fcc.html"))
    gui_app.set_modal_overlay(self._fcc_dialog, callback=setattr(self, '_fcc_dialog', None))

  def _show_driver_camera(self):
    if not self._driver_camera:
      self._driver_camera = DriverCameraDialog()
    gui_app.set_modal_overlay(self._driver_camera, callback=lambda result: setattr(self, '_driver_camera', None))

  def _on_review_training_guide(self):
    if not self._training_guide:
      def completed_callback():
        gui_app.set_modal_overlay(None)

      self._training_guide = TrainingGuide(completed_callback=completed_callback)
    gui_app.set_modal_overlay(self._training_guide, callback=lambda result: setattr(self, '_training_guide', None))

  def _load_languages(self):
    with open(os.path.join(BASEDIR, "selfdrive/ui/translations/languages.json")) as f:
      self._languages = json.load(f)

  def show_event(self):
    super().show_event()
    self._scroller.show_event()

  def _render(self, rect: rl.Rectangle):
    self._scroller.render(rect)
