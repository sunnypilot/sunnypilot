from openpilot.cereal import log, custom
from openpilot.common.params import Params
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase

from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper, LaneChangeState, LaneChangeDirection
from openpilot.sunnypilot.selfdrive.controls.lib.lane_turn_desire import LaneTurnController, LANE_CHANGE_SPEED_MIN, MODEL_TURN_PROB, \
  DESIRE_PRED_WIDTH, model_turn_probs
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeMode
from openpilot.sunnypilot.selfdrive.controls.lib import lane_turn_desire


TurnDirection = custom.ModelDataV2SP.TurnDirection


class TestLaneTurnDesire(OpenpilotTestCase):
  @parameterized.expand([
    (True, False, 5, False, False, TurnDirection.turnLeft),
    (False, True, 6, False, False, TurnDirection.turnRight),
    (True, False, 9, False, False, TurnDirection.none),
    (True, False, 7, True, False, TurnDirection.none),
    (False, True, 6, False, True, TurnDirection.none),
    (False, False, 5, False, False, TurnDirection.none),
    (True, True, 5, False, False, TurnDirection.none),
  ])
  def test_lane_turn_desire_conditions(self, left_blinker, right_blinker, v_ego, blindspot_left, blindspot_right, expected):
    dh = DesireHelper()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.wait_for_turn = False
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(blindspot_left, blindspot_right, left_blinker, right_blinker, v_ego)
    assert controller.get_turn_direction() == expected

  def test_lane_turn_desire_disabled(self):
    dh = DesireHelper()
    controller = LaneTurnController(dh)
    controller.enabled = False
    controller.wait_for_turn = False
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(False, False, True, False, 7)
    assert controller.get_turn_direction() == TurnDirection.none

  def test_lane_turn_overrides_lane_change(self):
    dh = DesireHelper()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.wait_for_turn = False
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    # left turn desire
    controller.update_lane_turn(False, False, True, False, 5)
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    # right turn desire
    controller.update_lane_turn(False, False, False, True, 6)
    assert controller.get_turn_direction() == TurnDirection.turnRight
    # no turn
    controller.update_lane_turn(False, False, False, False, 7)
    assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([
    (8.93, TurnDirection.turnLeft),  # just below threshold
    (8.96, TurnDirection.none),  # above threshold
    (8.95, TurnDirection.none),  # just above threshold
  ])
  def test_lane_turn_desire_speed_boundary(self, v_ego, expected):
    dh = DesireHelper()
    controller = LaneTurnController(dh)
    controller.enabled = True
    controller.wait_for_turn = False
    controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
    controller.turn_direction = TurnDirection.none
    controller.update_lane_turn(False, True, True, False, v_ego)
    assert controller.get_turn_direction() == expected


class DummyCarState:
  def __init__(self, vEgo=0, leftBlinker=False, rightBlinker=False, leftBlindspot=False, rightBlindspot=False,
               steeringPressed=False, steeringTorque=0, brakePressed=False):
    self.vEgo = vEgo
    self.leftBlinker = leftBlinker
    self.rightBlinker = rightBlinker
    self.leftBlindspot = leftBlindspot
    self.rightBlindspot = rightBlindspot
    self.steeringPressed = steeringPressed
    self.steeringTorque = steeringTorque
    self.brakePressed = brakePressed


def set_lane_turn_params():
  lane_turn_desire.WAIT_FOR_TURN = False  # these cases cover the immediate turn desire
  params = Params()
  params.put("LaneTurnDesire", True)
  params.put("LaneTurnValue", 20.0)


