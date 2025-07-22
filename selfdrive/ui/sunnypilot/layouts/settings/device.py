import os
import json
from itertools import filterfalse
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout
from openpilot.selfdrive.ui.onroad.driver_camera_dialog import DriverCameraDialog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware import TICI
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.list_view import text_item, button_item, dual_button_item, ListItem, DualButtonAction
from openpilot.system.ui.lib.scroller import Scroller
from openpilot.system.ui.lib.widget import Widget, DialogResult
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.system.ui.sunnypilot.lib.list_view import option_item_sp, multiple_button_item_sp
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.confirm_dialog import confirm_dialog, alert_dialog
from openpilot.system.ui.widgets.html_render import HtmlRenderer

# Description constants
DESCRIPTIONS = {
  'pair_device': "Pair your device with comma connect (connect.comma.ai) and claim your comma prime offer.",
  'driver_camera': "Preview the driver facing camera to ensure that driver monitoring has good visibility. (vehicle must be off)",
  'reset_calibration': (
      "openpilot requires the device to be mounted within 4° left or right and within 5° " +
      "up or 9° down. openpilot is continuously calibrating, resetting is rarely required."
  ),
  'review_guide': "Review the rules, features, and limitations of openpilot",
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

    offroad_time_options = {
    "0": ["0", "Always On"],
    "1": ["5", "5m"],
    "2": ["10", "10m"],
    "3": ["15", "15m"],
    "4": ["30", "30m"],
    "5": ["60", "1h"],
    "6": ["120", "2h"],
    "7": ["180", "3h"],
    "8": ["300", "5h"],
    "9": ["600", "10h"],
    "10": ["1440", "24h"],
    "11": ["1800", "30h (Default)"]
    }

    items.append(
      option_item_sp(
        title="Max Time Offroad",
        description="Device will automatically shutdown after set time once the engine is turned off.<br/>(30h is the default)",
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
    ),

    items.append(
      multiple_button_item_sp(
        "Wake Up Behavior",
        "Wake Up Behavior",
        param="DeviceBootMode",
        buttons=["Default", "Offroad"],
        button_width=255,
      ),
    )

    items += [dual_button_item("Reboot", "Power Off", left_callback=self._reboot_prompt, right_callback=self._power_off_prompt),]

    return items
