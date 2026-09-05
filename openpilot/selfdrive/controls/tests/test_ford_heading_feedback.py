import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController, HeadingFeedback, PathTuning, PscmStatus


MODEL = SimpleNamespace(position=SimpleNamespace(x=np.linspace(0., 100., 33), y=np.zeros(33)),
                        orientation=SimpleNamespace(z=np.zeros(33)))
AUTO_STATUS = object()


def step(controller, now, desired=.02, yaw_rate=.08, speed=8., pscm_status=AUTO_STATUS, **overrides):
  if pscm_status is AUTO_STATUS:
    pscm_status = PscmStatus(timestamp=now, lateral_state=2, limit=0, capability=2, denied=False)
  inputs = {'yaw_rate': yaw_rate, 'speed': speed, 'now': now, 'measurement_time': now,
            'model_time': math.floor((now + 1e-6) / .05) * .05, 'reference_time': now,
            'active': True, 'pscm_status': pscm_status, 'steering_torque': 0.}
  inputs.update(overrides)
  return controller.update(MODEL, desired, **inputs)


def warm(controller, desired=.02, yaw_rate=.08, speed=8., count=200):
  command = None
  for i in range(count):
    command = step(controller, i * .01, desired, yaw_rate, speed)
  return command


class TestFordHeadingFeedback(unittest.TestCase):
  def test_limited_backoff_cannot_grow_the_command_when_model_base_rises(self):
    for sign in (-1, 1):
      feedback = HeadingFeedback(.2, PathTuning())
      previous = sign * .2
      for i in range(40):
        now = i * .01
        previous = feedback.update(sign * .2, sign * .02, yaw_rate=sign * .1, speed=5., now=now,
                                   measurement_time=now, dt=.01, previous_command=previous, heading_horizon=7.,
                                   driver_override=False, pscm_status=PscmStatus(now, 2, 0, 2, False))
      # A larger model base must not defeat the measured backoff by outweighing
      # its subtractive integral increment while the PSCM is already limited.
      target = feedback.update(sign * .4, sign * .02, yaw_rate=sign * .3, speed=5., now=.4,
                               measurement_time=.4, dt=.01, previous_command=previous, heading_horizon=7.,
                               driver_override=False, pscm_status=PscmStatus(.4, 2, 2, 2, False))
      self.assertGreaterEqual(sign * target, 0.)
      self.assertLessEqual(sign * target, sign * previous)
      # A model-base change is not measured yaw error. Its temporary output
      # ceiling must not become a persistent, artificially large integral.
      self.assertAlmostEqual(sign * feedback.bias, -.002)
      repeated = feedback.update(sign * .5, sign * .02, yaw_rate=sign * .3, speed=5., now=.41,
                                 measurement_time=.4, dt=.01, previous_command=target, heading_horizon=7.,
                                 driver_override=False, pscm_status=PscmStatus(.41, 2, 2, 2, False))
      self.assertGreaterEqual(sign * repeated, 0.)
      self.assertLessEqual(sign * repeated, sign * target)

  def test_under_and_over_response_change_only_heading(self):
    for sign in (-1, 1):
      deficient = FordVirtualAngleController()
      excessive = FordVirtualAngleController()
      matched = FordVirtualAngleController()
      low = warm(deficient, sign * .02, sign * .08)
      high = warm(excessive, sign * .02, sign * .24)
      steady = warm(matched, sign * .02, sign * .16)
      self.assertGreater(sign * low.path_angle, .20)
      self.assertLess(sign * high.path_angle, .12)
      self.assertAlmostEqual(sign * steady.path_angle, .16, delta=.0005)
      self.assertEqual(low.path_offset, high.path_offset)
      self.assertEqual(low.path_offset, steady.path_offset)
      self.assertEqual((low.curvature, low.curvature_rate), (0., 0.))

  def test_missing_pscm_status_keeps_the_existing_base(self):
    controller = FordVirtualAngleController()
    for i in range(300):
      command = step(controller, i * .01, pscm_status=None)
    self.assertAlmostEqual(command.path_angle, .16, delta=.0005)
    self.assertAlmostEqual(command.path_offset, .64, delta=.01)

  def test_generic_eps_limit_blocks_growth_but_allows_same_direction_backoff(self):
    for sign in (-1, 1):
      for yaw_rate in (0., .4):
        controller = FordVirtualAngleController()
        before = warm(controller, desired=sign * .02, yaw_rate=sign * .08)
        previous = sign * before.path_angle
        for i in range(200, 500):
          now = i * .01
          command = step(controller, now, desired=sign * .02, yaw_rate=sign * yaw_rate,
                         pscm_status=PscmStatus(now, 2, 2, 2, False))
          self.assertGreaterEqual(sign * command.path_angle, -.000501)
          self.assertLessEqual(sign * command.path_angle, previous + .000501)
          previous = sign * command.path_angle
          if yaw_rate == 0.:
            self.assertAlmostEqual(command.path_angle, before.path_angle, delta=.0005)
        if yaw_rate > 0.:
          self.assertAlmostEqual(command.path_angle, 0., delta=.0005)

  def test_release_allows_backoff_without_rebuilding_turn_demand(self):
    for sign in (-1, 1):
      controller = FordVirtualAngleController()
      warm(controller, desired=sign * .04, yaw_rate=sign * .32)
      previous = .32
      for i in range(200, 219):
        command = step(controller, i * .01, desired=sign * .035, yaw_rate=sign * .5)
        self.assertGreaterEqual(sign * command.path_angle, -.000501)
        self.assertLessEqual(sign * command.path_angle, previous + .000501)
        previous = sign * command.path_angle
      self.assertLess(sign * controller.diagnostics['heading_bias'], 0.)
      self.assertEqual(controller.diagnostics['feedback_status'], 'release_backoff')

  def test_ineligible_feedback_clears_bias_and_requires_fresh_history(self):
    # These guards affect feedback eligibility, while the existing base path
    # remains available. Limit 3 reports driver activity and clears, not freezes.
    cases = [
      {'pscm_status': None},
      {'pscm_status': PscmStatus(1., 2, 0, 2, False)},
      {'pscm_status': PscmStatus(2.01, 2, 0, 2, False)},
      {'pscm_status': PscmStatus(2., 2, 0, 2, False, False)},
      {'pscm_status': PscmStatus(2., 1, 0, 2, False)},
      {'pscm_status': PscmStatus(2., 2, 0, 0, False)},
      {'pscm_status': PscmStatus(2., 2, 0, 3, False)},
      {'pscm_status': PscmStatus(2., 2, 0, 2, True)},
      {'pscm_status': PscmStatus(2., 2, 3, 2, False)},
      {'pscm_status': PscmStatus(float('nan'), 2, 0, 2, False)},
      {'pscm_status': PscmStatus(2., 2, 4, 2, False)},
      {'pscm_status': PscmStatus(1.98, 2, 0, 2, False)},  # Fresh but moves backward.
      {'steering_pressed': True},
      {'steering_torque': 1.01},
      {'steering_torque': -1.01},
      {'steering_torque': float('nan')},
      {'speed': 1.9},
    ]
    for overrides in cases:
      with self.subTest(overrides=overrides):
        controller = FordVirtualAngleController()
        warm(controller)
        self.assertGreater(controller.diagnostics['heading_bias'], .04)
        command = step(controller, 2., **overrides)
        self.assertTrue(command.valid)
        self.assertEqual(controller.diagnostics['heading_bias'], 0.)
        for i in range(201, 220):
          step(controller, i * .01)
          self.assertEqual(controller.diagnostics['heading_bias'], 0.)
        for i in range(220, 232):
          step(controller, i * .01)
        self.assertGreater(controller.diagnostics['heading_bias'], 0.)

  def test_repeated_measurement_cannot_be_integrated_again(self):
    controller = FordVirtualAngleController()
    before = warm(controller)
    bias = controller.diagnostics['heading_bias']
    self.assertGreater(bias, .04)
    for i in range(200, 213):
      command = step(controller, i * .01, measurement_time=1.99)
      self.assertEqual(controller.diagnostics['heading_bias'], bias)
      self.assertAlmostEqual(command.path_angle, before.path_angle, delta=.0005)

  def test_delayed_reference_is_held_without_future_interpolation(self):
    controller = FordVirtualAngleController()
    for i in range(41):
      step(controller, i * .01, yaw_rate=.16)
    # No control request existed at .405: historical values straddle that time
    # at .400 and .415. The future .415 request must not enter the comparison.
    step(controller, .415, desired=.021, yaw_rate=.16)
    for now in np.arange(.425, .596, .01):
      step(controller, float(now), desired=.021, yaw_rate=.16)
    step(controller, .605, desired=.021, yaw_rate=.16)
    self.assertAlmostEqual(controller.diagnostics['feedback_reference_time'], .4, places=9)
    self.assertAlmostEqual(controller.diagnostics['heading_bias'], 0., places=10)
    step(controller, .625, desired=.021, yaw_rate=.16)
    self.assertGreater(controller.diagnostics['heading_bias'], 0.)

  def test_zero_and_reversal_cannot_rebuild_previous_turn_bias(self):
    for next_desired in (0., -.02):
      controller = FordVirtualAngleController()
      before = warm(controller)
      self.assertGreater(controller.diagnostics['heading_bias'], .04)
      previous = before.path_angle
      for i in range(200, 220):
        command = step(controller, i * .01, desired=next_desired)
        self.assertEqual(controller.diagnostics['heading_bias'], 0.)
        self.assertLessEqual(command.path_angle, previous + .0005)
        self.assertLessEqual(abs(command.path_angle - previous), .005501)
        previous = command.path_angle
      if next_desired == 0.:
        for i in range(220, 320):
          command = step(controller, i * .01, desired=0.)
        self.assertEqual(controller.diagnostics['heading_bias'], 0.)
        self.assertAlmostEqual(command.path_angle, 0., delta=.0005)

  def test_eps_limit_still_allows_base_relative_release(self):
    controller = FordVirtualAngleController()
    warm(controller)
    before_bias = controller.diagnostics['heading_bias']
    self.assertGreater(before_bias, .04)
    for i in range(200, 280):
      now = i * .01
      command = step(controller, now, desired=.01, pscm_status=PscmStatus(now, 2, 2, 2, False))
      self.assertAlmostEqual(controller.diagnostics['heading_bias'], before_bias * .5, places=10)
    self.assertAlmostEqual(command.path_angle, .08 + before_bias * .5, delta=.0005)

  def test_release_uses_clipped_base_not_raw_curvature(self):
    controller = FordVirtualAngleController()
    before = warm(controller, desired=.1, yaw_rate=1.)
    before_bias = controller.diagnostics['heading_bias']
    self.assertLess(before_bias, -.04)
    # Both requests give clipped base C1=.5. Scaling a negative bias by the raw
    # curvature reduction would increase total C1 during a release.
    after = step(controller, 2., desired=.09, yaw_rate=1., pscm_status=PscmStatus(2., 2, 2, 2, False))
    self.assertLessEqual(controller.diagnostics['heading_bias'], before_bias)
    self.assertLessEqual(after.path_angle, before.path_angle + .0005)
    self.assertGreaterEqual(after.path_angle, 0.)

  def test_host_field_limit_prevents_hidden_integral_growth(self):
    controller = FordVirtualAngleController()
    for i in range(500):
      command = step(controller, i * .01, desired=.1, yaw_rate=0.)
      self.assertAlmostEqual(controller.diagnostics['heading_bias'], 0., places=10)
      self.assertLessEqual(abs(command.path_angle), .5)
    self.assertAlmostEqual(command.path_angle, .5, delta=.0005)

  def test_host_slew_limit_does_not_store_undelivered_positive_bias(self):
    controller = FordVirtualAngleController()
    for i in range(30):
      command = step(controller, i * .01, desired=.02, yaw_rate=0.)
      self.assertAlmostEqual(controller.diagnostics['heading_bias'], 0., places=10)
      self.assertLessEqual(command.path_angle, (i + 1) * .005 + .0005)
    for i in range(30, 70):
      step(controller, i * .01, desired=.02, yaw_rate=0.)
    self.assertGreater(controller.diagnostics['heading_bias'], 0.)

  def test_large_or_batched_error_uses_available_host_slew(self):
    for measurement_period, yaw_rate in ((.01, -.4), (.02, -.1)):
      with self.subTest(measurement_period=measurement_period, yaw_rate=yaw_rate):
        controller = FordVirtualAngleController()
        previous = 0.
        for i in range(600):
          now = i * .01
          measurement_time = math.floor((now + 1e-6) / measurement_period) * measurement_period
          command = step(controller, now, desired=.04, speed=5., yaw_rate=yaw_rate, measurement_time=measurement_time)
          self.assertLessEqual(abs(command.path_angle - previous), .005501)
          self.assertLessEqual(abs(command.path_angle), .5)
          previous = command.path_angle
        # An increment larger than a control tick's available slew must admit
        # its deliverable portion, rather than permanently disabling feedback.
        self.assertGreater(controller.diagnostics['heading_bias'], .05)
        self.assertGreater(command.path_angle, .40)

  def test_can_packing_preserves_the_combined_feedback_command(self):
    controller = FordVirtualAngleController()
    base = FordVirtualAngleController()
    packer = CANPacker('ford_lincoln_base_pt')
    parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
    bus = CanBus(fingerprint={0: {}})
    bias_seen = False
    for i in range(600):
      sign = 1 if i < 300 else -1
      command = step(controller, i * .01, desired=sign * .02, yaw_rate=sign * .08)
      base_command = step(base, i * .01, desired=sign * .02, yaw_rate=sign * .08, pscm_status=None)
      self.assertEqual(command.path_offset, base_command.path_offset)
      bias_seen |= abs(controller.diagnostics['heading_bias']) > .04
      msg = custom.CarControlSP.new_message()
      msg.fordLateralPath.pathOffset = command.path_offset
      msg.fordLateralPath.pathAngle = command.path_angle
      packet = create_lat_ctl2_msg(packer, bus, 2, -msg.fordLateralPath.pathOffset, -msg.fordLateralPath.pathAngle, 0., 0., i % 16)
      parser.update([i * 10_000_000, [packet]])
      decoded = parser.vl['LateralMotionControl2']
      self.assertAlmostEqual(decoded['LatCtlPathOffst_L_Actl'], -command.path_offset)
      self.assertAlmostEqual(decoded['LatCtlPath_An_Actl'], -command.path_angle)
      self.assertEqual(decoded['LatCtlCurv_No_Actl'], 0.)
      self.assertEqual(decoded['LatCtlCrv_NoRate2_Actl'], 0.)
    self.assertTrue(bias_seen)

  def test_recorded_requests_use_pscm_guards_without_changing_c0(self):
    directory = Path(__file__).parent / 'fixtures'
    status_fixture = directory / 'ford_heading_feedback_route80_status.npz'
    metadata = json.loads(status_fixture.with_suffix('.json').read_text())
    base_fixture = directory / metadata['base_fixture']
    self.assertEqual(hashlib.sha256(status_fixture.read_bytes()).hexdigest(), metadata['fixture_sha256'])
    self.assertEqual(hashlib.sha256(base_fixture.read_bytes()).hexdigest(), metadata['base_fixture_sha256'])
    data, eps = dict(np.load(base_fixture)), dict(np.load(status_fixture))
    np.testing.assert_array_equal(data['t'], eps['t'])
    models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in data['models']]
    previous_episode = None
    commands, bases, biases, gates = [], [], [], []
    limit_guards = 0
    for i, now in enumerate(data['t']):
      if data['episode'][i] != previous_episode:
        controller = FordVirtualAngleController()
        base_controller = FordVirtualAngleController(tuning=PathTuning(feedback_gain=0.))
        previous_episode = data['episode'][i]
      pscm = PscmStatus(float(eps['pscm_timestamp'][i]), int(eps['lateral_state'][i]), int(eps['limit'][i]),
                        int(eps['capability'][i]), bool(eps['denied'][i]), bool(eps['valid'][i]))
      inputs = {'yaw_rate': data['yaw_rate'][i], 'speed': data['speed'][i], 'now': now,
                'measurement_time': data['measurement_time'][i], 'model_time': data['model_time'][i],
                'reference_time': data['reference_time'][i], 'active': bool(data['active'][i]), 'valid': bool(data['valid'][i]),
                'steering_pressed': bool(data['pressed'][i]), 'steering_torque': float(eps['steering_torque'][i]), 'pscm_status': pscm}
      command = controller.update(models[data['model_index'][i]], data['desired_curvature'][i], **inputs)
      base = base_controller.update(models[data['model_index'][i]], data['desired_curvature'][i], **inputs)
      commands.append((command.path_offset, command.path_angle, command.curvature, command.curvature_rate))
      bases.append((base.path_offset, base.path_angle))
      gates.append(command.valid)
      biases.append(controller.diagnostics['heading_bias'])
      if pscm.limit == 2:
        self.assertNotEqual(controller.diagnostics['feedback_status'], 'integrating')
      limit_guards += controller.diagnostics['feedback_status'] in ('pscm_limit', 'pscm_backoff')
    commands, bases, biases = np.array(commands), np.array(bases), np.array(biases)
    np.testing.assert_array_equal(commands[:, 0], bases[:, 0])
    np.testing.assert_array_equal(gates, data['v3_valid'])
    np.testing.assert_array_equal(commands[:, 2:], 0.)
    self.assertGreater(limit_guards, 0)
    for episode in (0, 2):
      mask = (data['episode'] == episode) & data['evidence'] & data['benchmark_clean']
      # Recorded motion is frozen: this establishes correction direction only,
      # not that a new vehicle drive will close the observed tracking deficit.
      self.assertGreater(float(np.max(biases[mask])), .001)
      self.assertGreater(float(np.max(commands[mask, 1] - bases[mask, 1])), .005)


if __name__ == '__main__':
  unittest.main()
