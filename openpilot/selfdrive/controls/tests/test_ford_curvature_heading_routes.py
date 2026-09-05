import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController


class TestFordCurvatureHeadingRoutes(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    fixture = Path(__file__).parent / 'fixtures/ford_curvature_heading_route80.npz'
    metadata = json.loads(fixture.with_suffix('.json').read_text())
    if hashlib.sha256(fixture.read_bytes()).hexdigest() != metadata['fixture_sha256']:
      raise ValueError('Route80 command fixture hash mismatch')
    cls.data = data = dict(np.load(fixture))
    models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in data['models']]
    previous_episode = None
    commands, gates, statuses, biases = [], [], [], []
    for i, now in enumerate(data['t']):
      if data['episode'][i] != previous_episode:
        controller = FordVirtualAngleController()
        previous_episode = data['episode'][i]
      command = controller.update(models[data['model_index'][i]], data['desired_curvature'][i],
                                  yaw_rate=data['yaw_rate'][i], speed=data['speed'][i], now=now,
                                  measurement_time=data['measurement_time'][i], model_time=data['model_time'][i],
                                  reference_time=data['reference_time'][i], active=bool(data['active'][i]),
                                  valid=bool(data['valid'][i]), steering_pressed=bool(data['pressed'][i]))
      commands.append((command.path_offset, command.path_angle, command.curvature, command.curvature_rate))
      gates.append(command.valid)
      statuses.append(controller.diagnostics['status'])
      biases.append(controller.diagnostics['heading_bias'])
    cls.commands = np.array(commands)
    cls.gates = np.array(gates)
    cls.statuses = np.array(statuses)
    cls.biases = np.array(biases)

  def test_output_gates_match_frozen_v3(self):
    np.testing.assert_array_equal(self.gates, self.data['v3_valid'])
    np.testing.assert_array_equal(self.statuses, self.data['v3_status'])
    np.testing.assert_array_equal(self.commands[:, 2:], 0.)

  def test_missing_pscm_retains_bounded_base_without_integrating(self):
    # These older inputs omit PSCM status. They must retain a usable base and
    # normal output guards without inventing feedback eligibility. Large-turn
    # authority and measured backoff have separate route83 evidence fixtures.
    np.testing.assert_array_equal(self.biases, 0.)
    self.assertTrue(np.isfinite(self.commands).all())
    self.assertLessEqual(float(np.max(abs(self.commands[:, 0]))), 5.11 + 1e-9)
    self.assertLessEqual(float(np.max(abs(self.commands[:, 1]))), .5 + 1e-9)
    np.testing.assert_array_equal(self.commands[~self.gates], 0.)
    for episode in range(3):
      mask = (self.data['episode'] == episode) & self.data['evidence'] & self.data['benchmark_clean']
      self.assertGreater(int(mask.sum()), 100)
      self.assertGreater(float(np.median(abs(self.commands[mask, 1]))), .03)
    continuing = self.gates[1:] & self.gates[:-1] & (np.diff(self.data['episode']) == 0)
    elapsed = np.diff(self.data['t'])[continuing]
    steps = abs(np.diff(self.commands[:, :2], axis=0))[continuing]
    self.assertTrue(np.all(steps[:, 0] <= 4. * elapsed + .010001))
    self.assertTrue(np.all(steps[:, 1] <= .5 * elapsed + .000501))


if __name__ == '__main__':
  unittest.main()
