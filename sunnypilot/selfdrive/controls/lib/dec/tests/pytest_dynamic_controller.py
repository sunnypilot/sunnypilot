import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants
from opendbc.car.hyundai.values import CAR

class MockLeadOne:
  def __init__(self, status=0.0, dRel=100.0, vRel=0.0, vLead=0.0):
    self.status = status
    self.dRel = dRel
    self.vRel = vRel
    self.vLead = vLead

class MockRadarState:
  def __init__(self, status=0.0, dRel=100.0, vRel=0.0):
    self.leadOne = MockLeadOne(status=status, dRel=dRel, vRel=vRel)

class MockCarState:
  def __init__(self, vEgo=0.0, vCruise=0.0, standstill=False):
    self.vEgo = vEgo
    self.vCruise = vCruise
    self.standstill = standstill

class MockModelData:
  def __init__(self, valid=True):
    size = 33 if valid else 10  # incomplete if invalid
    self.position = type("Pos", (), {"x": [100.0] * size})()
    self.orientation = type("Ori", (), {"x": [0.0] * size})()

class MockSelfDriveState:
  def __init__(self, experimentalMode=False):
    self.experimentalMode = experimentalMode

class MockParams:
  def __init__(self, **kwargs):
    self.params = {
      "DynamicExperimentalControl": True,
      "DynamicExperimentalStandstill": True,
      "DynamicExperimentalModelSlowDown": True,
      "DynamicExperimentalFCW": True,
      "DynamicExperimentalHasLead": True,
      "DynamicExperimentalSlowerLead": True,
      "DynamicExperimentalStoppedLead": True,
      "DynamicExperimentalDistanceBased": False,
      "DynamicExperimentalSpeedBased": False,
      "DynamicExperimentalFollowLead": False,
      **kwargs
    }

  def get_bool(self, name):
    return self.params.get(name, False)

  def get(self, name):
    return self.params.get(name, "50")

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
    carFingerprint = None
  return CP()

@pytest.fixture
def mock_mpc():
  class MPC:
    crash_cnt = 0
  return MPC()

# Fake SmoothKalmanFilter that returns a given value
class FakeSmoothKalman:
  def __init__(self, value=1.0):
    self.value = value
  def add_data(self, v): pass
  def get_value(self): return self.value
  def get_confidence(self): return 1.0
  def reset_data(self): pass

def test_initial_mode_is_acc(mock_cp, mock_mpc):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  assert controller.mode() == "acc"

def test_standstill_triggers_blended(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['carState'].standstill = True
  for _ in range(20):
    controller.update(default_sm)
  assert controller.mode() == "blended"

def test_emergency_blended_on_fcw(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  mock_mpc.crash_cnt = 1  # simulate FCW

  # Need a few updates for the smooth filter to respond to FCW
  for _ in range(3):
    controller.update(default_sm)
  assert controller.mode() == "blended"

def test_slowdown_triggers_blended(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'].leadOne.status = 0.0

  # Force high urgency slowdown condition by replacing the filter
  controller._slow_down_filter = FakeSmoothKalman(value=1.0)
  controller._urgency = 0.8
  controller._has_slow_down = True
  controller._has_lead_filtered = False

  controller.update(default_sm)
  assert controller.mode() == "blended"

def test_disabled_params_stay_acc(mock_cp, mock_mpc, default_sm):
  # All parameters disabled
  params = MockParams(
    DynamicExperimentalStandstill=False,
    DynamicExperimentalModelSlowDown=False,
    DynamicExperimentalFCW=False,
    DynamicExperimentalHasLead=False,
    DynamicExperimentalSlowerLead=False,
    DynamicExperimentalStoppedLead=False,
  )
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=params)

  # Even with standstill, should stay ACC since param is disabled
  default_sm['carState'].standstill = True
  mock_mpc.crash_cnt = 1

  for _ in range(20):
    controller.update(default_sm)

  assert controller.mode() == "acc"

def test_lead_distance_triggers_blended(mock_cp, mock_mpc, default_sm):
  params = MockParams(
    DynamicExperimentalDistanceBased=True,
    DynamicExperimentalDistanceValue="30"
  )
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=params)


  default_sm['radarState'].leadOne.dRel = 20.0
  default_sm['radarState'].leadOne.status = 1.0

  for _ in range(20):
    controller.update(default_sm)

  assert controller.mode() == "blended"

def test_lead_velocity_triggers_blended(mock_cp, mock_mpc, default_sm):
  params = MockParams(
    DynamicExperimentalHasLead=True
  )
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=params)

  # Set lead with negative relative velocity
  default_sm['radarState'].leadOne.vRel = -0.8
  default_sm['radarState'].leadOne.status = 1.0

  # Need multiple updates for lead filter to build up
  for _ in range(20):
    controller.update(default_sm)

  assert controller.mode() == "blended"

def test_stopped_lead_routing(mock_mpc, default_sm):
  params = MockParams(
    DynamicExperimentalHasLead=True,
    DynamicExperimentalSlowerLead=True,
    DynamicExperimentalStoppedLead=True,
  )

  def run_controller(controller, sm, vLead, vRel, dRel, expect_stopped, expect_slow=None):
    sm['radarState'].leadOne.vLead = vLead
    sm['radarState'].leadOne.vRel = vRel
    sm['radarState'].leadOne.dRel = dRel
    for _ in range(20):
      controller.update(sm)
    assert controller._has_stopped_lead is expect_stopped
    assert controller._has_stopped_lead_filtered is expect_stopped
    if expect_slow is not None:
      assert controller._has_slow_lead is expect_slow

  class CP:
    carFingerprint = None
  controller = DynamicExperimentalController(CP(), mock_mpc, params=params)
  sm = default_sm.copy()
  sm['radarState'].leadOne.status = 1.0

  run_controller(controller, sm, WMACConstants.SLOW_LEAD_STOPPED_THRESHOLD - 0.1, -1.0, 10.0, True)
  run_controller(controller, sm, WMACConstants.SLOW_LEAD_STOPPED_THRESHOLD + 0.1, -1.0, 10.0, False)
  run_controller(controller, sm, WMACConstants.SLOW_LEAD_STOPPED_THRESHOLD + 0.1, -2.0, 20, False, expect_slow=True)
  run_controller(controller, sm, WMACConstants.SLOW_LEAD_STOPPED_THRESHOLD + 0.1, -1.5, 20, False, expect_slow=False)

  class CP_PHEV:
    carFingerprint = CAR.KIA_NIRO_PHEV_2022
  controller_phev = DynamicExperimentalController(CP_PHEV(), mock_mpc, params=params)
  sm_phev = default_sm.copy()
  sm_phev['radarState'].leadOne.status = 1.0

  run_controller(controller_phev, sm_phev, 4.0, -1.0, 10.0, True)
  run_controller(controller_phev, sm_phev, 5.1, -1.0, 10.0, False)
