import numpy as np
import pytest
from opendbc.car import structs
from openpilot.sunnypilot.selfdrive.car import interfaces as si


class FakeParams:
  def __init__(self, values=None):
    self.values = values or {}

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    return self.values.get(key)

  def remove(self, key):
    self.values.pop(key, None)


class FakeCI:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.configure_torque_tune_calls = 0

  def configure_torque_tune(self, fingerprint, tune):
    self.configure_torque_tune_calls += 1
    tune.init('torque')


def make_prius_tss2_cp():
  CP = structs.CarParams(carFingerprint='TOYOTA_PRIUS_TSS2', steerControlType=structs.CarParams.SteerControlType.torque)
  CP.lateralTuning.init('torque')
  return CP


class TestPriusTss2PidGate:
  def test_disabled_for_other_toyota_platforms(self):
    CP = structs.CarParams(carFingerprint='TOYOTA_RAV4_TSS2')
    assert si._enforce_prius_tss2_pid_lateral_control(CP, FakeParams({'ToyotaPriusTss2Pid': True})) is False

  def test_disabled_when_param_off(self):
    CP = make_prius_tss2_cp()
    assert si._enforce_prius_tss2_pid_lateral_control(CP, FakeParams({'ToyotaPriusTss2Pid': False})) is False

  def test_enabled_for_prius_tss2_with_param_on(self):
    CP = make_prius_tss2_cp()
    assert si._enforce_prius_tss2_pid_lateral_control(CP, FakeParams({'ToyotaPriusTss2Pid': True})) is True


class TestPriusTss2PidApply:
  def test_flips_union_and_sets_gains(self):
    CP = make_prius_tss2_cp()
    assert CP.lateralTuning.which() == 'torque'

    si._initialize_prius_tss2_pid_lateral_control(CP)

    assert CP.lateralTuning.which() == 'pid'
    assert list(CP.lateralTuning.pid.kpV) == pytest.approx(si._PRIUS_TSS2_PID_KP_V)
    assert list(CP.lateralTuning.pid.kiV) == pytest.approx(si._PRIUS_TSS2_PID_KI_V)
    assert CP.lateralTuning.pid.kf == pytest.approx(si._PRIUS_TSS2_PID_KF)
    # PIDController interp needs non-empty breakpoints matching V lists.
    assert len(CP.lateralTuning.pid.kpBP) == len(CP.lateralTuning.pid.kpV)
    assert len(CP.lateralTuning.pid.kiBP) == len(CP.lateralTuning.pid.kiV)

  def test_kp_rises_toward_highway_not_boosted_at_low_speed(self):
    """Real on-road data (route 550a71ee4c7a7fbe/00000549--01e8f2ab51) showed boosting kp below
    5 m/s increased saturation and hunting rather than helping - the shape must rise toward highway
    speed, matching every other real multi-breakpoint PID car's tune (GM Volt, Cadillac Escalade
    ESV, Honda Civic 2022) and the LatControlTorqueV0-derived KP_INTERP shape, not the reverse."""
    CP = make_prius_tss2_cp()
    si._initialize_prius_tss2_pid_lateral_control(CP)

    kp_parking_lot = np.interp(2.0, CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV)
    kp_cruise = np.interp(5.0, CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV)
    kp_highway = np.interp(30.0, CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV)
    assert kp_parking_lot < kp_cruise < kp_highway


class TestSetupInterfacesPrecedence:
  def test_pid_toggle_wins_over_nnlc_and_enforce_torque(self):
    """The Prius TSS2 PID toggle must be the last thing to touch lateralTuning: if the user also
    has NNLC and/or EnforceTorqueControl on, the union must still end up 'pid' and
    configure_torque_tune must never run, or the car would silently keep driving on torque."""
    CP = make_prius_tss2_cp()
    CP_SP = structs.CarParamsSP()
    CI = FakeCI(CP, CP_SP)
    params = FakeParams({
      'EnforceTorqueControl': True,
      'NeuralNetworkLateralControl': True,
      'ToyotaPriusTss2Pid': True,
    })

    si.setup_interfaces(CI, params)

    assert CP.lateralTuning.which() == 'pid'
    assert CI.configure_torque_tune_calls == 0

  def test_other_toyota_platform_unaffected_by_toggle(self):
    """The same param being on must not leak into a different car's tuning."""
    CP = structs.CarParams(carFingerprint='TOYOTA_RAV4_TSS2', steerControlType=structs.CarParams.SteerControlType.torque)
    CP.lateralTuning.init('torque')
    CP_SP = structs.CarParamsSP()
    CI = FakeCI(CP, CP_SP)
    params = FakeParams({'ToyotaPriusTss2Pid': True})

    si.setup_interfaces(CI, params)

    assert CP.lateralTuning.which() == 'torque'
    assert CI.configure_torque_tune_calls == 0

  def test_toggle_off_leaves_torque_control_path_intact(self):
    CP = make_prius_tss2_cp()
    CP_SP = structs.CarParamsSP()
    CI = FakeCI(CP, CP_SP)
    params = FakeParams({'EnforceTorqueControl': True, 'ToyotaPriusTss2Pid': False})

    si.setup_interfaces(CI, params)

    assert CP.lateralTuning.which() == 'torque'
    assert CI.configure_torque_tune_calls == 1
