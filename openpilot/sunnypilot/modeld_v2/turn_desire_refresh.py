"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL

# The model gets the desire as a one-frame pulse on its rising edge (ModelState.run), and its desire and feature
# history is 5 s (100 model frames, sampled 25 x 4 or 100 x 1). A turn cued at a red light, or one still under way 5 s
# after the cue, is forgotten while there is turn left to do: on routes 92-96 the model's turn state fell 6.5 s after
# every cue, and after a cue at a light the car pulled away straight. While a turn desire is held, the input is cleared
# for one frame so the next frame is a new rising edge, before the last pulse leaves the history and again when the car
# pulls away.
ENABLED = True
TURN_DESIRES = (log.Desire.turnLeft, log.Desire.turnRight)  # a repeated lane change desire would start a second one
HISTORY_S = 5.0
REFRESH_AFTER_S = 4.0  # since the last pulse
STOPPED_SPEED = 0.3  # m/s
PULL_AWAY_SPEED = 1.0  # m/s
MIN_STOP_S = 1.0  # a stop this long, then moving off, is a pull-away
MIN_PULL_AWAY_GAP_S = 1.0  # a pulse this fresh already covers the pull-away
# Routes 85-9a: a turn is done 15-60 m after its cue (median ~30 m), and the blinker cancels about 1 s later. The cap
# stops a blinker left on (or a slow lane change, which is a turn desire under LaneTurnValue) being refreshed into a
# turn further down the road. A stop within it restarts it: the turn comes after the light. Once used up, that cue is
# never refreshed again, so a blinker left on doesn't turn the car at the next light.
MAX_TRAVEL_M = 40.
# Once the car has turned this far toward the turn the road out is ahead and in view, and the blinker cancels soon. A
# pulse later than that tells the model to turn again as it leaves the turn. Replaying the cue timing of routes 85-9a
# (74 single turns), the model's 5 s history held the turn until it was 80% done on 10 of them; with this refresh, 58
# (13 of the other 16 had the blinker cancel first). 60 deg leaves no pulse after a turn is 80% done (12 turns got one
# with no cap); 45 deg kept 4 fewer turns.
MAX_TURNED_DEG = 60.
_EPS = 1e-6


class TurnDesireRefresh:
  def __init__(self, enabled: bool = ENABLED):
    self.enabled = enabled
    self.reset()

  def reset(self) -> None:
    """Forget the held desire. The next held turn counts from its own rising edge (also after a model swap, whose new
    ModelState pulses a held desire on its first frame)."""
    self.desire = log.Desire.none
    self.since_pulse = 0.
    self.travel = 0.
    self.stopped_for = 0.
    self.turned = 0.  # deg toward the turn since the cue
    self.expired = False
    self.refreshes = 0

  def update(self, desire: int, v_ego: float, yaw_rate: float = 0., dt: float = DT_MDL) -> bool:
    """Called once per model frame with the held desire, speed and the model's own yaw rate (rad/s, + to the right, as
    cameraOdometry.rot[2]). True means clear the desire input this frame, so the model sees a new pulse on the next."""
    if desire != self.desire:
      self.reset()
      self.desire = desire
      return False  # the model pulses a new desire on its own
    if not self.enabled or desire not in TURN_DESIRES or self.expired:
      return False

    self.since_pulse += dt
    self.travel += max(v_ego, 0.) * dt
    self.turned += np.degrees(yaw_rate) * dt * (1. if desire == log.Desire.turnRight else -1.)
    pull_away = False
    if v_ego < STOPPED_SPEED:
      self.stopped_for += dt
    elif v_ego >= PULL_AWAY_SPEED:
      pull_away = self.stopped_for >= MIN_STOP_S - _EPS
      self.stopped_for = 0.
      if pull_away:
        self.travel = 0.

    if self.travel > MAX_TRAVEL_M or self.turned > MAX_TURNED_DEG:
      self.expired = True
      return False
    if self.since_pulse >= REFRESH_AFTER_S - _EPS or (pull_away and self.since_pulse >= MIN_PULL_AWAY_GAP_S - _EPS):
      self.since_pulse = -dt  # the pulse lands on the next frame
      self.refreshes += 1
      return True
    return False


def desire_input(desire: int, length: int, clear: bool) -> np.ndarray:
  """The model's held-desire input: one-hot, or all zero on a refresh frame."""
  vec = np.zeros(length, dtype=np.float32)
  if not clear and 0 <= desire < length:
    vec[desire] = 1
  return vec
