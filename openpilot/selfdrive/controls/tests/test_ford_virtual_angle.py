from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPath, FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_virtual_angle import (
  C0_PER_ACCEL, C1_PER_ACCEL, FordVirtualAngleController, ServoTuning, select_virtual_angle_controller,
)


def update(controller, t, desired=0.01, actual=0.0, speed=10.0, **kwargs):
  inputs = {'current_curvature': actual, 'speed': speed, 'now': t, 'measurement_time': t,
                'reference_time': t, 'active': True}
  inputs.update(kwargs)
  return controller.update(desired, **inputs)


def car_params(**kwargs):
  values = {'brand': 'ford', 'flags': FordFlags.CANFD, 'carFingerprint': 'FORD_F_150_LIGHTNING_MK1',
                'steerActuatorDelay': 0.2, 'carFw': [SimpleNamespace(ecu='eps', fwVersion=b'RL38-14D003-AA')]}
  values.update(kwargs)
  return SimpleNamespace(**values)


class TestVirtualAngleSelection(unittest.TestCase):
  def test_opt_in_and_exact_vehicle_firmware_scope(self):
    for previous in (FordPathController(), FordPscmObserverPathController()):
      self.assertIs(select_virtual_angle_controller(car_params(), False, previous), previous)
      for overrides in ({'brand': 'tesla'}, {'flags': 0}, {'carFingerprint': 'FORD_F_150_MK14'},
                        {'carFw': []}, {'carFw': [SimpleNamespace(ecu='eps', fwVersion=b'ML3V')]}):
        self.assertIs(select_virtual_angle_controller(car_params(**overrides), True, previous), previous)
      self.assertIsInstance(select_virtual_angle_controller(car_params(), True, previous), FordVirtualAngleController)

  def test_old_setting_cannot_enable_new_controller(self):
    from openpilot.common.params import Params
    with tempfile.TemporaryDirectory(prefix='ford-virtual-params-') as directory:
      params = Params(directory)
      # Simulate a stored key left on an upgraded device; it is no longer registered.
      Path(params.get_param_path('FordSharedPathController')).write_text('1')
      self.assertNotIn(b'FordSharedPathController', params.all_keys())
      self.assertIs(params.get_default_value('FordVirtualAngleController'), False)
      self.assertFalse(params.get_bool('FordVirtualAngleController'))
      previous = FordPathController()
      self.assertIs(select_virtual_angle_controller(car_params(), params.get_bool('FordVirtualAngleController'), previous), previous)
      params.put_bool('FordVirtualAngleController', True, block=True)
      chosen = select_virtual_angle_controller(car_params(), params.get_bool('FordVirtualAngleController'), previous)
      params.put_bool('FordVirtualAngleController', False, block=True)
      self.assertIsInstance(chosen, FordVirtualAngleController)  # only selected at startup


