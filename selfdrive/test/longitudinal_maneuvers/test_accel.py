#!/usr/bin/env python3
import os
import unittest

from common.params import Params
from selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver


maneuvers = [
  # In Stock with jerk cost of 5.0 this results in a maximum desired_dist_diff of 51m
  # Setting jerk cost to 0 drops it down to 25m
  # Setting jerk cost to .5 drops it down to 38m
  Maneuver(
    'Start from standstill behind car acc at 1.2m/s',
    duration=20.,
    initial_speed=0.,
    lead_relevancy=True,
    initial_distance_lead=4,  # In real world the stopping distance is less than desired
    speed_lead_values=[0., 12., 12.],
    breakpoints=[0., 10., 20.],
    cruise_values=[35., 35., 35.],
  ),
]


class LongitudinalControl(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    os.environ['SIMULATION'] = "1"
    os.environ['SKIP_FW_QUERY'] = "1"
    os.environ['NO_CAN_TIMEOUT'] = "1"

    params = Params()
    params.clear_all()
    params.put_bool("Passive", bool(os.getenv("PASSIVE")))
    params.put_bool("OpenpilotEnabledToggle", True)

  # hack
  def test_longitudinal_setup(self):
    pass


def run_maneuver_worker(k):
  def run(self):
    man = maneuvers[k]
    print(man.title)
    valid, _ = man.evaluate()
    self.assertTrue(valid, msg=man.title)
  return run


for k in range(len(maneuvers)):
  setattr(LongitudinalControl, f"test_longitudinal_maneuvers_{k+1}",
          run_maneuver_worker(k))

if __name__ == "__main__":
  unittest.main(failfast=True)
