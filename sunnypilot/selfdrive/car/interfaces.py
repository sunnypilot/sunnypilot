"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from typing import Any

from opendbc.car import structs
from opendbc.car.interfaces import CarInterfaceBase
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import get_nn_model_path

import openpilot.system.sentry as sentry


def log_fingerprint(CP: structs.CarParams) -> None:
  if CP.carFingerprint == "MOCK":
    sentry.capture_fingerprint_mock()
  else:
    sentry.capture_fingerprint(CP.carFingerprint, CP.brand)


def _initialize_neural_network_lateral_control(CI: CarInterfaceBase, CP: structs.CarParams, CP_SP: structs.CarParamsSP,
                                               params: Params = None, enabled: bool = False) -> None:
  if params is None:
    params = Params()

  nnlc_model_path, nnlc_model_name, exact_match = get_nn_model_path(CP)

  if nnlc_model_name == "MOCK":
    cloudlog.error({"nnlc event": "car doesn't match any Neural Network model"})

  if nnlc_model_name != "MOCK" and CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("NeuralNetworkLateralControl")

  if enabled:
    CI.configure_torque_tune(CP.carFingerprint, CP.lateralTuning)

  CP_SP.neuralNetworkLateralControl.model.path = nnlc_model_path
  CP_SP.neuralNetworkLateralControl.model.name = nnlc_model_name
  CP_SP.neuralNetworkLateralControl.fuzzyFingerprint = not exact_match


def setup_interfaces(CI: CarInterfaceBase, params: Params = None) -> None:
  CP = CI.CP
  CP_SP = CI.CP_SP

  _initialize_neural_network_lateral_control(CI, CP, CP_SP, params)


def initialize_params(params) -> list[dict[str, Any]]:
  keys: list = []

  # hyundai
  keys.extend([
    "HyundaiLongitudinalTuning"
  ])

  return [{k: params.get(k, return_default=True)} for k in keys]
