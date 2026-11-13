"""Path steering (recent_paths.py). Run on the device with:
  /usr/local/venv/bin/python -m unittest openpilot.sunnypilot.modeld_v2.tests.test_recent_paths"""
import unittest

import numpy as np

from openpilot.sunnypilot.modeld_v2 import recent_paths
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

T = ModelConstants.T_IDXS


def path(yaw_rate, v, harder=0.0):
  """A path's yaw rates and speeds at the model's time steps: turning at yaw_rate now, `harder` more every second."""
  t = np.asarray(T)
  return yaw_rate + harder * t, np.full(len(t), float(v))


class TestRecentPaths(unittest.TestCase):
  def run_frames(self, steer, frames, yaw_rate, v, action, cued):
    asked = 0.0
    for _ in range(frames):
      asked = steer.update(*path(yaw_rate, v), action, cued, v, 0.4, 0.05)
    return asked

  def test_with_no_signal_the_action_decides(self):
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    self.assertAlmostEqual(self.run_frames(steer, 60, 0.08, 4.0, 0.005, False), 0.005, places=9)

  def test_while_a_turn_is_signalled_the_paths_steer(self):
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    self.assertAlmostEqual(self.run_frames(steer, 60, 0.08, 4.0, 0.005, True), 0.08 / 4.0, places=9)

  def test_the_move_over_to_the_paths_takes_the_fade_time_and_never_jumps(self):
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    self.run_frames(steer, 40, 0.08, 4.0, 0.005, False)
    asked = [steer.update(*path(0.08, 4.0), 0.005, True, 4.0, 0.4, 0.05) for _ in range(20)]
    steps = np.diff([0.005] + asked)
    self.assertTrue((steps >= -1e-12).all())
    self.assertLessEqual(steps.max(), (0.02 - 0.005) * 0.05 / recent_paths.FADE + 1e-9)
    self.assertAlmostEqual(asked[11], 0.02, places=9)   # 0.6 s at 20 Hz

  def test_on_faster_roads_the_action_steers_alone(self):
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    self.assertAlmostEqual(self.run_frames(steer, 60, 0.4, 20.0, 0.005, True), 0.005, places=9)
    mixed = recent_paths.SignalSteer(T, anchor_turns=False)
    self.assertAlmostEqual(self.run_frames(mixed, 60, 0.22, 11.0, 0.005, True), 0.5 * 0.02 + 0.5 * 0.005, places=9)

  def test_paths_that_agree_about_the_road_give_no_delay(self):
    # every path knows the road turns harder the further along it is; the car drives slower than the paths expect
    paths = recent_paths.RecentPaths(T)
    road = lambda s: 0.002 * s
    odometer, t = 0.0, np.asarray(T)
    for _ in range(60):
      rates = 4.0 * np.array([road(odometer + 4.0 * x) for x in t])
      own, _ = paths.update(rates, np.full(len(t), 4.0), 0.0, 2.0, 0.5, 0.05)
      here = odometer
      odometer += 2.0 * 0.05
    self.assertAlmostEqual(own, road(here + 2.0 * 0.5), delta=2e-3 * road(here + 1.0))

  def test_one_frames_error_counts_for_little(self):
    rng = np.random.default_rng(0)
    paths, alone, averaged = recent_paths.RecentPaths(T), [], []
    for _ in range(400):
      rates, speeds = path(0.1 + rng.normal(0, 0.02), 4.0)
      own, _ = paths.update(rates, speeds, 0.0, 4.0, 0.4, 0.05)
      alone.append(rates[0] / 4.0)
      averaged.append(own)
    self.assertLess(np.std(averaged[40:]), 0.35 * np.std(alone[40:]))

  def test_a_reset_forgets_everything(self):
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    self.run_frames(steer, 30, 0.08, 4.0, 0.005, True)
    steer.reset()
    fresh = recent_paths.SignalSteer(T, anchor_turns=False)
    self.assertAlmostEqual(steer.update(*path(0.0, 4.0), 0.01, False, 4.0, 0.4, 0.05),
                           fresh.update(*path(0.0, 4.0), 0.01, False, 4.0, 0.4, 0.05), places=12)

  # the two switches (PathSteeringPursuit, PathSteeringGeometry)

  def straight_path(self, v, side=0.0):
    """A straight path at speed v, `side` m to the left of the car and parallel to it, in the car's frame."""
    t = np.asarray(T)
    xy = np.stack([v * t, np.full(len(t), side)], 1)
    xy[0, 1] = 0.0
    return np.zeros(len(t)), np.full(len(t), float(v)), xy, np.zeros(len(t))

  def test_switches_off_change_nothing(self):
    plain, wired = recent_paths.SignalSteer(T, anchor_turns=False), recent_paths.SignalSteer(T, anchor_turns=False)
    rng = np.random.default_rng(1)
    for _ in range(40):
      rates, speeds = path(0.1 + rng.normal(0, 0.02), 4.0)
      xy = np.stack([4.0 * np.asarray(T), rng.normal(0, 0.3, len(T))], 1)
      a = plain.update(rates, speeds, 0.01, True, 4.0, 0.4, 0.05)
      b = wired.update(rates, speeds, 0.01, True, 4.0, 0.4, 0.05, xy, rng.normal(0, 0.1, len(T)), 0.02)
      self.assertAlmostEqual(a, b, places=12)

  def test_pursuit_steers_back_to_a_path_the_car_has_drifted_off(self):
    # every path says: go straight, 0.5 m to the left. The paths' own ask (curvature only) never moves the car there
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    steer.pursuit = True
    for _ in range(40):
      rates, speeds, xy, yaws = self.straight_path(4.0, side=0.5)
      asked = steer.update(rates, speeds, 0.0, True, 4.0, 0.4, 0.05, xy, yaws, 0.0)
    look = max(recent_paths.PURSUIT_MIN, 4.0 * (0.4 + recent_paths.PURSUIT_LEAD))
    self.assertGreater(asked, 0.5 * 2 * 0.5 / look ** 2)  # steers left, about as hard as an arc onto the path
    self.assertLess(asked, 2.0 * 2 * 0.5 / look ** 2)

  def test_pursuit_follows_a_steady_turn_exactly(self):
    # on an arc the car is already on, pure pursuit asks for the arc's own curvature
    k, v = 0.05, 4.0
    t = np.asarray(T)
    s = v * t
    xy, yaws = np.stack([np.sin(k * s) / k, (1 - np.cos(k * s)) / k], 1), k * s
    steer = recent_paths.SignalSteer(T, anchor_turns=False)
    steer.pursuit = True
    for _ in range(40):
      asked = steer.update(np.full(len(t), k * v), np.full(len(t), v), k, True, v, 0.4, 0.05, xy, yaws, k)
    self.assertAlmostEqual(asked, k, delta=0.02 * k)

  def test_pursuit_knows_the_car_has_moved_since_an_old_path(self):
    # one path to the left; then the car really moves over and the paths stop coming: it is no longer asked to turn
    paths = recent_paths.RecentPaths(T)
    rates, speeds, xy, yaws = self.straight_path(4.0, side=0.5)
    paths.update(rates, speeds, 0.0, 4.0, 0.4, 0.05, xy, yaws, 0.0)
    first = paths.pursuit
    paths.held[0]['pose'][1] = 0.5  # as if dead reckoning had carried the car over onto that path
    rates, speeds, xy, yaws = self.straight_path(4.0, side=0.0)  # and the newest path agrees: straight on from here
    paths.update(rates, speeds, 0.0, 4.0, 0.4, 0.05, xy, yaws, 0.0)
    self.assertGreater(first, 0.01)
    self.assertLess(abs(paths.pursuit - 0.0), 0.5 * first)

  def test_geometric_curvature_reads_a_path_by_its_shape(self):
    # a path whose yaw rates are noisy at a creeping planned speed, but whose shape is a clean arc
    k, v = 0.05, 1.0
    t = np.asarray(T)
    s = v * t
    xy, yaws = np.stack([np.sin(k * s) / k, (1 - np.cos(k * s)) / k], 1), k * s
    rng = np.random.default_rng(2)
    by_rate, by_shape = recent_paths.RecentPaths(T), recent_paths.RecentPaths(T)
    for _ in range(40):
      rates = k * v + rng.normal(0, 0.05, len(t))
      own_rate, _ = by_rate.update(rates, np.full(len(t), v), k, v, 0.4, 0.05)
      own_shape, _ = by_shape.update(rates, np.full(len(t), v), k, v, 0.4, 0.05, xy, yaws, k, geometric=True)
    self.assertAlmostEqual(own_shape, k, delta=0.05 * k)
    self.assertLess(abs(own_shape - k), abs(own_rate - k) + 1e-9)

  def test_geometric_curvature_falls_back_on_a_path_too_short_to_read(self):
    t = np.asarray(T)
    xy = np.stack([0.1 * t, np.zeros(len(t))], 1)  # 1 m in 10 s: about to stop
    paths, plain = recent_paths.RecentPaths(T), recent_paths.RecentPaths(T)
    rates, speeds = path(0.02, 0.1)
    a, _ = paths.update(rates, speeds, 0.0, 0.5, 0.4, 0.05, xy, np.zeros(len(t)), 0.0, geometric=True)
    b, _ = plain.update(rates, speeds, 0.0, 0.5, 0.4, 0.05)
    self.assertAlmostEqual(a, b, places=12)


if __name__ == "__main__":
  unittest.main()
