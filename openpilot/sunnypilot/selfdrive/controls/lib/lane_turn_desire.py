"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import custom

from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.nav_turn_intent import NavTurnIntent, turn_route_ready
import time

TurnDirection = custom.ModelDataV2SP.TurnDirection

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS

# "Wait for the turn": the blinker only arms the turn, and the one-shot turn desire is sent when one of these says
# the turn is here. The model treats the desire as "turn now", so sending it early makes it take the first opening.
MODEL_TURN_PROB = 0.35  # model's own prediction that a turn starts within the next horizons
MODEL_TURN_HORIZONS = 2  # desirePrediction horizons checked, soonest first
DESIRE_PRED_WIDTH = 8
WAIT_FOR_TURN = True  # always on in this build: prebuilt branches can't add a param for it


def model_turn_probs(desire_prediction) -> tuple[float, float]:
  """Highest predicted (turnLeft, turnRight) probability over the soonest horizons of modelV2.meta.desirePrediction."""
  if desire_prediction is None or len(desire_prediction) < DESIRE_PRED_WIDTH * MODEL_TURN_HORIZONS:
    return 0., 0.
  desire_prediction = list(desire_prediction)  # a capnp list can't be sliced
  rows = [desire_prediction[h * DESIRE_PRED_WIDTH:(h + 1) * DESIRE_PRED_WIDTH] for h in range(MODEL_TURN_HORIZONS)]
  return max(r[1] for r in rows), max(r[2] for r in rows)


class LaneTurnController:
  def __init__(self, desire_helper):
    self.DH = desire_helper
    self.turn_direction = TurnDirection.none
    self.armed_direction = TurnDirection.none
    self.cue_sent = False
    self.params = Params()
    self.nav_intent = NavTurnIntent(self.params)
    self.navigation_enabled = False
    self.navigation_owns_signal = False
    self.lane_turn_value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.param_read_counter = 0
    self.enabled = self.params.get_bool("LaneTurnDesire")
    self.wait_for_turn = WAIT_FOR_TURN

  def read_params(self):
    self.enabled = self.params.get_bool("LaneTurnDesire")
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)
    self.navigation_enabled = self.params.get_bool("MapboxNextTurnEnabled")

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def update_lane_turn(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float,
                       steering_pressed: bool = False, steering_torque: float = 0., turn_probs: tuple[float, float] = (0., 0.),
                       lateral_active: bool = True, model_position=None, map_turn_supported: bool = False) -> None:
    signal = 'left' if left_blinker and not right_blinker else 'right' if right_blinker and not left_blinker else None
    self.nav_intent.update(signal, self.navigation_enabled, map_turn_supported, lateral_active)
    self.navigation_owns_signal = (self.navigation_enabled and map_turn_supported and
                                    self.nav_intent.mode == 'turn' and signal is not None)
    self.turn_blindspot = blindspot_left if signal == 'left' else blindspot_right
    # Navigation-conditioned models consume the short route continuously. Sending
    # the legacy turn-now desire as well would introduce a second timing source.
    if self.navigation_enabled and map_turn_supported:
      self.turn_direction = TurnDirection.none
      self.armed_direction = TurnDirection.none
      self.cue_sent = False
      return
    if not left_blinker and not right_blinker:
      self.armed_direction = TurnDirection.none
      self.cue_sent = False
    elif left_blinker != right_blinker:
      direction = TurnDirection.turnLeft if left_blinker else TurnDirection.turnRight
      if direction != self.armed_direction:
        self.armed_direction = direction
        self.turn_direction = TurnDirection.none
        self.cue_sent = False

    if left_blinker and not right_blinker and v_ego < self.lane_turn_value and not blindspot_left:
      requested = TurnDirection.turnLeft
    elif right_blinker and not left_blinker and v_ego < self.lane_turn_value and not blindspot_right:
      requested = TurnDirection.turnRight
    else:
      requested = TurnDirection.none

    if not self.wait_for_turn or requested == TurnDirection.none:
      self.turn_direction = requested
      return

    if not self.enabled and self.cue_sent:
      self.turn_direction = TurnDirection.none

    # Eligibility can clear the request, but only a canceled or switched signal permits another cue.
    if self.turn_direction == TurnDirection.none and not self.cue_sent:
      ready = self.turn_is_here(requested, v_ego, steering_pressed, steering_torque, turn_probs)
      if ready:
        self.turn_direction = requested
    if self.enabled and self.turn_direction != TurnDirection.none:
      self.cue_sent = True

  @staticmethod
  def turn_is_here(direction, v_ego: float, steering_pressed: bool, steering_torque: float, turn_probs: tuple[float, float]) -> bool:
    left = direction == TurnDirection.turnLeft
    nudged = steering_pressed and (steering_torque > 0 if left else steering_torque < 0)
    model_sees_turn = (turn_probs[0] if left else turn_probs[1]) >= MODEL_TURN_PROB
    return nudged or model_sees_turn

  def finalize_navigation_intent(self, lane_change_requested, speed, lateral_active, model_supported, lane_change_completed=False):
    if not self.navigation_enabled or not model_supported or not lateral_active:
      return
    if lane_change_requested:
      self.nav_intent.commit('lane_change')
    else:
      if lane_change_completed:
        self.nav_intent.resume_after_lane_change()
      if (self.nav_intent.mode == 'pending' and 0. <= speed < self.lane_turn_value and not self.turn_blindspot and
          turn_route_ready(self.params.get('MapboxTurnContext'), self.nav_intent.session, self.nav_intent.direction, time.monotonic())):
        self.nav_intent.commit('turn')
    self.navigation_owns_signal = self.nav_intent.mode == 'turn'

  def get_turn_direction(self):
    if not self.enabled:
      return TurnDirection.none
    return self.turn_direction
