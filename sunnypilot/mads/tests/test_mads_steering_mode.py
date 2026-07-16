"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pytest

from cereal import log, custom
from opendbc.car import structs
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.mads.helpers import MadsSteeringModeOnBrake, read_steering_mode_param
from openpilot.sunnypilot.mads.mads import ModularAssistiveDrivingSystem
from opendbc.sunnypilot.car.tesla.values import TeslaFlagsSP

State = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState
EventName = log.OnroadEvent.EventName
EventNameSP = custom.OnroadEventSP.EventName
SafetyModel = structs.CarParams.SafetyModel


def make_car_state(brake_pressed=False, regen_braking=False, standstill=False, v_ego=0.0):
  cs = structs.CarState()
  cs.brakePressed = brake_pressed
  cs.regenBraking = regen_braking
  cs.standstill = standstill
  cs.vEgo = v_ego
  cs.cruiseState.available = True
  return cs


def make_panda_state(mocker, controls_allowed_lateral=True):
  ps = mocker.MagicMock()
  ps.controlsAllowedLateral = controls_allowed_lateral
  ps.safetyModel = SafetyModel.hyundai
  return ps


def make_mads(mocker, steering_mode):
  sd = mocker.MagicMock()
  sd.CP = structs.CarParams()
  sd.CP.brand = "hyundai"
  sd.CP_SP = structs.CarParamsSP()
  sd.params = mocker.MagicMock()
  sd.params.get_bool = mocker.MagicMock(side_effect=lambda k: {
    "Mads": True, "MadsMainCruiseAllowed": False,
    "DisengageOnAccelerator": True, "MadsUnifiedEngagementMode": False,
  }.get(k, False))
  sd.params.get = mocker.MagicMock(return_value=steering_mode)
  sd.events = Events()
  sd.events_sp = EventsSP()
  sd.enabled = False
  sd.enabled_prev = False
  sd.initialized = True
  sd.CS_prev = make_car_state()
  sd.sm = {'pandaStates': [make_panda_state(mocker)]}
  sd.state_machine = mocker.MagicMock()

  mads = ModularAssistiveDrivingSystem(sd)
  mads.enabled_toggle = True
  mads.steering_mode_on_brake = steering_mode
  return mads, sd


def run_frames(mads, sd, cs, n=1):
  for _ in range(n):
    mads.update(cs)
    sd.CS_prev = cs
    sd.events.clear()
    sd.events_sp.clear()


# should_silent_lkas_enable across all modes

class TestShouldSilentLkasEnable:
  @pytest.mark.parametrize("brake,regen", [(True, False), (False, True)])
  def test_pause_blocks_reenable_on_braking_at_standstill(self, mocker, brake, regen):
    mads, _ = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    cs = make_car_state(brake_pressed=brake, regen_braking=regen, standstill=True)
    assert mads.should_silent_lkas_enable(cs) is False

  def test_pause_allows_reenable_on_brake_release(self, mocker):
    mads, _ = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    cs = make_car_state(standstill=True)
    assert mads.should_silent_lkas_enable(cs) is True

  def test_remain_active_ignores_brake(self, mocker):
    mads, _ = make_mads(mocker, MadsSteeringModeOnBrake.REMAIN_ACTIVE)
    cs = make_car_state(brake_pressed=True, standstill=True)
    assert mads.should_silent_lkas_enable(cs) is True

  def test_disengage_ignores_brake_for_silent_enable(self, mocker):
    mads, _ = make_mads(mocker, MadsSteeringModeOnBrake.DISENGAGE)
    cs = make_car_state(brake_pressed=True, standstill=True)
    assert mads.should_silent_lkas_enable(cs) is True


# pause

