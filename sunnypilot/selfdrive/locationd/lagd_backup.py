"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from cereal import car, log
from openpilot.common.swaglog import cloudlog


class LagdBackup:
  def __init__(self, CP: car.CarParams):
    self._params = Params()
    self.CP = CP

  def backup_lagd(self) -> bool:
    if not self._params.get_bool("LagdBackup"):
      return False

    live_delay_data = self._params.get("LiveDelay")
    if live_delay_data:
      self._params.put_nonblocking("LagdBackupData", live_delay_data)
      cloudlog.info("LiveDelay backup saved")
      return True
    return False

  def restore_lagd(self) -> tuple[float, int] | None:
    backup_data = self._params.get("LagdBackupData")
    if not backup_data:
      return None

    try:
      with log.Event.from_bytes(backup_data) as lag_msg:
        ld = lag_msg.liveDelay
        cloudlog.info(f"Restoring LiveDelay backup: delay={ld.lateralDelayEstimate:.3f}s, blocks={ld.validBlocks}")
        return ld.lateralDelayEstimate, ld.validBlocks
    except Exception as e:
      cloudlog.error(f"Failed to restore LiveDelay backup: {e}")
      self._params.remove("LagdBackupData")
    return None

  def get_initial_lag(self) -> tuple[float, int] | None:
    if not self._params.get_bool("LagdBackup"):
      return None
    return self.restore_lagd()
