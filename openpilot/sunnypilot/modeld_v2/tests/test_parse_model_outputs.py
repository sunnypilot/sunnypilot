import numpy as np
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser, _infer_mhp, sigmoid, softmax


class TestParseModelOutputs(OpenpilotTestCase):
  def test_infer_mhp_lead(self):
    in_hypotheses, out_selections = _infer_mhp(102, 24)
    assert in_hypotheses == 2
    assert out_selections == 3

  def test_infer_mhp_plan(self):
    in_hypotheses, out_selections = _infer_mhp(4955, 495)
    assert in_hypotheses == 5
    assert out_selections == 1

  def test_infer_mhp_non_mdn(self):
    in_hypotheses, out_selections = _infer_mhp(48, 24)
    assert in_hypotheses == 1
    assert out_selections == 0

  def test_check_missing_raises(self):
    parser = Parser(ignore_missing=False)
    with self.assertRaises(ValueError):
      parser.check_missing({}, "missing_key")

  def test_check_missing_ignored(self):
    parser = Parser(ignore_missing=True)
    assert parser.check_missing({}, "missing_key") is True

  def test_binary_crossentropy(self):
    parser = Parser()
    raw_logits = np.array([[-10.0, 0.0, 10.0]], dtype=np.float32)
    outs = {"meta": raw_logits.copy()}
    parser.parse_binary_crossentropy("meta", outs)
    expected_probabilities = sigmoid(raw_logits)
    np.testing.assert_allclose(outs["meta"], expected_probabilities, rtol=1e-5, atol=1e-6)

  def test_categorical_crossentropy(self):
    parser = Parser()
    raw_logits = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
    outs = {"desire_state": raw_logits.copy()}
    parser.parse_categorical_crossentropy("desire_state", outs)
    expected_probabilities = softmax(raw_logits)
    np.testing.assert_allclose(outs["desire_state"], expected_probabilities, rtol=1e-5, atol=1e-6)

  def test_parse_vision_outputs(self):
    parser = Parser()
    pose_raw = np.zeros((1, ModelConstants.POSE_WIDTH * 2), dtype=np.float32)
    road_transform_raw = np.zeros((1, ModelConstants.POSE_WIDTH * 2), dtype=np.float32)
    lead_raw = np.zeros((1, 102), dtype=np.float32)
    meta_raw = np.zeros((1, 55), dtype=np.float32)
    vision_outputs = {"pose": pose_raw, "road_transform": road_transform_raw, "lead": lead_raw, "meta": meta_raw}
    parsed = parser.parse_vision_outputs(vision_outputs)
    assert "pose" in parsed
    assert "road_transform" in parsed
    assert "lead" in parsed
    assert "meta" in parsed
    assert parsed["pose"].shape == (1, ModelConstants.POSE_WIDTH)
    assert parsed["lead"].shape == (1, ModelConstants.LEAD_MHP_SELECTION, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)

  def test_parse_policy_outputs(self):
    parser = Parser()
    plan_raw = np.zeros((1, 4955), dtype=np.float32)
    desire_state_raw = np.zeros((1, ModelConstants.DESIRE_PRED_WIDTH), dtype=np.float32)
    action_raw = np.zeros((1, ModelConstants.ACTION_WIDTH * 2), dtype=np.float32)
    policy_outputs = {"plan": plan_raw, "desire_state": desire_state_raw, "action": action_raw}
    parsed = parser.parse_policy_outputs(policy_outputs)
    assert parsed["plan"].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert parsed["action"].shape == (1, ModelConstants.ACTION_WIDTH)
    assert parsed["desire_state"].shape == (1, ModelConstants.DESIRE_PRED_WIDTH)

  def test_parse_outputs_combined(self):
    parser = Parser()
    outputs = {"plan": np.zeros((1, 4955), dtype=np.float32), "pose": np.zeros((1, ModelConstants.POSE_WIDTH * 2),
               dtype=np.float32), "meta": np.zeros((1, 55), dtype=np.float32)}
    parsed = parser.parse_outputs(outputs)
    assert parsed["plan"].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert parsed["pose"].shape == (1, ModelConstants.POSE_WIDTH)
    assert parsed["meta"].shape == (1, 55)
