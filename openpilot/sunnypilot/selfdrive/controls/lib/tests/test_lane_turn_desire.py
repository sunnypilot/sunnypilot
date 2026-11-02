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
    ("stopped", {"v_ego": 0.2}),
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
    controller.update_lane_turn(False, False, True, False, 0.)
    assert controller.get_turn_direction() == TurnDirection.turnLeft
    controller.update_lane_turn(False, False, False, False, 6)
    controller.update_lane_turn(False, False, True, False, 6)
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
