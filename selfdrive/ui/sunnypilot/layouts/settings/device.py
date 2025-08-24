from itertools import filterfalse
from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout
from openpilot.system.ui.widgets.list_view import dual_button_item, DualButtonAction
from openpilot.system.ui.sunnypilot.lib.list_view import option_item_sp, multiple_button_item_sp

offroad_time_options = {
  0: [0, "Always On"],
  1: [5, "5m"],
  2: [10, "10m"],
  3: [15, "15m"],
  4: [30, "30m"],
  5: [60, "1h"],
  6: [120, "2h"],
  7: [180, "3h"],
  8: [300, "5h"],
  9: [600, "10h"],
  10: [1440, "24h"],
  11: [1800, "30h (Default)"]
}
brightness_options = {
  0: [1, "Auto (Dark)"],
  1: [0, "Auto"],
  2: [10, "10"],
  3: [20, "20"],
  4: [30, "30"],
  5: [40, "40"],
  6: [50, "50"],
  7: [60, "60"],
  8: [70, "70"],
  9: [80, "80"],
  10: [90, "90"],
  11: [100, "100"]
}

class DeviceLayoutSP(DeviceLayout):
  def __init__(self):
    DeviceLayout.__init__(self)

  def _hide_item(self, item):
    return (item.title in {"Driver Camera", "Regulatory", "Review Training Guide", "Change Language"}
            or (isinstance(item.action_item, DualButtonAction) and item.action_item.left_text == "Reboot"))

  def _initialize_items(self):

    items = DeviceLayout._initialize_items(self)
    items[:] = filterfalse(self._hide_item, items)

    self.max_time_offroad = option_item_sp(
      title="Max Time Offroad",
      description="Device will automatically shutdown after set time once the engine is turned off.\n(30h is the default)",
      param="MaxTimeOffroad",
      min_value=0,
      max_value=11,
      value_change_step=1,
      on_value_changed=None,
      enabled=True,
      icon="",
      value_map=offroad_time_options,
      label_width=300,
      use_float_scaling=False)

    self.device_wake_mode = multiple_button_item_sp(
      "Wake Up Behavior",
      description=self.wake_mode_description,
      param="DeviceBootMode",
      buttons=["Default", "Offroad"],
      button_width=255,
      callback=None,
    )

    self.interactivity_timeout = option_item_sp(
      title="Interactivity Timeout",
      description="""Apply a custom timeout for settings UI.\n
                  This is the time after which settings UI closes automatically
                  if user is not interacting with the screen.""",
      param="InteractivityTimeout",
      min_value=0,
      max_value=120,
      value_change_step=10,
      on_value_changed=None,
      enabled=True,
      icon="",
      value_map=None,
      label_width=300,
      use_float_scaling=False,
      label_callback=self.update_interactivity_timeout_label
    )

    self.brightness = option_item_sp(
      title="Brightness",
      description="Overrides the brightness of the device.",
      param="Brightness",
      min_value=0,
      max_value=11,
      value_change_step=1,
      on_value_changed=None,
      enabled=True,
      icon="",
      value_map=brightness_options,
      label_width=300,
      use_float_scaling=False,
      label_callback=None
    )

    items += [
      self.device_wake_mode,
      self.max_time_offroad,
      self.interactivity_timeout,
      self.brightness,
    ]

    items += [
      dual_button_item("Reboot", "Power Off", left_callback=self._reboot_prompt, right_callback=self._power_off_prompt),
    ]

    return items

  def wake_mode_description(self) -> str:
    def_str = "Default: Device will boot/wake-up normally & will be ready to engage."
    offrd_str = "Offroad: Device will be in Always Offroad mode after boot/wake-up."
    header = "Controls state of the device after boot/sleep."

    return f"{header}\n\n{def_str}\n{offrd_str}"

  def update_interactivity_timeout_label(self, value: int) -> str:
    return "Default" if value == 0 else f"{value}s"
