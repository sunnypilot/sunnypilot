"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.structs import car

from openpilot.sunnypilot.modeld_v2.steering_smoothing import ANGLE_LAT_SMOOTH_SECONDS, lat_smooth_seconds

ANGLE = car.CarParams.SteerControlType.angle
TORQUE = car.CarParams.SteerControlType.torque


def test_angle_cars_get_at_least_the_minimum():
  assert lat_smooth_seconds(0., ANGLE) == ANGLE_LAT_SMOOTH_SECONDS


def test_a_bundle_asking_for_more_keeps_it():
  assert lat_smooth_seconds(0.2, ANGLE) == 0.2


def test_other_cars_keep_the_bundle_value():
  assert lat_smooth_seconds(0., TORQUE) == 0.
  assert lat_smooth_seconds(0.1, TORQUE) == 0.1
