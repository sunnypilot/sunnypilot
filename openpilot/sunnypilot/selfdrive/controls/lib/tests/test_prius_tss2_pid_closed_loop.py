"""
Closed-loop smoke test for the Prius TSS2 PID lateral-control toggle's starting gains
(openpilot/sunnypilot/selfdrive/car/interfaces.py::_PRIUS_TSS2_PID_*).

IMPORTANT LIMITATION: there is no real Prius TSS2 EPS actuator model anywhere in this repo (unlike
the longitudinal plant model used by test_accel_controller_closed_loop.py, which was fit to logged
routes). The actuator here is a generic, uncalibrated 2nd-order lag (see `SurrogateEpsActuator`) —
it stands in for "some steering rack with plausible bandwidth," not this specific car's real EPS.

This test can only prove the starting gains are stable and roughly critically damped against that
generic surrogate. It CANNOT prove they are correctly tuned for a real Prius TSS2 — that requires
on-road A/B via tools/lateral_maneuvers (see its README) before trusting this tune on its own.

SCOPE: cruise-speed (20-30mph) only. The surrogate's steady-state gain is K = 1/(kf*v_ego**2) (see
`SurrogateEpsActuator`), which blows up as v_ego -> 0 and produces meaningless multi-hundred-degree
oscillation at parking-lot speed — an artifact of the surrogate, not of the kp/ki tune. This mirrors
a real constraint: angle*v_ego**2 feedforward (and this kf calibration) is explicitly a higher-speed
approximation (see the "25+mph" comment in latcontrol_torque_v0.py) — there's no valid basis here to
simulate the low-speed "sharp turn" boost in _PRIUS_TSS2_PID_KP_BP/_V at all. That boost is only
covered by the static shape check in test_prius_tss2_pid.py
(test_kp_is_boosted_below_integrator_freeze_speed) — it has NOT been closed-loop or on-road
verified. Validate it in a parking lot before trusting it anywhere faster.
"""
import math

import numpy as np
import pytest

from opendbc.car import DT_CTRL
from opendbc.car.car_helpers import interfaces as car_interfaces
from opendbc.car.vehicle_model import VehicleModel
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID
from openpilot.sunnypilot.selfdrive.car.interfaces import _initialize_prius_tss2_pid_lateral_control

MPH_TO_MS = 0.44704
DURATION_S = 6.0
STEADY_WINDOW_S = 1.0
TARGET_LAT_ACCEL = 1.5  # m/s^2, roughly a lateral_maneuvers "step" size


class FakeCarState:
  def __init__(self, v_ego):
    self.vEgo = v_ego
    self.steeringAngleDeg = 0.0
    self.steeringRateDeg = 0.0
    self.steeringPressed = False


class FakeLiveParams:
  roll = 0.0
  angleOffsetDeg = 0.0


class SurrogateEpsActuator:
  """Generic critically-damped 2nd-order torque->angle lag. NOT fit to any real car.

  The steady-state gain (deg per unit torque) is derived from the tune's own `kf`, i.e.
  K = 1 / (kf * v_ego**2) — the same steady-state relationship LatControlPID's feedforward term
  assumes (ff = kf * angle_deg * v_ego**2 ~= torque needed to hold that angle). A fixed, unrelated
  gain guess saturated the actuator well below the test's target angle at 20-30mph — this ties the
  surrogate to the one steady-state assumption already baked into the tune, so the test only
  exercises kp/ki dynamic response and stability, not an arbitrary extra unknown.
  """

  def __init__(self, deg_per_unit_torque, natural_freq_hz=3.0, zeta=1.0):
    self.wn = 2 * math.pi * natural_freq_hz
    self.zeta = zeta
    self.k = deg_per_unit_torque
    self.angle = 0.0
    self.rate = 0.0

  def step(self, torque, dt):
    accel = self.wn ** 2 * (self.k * torque - self.angle) - 2 * self.zeta * self.wn * self.rate
    self.rate += accel * dt
    self.angle += self.rate * dt
    return self.angle, self.rate


