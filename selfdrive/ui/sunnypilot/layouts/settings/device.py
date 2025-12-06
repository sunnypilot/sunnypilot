"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import option_item_sp, multiple_button_item_sp, button_item_sp
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.button import ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog, ConfirmDialog
from openpilot.system.ui.widgets.list_view import dual_button_item, text_item
from openpilot.system.ui.widgets.scroller_tici import LineSeparator

offroad_time_options = {
  0: 0,
  1: 5,
  2: 10,
  3: 15,
  4: 30,
  5: 60,
  6: 120,
  7: 180,
  8: 300,
  9: 600,
  10: 1440,
  11: 1800,
}

class DeviceLayoutSP(DeviceLayout):
  def __init__(self):
    DeviceLayout.__init__(self)
    self._scroller._line_separator = None

  def _initialize_items(self):
    DeviceLayout._initialize_items(self)

    # Using dual button with no right button for better alignment
    self._always_offroad_btn = dual_button_item(
      left_text=lambda: tr("Enable Always Offroad"),
      left_callback=self._handle_always_offroad,
      right_text="",
      right_callback=None,
    )
    self._always_offroad_btn.action_item.right_button.set_visible(False)

    self._max_time_offroad = option_item_sp(
      title=lambda: tr("Max Time Offroad"),
      description=lambda: tr("Device will automatically shutdown after set time once the engine is turned off.\n(30h is the default)"),
      param="MaxTimeOffroad",
      min_value=0,
      max_value=11,
      value_change_step=1,
      on_value_changed=None,
      enabled=True,
      icon="",
      value_map=offroad_time_options,
      label_width=355,
      use_float_scaling=False,
      label_callback=self._update_max_time_offroad_label
    )

    self._device_wake_mode = multiple_button_item_sp(
      title=lambda: tr("Wake Up Behavior"),
      description=self.wake_mode_description,
      param="DeviceBootMode",
      buttons=[lambda: tr("Default"), lambda: tr("Offroad")],
      button_width=360,
      callback=None,
      inline=True,
    )

    self._quiet_mode_and_dcam = dual_button_item(
      left_text=lambda: tr("Quiet Mode"),
      right_text=lambda: tr("Driver Camera Preview"),
      left_callback=self._handle_quiet_mode,
      right_callback=self._show_driver_camera
    )
    self._quiet_mode_btn = self._quiet_mode_and_dcam.action_item.left_button
    self._dcam_btn = self._quiet_mode_and_dcam.action_item.right_button
    self._dcam_btn.set_button_style(ButtonStyle.NORMAL)

    self._reg_and_training = dual_button_item(
      left_text=lambda: tr("Regulatory"),
      left_callback=self._on_regulatory,
      right_text=lambda: tr("Training Guide"),
      right_callback=self._on_review_training_guide
    )
    self._reg_btn = self._reg_and_training.action_item.left_button
    self._training_btn = self._reg_and_training.action_item.right_button
    self._training_btn.set_button_style(ButtonStyle.NORMAL)

    self._onroad_uploads_and_reset = dual_button_item(
      left_text=lambda: tr("Onroad Uploads"),
      left_callback=self._onroad_uploads,
      right_text=lambda: tr("Reset Settings"),
      right_callback=self._reset_settings
    )
    self._onroad_uploads_btn = self._onroad_uploads_and_reset.action_item.left_button
    self._reset_settings_btn = self._onroad_uploads_and_reset.action_item.right_button

    items = [
      text_item(lambda: tr("Dongle ID"), self._params.get("DongleId") or (lambda: tr("N/A"))),
      LineSeparator(),
      text_item(lambda: tr("Serial"), self._params.get("HardwareSerial") or (lambda: tr("N/A"))),
      LineSeparator(),
      self._pair_device_btn,
      LineSeparator(),
      self._reset_calib_btn,
      LineSeparator(),
      button_item_sp(lambda: tr("Change Language"), lambda: tr("CHANGE"), callback=self._show_language_dialog),
      LineSeparator(),
    ]

    items += [
      self._device_wake_mode,
      LineSeparator(),
      self._max_time_offroad,
      LineSeparator(),
      self._quiet_mode_and_dcam,
      self._reg_and_training,
      self._onroad_uploads_and_reset,
      LineSeparator(),
    ]

    self._power_buttons = dual_button_item(
      left_text=lambda: tr("Reboot"),
      right_text=lambda: tr("Power Off"),
      left_callback=self._reboot_prompt,
      right_callback=self._power_off_prompt
    )
    self._reboot_btn = self._power_buttons.action_item.left_button
    self._power_btn = self._power_buttons.action_item.right_button

    items += [
      dual_button_item(
        left_text=lambda: tr("Reboot"),
        right_text=lambda: tr("Power Off"),
        left_callback=self._reboot_prompt,
        right_callback=self._power_off_prompt),
    ]

    return items

  def wake_mode_description(self) -> str:
    def_str = tr("Default: Device will boot/wake-up normally & will be ready to engage.")
    offrd_str = tr("Offroad: Device will be in Always Offroad mode after boot/wake-up.")
    header = tr("Controls state of the device after boot/sleep.")

    return f"{header}\n\n{def_str}\n{offrd_str}"

  def _handle_quiet_mode(self):
    ui_state.params.put_bool("QuietMode", not ui_state.params.get_bool("QuietMode"))

  def _onroad_uploads(self):
    ui_state.params.put_bool("OnroadUploads", not ui_state.params.get_bool("OnroadUploads"))

  def _reset_settings(self):
    def _do_reset(result: int):
      if result == DialogResult.CONFIRM:
        for _key in ui_state.params.all_keys():
          ui_state.params.remove(_key)
        HARDWARE.reboot()

    def _second_confirm(result: int):
      if result == DialogResult.CONFIRM:
        gui_app.set_modal_overlay(ConfirmDialog(
          text=tr("The reset cannot be undone. You have been warned."),
          confirm_text=tr("Confirm")
        ), callback=_do_reset)

    gui_app.set_modal_overlay(ConfirmDialog(
      text=tr("Are you sure you want to reset all sunnypilot settings to default? Once the settings are reset, there is no going back."),
      confirm_text=tr("Reset")
    ), callback=_second_confirm)

  def _handle_always_offroad(self):
    def _set_always_offroad(result: int, value: bool):
      if result == DialogResult.CONFIRM and not ui_state.engaged:
        ui_state.params.put_bool("OffroadMode", value)

    if ui_state.engaged:
      gui_app.set_modal_overlay(alert_dialog(tr("Disengage to Enter Always Offroad Mode")))
    else:
      if ui_state.params.get_bool("OffroadMode"):
        gui_app.set_modal_overlay(ConfirmDialog(
          text=tr("Are you sure you want to exit Always Offroad mode?"),
          confirm_text=tr("Confirm")
        ), callback=lambda result: _set_always_offroad(result, False))
      else:
        gui_app.set_modal_overlay(ConfirmDialog(
          text=tr("Are you sure you want to enter Always Offroad mode?"),
          confirm_text=tr("Confirm")
        ), callback=lambda result: _set_always_offroad(result, True))

  def _update_max_time_offroad_label(self, value: int) -> str:
    label = tr("Always On") if value == 0 else f"{value}" + tr("m") if value < 60 else f"{value//60}" + tr("h")
    label += tr(" (Default)") if value == 1800 else ""
    return label

  def _update_state(self):
    super()._update_state()

    # Handle Always Offroad button
    always_offroad = ui_state.params.get_bool("OffroadMode")

    # Text & Color
    if always_offroad:
      self._always_offroad_btn.action_item.left_button.set_text(tr("Exit Always Offroad"))
      self._always_offroad_btn.action_item.left_button.set_button_style(ButtonStyle.NORMAL)
    else:
      self._always_offroad_btn.action_item.left_button.set_text(tr("Enable Always Offroad"))
      self._always_offroad_btn.action_item.left_button.set_button_style(ButtonStyle.DANGER)

    # Position
    if self._scroller._items.__contains__(self._always_offroad_btn):
      self._scroller._items.remove(self._always_offroad_btn)
    if ui_state.is_offroad() and not always_offroad:
      self._scroller._items.insert(len(self._scroller._items) - 1, self._always_offroad_btn)
    else:
      self._scroller._items.insert(0, self._always_offroad_btn)

    # Quiet Mode button
    self._quiet_mode_btn.set_button_style(ButtonStyle.PRIMARY if ui_state.params.get_bool("QuietMode") else ButtonStyle.NORMAL)

    # Onroad Uploads
    self._onroad_uploads_btn.set_button_style(ButtonStyle.PRIMARY if ui_state.params.get_bool("OnroadUploads") else ButtonStyle.NORMAL)

    # Offroad only buttons
    self._dcam_btn.set_enabled(ui_state.is_offroad())
    self._reg_btn.set_enabled(ui_state.is_offroad())
    self._training_btn.set_enabled(ui_state.is_offroad())
    self._reset_settings_btn.set_enabled(ui_state.is_offroad())

    # Always enabled buttons
    self._reboot_btn.set_visible(True)
    self._power_btn.set_visible(True)
