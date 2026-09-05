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
    commands, gates, statuses = [], [], []
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
    cls.commands = np.array(commands)
    cls.gates = np.array(gates)
    cls.statuses = np.array(statuses)

  def test_c0_and_output_gates_match_frozen_v3(self):
    np.testing.assert_array_equal(self.commands[:, 0], self.data['v3_replay'][:, 0])
    np.testing.assert_array_equal(self.gates, self.data['v3_valid'])
    np.testing.assert_array_equal(self.statuses, self.data['v3_status'])
    np.testing.assert_array_equal(self.commands[:, 2:], 0.)

  def test_recorded_turns_follow_the_common_curvature_heading(self):
    # Expected values come from the independent shadow candidate evaluated on
    # these frozen route inputs. This checks commands, not new vehicle motion.
    np.testing.assert_array_equal(self.commands[:, 1], self.data['expected_common_c1'])
    for episode, expected_heading in enumerate((.14375, .286, .1895)):
      mask = (self.data['episode'] == episode) & self.data['evidence'] & self.data['benchmark_clean']
      self.assertGreater(int(mask.sum()), 100)
      self.assertAlmostEqual(float(np.median(abs(self.commands[mask, 1]))), expected_heading, delta=.001)
    # The over-response witness previously held C1 at its bound even though the
    # selected action requested substantially less heading over the same preview.
    mask = (self.data['episode'] == 1) & self.data['evidence'] & self.data['benchmark_clean']
    self.assertAlmostEqual(float(np.median(abs(self.data['recorded'][mask, 1]))), .5, delta=.0005)
    self.assertLess(float(np.median(abs(self.commands[mask, 1]))), .30)


if __name__ == '__main__':
  unittest.main()