class TestPauseMode:
  def test_stays_paused_at_standstill_brake_held(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    mads.state_machine.state = State.enabled
    mads.enabled = True
    mads.active = True

    sd.events.add(EventName.pedalPressed)
    run_frames(mads, sd, make_car_state(brake_pressed=True, v_ego=15.0))
    assert mads.state_machine.state == State.paused

    sd.sm['pandaStates'] = [make_panda_state(mocker, False)]
    run_frames(mads, sd, make_car_state(brake_pressed=True, standstill=True), n=250)
    assert mads.state_machine.state == State.paused

  def test_resumes_on_brake_release_at_standstill(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    mads.state_machine.state = State.paused
    mads.enabled = True
    mads.active = False

    run_frames(mads, sd, make_car_state(standstill=True))
    assert mads.state_machine.state == State.enabled

  def test_full_cycle_moving_to_standstill(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    mads.state_machine.state = State.enabled
    mads.enabled = True
    mads.active = True

    sd.events.add(EventName.pedalPressed)
    run_frames(mads, sd, make_car_state(brake_pressed=True, v_ego=15.0))
    assert mads.state_machine.state == State.paused

    sd.sm['pandaStates'] = [make_panda_state(mocker, False)]
    run_frames(mads, sd, make_car_state(brake_pressed=True, standstill=True), n=250)
    assert mads.state_machine.state == State.paused

    sd.sm['pandaStates'] = [make_panda_state(mocker, True)]
    run_frames(mads, sd, make_car_state(standstill=True))
    assert mads.state_machine.state == State.enabled


# disengage

class TestDisengageMode:
  def test_brake_while_enabled_disables(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.DISENGAGE)
    mads.state_machine.state = State.enabled
    mads.enabled = True
    mads.active = True

    sd.events.add(EventName.pedalPressed)
    run_frames(mads, sd, make_car_state(brake_pressed=True, v_ego=10.0))
    assert mads.state_machine.state == State.disabled

  def test_brake_sends_lkas_disable_when_enabled(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.DISENGAGE)
    mads.state_machine.state = State.enabled
    mads.enabled = True
    mads.active = True

    sd.events.add(EventName.pedalPressed)
    mads.update_events(make_car_state(brake_pressed=True, v_ego=5.0))
    assert sd.events_sp.has(EventNameSP.lkasDisable)


# remain active

class TestRemainActiveMode:
  def test_brake_does_not_pause_or_disable(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.REMAIN_ACTIVE)
    mads.state_machine.state = State.enabled
    mads.enabled = True
    mads.active = True

    sd.events.add(EventName.pedalPressed)
    run_frames(mads, sd, make_car_state(brake_pressed=True, v_ego=10.0))
    assert mads.state_machine.state == State.enabled


# lateral mismatch counter

class TestLateralMismatchCounter:
  def test_no_accumulation_while_paused(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    mads.state_machine.state = State.paused
    mads.enabled = True
    mads.active = False
    sd.sm['pandaStates'] = [make_panda_state(mocker, False)]

    run_frames(mads, sd, make_car_state(brake_pressed=True, standstill=True), n=250)
    assert mads.lateral_mismatch_counter == 0

  def test_accumulates_when_active_and_panda_disagrees(self, mocker):
    mads, sd = make_mads(mocker, MadsSteeringModeOnBrake.PAUSE)
    mads.enabled = True
    mads.active = True
    sd.sm['pandaStates'] = [make_panda_state(mocker, False)]

    for _ in range(200):
      mads.data_sample()
    assert mads.lateral_mismatch_counter == 200


# brand restrictions

class TestBrandSteeringModeRestrictions:
  def test_rivian_forced_to_disengage(self, mocker):
    CP = structs.CarParams()
    CP.brand = "rivian"
    CP_SP = structs.CarParamsSP()
    params = mocker.MagicMock()
    assert read_steering_mode_param(CP, CP_SP, params) == MadsSteeringModeOnBrake.DISENGAGE
    params.get.assert_not_called()

  def test_tesla_without_vehicle_bus_forced_to_disengage(self, mocker):
    CP = structs.CarParams()
    CP.brand = "tesla"
    CP_SP = structs.CarParamsSP()
    CP_SP.flags = 0
    params = mocker.MagicMock()
    assert read_steering_mode_param(CP, CP_SP, params) == MadsSteeringModeOnBrake.DISENGAGE

  def test_tesla_with_vehicle_bus_uses_param(self, mocker):
    CP = structs.CarParams()
    CP.brand = "tesla"
    CP_SP = structs.CarParamsSP()
    CP_SP.flags = TeslaFlagsSP.HAS_VEHICLE_BUS
    params = mocker.MagicMock()
    params.get = mocker.MagicMock(return_value=MadsSteeringModeOnBrake.REMAIN_ACTIVE)
    assert read_steering_mode_param(CP, CP_SP, params) == MadsSteeringModeOnBrake.REMAIN_ACTIVE

  @pytest.mark.parametrize("brand", ["hyundai", "toyota", "honda", "gm"])
  def test_other_brands_use_param(self, mocker, brand):
    CP = structs.CarParams()
    CP.brand = brand
    CP_SP = structs.CarParamsSP()
    params = mocker.MagicMock()
    params.get = mocker.MagicMock(return_value=MadsSteeringModeOnBrake.REMAIN_ACTIVE)
    assert read_steering_mode_param(CP, CP_SP, params) == MadsSteeringModeOnBrake.REMAIN_ACTIVE
