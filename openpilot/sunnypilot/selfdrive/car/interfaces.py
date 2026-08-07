"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from typing import Any

from opendbc.car import structs
from opendbc.car.interfaces import CarInterfaceBase
from opendbc.car.toyota.values import CAR as TOYOTA_CAR
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import get_nn_model_path
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers import set_speed_limit_assist_availability

import openpilot.system.sentry as sentry

from openpilot.sunnypilot.sunnylink.statsd import STATSLOGSP


def log_fingerprint(CP: structs.CarParams) -> None:
  if CP.carFingerprint == "MOCK":
    sentry.capture_fingerprint_mock()
  else:
    sentry.capture_fingerprint(CP.carFingerprint, CP.brand)


def _enforce_torque_lateral_control(CP: structs.CarParams, params: Params = None, enabled: bool = False) -> bool:
  if params is None:
    params = Params()

  if CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("EnforceTorqueControl")

  return enabled


def _initialize_neural_network_lateral_control(CP: structs.CarParams, CP_SP: structs.CarParamsSP,
                                               params: Params = None, enabled: bool = False) -> bool:
  if params is None:
    params = Params()

  nnlc_model_path, nnlc_model_name, exact_match = get_nn_model_path(CP)

  if nnlc_model_name == "MOCK":
    cloudlog.error({"nnlc event": "car doesn't match any Neural Network model"})

  if nnlc_model_name != "MOCK" and CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("NeuralNetworkLateralControl")

  CP_SP.neuralNetworkLateralControl.model.path = nnlc_model_path
  CP_SP.neuralNetworkLateralControl.model.name = nnlc_model_name
  CP_SP.neuralNetworkLateralControl.fuzzyFingerprint = not exact_match

  return enabled


def _initialize_intelligent_cruise_button_management(CP: structs.CarParams, CP_SP: structs.CarParamsSP, params: Params = None) -> None:
  if params is None:
    params = Params()

  icbm_enabled = params.get_bool("IntelligentCruiseButtonManagement")
  if icbm_enabled and CP_SP.intelligentCruiseButtonManagementAvailable and not CP.openpilotLongitudinalControl:
    CP_SP.pcmCruiseSpeed = False


def _initialize_torque_lateral_control(CI: CarInterfaceBase, CP: structs.CarParams, enforce_torque: bool, nnlc_enabled: bool) -> None:
  if nnlc_enabled or enforce_torque:
    CI.configure_torque_tune(CP.carFingerprint, CP.lateralTuning)


_PRIUS_TSS2_PID_KP_BP = [1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 30.0]
_PRIUS_TSS2_PID_KI_BP = [1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 30.0]
_PRIUS_TSS2_PID_KP_V = [0.1304, 0.1409, 0.1357, 0.1409, 0.15, 0.1614, 0.1826, 0.2348, 0.4696]
_PRIUS_TSS2_PID_KI_V = [0.00016, 0.00035, 0.00063, 0.00141, 0.00391, 0.0088, 0.01565, 0.03522, 0.14087]
_PRIUS_TSS2_PID_KF = 4e-05


def _enforce_prius_tss2_pid_lateral_control(CP: structs.CarParams, params: Params = None) -> bool:
  if params is None:
    params = Params()

  if CP.carFingerprint != TOYOTA_CAR.TOYOTA_PRIUS_TSS2:
    return False

  return params.get_bool("ToyotaPriusTss2Pid")


def _initialize_prius_tss2_pid_lateral_control(CP: structs.CarParams) -> None:
  CP.lateralTuning.init('pid')
  CP.lateralTuning.pid.kpBP = _PRIUS_TSS2_PID_KP_BP
  CP.lateralTuning.pid.kpV = _PRIUS_TSS2_PID_KP_V
  CP.lateralTuning.pid.kiBP = _PRIUS_TSS2_PID_KI_BP
  CP.lateralTuning.pid.kiV = _PRIUS_TSS2_PID_KI_V
  CP.lateralTuning.pid.kf = _PRIUS_TSS2_PID_KF


def _cleanup_unsupported_params(CP: structs.CarParams, CP_SP: structs.CarParamsSP, params: Params = None) -> None:
  if params is None:
    params = Params()

  if CP.steerControlType == structs.CarParams.SteerControlType.angle:
    cloudlog.warning("SteerControlType is angle, cleaning up params")
    params.remove("NeuralNetworkLateralControl")
    params.remove("EnforceTorqueControl")

  if not CP_SP.intelligentCruiseButtonManagementAvailable or CP.openpilotLongitudinalControl:
    cloudlog.warning("ICBM not available or openpilot Longitudinal Control enabled, cleaning up params")
    params.remove("IntelligentCruiseButtonManagement")

  if not CP.openpilotLongitudinalControl and CP_SP.pcmCruiseSpeed:
    cloudlog.warning("openpilot Longitudinal Control and ICBM not available, cleaning up params")
    params.remove("DynamicExperimentalControl")
    params.remove("CustomAccIncrementsEnabled")
    params.remove("SmartCruiseControlVision")
    params.remove("SmartCruiseControlMap")

  set_speed_limit_assist_availability(CP, CP_SP, params)


def setup_interfaces(CI: CarInterfaceBase, params: Params = None) -> None:
  enforce_torque = _enforce_torque_lateral_control(CI.CP, params)
  nnlc_enabled = _initialize_neural_network_lateral_control(CI.CP, CI.CP_SP, params)
  prius_tss2_pid_enabled = _enforce_prius_tss2_pid_lateral_control(CI.CP, params)
  if prius_tss2_pid_enabled:
    # Prius TSS2 PID toggle takes priority over NNLC/EnforceTorqueControl for this car.
    enforce_torque = False
    nnlc_enabled = False
  _initialize_intelligent_cruise_button_management(CI.CP, CI.CP_SP, params)
  _initialize_torque_lateral_control(CI, CI.CP, enforce_torque, nnlc_enabled)
  if prius_tss2_pid_enabled:
    _initialize_prius_tss2_pid_lateral_control(CI.CP)
  _cleanup_unsupported_params(CI.CP, CI.CP_SP)

  try:
    STATSLOGSP.raw('sunnypilot.car_params', CI.CP.to_dict())
  except RuntimeError:
    pass  # to_dict fails on macOS due to library issues.
  # STATSLOGSP.raw('sunnypilot_params.car_params_sp', CP_SP.to_dict()) # https://github.com/sunnypilot/opendbc/pull/361


def initialize_params(params) -> list[dict[str, Any]]:
  keys: list = []

  # hyundai
  keys.extend([
    "HyundaiLongitudinalTuning",
  ])

  # subaru
  keys.extend([
    "SubaruStopAndGo",
    "SubaruStopAndGoManualParkingBrake",
  ])

  # tesla
  keys.extend([
    "TeslaCoopSteering",
    "TeslaMadsScreenButton",
  ])

  # toyota
  keys.extend([
    "ToyotaEnforceStockLongitudinal",
    "ToyotaStopAndGoHack",
    "ToyotaEnhancedBsm",
    "ToyotaAutoHold",
    "ToyotaPriusTss2Pid",
  ])

  return [{k: params.get(k, return_default=True)} for k in keys]
