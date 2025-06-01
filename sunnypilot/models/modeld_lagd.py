"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import car
import cereal.messaging as messaging
from openpilot.common.params import Params
from sunnypilot.modeld_v2.modeld import ModelState


class ModeldLagd:
  def __init__(self, CP : car.CarParams):
    self.params = Params()
    self.CP = CP

  def lagd_main(self, sm: messaging.SubMaster, model: ModelState):
    if self.params.get_bool("LagdToggle"):
      return sm["liveDelay"].lateralDelay + model.LAT_SMOOTH_SECONDS
    return self.CP.steerActuatorDelay + 0.2
