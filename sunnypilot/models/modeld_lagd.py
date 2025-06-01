"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class ModeldLagd:
  def __init__(self):
    self.params = Params()

  def lagd_main(self, CP, sm, model):
    if self.params.get_bool("LagdToggle"):
      lateral_delay = sm["liveDelay"].lateralDelay
      lat_smooth = model.LAT_SMOOTH_SECONDS
      result = lateral_delay + lat_smooth
      cloudlog.debug(f"LAGD USING LIVE DELAY: {lateral_delay:.3f} + {lat_smooth:.3f} = {result:.3f}")
      return result
    steer_actuator_delay = CP.steerActuatorDelay
    lat_smooth = model.LAT_SMOOTH_SECONDS
    result = (steer_actuator_delay + 0.2) + lat_smooth
    cloudlog.debug(f"LAGD USING STEER ACTUATOR: {steer_actuator_delay:.3f} + 0.2 + {lat_smooth:.3f} = {result:.3f}")
    return result
