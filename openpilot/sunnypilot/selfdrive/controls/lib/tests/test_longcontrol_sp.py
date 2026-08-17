import numpy as np
from unittest import mock

from opendbc.car import DT_CTRL, gen_empty_fingerprint, structs
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from opendbc.car.body.values import CAR as BODY
from opendbc.car.car_helpers import interfaces
from opendbc.car.ford.values import CAR as FORD
from opendbc.car.gm.values import CAR as GM
from opendbc.car.honda.values import CAR as HONDA
from opendbc.car.hyundai.values import CAR as HYUNDAI
from opendbc.car.rivian.values import CAR as RIVIAN
from opendbc.car.subaru.values import CAR as SUBARU
from opendbc.car.tesla.values import CAR as TESLA
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.volkswagen.values import CAR as VOLKSWAGEN
from openpilot.selfdrive.controls.lib.drive_helpers import should_stop
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState
from openpilot.sunnypilot.selfdrive.controls.lib.longcontrol import (
  STOPPING_HOLD_ACCEL, STOPPING_HOLD_MARGIN, STOPPING_SETTLE_FRAMES, STOPPING_SPEED_TOLERANCE,
)
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PRIUS_TSS2_ROUTE_MODEL, PlantSP


PRESERVED_HOLD_VEHICLES = (
  FORD.FORD_ESCAPE_MK4,
  GM.CHEVROLET_VOLT,
  GM.CHEVROLET_BOLT_EUV,
  HONDA.HONDA_CIVIC_2022,
  HYUNDAI.HYUNDAI_SONATA,
  SUBARU.SUBARU_ASCENT,
  TESLA.TESLA_MODEL_3,
  TOYOTA.TOYOTA_RAV4_TSS2,
  VOLKSWAGEN.VOLKSWAGEN_ARTEON_MK1,
)
STOP_ACCEL_VEHICLES = (*PRESERVED_HOLD_VEHICLES, RIVIAN.RIVIAN_R1)
SETTLE_VEHICLES = (TOYOTA.TOYOTA_RAV4_TSS2, HONDA.HONDA_CIVIC_2022, VOLKSWAGEN.VOLKSWAGEN_ARTEON_MK1)
UNSUPPORTED_HOLD_VEHICLES = (
  (BODY.COMMA_BODY, True),
  (SUBARU.SUBARU_OUTBACK, True),
  (HYUNDAI.HYUNDAI_SONATA, False),
  (RIVIAN.RIVIAN_R1, True),
)
ROUTE_STOP_ONSETS = (
  (0.280, -0.290, -0.220, -0.220),
  (0.290, -0.497, -0.270, -0.302),
  (0.464, -0.223, -0.264, -0.292),
  (0.467, -0.582, -0.316, -0.359),
  (0.530, -0.311, -0.309, -0.333),
  (0.581, -0.467, -0.312, -0.352),
  (0.398, -0.557, -0.311, -0.348),
  (0.517, -0.290, -0.301, -0.327),
  (0.312, -0.420, -0.271, -0.304),
  (0.474, -0.509, -0.303, -0.347),
  (0.241, -0.554, -0.573, -0.617),
  (0.292, -0.154, -0.302, -0.326),
)
GRADE_HOLD_CASES = (
  (-0.49, -1.40),
  (0.00, -1.40),
  (0.49, -1.40),
  (0.75, -1.40),
  (0.98, -1.65),
  (1.25, -2.00),
  (1.47, -2.00),
)


def get_car_params(candidate, experimental_long=True):
  fingerprint = gen_empty_fingerprint()
  interface = interfaces[candidate]
  CP = interface.get_params(candidate, fingerprint, [], experimental_long, False, False)
  return CP, interface.get_params_sp(CP, candidate, fingerprint, [], experimental_long, False, False)


def make_car_state(v_ego=0.2, a_ego=0.0, standstill=False, v_ego_raw=None) -> structs.CarState:
  raw_speed = v_ego if v_ego_raw is None else v_ego_raw
  state = structs.CarState(vEgo=float(v_ego), vEgoRaw=float(raw_speed), aEgo=float(a_ego), standstill=standstill)
  state.cruiseState.standstill = standstill
  return state


