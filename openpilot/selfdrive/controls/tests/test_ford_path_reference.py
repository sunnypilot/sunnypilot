import math
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import custom

from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController


def circle(curvature=0.0, offset=0.0):
  arc = np.linspace(0, 60, 241)
  heading = curvature * arc
  x = np.sin(heading) / curvature if curvature else arc
  y = (1 - np.cos(heading)) / curvature if curvature else np.zeros(len(arc))
  return SimpleNamespace(position=SimpleNamespace(x=x, y=y + offset), orientation=SimpleNamespace(z=heading))


def run_step(controller, model, t, curvature=0.0, speed=8.0, **kwargs):
  inputs = {'yaw_rate': curvature * speed, 'speed': speed, 'now': t, 'measurement_time': t,
            'model_time': math.floor((t + 1e-6) / .05) * .05, 'active': True}
  inputs.update(kwargs)
  return controller.update(model, **inputs)


class TestFordPathReference(unittest.TestCase):
  def test_c0_preserves_centering_when_curvature_and_heading_are_zero(self):
    for offset in (-.8, .8):
      controller = FordVirtualAngleController()
      model = circle(offset=offset)
      for i in range(500):
        path = run_step(controller, model, i * .01)
      self.assertAlmostEqual(path.path_offset, offset, delta=.01)
      self.assertAlmostEqual(path.path_angle, 0., delta=.0005)
      self.assertEqual((path.curvature, path.curvature_rate), (0, 0))

  def test_large_path_demands_survive_even_when_measured_curvature_matches(self):
    for sign in (-1, 1):
      for curvature, speed, min_offset, min_heading in ((.02, 8., .4, .14), (.08, 4., 1.8, .45)):
        controller = FordVirtualAngleController()
        model = circle(sign * curvature)
        for i in range(600):
          path = run_step(controller, model, i * .01, curvature=sign * curvature, speed=speed)
        self.assertGreater(sign * path.path_offset, min_offset)
        self.assertGreater(sign * path.path_angle, min_heading)
        self.assertEqual((path.curvature, path.curvature_rate), (0, 0))

  def test_ego_motion_is_not_delayed_by_the_model_filter(self):
    controller = FordVirtualAngleController()
    model = circle(offset=.5)
    run_step(controller, model, 0., curvature=.02, speed=10.)
    initial = tuple(a.copy() for a in controller.reference.path)
    for i in range(1, 11):
      run_step(controller, model, i * .01, curvature=.02, speed=10., model_time=0.)
    _, x, y, heading = controller.reference.path
    yaw = .02  # 1 m traveled on 0.02/m curvature
    dx, dy = math.sin(yaw) / .02, (1 - math.cos(yaw)) / .02
    expected_x = math.cos(yaw) * (initial[1] - dx) + math.sin(yaw) * (initial[2] - dy)
    expected_y = -math.sin(yaw) * (initial[1] - dx) + math.cos(yaw) * (initial[2] - dy)
    np.testing.assert_allclose(x, expected_x, atol=1e-10)
    np.testing.assert_allclose(y, expected_y, atol=1e-10)
    np.testing.assert_allclose(heading, initial[3] - yaw, atol=1e-10)

  def test_model_noise_is_filtered_without_losing_a_centering_offset(self):
    controller = FordVirtualAngleController()
    values = []
    for i in range(1600):
      t = i * .01
      mt = math.floor((t + 1e-6) / .05) * .05
      model = circle(offset=.8 + .1 * math.sin(2 * math.pi * 1.78 * mt))
      path = run_step(controller, model, t)
      values.append(path.path_offset)
    values = np.array(values[600:])
    self.assertAlmostEqual(float(np.mean(values)), .8, delta=.015)
    self.assertLess(float(np.ptp(values)), .09)  # raw offset varies by 0.2 m

  def test_invalid_or_stale_path_resets_and_reengages_from_zero(self):
    for overrides in ({'valid': False}, {'active': False}, {'speed': .1}, {'model_time': 0.},
                      {'measurement_time': 0.}, {'yaw_rate': float('nan')}):
      controller = FordVirtualAngleController()
      for i in range(100):
        run_step(controller, circle(.03), i * .01)
      self.assertEqual(run_step(controller, circle(.03), 1., **overrides), FordPath())
      path = run_step(controller, circle(.03), 1.01)
      self.assertLessEqual(abs(path.path_offset), .05)
      self.assertLessEqual(abs(path.path_angle), .0055)

  def test_clock_faults_clear_the_reference_and_slew_state(self):
    for now, overrides in ((1.04, {}), (1.25, {}), (1.06, {'measurement_time': 1.049}), (1.06, {'model_time': 1.049})):
      controller = FordVirtualAngleController()
      run_step(controller, circle(.03), 1.)
      run_step(controller, circle(.03), 1.05)
      path = run_step(controller, circle(.03), now, **overrides)
      self.assertEqual(path, FordPath())
      self.assertEqual(controller.diagnostics['status'], 'timing_reset')
      self.assertIsNone(controller.reference.path)
      self.assertEqual((controller.offset_request, controller.heading_request), (0., 0.))

  def test_malformed_new_geometry_cannot_keep_an_old_active_request(self):
    malformed = [None, circle(), circle(), circle()]
    malformed[1].position.y[5] = float('nan')
    malformed[2].position.x = []
    malformed[3].position.x[:] = 0.
    for model in malformed:
      controller = FordVirtualAngleController()
      run_step(controller, circle(.03), 1.)
      self.assertEqual(run_step(controller, model, 1.05), FordPath())
      self.assertIsNone(controller.reference.path)

  def test_paired_slew_and_dbc_bounds_during_large_reversal(self):
    controller = FordVirtualAngleController()
    previous = FordPath()
    for i in range(900):
      model = circle(.1 if i < 400 else -.1)
      path = run_step(controller, model, i * .01, speed=5.)
      self.assertLessEqual(abs(path.path_offset), 5.11)
      self.assertLessEqual(abs(path.path_angle), .5)
      self.assertLessEqual(abs(path.path_offset - previous.path_offset), .050001)
      self.assertLessEqual(abs(path.path_angle - previous.path_angle), .005501)
      self.assertEqual((path.curvature, path.curvature_rate), (0, 0))
      previous = path
    self.assertLess(path.path_offset, -1.)
    self.assertLess(path.path_angle, -.3)

  def test_float32_and_can_packing_preserve_the_path(self):
    controller = FordVirtualAngleController()
    packer = CANPacker('ford_lincoln_base_pt')
    parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
    bus = CanBus(fingerprint={0: {}})
    for i in range(600):
      path = run_step(controller, circle(.08 if i < 300 else -.08), i * .01, speed=5.)
      msg = custom.CarControlSP.new_message()
      msg.fordLateralPath.pathOffset = path.path_offset
      msg.fordLateralPath.pathAngle = path.path_angle
      packet = create_lat_ctl2_msg(packer, bus, 2, -msg.fordLateralPath.pathOffset, -msg.fordLateralPath.pathAngle, 0., 0., i % 16)
      parser.update([i * 10_000_000, [packet]])
      decoded = parser.vl['LateralMotionControl2']
      self.assertAlmostEqual(decoded['LatCtlPathOffst_L_Actl'], -path.path_offset)
      self.assertAlmostEqual(decoded['LatCtlPath_An_Actl'], -path.path_angle)
      self.assertEqual(decoded['LatCtlCurv_No_Actl'], 0.)

  def test_recorded_large_maneuvers_keep_substantial_path_demand(self):
    fixture = Path(__file__).parent / 'fixtures/ford_c2_free_path_routes.npz'
    metadata = json.loads(fixture.with_suffix('.json').read_text())
    self.assertEqual(hashlib.sha256(fixture.read_bytes()).hexdigest(), metadata['fixture_sha256'])
    z = np.load(fixture)
    models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in z['models']]
    previous_episode = None
    commands = []
    for i, t in enumerate(z['t']):
      if z['episode'][i] != previous_episode:
        controller = FordVirtualAngleController()
        previous_episode = z['episode'][i]
      path = controller.update(models[z['model_index'][i]], yaw_rate=z['yaw_rate'][i], speed=z['speed'][i], now=t,
                               measurement_time=z['measurement_time'][i], model_time=z['model_time'][i],
                               active=bool(z['active'][i]), valid=bool(z['valid'][i]), steering_pressed=bool(z['pressed'][i]))
      commands.append((path.path_offset, path.path_angle))
      self.assertEqual((path.curvature, path.curvature_rate), (0, 0))
    commands = np.array(commands)
    for episode in range(4):
      mask = (z['episode'] == episode) & z['evidence']
      # Do not reward a quiet controller for throwing away large maneuver demand.
      # This is a command-envelope check against the earlier path controller,
      # not a claim that the measured motion was solely due to these fields.
      reference = np.median(abs(z['recorded'][mask, :2]), axis=0)
      actual = np.median(abs(commands[mask]), axis=0)
      self.assertGreater(actual[0], .7 * reference[0])
      self.assertGreater(actual[1], .7 * reference[1])
      direction = np.sign(np.median(z['recorded'][mask, 1]))
      self.assertGreater(direction * np.median(commands[mask, 1]), 0.)
    for episode in (5, 6):
      mask = (z['episode'] == episode) & z['evidence']
      # Both newly supplied failed turns must receive heading as a path term,
      # rather than the v1 controller's tiny acceleration-error correction.
      self.assertGreater(np.median(abs(commands[mask, 1])), .03)


if __name__ == '__main__':
  unittest.main()
