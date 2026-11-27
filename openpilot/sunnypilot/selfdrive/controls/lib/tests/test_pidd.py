"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.car_helpers import interfaces
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.interfaces import get_torque_params
from opendbc.car.nissan.values import CAR as NISSAN
from opendbc.car.structs import car
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.vehicle_model import VehicleModel
from openpilot.cereal import log
from openpilot.common.mock.generators import generate_deviceMotion
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.locationd.helpers import Pose
from openpilot.selfdrive.locationd.torqued import TorqueEstimator
from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces
from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import ControlsExt
from openpilot.sunnypilot.selfdrive.controls.lib.pidd import LatControlPidd, PIDD_VERSION


def setup_car(car_name):
  CarInterface = interfaces[car_name]
  CP = CarInterface.get_non_essential_params(car_name)
  CP_SP = CarInterface.get_non_essential_params_sp(CP, car_name)
  CI = CarInterface(CP, CP_SP)
  sunnypilot_interfaces.setup_interfaces(CI)
  return CI


def make_controller(CI):
  return LatControlPidd(CI.CP.as_reader(), convert_to_capnp(CI.CP_SP).as_reader(), CI, DT_CTRL)


def drive(controller, CS, VM, angles, curvature=0.0):
  params = log.VehicleParameters.new_message()
  pose = Pose.from_device_motion(generate_deviceMotion().deviceMotion)
  return [controller.update(True, CS, VM, params, False, curvature, pose, False, 0.2)[0] for CS.steeringAngleDeg in angles]


class TestPidd(OpenpilotTestCase):
  def setup_method(self):
    self.params = Params()
    self.params.put_bool("EnforceTorqueControl", True, block=True)
    self.params.put("TorqueControlTune", PIDD_VERSION, block=True)

  def test_selected_on_any_torque_car(self):
    for car_name in (HONDA.HONDA_CIVIC, TOYOTA.TOYOTA_RAV4, HYUNDAI.KIA_NIRO_EV):
      assert setup_car(car_name).CP.lateralTuning.which() == 'pid'

  def test_needs_enforce_torque(self):
    self.params.remove("EnforceTorqueControl")
    assert setup_car(HYUNDAI.KIA_NIRO_EV).CP.lateralTuning.which() == 'torque'

  def test_not_on_angle_cars(self):
    CI = setup_car(NISSAN.NISSAN_LEAF)
    assert CI.CP.steerControlType == car.CarParams.SteerControlType.angle
    assert not self.params.get_bool("EnforceTorqueControl")

  def test_controlsd_builds_it(self):
    CI = setup_car(HYUNDAI.KIA_NIRO_EV)
    ext = SimpleNamespace(params=self.params, CP=CI.CP.as_reader(), CP_SP=convert_to_capnp(CI.CP_SP).as_reader())
    assert isinstance(ControlsExt.initialize_lateral_control(ext, None, CI, DT_CTRL), LatControlPidd)

  def test_selection_follows_car_params(self):
    # params changing after card picked pidd must not leave controlsd with a pid that has no gains
    CI = setup_car(HYUNDAI.KIA_NIRO_EV)
    self.params.remove("EnforceTorqueControl")
    self.params.put("TorqueControlTune", 1.0, block=True)
    ext = SimpleNamespace(params=self.params, CP=CI.CP.as_reader(), CP_SP=convert_to_capnp(CI.CP_SP).as_reader())
    assert isinstance(ControlsExt.initialize_lateral_control(ext, None, CI, DT_CTRL), LatControlPidd)

  def test_damps_wheel_swing(self):
    CI = setup_car(HONDA.HONDA_CIVIC)
    VM = VehicleModel(CI.CP)
    corr = {}
    for pressed in (False, True):
      controller = make_controller(CI)
      CS = car.CarState.new_message(vEgo=8.0, steeringPressed=pressed)
      angles = [2.0 * math.sin(2 * math.pi * 2.0 * i * DT_CTRL) for i in range(300)]
      out = drive(controller, CS, VM, angles)[100:]
      rate = [math.cos(2 * math.pi * 2.0 * i * DT_CTRL) for i in range(100, 300)]
      corr[pressed] = float(np.corrcoef(out, rate)[0, 1])
    assert corr[False] < corr[True] - 0.3

  def test_output_within_steer_max(self):
    CI = setup_car(HYUNDAI.KIA_NIRO_EV)
    controller = make_controller(CI)
    controller.pid.update = lambda *args, **kwargs: controller.steer_max
    CS = car.CarState.new_message(vEgo=8.0)
    out = drive(controller, CS, VehicleModel(CI.CP), [2.0 * math.sin(2 * math.pi * 2.5 * i * DT_CTRL) for i in range(500)])
    assert max(abs(x) for x in out) <= controller.steer_max

  def test_reset_clears_swing_gate(self):
    CI = setup_car(HYUNDAI.KIA_NIRO_EV)
    controller = make_controller(CI)
    drive(controller, car.CarState.new_message(vEgo=8.0), VehicleModel(CI.CP), [30.0] * 200, curvature=-0.02)
    controller.reset()
    assert not controller.command_slow.initialized

  def test_live_torque_params_rescale_gains(self):
    controller = make_controller(setup_car(HYUNDAI.KIA_NIRO_EV))
    kp = list(controller.kp)
    controller.update_torque_parameters(2 * controller.lat_accel_factor, 0.0, controller.friction)
    assert np.allclose(controller.kp, [k / 2 for k in kp])
    assert np.allclose(controller.pid._k_p[1], controller.kp)
    controller.update_torque_parameters(0.5 * controller.offline_lat_accel_factor, 0.0, 0.0)
    assert np.allclose(controller.kp, kp)

  def test_torqued_learns_under_pidd(self):
    estimator = TorqueEstimator(setup_car(HYUNDAI.KIA_NIRO_EV).CP.as_reader())
    offline = get_torque_params()[HYUNDAI.KIA_NIRO_EV]
    assert estimator.offline_latAccelFactor == pytest.approx(offline['LAT_ACCEL_FACTOR'])
    assert estimator.offline_friction == pytest.approx(offline['FRICTION'])
    assert estimator.max_lataccel_factor > estimator.min_lataccel_factor
