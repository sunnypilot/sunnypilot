import unittest

from opendbc.car.toyota.carstate import AccelPersonality, get_accel_personality


class TestDriveMode(unittest.TestCase):
  def test_acceleration_profile_mapping(self):
    self.assertEqual(get_accel_personality(0, 0), AccelPersonality.normal)
    self.assertEqual(get_accel_personality(0, 1), AccelPersonality.eco)
    self.assertEqual(get_accel_personality(1, 0), AccelPersonality.sport)
    self.assertEqual(get_accel_personality(1, 1), AccelPersonality.sport)


if __name__ == "__main__":
  unittest.main()
