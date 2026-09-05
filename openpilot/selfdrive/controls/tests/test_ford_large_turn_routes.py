import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController, PscmStatus


class TestFordLargeTurnRoutes(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.fixture = Path(__file__).parent / 'fixtures/ford_large_turn_requests_route83.npz'
    cls.metadata = json.loads(cls.fixture.with_suffix('.json').read_text())
    cls.data = dict(np.load(cls.fixture))
    cls.models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in cls.data['models']]
    data = cls.data
    commands, gates, statuses, bases, targets, errors, before_backoff = [], [], [], [], [], [], []
    backoff_active, previous_commands, repeated_measurements = [], [], []
    previous_episode = None
    for i, now in enumerate(data['t']):
      if data['episode'][i] != previous_episode:
        controller = FordVirtualAngleController(response_delay=cls.metadata['response_delay'])
        previous_episode = data['episode'][i]
      pscm = PscmStatus(float(data['pscm_timestamp'][i]), int(data['pscm_lateral_state'][i]), int(data['pscm_limit'][i]),
                        int(data['pscm_capability'][i]), bool(data['pscm_denied'][i]), bool(data['pscm_valid'][i]))
      previous_base, previous_bias = controller.feedback.previous_base, controller.feedback.bias
      previous_commands.append(controller.heading_request)
      repeated_measurements.append(data['measurement_time'][i] == controller.feedback.last_measurement_time)
      path = controller.update(cls.models[data['model_index'][i]], data['desired_curvature'][i],
                               yaw_rate=data['yaw_rate'][i], speed=data['speed'][i], now=now,
                               measurement_time=data['measurement_time'][i], model_time=data['model_time'][i],
                               reference_time=data['reference_time'][i], active=bool(data['active'][i]), valid=bool(data['valid'][i]),
                               steering_pressed=bool(data['pressed'][i]), steering_torque=data['steering_torque'][i], pscm_status=pscm)
      commands.append((path.path_offset, path.path_angle, path.curvature, path.curvature_rate))
      gates.append(path.valid)
      statuses.append(controller.diagnostics['feedback_status'])
      base = controller.diagnostics.get('heading_base', 0.)
      # Account for release of the base before testing the direction of the
      # separate constrained feedback step on these changing recorded requests.
      retained_bias = previous_bias
      if previous_base is None or previous_base * base < 0.:
        retained_bias = 0.
      elif previous_base:
        retained_bias *= min(1., abs(base / previous_base))
      before_backoff.append(base + retained_bias)
      bases.append(base)
      targets.append(controller.diagnostics.get('heading_target', 0.))
      errors.append(controller.diagnostics.get('feedback_yaw_error') or 0.)
      backoff_active.append(controller.diagnostics.get('feedback_backoff_active', False))
    cls.commands, cls.gates, cls.statuses = np.array(commands), np.array(gates), np.array(statuses)
    cls.bases, cls.targets, cls.errors, cls.before_backoff = np.array(bases), np.array(targets), np.array(errors), np.array(before_backoff)
    cls.backoff_active = np.array(backoff_active)
    cls.previous_commands, cls.repeated_measurements = np.array(previous_commands), np.array(repeated_measurements)

  def test_fixture_authority_targets_are_recorded_successes(self):
    self.assertEqual(hashlib.sha256(self.fixture.read_bytes()).hexdigest(), self.metadata['fixture_sha256'])
    authority_targets = 0
    for i, window in enumerate(self.metadata['windows']):
      if window['role'] != 'authority_target':
        continue
      authority_targets += 1
      mask = self.data['window_masks'][:, i]
      ratio = np.median(self.data['recorded_response_curvature_02s'][mask] / self.data['desired_curvature'][mask])
      self.assertGreaterEqual(ratio, .90)
      self.assertLessEqual(ratio, 1.10)
      self.assertGreaterEqual(np.max(abs(self.data['wheel_deg'][mask])), 150.)
    self.assertGreaterEqual(authority_targets, 2)
    over = next(window for window in self.metadata['windows'] if window['name'] == 'large_over_response_290deg')
    self.assertEqual(over['role'], 'over_response_challenge_not_target')

  def test_successful_large_turns_retain_recorded_command_scale(self):
    # The requirement is command construction, not a predicted wheel response.
    # Retain at least 85% of the successful send-clamped C0/C1 medians during
    # the complete eligible turn, held request, and eligible increasing request.
    for i, window in enumerate(self.metadata['windows']):
      if window['role'] != 'authority_target':
        continue
      for phase in (None, 'phase_held', 'phase_turn_in'):
        with self.subTest(window=window['name'], phase=phase):
          mask = self.data['window_masks'][:, i].copy()
          if phase is not None:
            mask &= self.data[phase]
          self.assertGreaterEqual(int(mask.sum()), 10)
          recorded = np.median(abs(self.data['recorded_send_clamped'][mask, :2]), axis=0)
          candidate = np.median(abs(self.commands[mask, :2]), axis=0)
          self.assertTrue(np.all(candidate >= .85 * recorded), (candidate, recorded))
          self.assertGreater(np.median(self.commands[mask, 0] * self.data['desired_curvature'][mask]), 0.)
          self.assertGreater(np.median(self.commands[mask, 1] * self.data['desired_curvature'][mask]), 0.)

  def test_small_release_and_reversal_keep_curvature_centering(self):
    for i, window in enumerate(self.metadata['windows']):
      if window['role'] not in ('release', 'reversal'):
        continue
      with self.subTest(window=window['name']):
        mask = self.data['window_masks'][:, i]
        np.testing.assert_array_equal(self.commands[mask, 0], self.data['v5_full_replay'][mask, 0])
        np.testing.assert_array_equal(self.bases[mask], self.data['v5_full_heading_base'][mask])

  def test_all_windows_respect_gates_limits_and_pscm_guards(self):
    data = self.data
    np.testing.assert_array_equal(self.commands[:, 2:], 0.)
    np.testing.assert_array_equal(self.gates[data['evidence']], data['v5_full_valid'][data['evidence']])
    self.assertTrue(np.isfinite(self.commands).all())
    self.assertTrue((abs(self.commands[:, :2]) <= np.array([5.110000001, .500000001])).all())
    continuous = (data['episode'][1:] == data['episode'][:-1]) & self.gates[1:] & self.gates[:-1]
    limits = np.diff(data['t'])[:, None] * np.array([4., .5]) + np.array([.01, .0005]) + 1e-8
    self.assertTrue((abs(np.diff(self.commands[:, :2], axis=0))[continuous] <= limits[continuous]).all())
    limited = data['pscm_limit'] >= 2
    self.assertFalse(np.isin(self.statuses[limited], ('integrating', 'host_limit')).any())

  def test_constrained_backoff_only_reduces_same_sign_heading(self):
    backoff = np.isin(self.statuses, ('release_backoff', 'pscm_backoff'))
    self.assertGreater(int(backoff.sum()), 100)
    self.assertTrue((self.errors[backoff] * self.bases[backoff] < 0.).all())
    current_error = self.data['speed'] * self.data['desired_curvature'] - self.data['yaw_rate']
    self.assertTrue((current_error[backoff] * self.bases[backoff] < 0.).all())
    self.assertTrue((self.before_backoff[backoff] * self.bases[backoff] > 0.).all())
    self.assertTrue((abs(self.targets[backoff]) <= abs(self.before_backoff[backoff]) + 1e-10).all())
    self.assertTrue((self.targets[backoff] * self.bases[backoff] >= -1e-12).all())

  def test_recorded_over_response_gets_heading_backoff(self):
    index = next(i for i, window in enumerate(self.metadata['windows']) if window['name'] == 'large_over_response_290deg')
    mask = self.data['window_masks'][:, index]
    # With this same v6 feedforward and the former freeze-only feedback policy,
    # the recorded challenge's median C1 is .5 rad. Require a measurable command
    # reduction, not a simulated improvement in the old vehicle trajectory.
    self.assertLess(float(np.median(abs(self.commands[mask, 1]))), .5 - .02)
    self.assertTrue(np.isin(self.statuses[mask], ('release_backoff', 'pscm_backoff')).any())
    # The overshooting fallback C0 is a ceiling comparison, never an authority
    # target that a test should force the candidate to reach or exceed.
    self.assertLessEqual(float(np.median(abs(self.commands[mask, 0]))),
                         float(np.median(abs(self.data['recorded_send_clamped'][mask, 0]))) + .01)

  def test_backoff_ceiling_prevents_heading_growth_between_measurements(self):
    # A rising model heading must not outweigh a measured backoff, including
    # controller ticks that reuse the same CAN yaw observation. C0 is separate.
    mask = self.backoff_active
    self.assertGreater(int(mask.sum()), 100)
    ceiling = np.maximum(0., np.sign(self.bases[mask]) * self.previous_commands[mask])
    self.assertTrue((abs(self.targets[mask]) <= ceiling + 1e-10).all())
    self.assertTrue((self.targets[mask] * self.bases[mask] >= -1e-12).all())
    self.assertTrue((abs(self.commands[mask, 1]) <= abs(self.previous_commands[mask]) + .0005 + 1e-10).all())
    repeated = mask & self.repeated_measurements
    self.assertGreater(int(repeated.sum()), 0)
    self.assertTrue((self.statuses[repeated] == 'no_new_measurement').all())

  def test_feedback_error_sign_with_a_large_recorded_model(self):
    window_index = next(i for i, window in enumerate(self.metadata['windows']) if window['name'] == 'successful_large_181deg')
    indices = np.flatnonzero(self.data['window_masks'][:, window_index] & self.data['phase_held'])
    index = int(indices[len(indices) // 2])
    recorded_model = self.data['models'][self.data['model_index'][index]]
    magnitude = abs(self.data['desired_curvature'][index])
    speed = self.data['speed'][index]
    original_sign = np.sign(self.data['desired_curvature'][index])
    # Hold this recorded geometry and request while varying the yaw observation.
    # This tests feedback direction with model-pose feedforward, not plant motion.
    for sign in (-1., 1.):
      model = SimpleNamespace(position=SimpleNamespace(x=recorded_model[0], y=recorded_model[1] * sign / original_sign),
                              orientation=SimpleNamespace(z=recorded_model[2] * sign / original_sign))
      for response_fraction in (.5, 1.5):
        with self.subTest(sign=sign, response_fraction=response_fraction):
          controller = FordVirtualAngleController()
          for i in range(400):
            now = i * .01
            controller.update(model, sign * magnitude, yaw_rate=sign * magnitude * speed * response_fraction,
                              speed=speed, now=now, measurement_time=now, model_time=now, reference_time=now, active=True,
                              pscm_status=PscmStatus(now, 2, 0, 2, False))
          self.assertEqual(controller.diagnostics['base_guard'], 'model_pose')
          correction_along_error = controller.diagnostics['heading_bias'] * sign * np.sign(1. - response_fraction)
          self.assertGreater(correction_along_error, .01)


if __name__ == '__main__':
  unittest.main()
