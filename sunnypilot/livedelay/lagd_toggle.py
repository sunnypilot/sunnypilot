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
    self.software_delay = 0.2

  def lagd_main(self, CP, sm, model):
    if self.params.get_bool("LagdToggle"):
      lateral_delay = sm["liveDelay"].lateralDelay
      lat_smooth = model.LAT_SMOOTH_SECONDS
      result = lateral_delay + lat_smooth
      cloudlog.debug(f"MODELD USING LIVE DELAY: {lateral_delay:.3f} + {lat_smooth:.3f} = {result:.3f}")
      return result

    steer_actuator_delay = CP.steerActuatorDelay
    lat_smooth = model.LAT_SMOOTH_SECONDS
    delay = self.software_delay
    result = (steer_actuator_delay + delay) + lat_smooth
    cloudlog.debug(f"MODELD USING STEER ACTUATOR: {steer_actuator_delay:.3f} + {delay:.3f} + {lat_smooth:.3f} = {result:.3f}")
    return result

  def lagd_torqued_main(self, CP, msg):
    if self.params.get_bool("LagdToggle"):
      self.lag = msg.lateralDelay
      cloudlog.debug(f"TORQUED USING LIVE DELAY: {self.lag:.3f}")
    else:
      self.lag = CP.steerActuatorDelay + self.software_delay
      cloudlog.debug(f"TORQUED USING STEER ACTUATOR: {self.lag:.3f}")
    return self.lag
