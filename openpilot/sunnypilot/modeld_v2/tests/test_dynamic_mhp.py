"""Tests for the dynamic MDN-hypothesis inference in ``parse_model_outputs``."""

import numpy as np
import pytest


from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser, _infer_mhp
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants


# -- _infer_mhp -------------------------------------------------------------

class TestInferMhp:
  P_PLAN = ModelConstants.IDX_N * ModelConstants.PLAN_WIDTH  # 495
  P_LEAD = ModelConstants.LEAD_TRAJ_LEN * ModelConstants.LEAD_WIDTH  # 24

  def test_legacy_plan(self):
    # 5 hypotheses * (2*495 + 1) = 4955
    assert _infer_mhp(4955, self.P_PLAN) == (5, 1)

  def test_legacy_lead(self):
    # 2 hypotheses * (2*24 + 3) = 102
    assert _infer_mhp(102, self.P_LEAD) == (2, 3)

  def test_new_plan(self):
    # 1 hypothesis * (2*495 + 0) = 990
    assert _infer_mhp(990, self.P_PLAN) == (1, 0)

  def test_new_lead(self):
    # 3 hypotheses * (2*24 + 0) = 144
    assert _infer_mhp(144, self.P_LEAD) == (3, 0)

  def test_no_mhp_output(self):
    # lane_lines (528 = 4*132): 1 hypothesis * (2*528 + 0) = 1056; 2 hypotheses * 528+0 = 1056 too — same.
    # In practice a single-hypothesis MDN with ``out_N == 0`` yields 1*2*prod = 528 * 2 = ... no, lane_lines is
    # ``in_N=0`` because it's laid out as 2*prod directly (1056 = 4 * 132 * 2 simply). The auto-detect prefers
    # the smallest valid ``in_N``, so 1056 = 2*1*528 + 0 -> (1, 0).
    assert _infer_mhp(1056, 528) == (1, 0)

  def test_unknown_size_keeps_single_hypothesis(self):
    # 989 doesn't divide cleanly under any out_N ∈ {0..6} for P = 495, so we
    # fall back to the safe single-hypothesis default.
    assert _infer_mhp(989, self.P_PLAN) == (1, 0)


# -- CombinedParser ---------------------------------------------------------

def _synth_outs(
  plan_in_n: int = 5, plan_out_n: int = 1,
  lead_in_n: int = 2, lead_out_n: int = 3,
  extras: bool = True,
) -> dict[str, np.ndarray]:
  plan_size = plan_in_n * (2 * ModelConstants.IDX_N * ModelConstants.PLAN_WIDTH + plan_out_n)
  lead_size = lead_in_n * (2 * ModelConstants.LEAD_TRAJ_LEN * ModelConstants.LEAD_WIDTH + lead_out_n)
  rng = np.random.RandomState(0)
  d = {
    'plan': rng.randn(1, plan_size).astype(np.float32),
    'lead': rng.randn(1, lead_size).astype(np.float32),
  }
  if extras:
    d.update({
      'lane_lines':     rng.randn(1, 528).astype(np.float32),
      'road_edges':     rng.randn(1, 264).astype(np.float32),
      'pose':           rng.randn(1, 12).astype(np.float32),
      'road_transform': rng.randn(1, 12).astype(np.float32),
      'wide_from_device_euler': rng.randn(1, 6).astype(np.float32),
      'lead_prob':      rng.randn(1, 3).astype(np.float32),
      'lane_lines_prob':rng.randn(1, 8).astype(np.float32),
      'meta':           rng.randn(1, 55).astype(np.float32),
      'desire_state':   rng.randn(1, 8).astype(np.float32),
      'desire_pred':    rng.randn(1, 32).astype(np.float32),
    })
  return d


class TestCombinedParser:
  def test_legacy_supercombo_shapes(self):
    p = Parser()
    out = p.parse_outputs(_synth_outs(plan_in_n=5, plan_out_n=1, lead_in_n=2, lead_out_n=3))
    assert out['plan'].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert out['plan_stds'].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert out['lead'].shape == (1, ModelConstants.LEAD_MHP_SELECTION, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)
    assert out['lead_stds'].shape == (1, ModelConstants.LEAD_MHP_SELECTION, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)
    # Per-hypothesis outputs preserved by legacy code path
    assert out['plan_hypotheses'].shape == (1, 5, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert out['lead_hypotheses'].shape == (1, 2, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)

  def test_new_supercombo_shapes(self):
    p = Parser()
    out = p.parse_outputs(_synth_outs(plan_in_n=1, plan_out_n=0, lead_in_n=3, lead_out_n=0))
    # Plan single hypothesis collapses straight to (1, IDX_N, PLAN_WIDTH)
    assert out['plan'].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert out['plan_stds'].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    # Lead with 3 hypotheses and no weights keeps all hypotheses
    assert out['lead'].shape == (1, 3, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)
    assert out['lead_stds'].shape == (1, 3, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)
    assert out['lead_hypotheses'].shape == (1, 3, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)

  def test_unknown_size_does_not_crash_legacy_layout(self):
    # Provide EVERY output parse_outputs expects so the parser can auto-detect
    # each head from the actual raw slice size, including the new-supercombo
    # mixture (legacy-shaped lane_lines/etc. + new-shaped plan/lead).
    p = Parser()
    out = p.parse_outputs(_synth_outs(plan_in_n=1, plan_out_n=0, lead_in_n=3, lead_out_n=0))
    assert out['plan'].shape == (1, ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH)
    assert out['lead'].shape == (1, 3, ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH)
    # Non-MHP outputs must keep the historical 3D shape (no spurious leading 1).
    assert out['lane_lines'].shape == (1, ModelConstants.NUM_LANE_LINES, ModelConstants.IDX_N, ModelConstants.LANE_LINES_WIDTH)
    assert out['pose'].shape == (1, ModelConstants.POSE_WIDTH)
    assert out['road_transform'].shape == (1, ModelConstants.POSE_WIDTH)


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
