import unittest

from opendbc.sunnypilot.car.toyota.brake_onset import (BrakeOvershootLimiter, OVERSHOOT_CMD_CEIL, OVERSHOOT_DEADBAND,
                                                       OVERSHOOT_MAX, OVERSHOOT_MOD_DEADBAND, OVERSHOOT_MOD_KEEP,
                                                       OVERSHOOT_MOD_RATE)

DT = 0.03


class TestBrakeOvershootLimiter(unittest.TestCase):
  def run_steady(self, req, a_ego, n=200, active=True):
    lim = BrakeOvershootLimiter(DT)
    for _ in range(n):
      lim.update(req, a_ego, active)
    return lim

  def test_moderate_braking_is_untouched(self):
    self.assertEqual(self.run_steady(-2.0, -3.0).lift, 0.0)

  def test_overshoot_inside_the_deadband_is_untouched(self):
    self.assertEqual(self.run_steady(-3.4, -3.4 - OVERSHOOT_DEADBAND + 0.01).lift, 0.0)

  def test_19_41_overshoot_is_taken_back(self):
    lim = self.run_steady(-3.4, -4.3)
    self.assertAlmostEqual(lim.lift, 0.8 * (0.9 - OVERSHOOT_DEADBAND), places=6)
    self.assertAlmostEqual(lim.apply(-3.4), -3.4 + lim.lift, places=6)

  def test_under_braking_never_lifts(self):
    self.assertEqual(self.run_steady(-3.4, -2.5).lift, 0.0)

  def test_lift_is_capped_and_command_stays_a_firm_brake(self):
    lim = self.run_steady(-2.6, -6.0)
    self.assertEqual(lim.lift, OVERSHOOT_MAX)
    self.assertAlmostEqual(lim.apply(-2.6), -2.6 + OVERSHOOT_MAX)
    self.assertEqual(lim.apply(-2.2), OVERSHOOT_CMD_CEIL)   # a PID-lightened command is not lifted past a firm brake

  def test_lift_grows_and_fades_gradually(self):
    lim = BrakeOvershootLimiter(DT)
    prev = 0.0
    for _ in range(10):
      lift = lim.update(-3.4, -5.0)
      self.assertLessEqual(lift - prev, 3.0 * DT + 1e-9)
      prev = lift
    for _ in range(10):
      lift = lim.update(-1.0, -1.0)   # the hard request ends
      self.assertLessEqual(prev - lift, 2.0 * DT + 1e-9)
      prev = lift

  def test_inactive_gives_it_back(self):
    lim = self.run_steady(-3.4, -4.3)
    for _ in range(100):
      lim.update(-3.4, -4.3, active=False)
    self.assertEqual(lim.lift, 0.0)


class TestModerateBand(unittest.TestCase):
  """Altis Hybrid only: route 0000010e 17:38:41, asked -1.60 at 40-50 km/h, the car delivered -1.95."""
  def run_steady(self, req, a_ego, v_kph, moderate=True, n=200):
    lim = BrakeOvershootLimiter(DT, moderate=moderate)
    for _ in range(n):
      lim.update(req, a_ego, True, v_ego=v_kph / 3.6)
    return lim

  def test_17_38_41_overshoot_is_taken_back(self):
    lim = self.run_steady(-1.60, -1.95, 45.0)
    self.assertAlmostEqual(lim.lift, 0.8 * (0.35 - OVERSHOOT_MOD_DEADBAND), places=4)  # low-pass converged
    self.assertAlmostEqual(lim.apply(-1.60), -1.60 + lim.lift, places=6)

  def test_never_lighter_than_three_quarters_of_the_command(self):
    lim = self.run_steady(-1.2, -3.0, 45.0)
    self.assertAlmostEqual(lim.apply(-1.2), OVERSHOOT_MOD_KEEP * -1.2, places=6)

  def test_off_for_other_cars_low_speed_and_light_requests(self):
    self.assertEqual(self.run_steady(-1.60, -1.95, 45.0, moderate=False).lift, 0.0)
    self.assertEqual(self.run_steady(-1.60, -1.95, 10.0).lift, 0.0)
    self.assertEqual(self.run_steady(-0.9, -1.4, 45.0).lift, 0.0)
    self.assertEqual(self.run_steady(-1.60, -1.70, 45.0).lift, 0.0)  # inside the deadband

  def test_hard_band_unchanged_with_moderate_on(self):
    lim = self.run_steady(-3.4, -4.3, 45.0)
    self.assertAlmostEqual(lim.lift, 0.8 * (0.9 - OVERSHOOT_DEADBAND), places=6)
    self.assertAlmostEqual(lim.apply(-3.4), -3.4 + lim.lift, places=6)

  def test_moderate_band_is_a_slow_smooth_trim(self):
    lim = BrakeOvershootLimiter(DT, moderate=True)
    prev = 0.0
    for k in range(100):
      a = -1.95 if k % 2 else -1.45   # noisy aEgo around -1.70 at a steady -1.60 request
      lift = lim.update(-1.60, a, True, v_ego=45 / 3.6, a_ego=a)
      self.assertLessEqual(abs(lift - prev), OVERSHOOT_MOD_RATE * DT + 1e-9)
      prev = lift
    self.assertEqual(lift, 0.0)   # averaged overshoot 0.10 is inside the deadband

  def test_moderate_band_only_in_relaxed(self):
    lim = BrakeOvershootLimiter(DT, moderate=True)
    for _ in range(200):
      lim.update(-1.60, -1.95, True, v_ego=45 / 3.6, moderate_allowed=False)
    self.assertEqual(lim.lift, 0.0)
    for _ in range(200):
      lim.update(-3.4, -4.3, True, v_ego=45 / 3.6, moderate_allowed=False)   # the hard band in every personality
    self.assertGreater(lim.lift, 0.5)


if __name__ == "__main__":
  unittest.main()
