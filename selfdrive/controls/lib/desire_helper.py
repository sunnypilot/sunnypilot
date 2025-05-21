from cereal import log
from openpilot.common.conversions import Conversions as CV
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeController, AutoLaneChangeMode

LaneChangeState = log.LaneChangeState
LaneChangeDirection = log.LaneChangeDirection

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS
LANE_CHANGE_TIME_MAX = 10.

DESIRES = {
  LaneChangeDirection.none: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.none,
    LaneChangeState.laneChangeFinishing: log.Desire.none,
  },
  LaneChangeDirection.left: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.laneChangeLeft,
    LaneChangeState.laneChangeFinishing: log.Desire.laneChangeLeft,
  },
  LaneChangeDirection.right: {
    LaneChangeState.off: log.Desire.none,
    LaneChangeState.preLaneChange: log.Desire.none,
    LaneChangeState.laneChangeStarting: log.Desire.laneChangeRight,
    LaneChangeState.laneChangeFinishing: log.Desire.laneChangeRight,
  },
}


class DesireHelper:
  def __init__(self):
    self.lane_change_state = LaneChangeState.off
    self.lane_change_direction = LaneChangeDirection.none
    self.lane_change_timer = 0.0
    self.lane_change_ll_prob = 1.0
    self.keep_pulse_timer = 0.0
    self.prev_one_blinker = False
    self.desire = log.Desire.none
    self.alc = AutoLaneChangeController(self)

  def update(self, carstate, lateral_active, lane_change_prob, lane_line_probs=None, sm=None):
    # Update Auto-Lane-Change parameters each tick so hot-reloaded params take effect immediately
    self.alc.update_params()
    if lane_line_probs is not None and len(lane_line_probs) >= 3:
      self.alc.update_lane_lines(lane_line_probs[1], lane_line_probs[2])

    v_ego = carstate.vEgo
    one_blinker = carstate.leftBlinker != carstate.rightBlinker
    below_lane_change_speed = v_ego < LANE_CHANGE_SPEED_MIN

    # Blind-spot detection helper usable in multiple states/branches
    blindspot_detected = ((carstate.leftBlindspot and carstate.leftBlinker) or
                          (carstate.rightBlindspot and carstate.rightBlinker))

    # Reset if lateral disabled, timed out, or ALC controller finished/aborted
    # (When the feature is disabled via params the controller is never armed,
    #  so it remains in OFF and will be effectively ignored.)
    if not lateral_active or self.lane_change_timer > LANE_CHANGE_TIME_MAX or \
       self.alc.mode in (AutoLaneChangeMode.DONE, AutoLaneChangeMode.ABORTED):
      # Reset desire helper state and AutoLaneChangeController on completion or abort
      self.lane_change_state = LaneChangeState.off
      self.lane_change_direction = LaneChangeDirection.none
      # Reinitialize ALC controller after finishing or aborting to allow subsequent lane changes
      if self.alc.mode in (AutoLaneChangeMode.DONE, AutoLaneChangeMode.ABORTED):
        self.alc.reset()
    else:
      # LaneChangeState.off
      if self.lane_change_state == LaneChangeState.off and one_blinker and not self.prev_one_blinker and not below_lane_change_speed:
        # New lane-change request – reset and arm the Auto-LC controller so its
        # internal state machine can progress beyond OFF.
        self.alc.reset()
        self.lane_change_state = LaneChangeState.preLaneChange
        self.lane_change_ll_prob = 1.0

      elif self.lane_change_state == LaneChangeState.off and sm is not None and not below_lane_change_speed:
        # Attempt to arm automatically if conditions are met
        if self.alc.should_arm(sm):
          direction = LaneChangeDirection.right if getattr(sm["driverMonitoringState"], "isRHD", False) else LaneChangeDirection.left
          self.alc.reset()
          self.alc.arm(direction, trigger="auto")
          self.lane_change_state = LaneChangeState.preLaneChange
          self.lane_change_direction = direction
          self.lane_change_ll_prob = 1.0

      # LaneChangeState.preLaneChange
      elif self.lane_change_state == LaneChangeState.preLaneChange:
        # Set lane change direction
        self.lane_change_direction = LaneChangeDirection.left if \
          carstate.leftBlinker else LaneChangeDirection.right

        # Ensure ALC controller is armed in the correct direction exactly once
        if self.alc.mode == AutoLaneChangeMode.OFF:
          self.alc.arm(self.lane_change_direction)

        torque_applied = carstate.steeringPressed and \
                         ((carstate.steeringTorque > 0 and self.lane_change_direction == LaneChangeDirection.left) or
                          (carstate.steeringTorque < 0 and self.lane_change_direction == LaneChangeDirection.right))

        blindspot_detected = ((carstate.leftBlindspot and self.lane_change_direction == LaneChangeDirection.left) or
                              (carstate.rightBlindspot and self.lane_change_direction == LaneChangeDirection.right))

# ALC state update will be performed once per cycle at the end of the method

        if not one_blinker or below_lane_change_speed:
          self.lane_change_state = LaneChangeState.off
          self.lane_change_direction = LaneChangeDirection.none
        elif (torque_applied or self.alc.auto_lane_change_allowed) \
             and not blindspot_detected \
             and self.alc.lane_exists:
          self.lane_change_state = LaneChangeState.laneChangeStarting

      # LaneChangeState.laneChangeStarting
      elif self.lane_change_state == LaneChangeState.laneChangeStarting:
        # fade out over .5s
        self.lane_change_ll_prob = max(self.lane_change_ll_prob - 2 * DT_MDL, 0.0)

        # 98% certainty
        if lane_change_prob < 0.02 and self.lane_change_ll_prob < 0.01:
          self.lane_change_state = LaneChangeState.laneChangeFinishing

      # LaneChangeState.laneChangeFinishing
      elif self.lane_change_state == LaneChangeState.laneChangeFinishing:
        # fade in laneline over 1s
        self.lane_change_ll_prob = min(self.lane_change_ll_prob + DT_MDL, 1.0)

        if self.lane_change_ll_prob > 0.99:
          self.lane_change_direction = LaneChangeDirection.none
          if one_blinker:
            self.lane_change_state = LaneChangeState.preLaneChange
          else:
            self.lane_change_state = LaneChangeState.off

    if self.lane_change_state in (LaneChangeState.off, LaneChangeState.preLaneChange):
      self.lane_change_timer = 0.0
    else:
      self.lane_change_timer += DT_MDL

    self.prev_one_blinker = one_blinker

    self.desire = DESIRES[self.lane_change_direction][self.lane_change_state]

    # Send keep pulse once per second during LaneChangeStart.preLaneChange
    if self.lane_change_state in (LaneChangeState.off, LaneChangeState.laneChangeStarting):
      self.keep_pulse_timer = 0.0
    elif self.lane_change_state == LaneChangeState.preLaneChange:
      self.keep_pulse_timer += DT_MDL
      if self.keep_pulse_timer > 1.0:
        self.keep_pulse_timer = 0.0
      elif self.desire in (log.Desire.keepLeft, log.Desire.keepRight):
        self.desire = log.Desire.none

    # Removed obsolete update_state call (auto lane change logic handled in update_lane_change)

    # Keep the Auto Lane Change controller updated each cycle so that it can
    # handle abort/timeout logic even outside the preLaneChange branch.
    self.alc.update(blindspot_detected, carstate.brakePressed, DT_MDL)
