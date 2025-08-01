"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class LagdToggle:
  def __init__(self):
    self.params = Params()
    self.lag = 0.0
    self._last_desc = None

  @property
  def software_delay(self):
    return self.params.get("LagdToggleDelay")

  def _maybe_update_desc(self, desc):
    if desc != self._last_desc:
      self.params.put_nonblocking("LagdToggleDesc", desc)
      self._last_desc = desc

  def lagd_main(self, CP, sm, model):
    if self.params.get_bool("LagdToggle"):
      lateral_delay = sm["liveDelay"].lateralDelay
      lat_smooth = model.LAT_SMOOTH_SECONDS
      result = lateral_delay + lat_smooth
      desc = f"live steer delay learner ({lateral_delay:.3f}s) + model smoothing filter ({lat_smooth:.3f}s) = total delay ({result:.3f}s)"
      self._maybe_update_desc(desc)
      return result

    steer_actuator_delay = CP.steerActuatorDelay
    lat_smooth = model.LAT_SMOOTH_SECONDS
    delay = self.software_delay
    result = (steer_actuator_delay + delay) + lat_smooth
    desc = (f"Vehicle steering delay ({steer_actuator_delay:.3f}s) + software delay ({delay:.3f}s) + " +
            f"model smoothing filter ({lat_smooth:.3f}s) = total delay ({result:.3f}s)")
    self._maybe_update_desc(desc)
    return result

  def lagd_torqued_main(self, CP, msg):
    if self.params.get_bool("LagdToggle"):
      self.lag = msg.lateralDelay
      cloudlog.debug(f"TORQUED USING LIVE DELAY: {self.lag:.3f}")
    else:
      self.lag = CP.steerActuatorDelay + self.software_delay
      cloudlog.debug(f"TORQUED USING STEER ACTUATOR: {self.lag:.3f}")
    return self.lag
