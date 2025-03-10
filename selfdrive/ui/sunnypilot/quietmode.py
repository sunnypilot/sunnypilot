"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from cereal import car

AudibleAlert = car.CarControl.HUDControl.AudibleAlert

class QuietDriveManager:
  def __init__(self):
    self.current_alert = AudibleAlert.none
    self.param_s = Params()
    self.quiet_drive = self.param_s.get_bool("QuietDrive")
    self._frame = 0

  def load_param(self):
    self._frame += 1
    if self._frame == 50:
      self.quiet_drive = self.param_s.get_bool("QuietDrive")
  def is_quiet_drive_enabled(self) -> bool:
    return self.quiet_drive
  def should_play_sound(self, current_alert: int) -> bool:
    """
    Check if a sound should be played based on the quiet drive setting
    and the current alert.
    """
    AudibleAlert = car.CarControl.HUDControl.AudibleAlert
    # Define the conditions under which sounds should be played, using valid AudibleAlert values
    return bool((self.current_alert == AudibleAlert.warningSoft or
                 self.current_alert == AudibleAlert.warningImmediate or
                 self.current_alert == AudibleAlert.promptDistracted or
                 self.current_alert == AudibleAlert.promptRepeat) or
                (not self.is_quiet_drive_enabled() and current_alert != AudibleAlert.none))