class TestDesireHelperIntegration(OpenpilotTestCase):
  @parameterized.expand([(True,), (False,)], names=["left"])
  def test_turn_cue_is_not_repeated_after_lateral_reengagement(self, left, set_lane_turn_params):
    dh = DesireHelper()
    dh.lane_turn_controller.wait_for_turn = True
    carstate = DummyCarState(vEgo=6, leftBlinker=left, rightBlinker=not left)
    direction = log.Desire.turnLeft if left else log.Desire.turnRight
    prediction = [0.] * (DESIRE_PRED_WIDTH * 4)
    prediction[1 if left else 2] = MODEL_TURN_PROB
    requests = [log.Desire.none]

    def update(active):
      dh.update(carstate, active, 1., desire_prediction=prediction)
      requests.append(dh.desire)

    update(True)
    carstate.vEgo = LANE_CHANGE_SPEED_MIN + .1
    update(False)
    carstate.vEgo = 6
    carstate.steeringPressed = True
    carstate.steeringTorque = 2.08 if left else -2.08
    update(False)
    carstate.steeringPressed = False
    update(True)
    assert requests == [log.Desire.none, direction, log.Desire.none, log.Desire.none, log.Desire.none]

    carstate.leftBlinker = carstate.rightBlinker = False
    update(True)
    carstate.leftBlinker, carstate.rightBlinker = left, not left
    update(True)
    pulses = sum(current == direction and previous != direction for previous, current in zip(requests, requests[1:], strict=False))
    assert pulses == 2
    assert requests[-1] == direction

  @parameterized.expand([
    # Lane turn desire overrides lane change desire
    (DummyCarState(vEgo=5, leftBlinker=True, rightBlinker=False, leftBlindspot=False, rightBlindspot=False), True, 1.0,
     log.Desire.turnLeft),
    (DummyCarState(vEgo=7, leftBlinker=False, rightBlinker=True, leftBlindspot=False, rightBlindspot=False), True, 1.0,
     log.Desire.turnRight),
    # Lane change desire only (no turn desires)
    (DummyCarState(vEgo=9, leftBlinker=True, rightBlinker=False, leftBlindspot=False, rightBlindspot=False,
                   steeringPressed=True, steeringTorque=1), True, 1.0, log.Desire.laneChangeLeft),
    (DummyCarState(vEgo=9, leftBlinker=False, rightBlinker=True, leftBlindspot=False, rightBlindspot=False,
                   steeringPressed=True, steeringTorque=-1), True, 1.0, log.Desire.laneChangeRight),
    # No desire (inactive)
    (DummyCarState(vEgo=9, leftBlinker=False, rightBlinker=False), False, 1.0, log.Desire.none),
    (DummyCarState(vEgo=4, leftBlinker=False, rightBlinker=False), True, 1.0, log.Desire.none),  # No blinkers? no desire!
  ], names=["carstate", "lateral_active", "lane_change_prob", "expected_desire"])
  def test_desire_helper_integration(self, carstate, lateral_active, lane_change_prob, expected_desire, set_lane_turn_params):
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGE
    for _ in range(10):
      dh.update(carstate, lateral_active, lane_change_prob,
                left_edge_detected=False, right_edge_detected=False)
    assert dh.desire == expected_desire

  def test_nudge_overrides_edge_detection(self, set_lane_turn_params):
    """Manual steering nudge should override road edge detection and allow lane change."""
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGE
    carstate = DummyCarState(vEgo=15, leftBlinker=True, steeringPressed=True, steeringTorque=1)
    for _ in range(10):
      dh.update(carstate, True, 1.0, left_edge_detected=True, right_edge_detected=False)
    assert dh.lane_change_state == LaneChangeState.laneChangeStarting
    assert dh.lane_change_direction == LaneChangeDirection.left
    assert dh.desire == log.Desire.laneChangeLeft

  def test_nudge_does_not_override_bsm(self, set_lane_turn_params):
    """Manual steering nudge must NOT override BSM blindspot detection."""
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGE
    carstate = DummyCarState(vEgo=15, leftBlinker=True, leftBlindspot=True, steeringPressed=True, steeringTorque=1)
    for _ in range(10):
      dh.update(carstate, True, 1.0, left_edge_detected=False, right_edge_detected=False)
    assert dh.lane_change_state == LaneChangeState.preLaneChange
    assert dh.desire == log.Desire.none

  def test_edge_blocks_auto_lane_change(self, set_lane_turn_params):
    """Road edge detection should still block auto (nudgeless) lane changes."""
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGELESS
    dh.alc.param_read_counter = 1
    carstate = DummyCarState(vEgo=15, leftBlinker=True)
    for _ in range(10):
      dh.update(carstate, True, 1.0, left_edge_detected=True, right_edge_detected=False)
    assert dh.lane_change_state == LaneChangeState.preLaneChange
    assert dh.desire == log.Desire.none

  def test_auto_lane_change_allowed_without_edge(self, set_lane_turn_params):
    """Auto lane change should proceed when no edge and no BSM detected."""
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGELESS
    dh.alc.param_read_counter = 1
    carstate = DummyCarState(vEgo=15, leftBlinker=True)
    for _ in range(10):
      dh.update(carstate, True, 1.0, left_edge_detected=False, right_edge_detected=False)
    assert dh.lane_change_state == LaneChangeState.laneChangeStarting
    assert dh.desire == log.Desire.laneChangeLeft

  def test_right_edge_does_not_block_left_lane_change(self, set_lane_turn_params):
    """Edge on opposite side should not affect lane change direction."""
    dh = DesireHelper()
    dh.alc.lane_change_set_timer = AutoLaneChangeMode.NUDGELESS
    dh.alc.param_read_counter = 1
    carstate = DummyCarState(vEgo=15, leftBlinker=True)
    for _ in range(10):
      dh.update(carstate, True, 1.0, left_edge_detected=False, right_edge_detected=True)
    assert dh.lane_change_state == LaneChangeState.laneChangeStarting
    assert dh.desire == log.Desire.laneChangeLeft


