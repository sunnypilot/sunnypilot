"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.selfdrive.ui.sunnypilot.onroad.chevron_metrics import ChevronMetrics
from openpilot.selfdrive.ui.sunnypilot.onroad.rainbow_path import RainbowPath
from openpilot.selfdrive.ui.sunnypilot.ui_state import MADSState
from openpilot.system.ui.lib.application import gui_app


class ModelRendererSP:
  def __init__(self):
    self.rainbow_path = RainbowPath()
    self.chevron_metrics = ChevronMetrics()
    self._width_filter = FirstOrderFilter(0.9, 0.1, 1 / gui_app.target_fps)

  @property
  def _lateral_active(self) -> bool:
    sm = ui_state.sm
    if sm.valid["selfdriveStateSP"]:
      mads = sm["selfdriveStateSP"].mads
      if mads.available:
        return mads.enabled and mads.state != MADSState.paused
    return ui_state.status in (UIStatus.ENGAGED, UIStatus.LAT_ONLY)

  def _get_path_half_width(self) -> float:
    target = 0.9 if self._lateral_active else 0.40
    return self._width_filter.update(target)
