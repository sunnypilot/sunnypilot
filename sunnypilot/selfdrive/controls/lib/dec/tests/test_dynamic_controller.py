import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController, HysteresisSignal


class MockLeadOne:
  def __init__(self, status=0.0, dRel=30.0, vRel=0.0):
    self.status = status
    self.dRel = dRel
    self.vRel = vRel


class MockRadarState:
  def __init__(self, status=0.0, dRel=30.0, vRel=0.0):
    self.leadOne = MockLeadOne(status=status, dRel=dRel, vRel=vRel)


class MockCarState:
  def __init__(self, vEgo=0.0, vCruise=0.0, standstill=False):
    self.vEgo = vEgo
    self.vCruise = vCruise
    self.standstill = standstill


class MockAction:
  def __init__(self, desiredAcceleration=0.0, shouldStop=False):
    self.desiredAcceleration = desiredAcceleration
    self.shouldStop = shouldStop


class MockModelData:
  def __init__(self, valid=True, endpoint_x=200.0, orientation_valid=None, desired_acceleration=0.0, should_stop=False):
    position_size = 33 if valid else 10
    orientation_size = position_size if orientation_valid is None else (33 if orientation_valid else 10)
    position_x = [0.0] * position_size
    if position_x:
      position_x[-1] = endpoint_x
    self.position = type("Pos", (), {"x": position_x})()
    self.orientation = type("Ori", (), {"x": [0.0] * orientation_size})()
    self.acceleration = type("Accel", (), {"x": [0.0] * position_size})()
    self.action = MockAction(desired_acceleration, should_stop)


class MockSelfDriveState:
  def __init__(self, experimentalMode=False):
    self.experimentalMode = experimentalMode


class MockParams:
  def get_bool(self, name):
    return True


@pytest.fixture
def default_sm():
  sm = {
    'carState': MockCarState(vEgo=10.0, vCruise=20.0),
    'radarState': MockRadarState(status=1.0),
    'modelV2': MockModelData(valid=True),
    'selfdriveState': MockSelfDriveState(experimentalMode=True),
  }
  return sm


@pytest.fixture
def mock_cp():
  class CP:
    radarUnavailable = False
  return CP()


@pytest.fixture
def mock_mpc():
  class MPC:
    crash_cnt = 0
  return MPC()


def test_initial_mode_is_acc(mock_cp, mock_mpc):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  assert controller.mode() == "acc"


def test_standstill_triggers_blended(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['carState'].standstill = True
  for _ in range(20):
    controller.update(default_sm)
  assert controller.mode() == "blended"


def test_emergency_blended_on_fcw(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  mock_mpc.crash_cnt = 1
  controller.update(default_sm)
  assert controller.mode() == "blended"


def test_radarless_slowdown_triggers_blended(mock_cp, mock_mpc, default_sm):
  mock_cp.radarUnavailable = True
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  controller.update(default_sm)

  assert controller.mode() == "blended"


def test_valid_position_with_missing_orientation_can_trigger_slowdown(mock_cp, mock_mpc, default_sm):
  mock_cp.radarUnavailable = True
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0, orientation_valid=False)

  controller.update(default_sm)

  assert controller._trajectory_valid
  assert controller.mode() == "blended"


def test_incomplete_position_does_not_trigger_slowdown(mock_cp, mock_mpc, default_sm):
  mock_cp.radarUnavailable = True
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=False, endpoint_x=0.0)

  for _ in range(3):
    controller.update(default_sm)

  assert not controller._trajectory_valid
  assert not controller._has_slow_down
  assert controller.mode() == "acc"


def test_slowdown_hysteresis_prevents_threshold_chatter():
  signal = HysteresisSignal(enter_threshold=0.5, exit_threshold=0.4, rise_rate=1.0, fall_rate=1.0)

  assert signal.update(0.55)
  assert signal.update(0.45)
  assert not signal.update(0.35)


def test_model_should_stop_triggers_blended_without_valid_trajectory(mock_cp, mock_mpc, default_sm):
  mock_cp.radarUnavailable = True
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=False, should_stop=True)

  controller.update(default_sm)

  assert not controller._trajectory_valid
  assert controller.mode() == "blended"


def test_radar_lead_keeps_acc_over_model_slowdown(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  for _ in range(3):
    controller.update(default_sm)

  assert controller._has_slow_down
  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_far_radar_lead_allows_blended_until_acc_relevant(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, vRel=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  controller.update(default_sm)

  assert controller._has_lead_filtered
  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"


def test_relevant_radar_lead_smoothly_returns_to_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, vRel=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)
  assert controller.mode() == "blended"

  default_sm['radarState'] = MockRadarState(status=1.0, dRel=45.0, vRel=0.0)
  for _ in range(20):
    controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_closing_far_radar_lead_returns_to_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, vRel=-25.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  for _ in range(20):
    controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_radar_lead_keeps_acc_over_fcw_and_standstill(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0)
  default_sm['carState'].standstill = True
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0, should_stop=True)
  mock_mpc.crash_cnt = 1

  for _ in range(10):
    controller.update(default_sm)

  assert controller._has_lead_filtered
  assert controller._has_mpc_fcw
  assert controller.mode() == "acc"


def test_lead_flicker_hold_prevents_one_frame_mode_flip(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0)
  controller.update(default_sm)

  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert controller._has_lead_filtered
  assert controller.mode() == "acc"