def run_closed_loop(CP, v_ego, target_lat_accel, duration_s=DURATION_S):
  VM = VehicleModel(CP)
  lac = LatControlPID(CP, structs_car_params_sp(), FakeCI(), DT_CTRL)
  deg_per_unit_torque = 1.0 / (CP.lateralTuning.pid.kf * v_ego ** 2)
  actuator = SurrogateEpsActuator(deg_per_unit_torque)
  CS = FakeCarState(v_ego)
  params = FakeLiveParams()

  desired_curvature = -target_lat_accel / v_ego ** 2
  desired_angle_deg = math.degrees(VM.get_steer_from_curvature(-desired_curvature, v_ego, 0.0))

  n_steps = int(duration_s / DT_CTRL)
  angle_trace = np.zeros(n_steps)
  torque_trace = np.zeros(n_steps)

  for i in range(n_steps):
    output_torque, _, _ = lac.update(True, CS, VM, params, False, desired_curvature, None, False, 0.0)
    output_torque = float(output_torque)
    angle, rate = actuator.step(output_torque, DT_CTRL)
    CS.steeringAngleDeg = float(angle)
    CS.steeringRateDeg = float(rate)
    angle_trace[i] = angle
    torque_trace[i] = output_torque

  return angle_trace, torque_trace, desired_angle_deg


def structs_car_params_sp():
  from opendbc.car import structs
  return structs.CarParamsSP()


class FakeCI:
  @staticmethod
  def get_steer_feedforward_function():
    return lambda desired_angle, v_ego: desired_angle * (v_ego ** 2)


def make_prius_tss2_cp():
  CarInterface = car_interfaces['TOYOTA_PRIUS_TSS2']
  CP = CarInterface.get_params('TOYOTA_PRIUS_TSS2', {0: {}, 1: {}, 2: {}}, [], alpha_long=False, is_release=False, docs=False)
  _initialize_prius_tss2_pid_lateral_control(CP)
  assert CP.lateralTuning.which() == 'pid'
  return CP


@pytest.mark.parametrize('v_mph', [20.0, 30.0])
def test_starting_gains_settle_without_diverging(v_mph):
  CP = make_prius_tss2_cp()
  v_ego = v_mph * MPH_TO_MS

  angle_trace, torque_trace, desired_angle_deg = run_closed_loop(CP, v_ego, TARGET_LAT_ACCEL)

  assert np.all(np.isfinite(angle_trace)), "diverged/NaN — unsafe to ever test on-road"
  assert np.all(np.abs(torque_trace) <= 1.0 + 1e-6), "output_torque exceeded steer_max=1.0 saturation bound"

  steady_n = int(STEADY_WINDOW_S / DT_CTRL)
  steady_angle = angle_trace[-steady_n:]
  settle_error_deg = abs(np.mean(steady_angle) - desired_angle_deg)
  oscillation_deg = np.ptp(steady_angle)

  assert settle_error_deg < 1.0, f"steady-state tracking error too large: {settle_error_deg:.3f} deg (target {desired_angle_deg:.2f} deg)"
  assert oscillation_deg < 0.5, f"sustained oscillation in tail window: {oscillation_deg:.3f} deg peak-to-peak (limit-cycle candidate)"


def test_gains_are_not_a_no_op_sanity_check():
  """Confirms this harness actually has teeth: gains far more aggressive than the shipped starting
  point produce a limit cycle against the same surrogate actuator, so the tolerances above aren't
  trivially satisfied by any input."""
  CP = make_prius_tss2_cp()
  CP.lateralTuning.pid.kpBP = [0.0]
  CP.lateralTuning.pid.kpV = [1.5]   # 10x the cruise-speed kp
  CP.lateralTuning.pid.kiBP = [0.0]
  CP.lateralTuning.pid.kiV = [0.5]   # 10x the shipped ki
  v_ego = 20.0 * MPH_TO_MS

  angle_trace, _, desired_angle_deg = run_closed_loop(CP, v_ego, TARGET_LAT_ACCEL)

  steady_n = int(STEADY_WINDOW_S / DT_CTRL)
  oscillation_deg = np.ptp(angle_trace[-steady_n:])
  assert oscillation_deg > 0.5, "expected an aggressive 10x-gain tune to visibly ring against this actuator; harness may not be sensitive"
