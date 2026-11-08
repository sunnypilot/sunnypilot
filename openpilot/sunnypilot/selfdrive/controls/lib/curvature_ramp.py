"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.realtime import DT_CTRL, DT_MDL

# The model's curvature arrives at 20 Hz and controlsd runs at 100 Hz, so an angle command used to hold each model
# value for 5 ticks and then jump: 3-6 deg per step through a turn-in on the Model Y (routes 9e/9f), which the Tesla
# rate limit (up to 250 deg/s at low speed) passes straight to the rack and the driver feels as a buzz in the wheel.
# Ramping each new value in over one model frame turns the staircase into a slope: on routes 98-9f the 95th percentile
# step fell from 5.5 to 1.1 deg per 10 ms, for about 20 ms of added delay.
RAMP_TICKS = round(DT_MDL / DT_CTRL)


class CurvatureRamp:
  def __init__(self, ticks: int = RAMP_TICKS):
    self.ticks = ticks
    self.start = 0.
    self.target = 0.
    self.tick = ticks
    self.output = 0.

  def update(self, target: float, new_frame: bool, active: bool) -> float:
    """target: the model's curvature (or, inactive, the car's own); new_frame: a new model frame arrived this tick."""
    if not active:
      self.start = self.target = self.output = target
      self.tick = self.ticks
      return target
    if new_frame:
      self.start, self.target, self.tick = self.output, target, 0
    self.tick = min(self.tick + 1, self.ticks)
    self.output = self.start + (self.target - self.start) * self.tick / self.ticks
    return self.output
