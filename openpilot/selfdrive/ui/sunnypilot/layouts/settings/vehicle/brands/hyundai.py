"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from opendbc.car.hyundai.values import CAR, UNSUPPORTED_LONGITUDINAL_CAR


class HyundaiSettings(BrandSettings):
  def __init__(self):
    super().__init__()
    self.alpha_long_available = False

    self.longitudinal_tuning_item = toggle_item_sp(tr("Custom Longitudinal Tuning"), "", param="HyundaiLongitudinalTuning")
    self.items = [self.longitudinal_tuning_item]

  def update_settings(self):
    self.alpha_long_available = False
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      self.alpha_long_available = CAR[platform] not in set().union(*UNSUPPORTED_LONGITUDINAL_CAR.values())
    elif ui_state.CP is not None:
      self.alpha_long_available = ui_state.CP.alphaLongitudinalAvailable

    long_enabled = ui_state.has_longitudinal_control
    desc = tr("Accelerates and brakes the way your car's own cruise control does.")
    if not ui_state.is_offroad():
      desc = tr("This feature is unavailable while the car is onroad.")
    elif not long_enabled:
      desc = tr("This feature is unavailable because sunnypilot Longitudinal Control (Alpha) is not enabled.")

    self.longitudinal_tuning_item.action_item.set_enabled(ui_state.is_offroad() and long_enabled)
    self.longitudinal_tuning_item.set_description(desc)
    self.longitudinal_tuning_item.show_description(True)
    self.longitudinal_tuning_item.set_visible(self.alpha_long_available)
