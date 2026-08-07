import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController, HysteresisSignal


class MockLeadOne:
  def __init__(self, status=0.0, dRel=30.0, vRel=0.0, radar=False, radarTrackId=-1):
    self.present = status
    self.dRel = dRel
    self.vRel = vRel
    self.radar = radar
    self.radarTrackId = radarTrackId


class MockRadarState:
  def __init__(self, status=0.0, dRel=30.0, vRel=0.0, radar=False, radarTrackId=-1, leadTwo=None):
    self.leadOne = MockLeadOne(status=status, dRel=dRel, vRel=vRel, radar=radar, radarTrackId=radarTrackId)
    self.leadTwo = leadTwo if leadTwo is not None else MockLeadOne()


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
    'radarState': MockRadarState(status=1.0, radar=True, radarTrackId=7),
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
    a_solution = [0.0, 0.0]
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


def test_confirmed_model_decel_trend_enters_blended_before_a_large_command(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)

  for desired_acceleration in (-0.02, -0.05, -0.08):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)
    assert controller.mode() == "acc"

  default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=-0.12)
  controller.update(default_sm, planner_accel=0.0)

  assert controller._model_decel_trending
  assert not controller._has_slow_down
  assert controller.mode() == "blended"


def test_confirmed_model_decel_handoff_stays_latched_through_a_plateau(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)

  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)

  for _ in range(WMACConstants.EMERGENCY_HOLD_FRAMES + WMACConstants.EXIT_BLENDED_FRAMES + 1):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=-0.12)
    controller.update(default_sm, planner_accel=0.0)

  assert not controller._model_decel_trending
  assert controller._model_decel_latched
  assert controller.mode() == "blended"

  for _ in range(WMACConstants.MODEL_DECEL_TREND_FRAMES + WMACConstants.EXIT_BLENDED_FRAMES):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=0.0)
    controller.update(default_sm, planner_accel=0.0)

  assert not controller._model_decel_latched
  assert controller.mode() == "acc"


def test_model_decel_trend_never_overrides_a_radar_lead(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())

  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm)

  assert not controller._model_accel_samples
  assert not controller._model_decel_latched
  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_radar_acquisition_clears_a_latched_model_decel_handoff(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)
  assert controller._model_decel_latched

  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  controller.update(default_sm, planner_accel=0.0)

  assert not controller._model_accel_samples
  assert not controller._model_decel_latched
  assert controller.mode() == "acc"


def test_model_decel_trend_does_not_accumulate_while_dec_is_inactive(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['selfdriveState'].experimentalMode = False
  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)

  assert not controller._model_accel_samples
  assert not controller._model_decel_latched

  default_sm['selfdriveState'].experimentalMode = True
  controller.update(default_sm, planner_accel=0.0)
  assert not controller._model_decel_trending
  assert controller.mode() == "acc"


def test_disabling_dec_clears_a_latched_model_decel_mode(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)
  assert controller._model_decel_latched
  assert controller.mode() == "blended"

  default_sm['selfdriveState'].experimentalMode = False
  default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=0.0)
  controller.update(default_sm, planner_accel=0.0)

  assert not controller._model_decel_latched
  assert controller.mode() == "acc"


def test_model_decel_trend_waits_while_mpc_is_accelerating(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  mock_mpc.a_solution[1] = 0.5

  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.0)

  assert controller._model_decel_trending
  assert controller.mode() == "acc"


def test_steep_model_decel_trend_defers_to_the_existing_urgent_path(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)

  for desired_acceleration in (0.0, -0.2, -0.4, -0.6):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.05)

  assert controller._model_decel_trending
  assert controller.mode() == "acc"


def test_model_decel_trend_waits_while_the_planner_is_accelerating(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)

  for desired_acceleration in (-0.02, -0.05, -0.08, -0.12):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm, planner_accel=0.2)

  assert controller._model_decel_trending
  assert controller.mode() == "acc"


def test_alternating_model_accel_noise_does_not_trigger_an_early_handoff(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)

  for desired_acceleration in (0.0, -0.2, 0.0, -0.2):
    default_sm['modelV2'] = MockModelData(valid=False, desired_acceleration=desired_acceleration)
    controller.update(default_sm)

  assert not controller._model_decel_trending
  assert controller.mode() == "acc"


