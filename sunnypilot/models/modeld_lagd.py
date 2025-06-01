"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params


class ModeldLagd:
  def __init__(self):
    self.params = Params()

  def lagd_main(self, CP, sm, model):
    if self.params.get_bool("LagdToggle"):
      return sm["liveDelay"].lateralDelay + model.LAT_SMOOTH_SECONDS
    return CP.steerActuatorDelay + 0.2
