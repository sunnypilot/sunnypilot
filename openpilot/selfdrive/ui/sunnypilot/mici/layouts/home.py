"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.home import MiciHomeLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.label import UnifiedLabel

RUNNER_TINYGRAD = 1


class MiciHomeLayoutSP(MiciHomeLayout):
  def __init__(self):
    super().__init__()
    self._openpilot_label = UnifiedLabel("sunnypilot", font_size=88, font_weight=FontWeight.AUDIOWIDE, max_width=480, wrap_text=False)

  def _render(self, rect):
    super()._render(rect)
    chestnut = ui_state.sm["deviceState"].chestnutPresent
    if chestnut:
      gpu_ready = ui_state.usbgpu_compiled or (ui_state.params.get("ModelRunnerTypeCache") == RUNNER_TINYGRAD)
      self._egpu_icon.set_visible(gpu_ready)
      self._egpu_icon_gray.set_visible(not gpu_ready)
