"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

import cereal.messaging as messaging
from cereal import car

from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

RELAXED_MIN_BUCKET_POINTS = np.array([0, 200, 300, 500, 500, 300, 200, 0])

ALLOWED_CARS = ['toyota', 'hyundai', 'rivian', 'honda']



class TorqueEstimatorExt:
  def __init__(self, CP: car.CarParams):
    self.CP = CP
    self._params = Params()

    self.enforce_torque_control_toggle = self._params.get_bool("EnforceTorqueControl")
    self.use_params = False
    self.use_live_torque_params = False
    self.torque_override_enabled = False
    self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS
    self.factor_sanity = 0.0
    self.friction_sanity = 0.0
    self.offline_latAccelFactor = 0.0
    self.offline_friction = 0.0

  def initialize_custom_params(self, decimated=False):
    self.update_use_params()

    if self.enforce_torque_control_toggle:
      if self._params.get_bool("LiveTorqueParamsRelaxedToggle"):
        self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS / (10 if decimated else 1)
        self.factor_sanity = 0.5 if decimated else 1.0
        self.friction_sanity = 0.8 if decimated else 1.0

      if self._params.get_bool("CustomTorqueParams"):
        self.offline_latAccelFactor = float(self._params.get("TorqueParamsOverrideLatAccelFactor", return_default=True))
        self.offline_friction = float(self._params.get("TorqueParamsOverrideFriction", return_default=True))

  def update_params(self, sm: messaging.SubMaster):
    if sm.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.use_live_torque_params = self._params.get_bool("LiveTorqueParamsToggle")
      self.torque_override_enabled = self._params.get_bool("TorqueParamsOverrideEnabled")

  def update_use_params(self, sm: messaging.SubMaster):
    self.update_params(sm)

    if self.enforce_torque_control_toggle:
      if self.torque_override_enabled:
        self.use_params = False
      else:
        self.use_params = self.use_live_torque_params
    else:
      self.use_params = self.CP.brand in ALLOWED_CARS and self.CP.lateralTuning.which() == 'torque'
