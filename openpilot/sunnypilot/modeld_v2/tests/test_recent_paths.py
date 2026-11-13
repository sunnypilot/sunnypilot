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


if __name__ == "__main__":
  unittest.main()
