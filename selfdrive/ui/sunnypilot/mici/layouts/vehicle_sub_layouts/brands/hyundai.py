"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiParamToggle
from opendbc.car.hyundai.values import CAR, UNSUPPORTED_LONGITUDINAL_CAR


class HyundaiSettingsMici(BrandSettingsMici):
  def __init__(self):
    super().__init__()
    self.alpha_long_available = False

    tuning_texts = [tr("Off"), tr("Dynamic"), tr("Predictive")]
    self.longitudinal_tuning_item = BigMultiParamToggle(
      tr("Custom Longitudinal Tuning"),
      "HyundaiLongitudinalTuning",
      tuning_texts,
      select_callback=self._on_tuning_selected
    )
    self.items = [self.longitudinal_tuning_item]

  def _on_tuning_selected(self, option: str):
    self.update_settings()

  def update_settings(self):
    self.alpha_long_available = False
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      self.alpha_long_available = CAR[platform] not in set().union(*UNSUPPORTED_LONGITUDINAL_CAR.values())
    elif ui_state.CP is not None:
      self.alpha_long_available = ui_state.CP.alphaLongitudinalAvailable

    long_enabled = ui_state.has_longitudinal_control
    longitudinal_tuning_disabled = not ui_state.is_offroad() or not long_enabled

    self.longitudinal_tuning_item.set_enabled(not longitudinal_tuning_disabled)
    self.longitudinal_tuning_item.set_visible(self.alpha_long_available)
