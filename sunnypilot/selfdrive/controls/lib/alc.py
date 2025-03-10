from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

AUTO_LANE_CHANGE_TIMER = {
  -1: 0.0,
  0: 0.0,
  1: 0.1,
  2: 0.5,
  3: 1.0,
  4: 1.5,
}

class AutoLaneChangeController:
  def __init__(self):
    self.param_s = Params()
    self.lane_change_wait_timer = 0.0
    self.param_read_counter = 0
    self.lane_change_set_timer = 2.0
    self.lane_change_bsm_delay = False
    self.read_param()

  def read_param(self):
    self.lane_change_set_timer = int(self.param_s.get("AutoLaneChangeTimer", encoding="utf8"))
    self.lane_change_bsm_delay = self.param_s.get_bool("AutoLaneChangeBsmDelay")

  def update(self, blindspot_detected: bool):
    if self.param_read_counter % 50 == 0:
      self.read_param()
    self.param_read_counter += 1

    lane_change_auto_timer = AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer, 2.0)

    self.lane_change_wait_timer += DT_MDL

    if self.lane_change_bsm_delay and blindspot_detected and lane_change_auto_timer:
      if lane_change_auto_timer == 0.1:
        self.lane_change_wait_timer = -1
      else:
        self.lane_change_wait_timer = lane_change_auto_timer - 1

    auto_lane_change_allowed = lane_change_auto_timer and self.lane_change_wait_timer > lane_change_auto_timer
    return auto_lane_change_allowed

  def reset(self):
    self.lane_change_wait_timer = 0.0