def make_wait_controller():
  controller = LaneTurnController(DesireHelper())
  controller.enabled = True
  controller.wait_for_turn = True
  controller.lane_turn_value = LANE_CHANGE_SPEED_MIN
  return controller


class TestWaitForTurn(OpenpilotTestCase):
  def test_blinker_only_arms(self):
    controller = make_wait_controller()
    for _ in range(20):
      controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([
    ("nudge", {"steering_pressed": True, "steering_torque": 1.5}),
    ("model", {"turn_probs": (MODEL_TURN_PROB, 0.)}),
  ])
  def test_trigger_fires_and_latches(self, _, trigger):
    controller = make_wait_controller()
    controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.none
    args = {"v_ego": 6} | trigger
    controller.update_lane_turn(False, False, True, False, args.pop('v_ego'), **args)
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    # stays on after the trigger goes away, so the model sees a single pulse
    controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.turnLeft

  @parameterized.expand([(-0.05,), (0.,), (0.2,), (0.49,)])
  def test_stopped_speed_alone_does_not_trigger(self, v_ego):
    for left_blinker in (True, False):
      controller = make_wait_controller()
      for _ in range(20):
        controller.update_lane_turn(False, False, left_blinker, not left_blinker, v_ego)
      assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([
    ("nudge_wrong_way", {"steering_pressed": True, "steering_torque": 1.5}),
    ("model_other_side", {"turn_probs": (0.9, 0.)}),
    ("model_low", {"turn_probs": (0., MODEL_TURN_PROB - 0.01)}),
  ])
  def test_wrong_side_triggers_ignored(self, _, trigger):
    controller = make_wait_controller()
    for _ in range(5):
      controller.update_lane_turn(False, False, False, True, 6, **trigger)
    assert controller.get_turn_direction() == TurnDirection.none

  def test_blinker_off_rearms(self):
    controller = make_wait_controller()
    controller.update_lane_turn(False, False, True, False, 0., turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    controller.update_lane_turn(False, False, False, False, 6)
    controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([(True, True), (True, False), (False, True), (False, False)])
  def test_speed_crossing_does_not_send_another_cue(self, left, model_trigger):
    controller = make_wait_controller()
    direction = TurnDirection.turnLeft if left else TurnDirection.turnRight
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == direction
    retry = {"turn_probs": probs} if model_trigger else {"steering_pressed": True, "steering_torque": 2.08 if left else -2.08}
    for speed in (LANE_CHANGE_SPEED_MIN + .1, LANE_CHANGE_SPEED_MIN, 6, 6):
      controller.update_lane_turn(False, False, left, not left, speed, **retry)
      assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([(True, True), (True, False), (False, True), (False, False)])
  def test_blindspot_interruption_does_not_send_another_cue(self, left, model_trigger):
    controller = make_wait_controller()
    direction = TurnDirection.turnLeft if left else TurnDirection.turnRight
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == direction
    controller.update_lane_turn(left, not left, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == TurnDirection.none
    retry = {"turn_probs": probs} if model_trigger else {"steering_pressed": True, "steering_torque": 2.08 if left else -2.08}
    controller.update_lane_turn(False, False, left, not left, 6, **retry)
    assert controller.get_turn_direction() == TurnDirection.none

  @parameterized.expand([(True, "speed"), (False, "speed"), (True, "blindspot"), (False, "blindspot")])
  def test_blocking_before_first_cue_does_not_consume_signal(self, left, block):
    controller = make_wait_controller()
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(block == "blindspot" and left, block == "blindspot" and not left,
                                left, not left, LANE_CHANGE_SPEED_MIN if block == "speed" else 6, turn_probs=probs)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, left, not left, 6)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == (TurnDirection.turnLeft if left else TurnDirection.turnRight)

  @parameterized.expand([(True,), (False,)])
  def test_canceling_consumed_signal_allows_next_turn(self, left):
    controller = make_wait_controller()
    direction = TurnDirection.turnLeft if left else TurnDirection.turnRight
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == direction
    controller.update_lane_turn(False, False, left, not left, LANE_CHANGE_SPEED_MIN)
    controller.update_lane_turn(False, False, False, False, 6)
    controller.update_lane_turn(False, False, left, not left, 6)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == direction

  @parameterized.expand([(True,), (False,)])
  def test_switching_signal_side_allows_next_turn(self, left):
    controller = make_wait_controller()
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == (TurnDirection.turnLeft if left else TurnDirection.turnRight)
    controller.update_lane_turn(False, False, not left, left, 6)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, not left, left, 6, turn_probs=probs[::-1])
    assert controller.get_turn_direction() == (TurnDirection.turnRight if left else TurnDirection.turnLeft)

  @parameterized.expand([(True,), (False,)])
  def test_hazards_do_not_rearm_same_signal(self, left):
    controller = make_wait_controller()
    probs = (MODEL_TURN_PROB, 0.) if left else (0., MODEL_TURN_PROB)
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == (TurnDirection.turnLeft if left else TurnDirection.turnRight)
    controller.update_lane_turn(False, False, True, True, 6, turn_probs=probs)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, left, not left, 6, turn_probs=probs)
    assert controller.get_turn_direction() == TurnDirection.none

  def test_disabled_feature_does_not_consume_unemitted_cue(self):
    controller = make_wait_controller()
    controller.enabled = False
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.none
    controller.update_lane_turn(False, False, True, False, LANE_CHANGE_SPEED_MIN)
    controller.enabled = True
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.turnLeft

  def test_enabling_latched_turn_remembers_emitted_cue(self):
    controller = make_wait_controller()
    controller.enabled = False
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    controller.enabled = True
    controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    controller.update_lane_turn(False, False, True, False, LANE_CHANGE_SPEED_MIN)
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.none

  def test_feature_toggle_does_not_repeat_emitted_cue(self):
    controller = make_wait_controller()
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    controller.enabled = False
    controller.update_lane_turn(False, False, True, False, 6)
    assert controller.get_turn_direction() == TurnDirection.none
    controller.enabled = True
    controller.update_lane_turn(False, False, True, False, 6, turn_probs=(MODEL_TURN_PROB, 0.))
    assert controller.get_turn_direction() == TurnDirection.none

  def test_model_turn_probs(self):
    pred = [0.] * (DESIRE_PRED_WIDTH * 4)
    pred[DESIRE_PRED_WIDTH + 1] = 0.6  # turnLeft, second horizon
    pred[2] = 0.2  # turnRight, first horizon
    pred[DESIRE_PRED_WIDTH * 3 + 2] = 0.9  # turnRight, beyond the horizons checked
    assert model_turn_probs(pred) == (0.6, 0.2)
    assert model_turn_probs(None) == (0., 0.)

  def test_model_turn_probs_capnp(self):
    # modeld passes modelV2.meta.desirePrediction, a capnp list, which can't be sliced
    msg = log.ModelDataV2.new_message()
    pred = [0.] * (DESIRE_PRED_WIDTH * 4)
    pred[1] = 0.5
    msg.meta.desirePrediction = pred
    assert model_turn_probs(msg.meta.desirePrediction) == (0.5, 0.)


class TestWaitForTurnDesireHelper(OpenpilotTestCase):
  def test_model_prediction_releases_turn(self):
    params = Params()
    params.put("LaneTurnDesire", True)
    lane_turn_desire.WAIT_FOR_TURN = True
    params.put("LaneTurnValue", 20.0)
    dh = DesireHelper()
    carstate = DummyCarState(vEgo=5, leftBlinker=True)
    pred = [0.] * (DESIRE_PRED_WIDTH * 4)
    for _ in range(10):
      dh.update(carstate, True, 0., desire_prediction=pred)
    assert dh.desire == log.Desire.none

    pred[log.Desire.turnLeft] = 0.9
    dh.update(carstate, True, 0., desire_prediction=pred)
    assert dh.desire == log.Desire.turnLeft
