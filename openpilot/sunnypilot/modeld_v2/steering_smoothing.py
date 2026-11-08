"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.structs import car

# On angle-steered cars the action head's frame-to-frame zig-zag (about +-0.003 1/m holding a turn, +-6 deg of wheel on
# the Model Y) goes straight to the rack and is felt as a ~4 Hz ripple. A 0.05 s low-pass on the model's curvature,
# on top of controlsd's ramp, took the 2-7 Hz ripple from 1.5 to 0.9 deg on routes 98-9f. The model is told the
# extra time through lat_delay (modeld adds LAT_SMOOTH_SECONDS to it), so it plans that much further ahead.
ANGLE_LAT_SMOOTH_SECONDS = 0.05


def lat_smooth_seconds(bundle_value: float, steer_control_type) -> float:
  if steer_control_type == car.CarParams.SteerControlType.angle:
    return max(bundle_value, ANGLE_LAT_SMOOTH_SECONDS)
  return bundle_value