def make_control(candidate, initial_accel=-0.33, experimental_long=True):
  CP, CP_SP = get_car_params(candidate, experimental_long)
  control = LongControl(CP, CP_SP)
  control.long_control_state = LongCtrlState.pid
  control.last_output_accel = initial_accel
  return CP, control


def stock_stopping_output(output_accel, stop_accel):
  return min(output_accel, 0.0) - DT_CTRL if output_accel > stop_accel else output_accel


def expected_hold_accel(CP, initial_accel=-0.33):
  minimum_hold = min(STOPPING_HOLD_ACCEL, CP.stopAccel + STOPPING_HOLD_MARGIN)
  return min(initial_accel, max(CP.stopAccel, minimum_hold))


def settle_preserved_hold(control):
  control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
  CS = make_car_state(0.0, 0.0, standstill=True)
  for _ in range(round(4.0 / DT_CTRL)):
    control.update(True, CS, -0.1, True, (-3.5, 2.0))


class TestLongControlSP(OpenpilotTestCase):
  def test_stop_threshold_matches_the_shared_helper(self):
    assert should_stop(0.29, 0.0)
    assert not should_stop(0.3, 0.0)
    assert not should_stop(0.29, 0.1)

  def test_hold_scope_matches_every_car_interface(self):
    for candidate in interfaces:
      for experimental_long in (False, True):
        with self.subTest(candidate=candidate, experimental_long=experimental_long):
          CP, control = make_control(candidate, experimental_long=experimental_long)
          output = control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
          supported = CP.openpilotLongitudinalControl and not CP.notCar and CP.stopAccel < 0.0

          self.assertAlmostEqual(output, -0.33)
          assert (control._stopping_hold_accel is not None) == supported

  @parameterized.expand(UNSUPPORTED_HOLD_VEHICLES, names=("candidate", "experimental_long"))
  def test_unsupported_hold_semantics_keep_the_cache_disabled(self, candidate, experimental_long):
    _, control = make_control(candidate, experimental_long=experimental_long)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))

    assert control._stopping_hold_accel is None

  @parameterized.expand(ROUTE_STOP_ONSETS, names=("v_ego", "a_ego", "a_target", "initial_accel"))
  def test_logged_stop_onsets_hold_the_existing_brake(self, v_ego, a_ego, a_target, initial_accel):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, initial_accel)
    output = control.update(True, make_car_state(v_ego, a_ego), a_target, True, (-3.5, 2.0))
    assert control.long_control_state == LongCtrlState.stopping
    self.assertAlmostEqual(output, initial_accel)

  @parameterized.expand(ROUTE_STOP_ONSETS, names=("v_ego", "a_ego", "a_target", "initial_accel"))
  def test_logged_stop_onsets_preserve_a_settled_hold(self, v_ego, a_ego, a_target, initial_accel):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, initial_accel)
    control.update(True, make_car_state(v_ego, a_ego), a_target, True, (-3.5, 2.0))
    CS = make_car_state(0.0, 0.0, standstill=True)
    outputs = [control.update(True, CS, a_target, True, (-3.5, 2.0)) for _ in range(round(10.0 / DT_CTRL))]

    hold_floor = expected_hold_accel(CP, initial_accel)
    self.assertAlmostEqual(outputs[-1], hold_floor)
    np.testing.assert_allclose(outputs[-100:], outputs[-1], rtol=0.0, atol=1e-12)
    assert all(current <= previous for previous, current in zip(outputs[:-1], outputs[1:], strict=True))

  @parameterized.expand(PRESERVED_HOLD_VEHICLES, names=("candidate",))
  def test_preserved_hold_does_not_change_the_moving_approach(self, candidate):
    CP, control = make_control(candidate)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    moving = [control.update(True, make_car_state(0.25, -0.25), -0.22, True, (-3.5, 2.0)) for _ in range(20)]
    CS = make_car_state(0.0, 0.0, standstill=True)
    terminal = [control.update(True, CS, -0.1, True, (-3.5, 2.0)) for _ in range(round(4.0 / DT_CTRL))]

    np.testing.assert_allclose(moving, -0.33, rtol=0.0, atol=1e-12)
    self.assertAlmostEqual(terminal[-1], expected_hold_accel(CP))

  def test_glide_hold_survives_a_soft_deceleration_sample(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.166)
    samples = ((0.388, -0.201, -0.164), (0.330, -0.120, -0.140), (0.283, -0.0675, -0.120))
    outputs = [control.update(True, make_car_state(v_ego, a_ego), a_target, True, (-3.5, 2.0)) for v_ego, a_ego, a_target in samples]

    np.testing.assert_allclose(outputs, [-0.166] * len(samples), rtol=1e-6, atol=1e-12)

  def test_glide_response_reaches_the_stock_rate_when_deceleration_stops(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.166)
    control.update(True, make_car_state(0.388, -0.201), -0.164, True, (-3.5, 2.0))
    output = control.update(True, make_car_state(0.330, -0.01), -0.140, True, (-3.5, 2.0))

    assert -0.176 < output < -0.175

  def test_glide_response_increases_with_stopping_distance_error(self):
    _, nominal = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.166)
    _, distance_error = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.166)
    for control in (nominal, distance_error):
      control.update(True, make_car_state(0.388, -0.201), -0.164, True, (-3.5, 2.0))
    nominal_output = nominal.update(True, make_car_state(0.330, -0.050), -0.140, True, (-3.5, 2.0))
    distance_error_output = distance_error.update(True, make_car_state(0.400, -0.050), -0.140, True, (-3.5, 2.0))

    assert -0.176 < distance_error_output < nominal_output

  @parameterized.expand(((1.0, 0.0), (0.75, 0.4375), (0.5, 0.75), (0.0, 1.0)), names=("decel_fraction", "expected_rate"))
  def test_stopping_rate_scales_with_realized_deceleration(self, decel_fraction, expected_rate):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    output = control.update(True, make_car_state(0.3, -0.12 * decel_fraction), 0.0, True, (-3.5, 2.0))

    self.assertAlmostEqual((-0.33 - output) / DT_CTRL, expected_rate, delta=1e-6)

  def test_stopping_rate_scales_with_planner_demand(self):
    _, gentle = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    _, urgent = make_control(TOYOTA.TOYOTA_RAV4_TSS2)

    gentle_output = gentle.update(True, make_car_state(0.3, -0.12), -0.34, True, (-3.5, 2.0))
    urgent_output = urgent.update(True, make_car_state(0.3, -0.12), -1.0, True, (-3.5, 2.0))

    assert -0.331 < gentle_output < -0.33
    self.assertAlmostEqual(urgent_output, -0.34)

  def test_glide_hold_yields_to_stronger_planner_braking(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.166)
    control.update(True, make_car_state(0.388, -0.201), -0.164, True, (-3.5, 2.0))
    output = control.update(True, make_car_state(0.330, -0.120), -1.0, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, stock_stopping_output(-0.166, CP.stopAccel))

  @parameterized.expand(STOP_ACCEL_VEHICLES, names=("candidate",))
  def test_urgent_braking_matches_the_stock_ramp(self, candidate):
    CP, control = make_control(candidate)
    CS = make_car_state(0.8, -0.1)
    output = control.last_output_accel

    for _ in range(round(1.0 / DT_CTRL)):
      output = control.update(True, CS, -3.0, True, (-3.5, 2.0))

    expected = -0.33
    for _ in range(round(1.0 / DT_CTRL)):
      expected = stock_stopping_output(expected, CP.stopAccel)
    self.assertAlmostEqual(output, expected)

  @parameterized.expand(STOP_ACCEL_VEHICLES, names=("candidate",))
  def test_stronger_planner_brake_matches_the_stock_ramp(self, candidate):
    CP, control = make_control(candidate)
    outputs = [control.update(True, make_car_state(0.3, -0.3), -1.0, True, (-3.5, 2.0)) for _ in range(10)]
    expected = []
    output = -0.33
    for _ in range(10):
      output = stock_stopping_output(output, CP.stopAccel)
      expected.append(output)
    np.testing.assert_allclose(outputs, expected, rtol=1e-6, atol=1e-12)

  @parameterized.expand(STOP_ACCEL_VEHICLES, names=("candidate",))
  def test_insufficient_deceleration_uses_most_of_the_stock_ramp(self, candidate):
    CP, control = make_control(candidate)
    output = control.update(True, make_car_state(0.6, -0.1), -0.1, True, (-3.5, 2.0))
    if -0.33 > CP.stopAccel:
      assert -0.34 < output < -0.338
    else:
      self.assertAlmostEqual(output, -0.33)

  def test_deceleration_noise_cannot_release_the_brake(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    outputs = [control.update(True, make_car_state(0.3, -0.3 if frame % 2 else 0.0), -0.1, True, (-3.5, 2.0)) for frame in range(40)]
    assert all(current <= previous for previous, current in zip(outputs[:-1], outputs[1:], strict=True))

  def test_planner_noise_cannot_release_the_brake(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    outputs = [control.update(True, make_car_state(0.3, -0.3), -1.0 if frame % 2 else -0.1, True, (-3.5, 2.0)) for frame in range(40)]
    assert all(current <= previous for previous, current in zip(outputs[:-1], outputs[1:], strict=True))

  @parameterized.expand(
    (
      (float("nan"), -0.3, -0.1),
      (0.3, float("nan"), -0.1),
      (0.3, -0.3, float("nan")),
      (float("inf"), -0.3, -0.1),
      (0.3, -float("inf"), -0.1),
      (0.3, -0.3, float("inf")),
    ),
    names=("v_ego", "a_ego", "a_target"),
  )
  def test_invalid_state_uses_the_stock_ramp(self, v_ego, a_ego, a_target):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    output = control.update(True, make_car_state(v_ego, a_ego), a_target, True, (-3.5, 2.0))
    self.assertAlmostEqual(output, stock_stopping_output(-0.33, CP.stopAccel))

  @parameterized.expand(
    (
      (0.24, 0.0, -0.49, 0.15, 0.0),
      (0.53, -0.31, -0.49, 0.35, 0.1),
      (0.24, 0.0, 0.0, 0.15, 0.0),
      (0.464, -0.223, 0.0, 0.25, 0.05),
      (0.53, -0.31, 0.0, 0.35, 0.1),
      (0.24, 0.0, 0.49, 0.15, 0.0),
      (0.53, -0.31, 0.49, 0.25, 0.05),
      (0.6, -0.3, 0.49, 0.35, 0.1),
      (0.6, -0.3, 0.49, 0.5, 0.1),
    ),
    names=("speed", "initial_accel", "grade_accel", "actuator_lag", "actuator_delay"),
  )
  def test_smooth_stop_distance_is_bounded(self, speed, initial_accel, grade_accel, actuator_lag, actuator_delay):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, initial_accel)
    applied_accel = initial_accel
    delay = [initial_accel] * round(actuator_delay / DT_CTRL)
    distance = 0.0
    outputs = []

    for _ in range(round(4.0 / DT_CTRL)):
      command = control.update(True, make_car_state(speed, applied_accel), -0.1, True, (-3.5, 2.0))
      outputs.append(command)
      delayed_command = command
      if delay:
        delay.append(command)
        delayed_command = delay.pop(0)
      applied_accel += DT_CTRL / actuator_lag * (delayed_command + grade_accel - applied_accel)
      speed = max(0.0, speed + applied_accel * DT_CTRL)
      distance += speed * DT_CTRL
      if speed == 0.0:
        break

    assert speed == 0.0
    assert distance < 1.0
    assert all(current <= previous for previous, current in zip(outputs[:-1], outputs[1:], strict=True))

  @parameterized.expand(STOP_ACCEL_VEHICLES, names=("candidate",))
  def test_standstill_uses_the_stock_ramp(self, candidate):
    CP, control = make_control(candidate)
    control.long_control_state = LongCtrlState.off
    CS = make_car_state(0.0, 0.0, standstill=True)
    outputs = [control.update(True, CS, 0.0, False, (-3.5, 2.0)) for _ in range(round(2.0 / DT_CTRL))]
    expected = -0.33
    for _ in range(round(2.0 / DT_CTRL)):
      expected = stock_stopping_output(expected, CP.stopAccel)
    self.assertAlmostEqual(outputs[0], stock_stopping_output(-0.33, CP.stopAccel))
    self.assertAlmostEqual(outputs[-1], expected)

  @parameterized.expand(PRESERVED_HOLD_VEHICLES, names=("candidate",))
  def test_preserved_hold_yields_to_stronger_planner_braking(self, candidate):
    CP, control = make_control(candidate)
    settle_preserved_hold(control)
    previous = control.last_output_accel
    output = control.update(True, make_car_state(0.0, 0.0, standstill=True), CP.stopAccel, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, stock_stopping_output(previous, CP.stopAccel))

  def test_false_departure_restores_a_stronger_preserved_hold(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    settle_preserved_hold(control)
    stronger_hold = control.update(True, make_car_state(0.0, 0.0, standstill=True), CP.stopAccel, True, (-3.5, 2.0))
    departure_state = make_car_state(0.0, 0.0, standstill=True)
    departure_state.cruiseState.standstill = False
    control.update(True, departure_state, 0.6, False, (-3.5, 2.0))
    restored = control.update(True, make_car_state(0.0, 0.0, standstill=True), -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(restored, stronger_hold)

  @parameterized.expand(SETTLE_VEHICLES, names=("candidate",))
  def test_false_departure_restores_a_command_at_the_stop_limit(self, candidate):
    CP, control = make_control(candidate)
    strong_hold = max(CP.stopAccel - 0.2, -3.5)
    control.last_output_accel = strong_hold
    held = control.update(True, make_car_state(0.0, 0.0, standstill=True), -0.1, True, (-3.5, 2.0))
    departure_state = make_car_state(0.0, 0.0, standstill=True)
    departure_state.cruiseState.standstill = False
    control.update(True, departure_state, 0.6, False, (-3.5, 2.0))
    restored = control.update(True, make_car_state(0.0, 0.0, standstill=True), -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(restored, held)

  @parameterized.expand(SETTLE_VEHICLES, names=("candidate",))
  def test_false_departure_after_reaching_the_stop_limit_restores_braking(self, candidate):
    CP, control = make_control(candidate)
    CS = make_car_state(0.0, 0.0, standstill=True)
    while control.last_output_accel > CP.stopAccel:
      reached = control.update(True, CS, -0.1, True, (-3.5, 2.0))

    departure_state = make_car_state(0.0, 0.0, standstill=True)
    departure_state.cruiseState.standstill = False
    control.update(True, departure_state, 0.6, False, (-3.5, 2.0))
    restored = control.update(True, CS, -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(restored, reached)

  @parameterized.expand(PRESERVED_HOLD_VEHICLES, names=("candidate",))
  def test_inadequate_preserved_hold_uses_the_stock_ramp(self, candidate):
    for v_ego, a_ego, standstill in ((0.0, 0.2, True), (-0.1, 0.0, False)):
      with self.subTest(v_ego=v_ego, a_ego=a_ego, standstill=standstill):
        CP, control = make_control(candidate)
        settle_preserved_hold(control)
        output = control.last_output_accel
        expected = output
        for _ in range(round(4.0 / DT_CTRL)):
          output = control.update(True, make_car_state(v_ego, a_ego, standstill), -0.1, True, (-3.5, 2.0))
          expected = max(stock_stopping_output(expected, CP.stopAccel), -3.5)

        self.assertAlmostEqual(output, expected)

  @parameterized.expand(PRESERVED_HOLD_VEHICLES, names=("candidate",))
  def test_false_departure_restores_the_preserved_hold(self, candidate):
    _, control = make_control(candidate)
    settle_preserved_hold(control)
    hold_accel = control.last_output_accel
    departure_state = make_car_state(0.0, 0.0, standstill=True)
    departure_state.cruiseState.standstill = False
    departure = control.update(True, departure_state, 0.6, False, (-3.5, 2.0))
    restored = control.update(True, make_car_state(0.0, 0.0, standstill=True), -0.1, True, (-3.5, 2.0))

    assert departure > 0.0
    self.assertAlmostEqual(restored, hold_accel)

  @parameterized.expand(
    ((True, 0.0, 0.0, True), (False, 0.06, 0.06, False), (False, 0.0, 0.06, False)),
    names=("inactive", "v_ego", "v_ego_raw", "standstill"),
  )
  def test_preserved_hold_clears_after_inactive_or_real_motion(self, inactive, v_ego, v_ego_raw, standstill):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    settle_preserved_hold(control)
    control.update(not inactive, make_car_state(v_ego, 0.0, standstill=standstill, v_ego_raw=v_ego_raw), 0.6, False, (-3.5, 2.0))
    output = control.update(True, make_car_state(0.0, 0.0, standstill=True), -0.1, True, (-3.5, 2.0))

    assert control._stopping_hold_accel is None
    self.assertAlmostEqual(output, stock_stopping_output(0.0, CP.stopAccel))

  @parameterized.expand(((float("nan"), 0.0), (0.0, float("nan"))), names=("v_ego", "v_ego_raw"))
  def test_invalid_speed_clears_the_preserved_hold(self, v_ego, v_ego_raw):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    settle_preserved_hold(control)
    previous = control.last_output_accel
    output = control.update(True, make_car_state(v_ego, 0.0, standstill=True, v_ego_raw=v_ego_raw), -0.1, True, (-3.5, 2.0))

    assert control._stopping_hold_accel is None
    self.assertAlmostEqual(output, previous - DT_CTRL)

  @parameterized.expand(((0.005, True), (-0.005, True), (0.02, True), (-0.02, False)), names=("v_ego_raw", "standstill"))
  def test_raw_wheel_motion_keeps_building_brake(self, v_ego_raw, standstill):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    settle_preserved_hold(control)
    previous = control.last_output_accel
    CS = make_car_state(0.0, 0.0, standstill=standstill, v_ego_raw=v_ego_raw)
    output = control.update(True, CS, -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, previous - DT_CTRL)

  def test_preserved_hold_removes_launch_brake_backlog(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    CS = make_car_state(0.0, 0.0, standstill=True)
    for _ in range(round(3.0 / DT_CTRL)):
      control.update(True, CS, -0.1, True, (-3.5, 2.0))
    preserved_hold = control.last_output_accel

    CS.cruiseState.standstill = False
    requested_accels = [control.update(True, CS, min(0.15 + frame * DT_CTRL, 1.2), False, (-3.5, 2.0)) for frame in range(round(1.0 / DT_CTRL))]

    def release_time(initial_accel):
      applied_accel = initial_accel
      for frame, requested_accel in enumerate(requested_accels):
        accel_step = PRIUS_TSS2_ROUTE_MODEL.command_rate_limit * DT_CTRL
        applied_accel += np.clip(requested_accel - applied_accel, -accel_step, accel_step)
        if applied_accel >= 0.0:
          return (frame + 1) * DT_CTRL
      raise AssertionError("brake command did not release")

    stock_release = release_time(CP.stopAccel)
    preserved_release = release_time(preserved_hold)
    self.assertAlmostEqual(preserved_hold, expected_hold_accel(CP))
    assert stock_release >= 0.45
    assert preserved_release <= 0.37
    assert stock_release - preserved_release >= 0.14

  @parameterized.expand(GRADE_HOLD_CASES, names=("grade_accel", "expected_hold"))
  def test_preserved_hold_adapts_to_grade_without_creep(self, grade_accel, expected_hold):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -0.3)
    speed = 0.6
    actuator_accel = -0.3
    physical_accel = actuator_accel + grade_accel
    stopped_frames = 0
    max_post_stop_speed = 0.0

    for _ in range(round(16.0 / DT_CTRL)):
      standstill = bool(speed <= 1e-6)
      measured_accel = max(physical_accel, 0.0) if standstill else physical_accel
      output = control.update(True, make_car_state(speed, measured_accel, standstill), -0.1, True, (-3.5, 2.0))
      actuator_accel += DT_CTRL / 0.25 * (output - actuator_accel)
      physical_accel = actuator_accel + grade_accel
      speed = max(0.0, speed + physical_accel * DT_CTRL) if speed > 0.0 or physical_accel > 0.0 else 0.0

      if stopped_frames:
        max_post_stop_speed = max(max_post_stop_speed, speed)
        stopped_frames += 1
      elif speed == 0.0:
        stopped_frames = 1
      if stopped_frames >= round(8.0 / DT_CTRL):
        break

    assert stopped_frames >= round(8.0 / DT_CTRL)
    assert max_post_stop_speed == 0.0
    self.assertAlmostEqual(output, expected_hold, delta=0.03)

  @parameterized.expand(SETTLE_VEHICLES, names=("candidate",))
  def test_final_stop_builds_brake_smoothly_while_vehicle_settles(self, candidate):
    _, control = make_control(candidate)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    outputs = [control.update(True, make_car_state(0.0006, a_ego, standstill=True), -0.032, True, (-3.5, 2.0)) for a_ego in (-1.098, -0.950, -0.609, -0.286)]
    changes = -np.diff([-0.33, *outputs])
    assert np.all(changes > 0.0)
    assert np.all(np.diff(changes) > 0.0)
    assert changes[-1] < 0.001

  @parameterized.expand((-0.09, 0.0, 0.1), names=("a_ego",))
  def test_settled_vehicle_uses_the_stock_hold_ramp(self, a_ego):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    output = control.update(True, make_car_state(0.0, a_ego, standstill=True), -0.1, True, (-3.5, 2.0))
    self.assertAlmostEqual(output, stock_stopping_output(-0.33, CP.stopAccel))

  @parameterized.expand(SETTLE_VEHICLES, names=("candidate",))
  def test_direct_terminal_entry_builds_brake_smoothly(self, candidate):
    _, control = make_control(candidate)
    CS = make_car_state(0.0006, -0.3, standstill=True)
    outputs = [control.update(True, CS, -0.1, True, (-3.5, 2.0)) for _ in range(4)]

    rates = -np.diff([-0.33, *outputs]) / DT_CTRL
    np.testing.assert_allclose(rates, [(frame / STOPPING_SETTLE_FRAMES) ** 2 for frame in range(1, 5)], rtol=1e-6, atol=1e-12)

  def test_direct_terminal_entry_keeps_urgent_stock_braking(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    output = control.update(True, make_car_state(0.0006, -0.3, standstill=True), -1.0, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, stock_stopping_output(-0.33, CP.stopAccel))

  @parameterized.expand((0.0, -0.05), names=("initial_accel",))
  def test_direct_terminal_entry_first_builds_meaningful_brake(self, initial_accel):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, initial_accel)
    output = control.update(True, make_car_state(0.0006, -0.3, standstill=True), 0.0, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, stock_stopping_output(initial_accel, CP.stopAccel))

  @parameterized.expand(SETTLE_VEHICLES, names=("candidate",))
  def test_final_settling_ramp_is_bounded(self, candidate):
    _, control = make_control(candidate)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    CS = make_car_state(0.0, -0.3, standstill=True)
    outputs = [control.update(True, CS, -0.1, True, (-3.5, 2.0)) for _ in range(STOPPING_SETTLE_FRAMES + 1)]

    rates = -np.diff([-0.33, *outputs]) / DT_CTRL
    expected = [(frame / STOPPING_SETTLE_FRAMES) ** 2 for frame in range(1, STOPPING_SETTLE_FRAMES + 1)] + [1.0]
    np.testing.assert_allclose(rates, expected, rtol=1e-6, atol=1e-12)

  @parameterized.expand(((0.6, -0.1, False), (0.0, 0.0, True)), names=("v_ego", "a_ego", "standstill"))
  def test_stopping_never_releases_a_stronger_command(self, v_ego, a_ego, standstill):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2, -3.0)
    output = control.update(True, make_car_state(v_ego, a_ego, standstill), 0.0, True, (-3.5, 2.0))
    self.assertAlmostEqual(output, -3.0)

  def test_reported_standstill_while_moving_can_hold_the_brake(self):
    _, control = make_control(GM.CHEVROLET_BOLT_EUV)
    control.long_control_state = LongCtrlState.off
    output = control.update(True, make_car_state(0.3, -0.3, standstill=True), -0.1, False, (-3.5, 2.0))
    self.assertAlmostEqual(output, -0.33)

  @parameterized.expand((-0.1, 0.09), names=("a_target",))
  def test_stopping_removes_positive_acceleration_immediately(self, a_target):
    _, control = make_control(HYUNDAI.HYUNDAI_SONATA, 0.2)
    output = control.update(True, make_car_state(0.2, -0.2), a_target, True, (-3.5, 2.0))
    self.assertAlmostEqual(output, -DT_CTRL)

  def test_rollback_uses_the_stock_ramp(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    output = control.update(True, make_car_state(-0.1, 0.1), -0.1, True, (-3.5, 2.0))
    self.assertAlmostEqual(output, stock_stopping_output(-0.33, CP.stopAccel))

  def test_rollback_after_settling_arms_uses_the_stock_ramp(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    control.update(True, make_car_state(0.01, -0.3), -0.1, True, (-3.5, 2.0))
    previous = control.last_output_accel
    output = control.update(True, make_car_state(-0.04, -0.3), -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, previous - DT_CTRL)

  def test_small_velocity_noise_does_not_trigger_the_stock_rate(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    output = control.update(True, make_car_state(-0.04, -0.3, standstill=True, v_ego_raw=0.0), -0.1, True, (-3.5, 2.0))
    assert -0.331 < output < -0.33

  def test_terminal_speed_chatter_cannot_extend_settling_ramp(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    outputs = [
      control.update(True, make_car_state(0.049 if frame % 2 == 0 else 0.051, -0.3, v_ego_raw=0.0), -0.1, True, (-3.5, 2.0))
      for frame in range(STOPPING_SETTLE_FRAMES + 2)
    ]

    rates = -np.diff([-0.33, *outputs]) / DT_CTRL
    np.testing.assert_allclose(
      rates[:STOPPING_SETTLE_FRAMES], [(frame / STOPPING_SETTLE_FRAMES) ** 2 for frame in range(1, STOPPING_SETTLE_FRAMES + 1)], rtol=1e-6, atol=1e-12
    )
    np.testing.assert_allclose(rates[-2:], [1.0, 1.0], rtol=1e-6, atol=1e-12)

  def test_terminal_speed_plateau_cannot_extend_settling_ramp(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    CS = make_car_state(0.03, -0.3, v_ego_raw=0.0)
    outputs = [control.update(True, CS, -0.1, True, (-3.5, 2.0)) for _ in range(STOPPING_SETTLE_FRAMES + 1)]

    rates = -np.diff([-0.33, *outputs]) / DT_CTRL
    np.testing.assert_allclose(rates[-2:], [1.0, 1.0], rtol=1e-6, atol=1e-12)

  def test_interrupted_stop_cannot_reuse_settling_hold(self):
    CP, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.update(True, make_car_state(0.28, -0.29), -0.22, True, (-3.5, 2.0))
    control.update(False, make_car_state(0.0, 0.0, standstill=True), 0.0, False, (-3.5, 2.0))
    output = control.update(True, make_car_state(0.0, -0.3, standstill=True), -0.1, True, (-3.5, 2.0))

    self.assertAlmostEqual(output, stock_stopping_output(0.0, CP.stopAccel))

  def test_departure_uses_the_stock_pid_path(self):
    _, control = make_control(TOYOTA.TOYOTA_RAV4_TSS2)
    control.long_control_state = LongCtrlState.stopping
    output = control.update(True, make_car_state(0.0), 0.6, False, (-3.5, 2.0))
    assert control.long_control_state == LongCtrlState.pid
    assert output > 0.0

  def test_planner_mpc_and_longcontrol_complete_a_smooth_stop(self):
    plant = PlantSP(
      lead_relevancy=True,
      speed=0.6,
      distance_lead=3.6,
      run_long_control=True,
      actuator_model=PRIUS_TSS2_ROUTE_MODEL,
    )
    plant.planner.accel_controller._enabled = True
    plant.planner.dec._enabled = False
    commands = []
    speeds = []
    states = []
    solver_statuses = []

    with (
      mock.patch.object(plant.planner.accel_controller, "update", return_value=None),
      mock.patch.object(plant.planner.dec, "_read_params", return_value=None),
    ):
      while plant.current_time < 5.0:
        result = plant.step(v_lead=0.0, v_cruise=8.0)
        commands.append(result["actuator_command"])
        speeds.append(result["speed"])
        states.append(result["long_control_state"])
        solver_statuses.append(plant.planner.mpc.solution_status)

    stopping = states.index(LongCtrlState.stopping)
    moving_stop_commands = [
      command for command, state, speed in zip(commands, states, speeds, strict=True) if state == LongCtrlState.stopping and speed > STOPPING_SPEED_TOLERANCE
    ]
    assert all(current <= previous + 1e-9 for previous, current in zip(commands[stopping:-1], commands[stopping + 1 :], strict=True))
    assert len(moving_stop_commands) > 1 and max(moving_stop_commands) - min(moving_stop_commands) < 1e-9
    assert plant.speed == 0.0 and plant.distance < 1.0
    assert plant.distance_lead - plant.distance > 3.0
    assert all(status == 0 for status in solver_statuses)