class TestVirtualAngleController(unittest.TestCase):
  def test_rejects_invalid_inputs_and_resets_state(self):
    for bad in ({'active': False}, {'valid': False}, {'steering_pressed': False, 'speed': 0.2},
                {'speed': 56}, {'current_curvature': float('nan')}, {'current_curvature': 1e308}, {'reference_time': 0.0},
                {'measurement_time': 0.0}, {'now': float('inf')}, {'reference_time': 2.1}):
      with self.subTest(bad=bad):
        controller = FordVirtualAngleController()
        for i in range(200):
          update(controller, i * 0.01)
        self.assertNotEqual(controller.command, FordPath())
        self.assertEqual(update(controller, 2.0, **bad), FordPath())
        self.assertEqual(controller.integral, 0.0)
        self.assertFalse(controller.history)
        command = update(controller, 2.01)
        self.assertLessEqual(abs(command.path_offset), 0.02)
        self.assertLessEqual(abs(command.path_angle), 0.001)

  def test_timing_gap_or_reversal_resets(self):
    for next_time in (1.0, 0.99, 1.101):
      controller = FordVirtualAngleController()
      update(controller, 1.0)
      self.assertEqual(update(controller, next_time), FordPath())
      self.assertEqual(controller.diagnostics['status'], 'timing_reset')

  def test_repeated_measurement_does_not_create_rate_impulse(self):
    controller = FordVirtualAngleController()
    update(controller, 1.0)
    update(controller, 1.01, actual=0.001)
    original_rate = controller.curvature_rate
    update(controller, 1.02, actual=0.001, measurement_time=1.01)
    self.assertEqual(controller.curvature_rate, original_rate)
    update(controller, 1.03, actual=0.002, measurement_time=1.03)
    self.assertTrue(0 < controller.curvature_rate < 0.1)

  def test_delayed_reference_uses_measurement_time(self):
    tuning = replace(ServoTuning(), ki=0, kd=0)
    controller = FordVirtualAngleController(tuning=tuning)
    for i in range(100):
      update(controller, i * 0.01, desired=0.0, measurement_time=i * 0.01 - 0.14)
    for i in range(100, 125):
      update(controller, i * 0.01, measurement_time=i * 0.01 - 0.14)
    # This sample precedes the response to the new reference even though now does not.
    update(controller, 1.25, measurement_time=1.11)
    self.assertAlmostEqual(controller.diagnostics['delayed_reference'], 0.0)

  def test_pending_correction_reduces_proportional_demand(self):
    controller = FordVirtualAngleController(tuning=replace(ServoTuning(), ki=0, kd=0))
    for i in range(150):
      update(controller, i * 0.01)
      d = controller.diagnostics
      if d['pending_feedback'] > 0.1:
        self.assertLess(d['p'], controller.tuning.kp * d['error_accel'])
        break
    else:
      self.fail('the delayed feedback path was never exercised')

  def test_stalled_response_stops_integrating_without_an_eps_limit_flag(self):
    controller = FordVirtualAngleController()
    for i in range(1000):
      update(controller, i * 0.01)
    self.assertTrue(controller.stalled)
    held = controller.integral
    for i in range(1000, 1200):
      update(controller, i * 0.01)
    self.assertEqual(controller.integral, held)
    update(controller, 12.0, actual=0.003)
    self.assertFalse(controller.stalled)

  def test_quantization_preserves_accumulated_slew_at_different_cycle_times(self):
    for dt in (0.005, 0.01, 0.02):
      for sign in (-1, 1):
        controller = FordVirtualAngleController()
        commands = [update(controller, i * dt, desired=sign * 0.1) for i in range(round(1 / dt))]
        expected = sign * controller.tuning.offset_rate * (0.01 + dt * (len(commands) - 1))
        self.assertAlmostEqual(commands[-1].path_offset, expected, delta=0.0051)
        for previous, command in zip(commands, commands[1:], strict=False):
          self.assertLessEqual(abs(command.path_offset - previous.path_offset), controller.tuning.offset_rate * dt + 0.01001)
          self.assertLessEqual(abs(command.path_angle - previous.path_angle), controller.tuning.heading_rate * dt + 0.000501)

  def test_limits_driver_override_and_reference_release(self):
    for sign in (-1, 1):
      controller = FordVirtualAngleController()
      for i in range(1000):
        command = update(controller, i * 0.01, desired=sign * 0.01)
        self.assertLessEqual(abs(command.path_offset), 5.11)
        self.assertLessEqual(abs(command.path_angle), C1_PER_ACCEL * controller.tuning.feedback_limit + 0.000251)
        self.assertEqual((command.curvature, command.curvature_rate), (0, 0))
        self.assertLessEqual(abs(controller.integral), controller.tuning.integral_limit)
      before = controller.integral
      for i in range(1000, 1100):
        update(controller, i * 0.01, desired=sign * 0.01, limited=True)
      self.assertEqual(controller.integral, before)
      for i in range(1100, 1200):
        command = update(controller, i * 0.01, desired=sign * 0.01, steering_pressed=True)
      self.assertEqual(controller.integral, 0)
      self.assertAlmostEqual(command.path_angle, 0.0)
      for i in range(1200, 1400):
        update(controller, i * 0.01, desired=sign * 0.01)
      update(controller, 14.0, desired=0.0)
      self.assertEqual(controller.integral, 0)

  def test_packed_requests_match_real_can_sign_and_resolution(self):
    from openpilot.cereal import custom
    packer = CANPacker('ford_lincoln_base_pt')
    parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
    can_bus = CanBus(fingerprint={0: {}})
    controller = FordVirtualAngleController()
    for i in range(800):
      command = update(controller, i * 0.01, desired=0.02 * math.sin(i * 0.02))
      msg = custom.CarControlSP.new_message()
      msg.fordLateralPath.valid = command.valid
      msg.fordLateralPath.pathOffset = command.path_offset
      msg.fordLateralPath.pathAngle = command.path_angle
      path = msg.fordLateralPath
      frame = create_lat_ctl2_msg(packer, can_bus, 2, -path.pathOffset, -path.pathAngle, -path.curvature,
                                  -path.curvatureRate, i % 16)
      parser.update([i * 10_000_000, [frame]])
      decoded = parser.vl['LateralMotionControl2']
      self.assertAlmostEqual(decoded['LatCtlPathOffst_L_Actl'], -command.path_offset)
      self.assertAlmostEqual(decoded['LatCtlPath_An_Actl'], -command.path_angle)
      self.assertEqual(decoded['LatCtlCurv_No_Actl'], 0.0)

  def test_conditional_delayed_plant_step_and_release(self):
    # Hypothetical plants expose controller regressions; these are NOT identified
    # Lightning dynamics or evidence that the recorded road oscillation is fixed.
    for gain in (0.5, 1.0, 2.0):
      for delay in (0.1, 0.2, 0.35):
        with self.subTest(gain=gain, delay=delay):
          controller = FordVirtualAngleController()
          actual = 0.0
          commands, motion = [0.0] * (round(delay / 0.01) + 1), []
          for i in range(3000):
            desired = 0.01 if i < 1500 else 0.0
            command = update(controller, i * 0.01, desired=desired, actual=actual / 100)
            effort = command.path_offset / C0_PER_ACCEL + command.path_angle / C1_PER_ACCEL
            commands.append(effort)
            actual += 0.01 / 0.15 * (gain * commands.pop(0) - actual)
            motion.append(actual)
          self.assertLess(max(abs(v) for v in motion), 2.2)
          self.assertLess(np.ptp(motion[1200:1500]), 0.12)
          self.assertLess(max(abs(v) for v in motion[-300:]), 0.08)

  def test_recorded_turn_command_forcing_is_attenuated(self):
    fixture = Path(__file__).parent / 'fixtures/ford_virtual_angle_route78.npz'
    meta = json.loads(fixture.with_suffix('.json').read_text())
    self.assertEqual(hashlib.sha256(fixture.read_bytes()).hexdigest(), meta['fixture_sha256'])
    z = np.load(fixture)
    controller = FordVirtualAngleController()
    commands = []
    for i, t in enumerate(z['t']):
      command = update(controller, t, desired=z['desired'][i], actual=z['actual'][i], speed=z['speed'][i],
                       measurement_time=z['measurement_time'][i], reference_time=z['reference_time'][i],
                       active=bool(z['active'][i]), valid=bool(z['valid'][i]), steering_pressed=bool(z['pressed'][i]))
      commands.append((command.path_offset, command.path_angle))
    # Use the complete oscillation window AND only its pre-intervention onset.
    # Measurements are frozen: this asserts command attenuation, not wheel stability.
    for end in (34.19, 36.1):
      m = (z['t'] >= 32.5) & (z['t'] <= end)
      t = z['t'][m] - 32.5
      phase = 2 * np.pi * float(z['frequency_hz']) * t
      basis = np.column_stack((np.ones(len(t)), t, t*t, np.sin(phase), np.cos(phase)))
      def amplitude(x, basis=basis, m=m):
        coefficients = np.linalg.lstsq(basis, x[m, :2], rcond=None)[0]
        return np.linalg.norm(coefficients[-2:], axis=0)
      old = amplitude(z['recorded'])
      new = amplitude(np.array(commands))
      self.assertTrue(np.all(old > [0.1, 0.03]))  # preserves the original command symptom
      self.assertLess(new[0], 0.2 * old[0])
      self.assertLess(new[1], 0.05 * old[1])


if __name__ == '__main__':
  unittest.main()