def test_radar_lead_keeps_acc_over_model_slowdown(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  for _ in range(3):
    controller.update(default_sm)

  assert controller._has_slow_down
  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_far_radar_lead_always_uses_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, vRel=0.0, radar=True)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  controller.update(default_sm)

  assert controller._has_lead_filtered
  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_radar_acquisition_immediately_returns_blended_to_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)
  assert controller.mode() == "blended"

  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, radar=True, radarTrackId=7)
  controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"

  default_sm['radarState'] = MockRadarState(status=0.0)
  default_sm['modelV2'] = MockModelData(valid=True)
  for _ in range(20):
    controller.update(default_sm)
  assert controller.mode() == "acc"


def test_close_vision_only_lead_can_use_blended(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=30.0, vRel=-5.0)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"


def test_second_radar_lead_forces_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  lead_two = MockLeadOne(status=1.0, dRel=120.0, radar=True, radarTrackId=8)
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=30.0, vRel=-5.0, leadTwo=lead_two)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_second_vision_only_lead_does_not_force_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  lead_two = MockLeadOne(status=1.0, dRel=20.0, vRel=-10.0)
  default_sm['radarState'] = MockRadarState(status=0.0, leadTwo=lead_two)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"


def test_inactive_lead_with_radar_marker_does_not_force_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=0.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"


def test_radarless_car_ignores_marked_radar_track(mock_cp, mock_mpc, default_sm):
  mock_cp.radarUnavailable = True
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "blended"


