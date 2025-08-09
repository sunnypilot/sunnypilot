"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import log

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.selfdrive.modeld.modeld import LAT_SMOOTH_SECONDS
from openpilot.sunnypilot.models.helpers import get_active_bundle


class LagdToggle:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.params = Params()
    self.lag = 0.0
    self._last_desc: str = ""

    modeld_bundle = get_active_bundle()
    if modeld_bundle:
      overrides = {override.key: override.value for override in modeld_bundle.overrides}
      self.LAT_SMOOTH_SECONDS = float(overrides.get('lat', ".0"))
    else:
      self.LAT_SMOOTH_SECONDS = LAT_SMOOTH_SECONDS

    self.lagd_toggle = self.params.get_bool("LagdToggle")
    self.software_delay = self.params.get("LagdToggleDelay")

  def read_params(self) -> None:
    self.lagd_toggle = self.params.get_bool("LagdToggle")
    self.software_delay = self.params.get("LagdToggleDelay")

  def _maybe_update_desc(self, desc: str) -> None:
    if desc != self._last_desc:
      self.params.put_nonblocking("LagdToggleDesc", desc)
      self._last_desc = desc

  def update(self, lag_msg: log.LiveDelayData) -> None:
    self.read_params()

    if not self.lagd_toggle:
      steer_actuator_delay = self.CP.steerActuatorDelay
      lat_smooth = self.LAT_SMOOTH_SECONDS
      delay = self.software_delay
      self.lag = (steer_actuator_delay + delay) + lat_smooth
      desc = (f"Vehicle steering delay ({steer_actuator_delay:.3f}s) + software delay ({delay:.3f}s) + " +
              f"model smoothing filter ({lat_smooth:.3f}s) = total delay ({self.lag:.3f}s)")
      self._maybe_update_desc(desc)
      self.params.put_nonblocking("LagdValueCache", self.lag)
      return

    lateral_delay = lag_msg.liveDelay.lateralDelay
    lat_smooth = self.LAT_SMOOTH_SECONDS
    self.lag = lateral_delay + lat_smooth
    desc = f"live steer delay learner ({lateral_delay:.3f}s) + model smoothing filter ({lat_smooth:.3f}s) = total delay ({self.lag:.3f}s)"
    self._maybe_update_desc(desc)
    self.params.put_nonblocking("LagdValueCache", self.lag)
