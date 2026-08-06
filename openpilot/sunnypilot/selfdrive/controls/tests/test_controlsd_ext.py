from opendbc.car import structs

from openpilot.sunnypilot.selfdrive.controls import controlsd_ext
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_pid_ext import LatControlPidSmooth


class FakeParams:
  def __init__(self, values=None):
    self.values = values or {}

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def get(self, key, return_default=False):
    return self.values.get(key)


class FakeCI:
  def get_steer_feedforward_function(self):
    return lambda desired_angle, v_ego: desired_angle * (v_ego ** 2)


def make_ext(CP, params_values=None):
  # Bypass __init__: it blocks on CarParamsSP over messaging, which isn't available in a unit test.
  ext = controlsd_ext.ControlsExt.__new__(controlsd_ext.ControlsExt)
  ext.CP = CP
  ext.CP_SP = structs.CarParamsSP()
  ext.params = FakeParams(params_values)
  return ext


def make_prius_tss2_pid_cp():
  CP = structs.CarParams(carFingerprint='TOYOTA_PRIUS_TSS2')
  CP.lateralTuning.init('pid')
  CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV = [0.0, 5.0], [0.30, 0.15]
  CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV = [0.0], [0.05]
  CP.lateralTuning.pid.kf = 4e-05
  return CP


class TestInitializeLateralControlPidSmoothDispatch:
  """The Prius TSS2 PID toggle's decaying-integrator variant must be scoped to exactly the one
  (fingerprint, union) combination it applies to - never touch any other PID car's controller."""

  def test_prius_tss2_pid_gets_smooth_variant(self):
    ext = make_ext(make_prius_tss2_pid_cp())
    lac = object()

    result = ext.initialize_lateral_control(lac, FakeCI(), 0.01)

    assert isinstance(result, LatControlPidSmooth)

  def test_other_native_pid_car_is_untouched(self):
    """A hypothetical other brand's native PID car must NOT get swapped to our variant just
    because the union happens to be 'pid' - only our exact fingerprint qualifies."""
    CP = structs.CarParams(carFingerprint='SOME_OTHER_PID_CAR')
    CP.lateralTuning.init('pid')
    ext = make_ext(CP)
    lac = object()

    result = ext.initialize_lateral_control(lac, FakeCI(), 0.01)

    assert result is lac


class TestInitializeLateralControlPidGuard:
  """Regression test for the crash this toggle would otherwise cause: torque-only LatControl
  variants read CP.lateralTuning.torque directly, which raises on a capnp union that's actually
  'pid' (e.g. the Prius TSS2 PID toggle). initialize_lateral_control must never attempt that."""

  def test_pid_union_returns_lac_unchanged_even_with_enforce_torque_on(self):
    CP = structs.CarParams()
    CP.lateralTuning.init('pid')
    ext = make_ext(CP, {'EnforceTorqueControl': True, 'TorqueControlTune': 0.0})

    lac = object()
    result = ext.initialize_lateral_control(lac, CI=None, dt=0.01)

    assert result is lac

  def test_pid_union_returns_lac_unchanged_with_enforce_torque_off(self):
    CP = structs.CarParams()
    CP.lateralTuning.init('pid')
    ext = make_ext(CP, {'EnforceTorqueControl': False})

    lac = object()
    result = ext.initialize_lateral_control(lac, CI=None, dt=0.01)

    assert result is lac

  def test_torque_union_still_dispatches_to_torque_v0(self, monkeypatch):
    calls = []

    class StubTorqueV0:
      def __init__(self, CP, CP_SP, CI, dt):
        calls.append((CP, CP_SP, CI, dt))

    monkeypatch.setattr(controlsd_ext, 'LatControlTorqueV0', StubTorqueV0)

    CP = structs.CarParams()
    CP.lateralTuning.init('torque')
    ext = make_ext(CP, {'EnforceTorqueControl': False})
    ext.CP_SP = None

    lac = object()
    result = ext.initialize_lateral_control(lac, CI=None, dt=0.01)

    assert isinstance(result, StubTorqueV0)
    assert len(calls) == 1