def test_closing_far_radar_lead_returns_to_acc(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, dRel=120.0, vRel=-25.0, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  for _ in range(20):
    controller.update(default_sm)

  assert controller._has_radar_acc_lead
  assert controller.mode() == "acc"


def test_radar_lead_keeps_acc_over_fcw_and_standstill(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
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
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=50.0)
  for _ in range(2):
    controller.update(default_sm)
  assert controller._has_slow_down

  default_sm['radarState'] = MockRadarState(status=0.0)
  controller.update(default_sm)

  assert controller._has_lead_filtered
  assert controller.mode() == "acc"


def test_radar_lead_continuity_with_vision_fallback_expires_into_confirmed_transition(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=50.0)
  for _ in range(2):
    controller.update(default_sm)
  assert controller._has_slow_down

  default_sm['radarState'] = MockRadarState(status=1.0)
  for _ in range(WMACConstants.RADAR_LEAD_CONTINUITY_FRAMES):
    controller.update(default_sm)
    assert controller._has_radar_acc_lead
    assert controller.mode() == "acc"

  controller.update(default_sm)
  assert not controller._has_radar_acc_lead
  assert controller.mode() == "acc"

  for _ in range(WMACConstants.ENTER_BLENDED_FRAMES - 1):
    controller.update(default_sm)
  assert controller.mode() == "blended"


def test_radar_lead_short_dropout_guard_expires_without_any_lead(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  controller.update(default_sm)

  default_sm['radarState'] = MockRadarState(status=0.0)
  for _ in range(WMACConstants.RADAR_LEAD_DROPOUT_FRAMES):
    controller.update(default_sm)
    assert controller._has_radar_acc_lead

  controller.update(default_sm)
  assert not controller._has_radar_acc_lead


def test_one_stale_radar_frame_does_not_drop_acc_authority(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  controller.update(default_sm)

  controller.update(default_sm, radar_fresh=False)

  assert not controller._has_current_radar_acc_lead
  assert controller._has_radar_acc_lead
  assert controller._radar_acc_lead_frames == WMACConstants.RADAR_LEAD_CONTINUITY_FRAMES - 1
  assert controller._radar_stale_frames == 1
  assert controller.mode() == "acc"


def test_one_stale_radar_frame_does_not_override_retained_lead_for_model_urgency(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  controller.update(default_sm)
  default_sm['modelV2'] = MockModelData(valid=False, should_stop=True)

  controller.update(default_sm, radar_fresh=False)
  assert controller.mode() == "acc"

  controller.update(default_sm, radar_fresh=False)
  assert controller.mode() == "blended"


def test_one_stale_radar_frame_does_not_delay_fcw(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  controller.update(default_sm)
  mock_mpc.crash_cnt = 1

  controller.update(default_sm, radar_fresh=False)

  assert controller.mode() == "blended"


def test_frozen_radar_marker_cannot_rearm_acc_authority(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  controller.update(default_sm)

  for _ in range(WMACConstants.RADAR_STALE_FRAMES - 1):
    controller.update(default_sm, radar_fresh=False)
    assert controller._has_radar_acc_lead

  controller.update(default_sm, radar_fresh=False)

  assert not controller._has_current_radar_acc_lead
  assert not controller._has_radar_acc_lead
  assert not controller._has_any_lead
  assert not controller._has_lead_filtered


def test_fresh_radar_reacquisition_after_stale_timeout_is_immediate(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  controller.update(default_sm)
  for _ in range(WMACConstants.RADAR_STALE_FRAMES):
    controller.update(default_sm, radar_fresh=False)

  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm, radar_fresh=False)
  assert controller.mode() == "blended"

  lead_two = MockLeadOne(status=1.0, radar=True, radarTrackId=8)
  default_sm['radarState'] = MockRadarState(status=0.0, leadTwo=lead_two)
  controller.update(default_sm, radar_fresh=True)

  assert controller._radar_stale_frames == 0
  assert controller._has_current_radar_acc_lead
  assert controller.mode() == "acc"


@pytest.mark.parametrize("urgent_source", ["fcw", "should_stop"])
def test_no_lead_urgent_slowdown_bypasses_radar_dropout_guard(mock_cp, mock_mpc, default_sm, urgent_source):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  controller.update(default_sm)

  default_sm['radarState'] = MockRadarState(status=0.0)
  if urgent_source == "fcw":
    mock_mpc.crash_cnt = 1
  else:
    default_sm['modelV2'] = MockModelData(valid=False, should_stop=True)
  controller.update(default_sm)

  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"

  mock_mpc.crash_cnt = 0
  default_sm['modelV2'] = MockModelData(valid=True)
  controller.update(default_sm)
  assert controller.mode() == "blended"


def test_lead_two_radar_authority_continues_with_vision_lead_one(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  lead_two = MockLeadOne(status=1.0, radar=True, radarTrackId=8)
  default_sm['radarState'] = MockRadarState(status=0.0, leadTwo=lead_two)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)
  assert controller._has_current_radar_acc_lead
  assert controller.mode() == "acc"

  default_sm['radarState'] = MockRadarState(status=1.0)
  for _ in range(WMACConstants.RADAR_LEAD_CONTINUITY_FRAMES):
    controller.update(default_sm)
    assert controller._has_radar_acc_lead
    assert controller.mode() == "acc"


def test_alternating_radar_slots_keep_acc_authority(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)

  for frame in range(WMACConstants.RADAR_LEAD_CONTINUITY_FRAMES * 2):
    if frame % 2 == 0:
      default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7, leadTwo=MockLeadOne(status=1.0))
    else:
      default_sm['radarState'] = MockRadarState(status=1.0, leadTwo=MockLeadOne(status=1.0, radar=True, radarTrackId=8))
    controller.update(default_sm)

    assert controller._has_current_radar_acc_lead
    assert controller.mode() == "acc"


def test_radar_reacquisition_immediately_restores_acc_after_continuity_expiry(mock_cp, mock_mpc, default_sm):
  controller = DynamicExperimentalController(mock_cp, mock_mpc, params=MockParams())
  default_sm['radarState'] = MockRadarState(status=1.0, radar=True, radarTrackId=7)
  default_sm['modelV2'] = MockModelData(valid=True, endpoint_x=0.0)
  controller.update(default_sm)

  default_sm['radarState'] = MockRadarState(status=1.0)
  for _ in range(WMACConstants.RADAR_LEAD_CONTINUITY_FRAMES + 1):
    controller.update(default_sm)
  assert not controller._has_radar_acc_lead
  assert controller.mode() == "blended"

  lead_two = MockLeadOne(status=1.0, radar=True, radarTrackId=8)
  default_sm['radarState'] = MockRadarState(status=1.0, leadTwo=lead_two)
  controller.update(default_sm)

  assert controller._has_current_radar_acc_lead
  assert controller.mode() == "acc"
