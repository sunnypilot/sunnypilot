"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp
from opendbc.car.hyundai.values import CAR, CANFD_UNSUPPORTED_LONGITUDINAL_CAR, UNSUPPORTED_LONGITUDINAL_CAR


class HyundaiSettings:
  def __init__(self):
    self.ui_state = None
    self.offroad = False
    self.alpha_long_available = False

    tuning_texts = [tr("Off"), tr("Dynamic"), tr("Predictive")]
    self.longitudinal_tuning_item = multiple_button_item_sp(tr("Custom Longitudinal Tuning"), "", tuning_texts,
                                                            button_width=300, callback=self._on_tuning_selected,
                                                            param="HyundaiLongitudinalTuning", inline=False)
    self.items = [self.longitudinal_tuning_item]

  def _on_tuning_selected(self, index):
    self.ui_state.params.put("HyundaiLongitudinalTuning", index)

  def update_settings(self):
    self.alpha_long_available = False
    bundle = self.ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      self.alpha_long_available = CAR[platform] not in (UNSUPPORTED_LONGITUDINAL_CAR | CANFD_UNSUPPORTED_LONGITUDINAL_CAR)
    elif self.ui_state.CP:
      self.alpha_long_available = self.ui_state.CP.alphaLongitudinalAvailable

    tuning_param = int(self.ui_state.params.get("HyundaiLongitudinalTuning") or "0")
    oplong_enabled = self.ui_state.has_longitudinal_control

    descriptions = [
      tr("Your vehicle will use the default longitudinal tuning."),
      tr("Your vehicle will use the dynamic longitudinal tuning."),
      tr("Your vehicle will use the predictive longitudinal tuning."),
    ]
    description = descriptions[tuning_param] if tuning_param < len(descriptions) else descriptions[0]

    longitudinal_tuning_disabled = not self.offroad or not oplong_enabled
    if longitudinal_tuning_disabled:
      if not self.offroad:
        description = tr("This feature is unavailable while the car is onroad.")
      elif not oplong_enabled:
        description = tr("This feature is unavailable because openpilot longitudinal control is not enabled.")

    self.longitudinal_tuning_item.action_item.set_enabled(not longitudinal_tuning_disabled)
    self.longitudinal_tuning_item.set_description(description)
    self.longitudinal_tuning_item.show_description(True)
    self.longitudinal_tuning_item.action_item.set_selected_button(tuning_param)
    self.longitudinal_tuning_item.set_visible(self.alpha_long_available)

  def update_state(self, ui_state):
    self.ui_state = ui_state
    self.offroad = ui_state.is_offroad()
    self.update_settings()
