"""Tests for the dynamic MDN inference in ``mhp_inference`` and the parser
changes that read from ``output_slices`` instead of hardcoded constants.
"""

import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2.mhp_inference import (
  infer_mhp,
  slice_size,
  infer_mhp_for_outputs,
)
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser as CombinedParser
from openpilot.sunnypilot.modeld_v2.parse_model_outputs_split import Parser as SplitParser
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants


# -- infer_mhp --------------------------------------------------------------

class TestInferMhp:
  N_PLAN = ModelConstants.IDX_N * ModelConstants.PLAN_WIDTH  # 495
  N_LEAD = ModelConstants.LEAD_TRAJ_LEN * ModelConstants.LEAD_WIDTH  # 24

  def test_legacy_plan_preserved(self):
    # Legacy: 5 hypotheses x (2*495 + 1) = 4955
    assert infer_mhp(4955, self.N_PLAN, legacy_in_n=5, legacy_out_n=1) == (5, 1)

  def test_legacy_lead_preserved(self):
    # Legacy: 2 hypotheses x (2*24 + 3) = 102
    assert infer_mhp(102, self.N_LEAD, legacy_in_n=2, legacy_out_n=3) == (2, 3)

  def test_new_supercombo_plan_single_hypothesis_no_weights(self):
    # New combined supercombo: 1 hypothesis x (2*495 + 0) = 990
    assert infer_mhp(990, self.N_PLAN, legacy_in_n=5, legacy_out_n=1) == (1, 0)

  def test_new_supercombo_lead_three_hypotheses_no_weights(self):
    # New combined supercombo: 3 hypotheses x (2*24 + 0) = 144
    assert infer_mhp(144, self.N_LEAD, legacy_in_n=2, legacy_out_n=3) == (3, 0)

  def test_out_n_one(self):
    # 4 hypotheses x (2*495 + 1) = 3964
    assert infer_mhp(3964, self.N_PLAN, legacy_in_n=5, legacy_out_n=1) == (4, 1)

  def test_out_n_three(self):
    # 2 hypotheses x (2*24 + 3) = 102 (matches legacy_lead as well)
    assert infer_mhp(102, self.N_LEAD, legacy_in_n=4, legacy_out_n=99) == (2, 3)

  def test_zero_or_invalid_returns_fallback(self):
    assert infer_mhp(0, self.N_PLAN, 5, 1) == (1, 0)
    assert infer_mhp(-1, self.N_PLAN, 5, 1) == (1, 0)
    assert infer_mhp(990, 0, 5, 1) == (1, 0)

  def test_no_match_returns_single_hypothesis(self):
    # 987 doesn't cleanly factor under the constraints we care about.
    assert infer_mhp(987, self.N_PLAN, 5, 1) == (1, 0)


class TestSliceSize:
  def test_none_returns_zero(self):
    assert slice_size(None) == 0

  def test_basic_slice(self):
    assert slice_size(slice(10, 50)) == 40

  def test_negative_stop_returns_zero(self):
    assert slice_size(slice(10, -2)) == 0

  def test_none_bounds(self):
    assert slice_size(slice(None, 100)) == 100


class TestInferMhpForOutputs:
  def test_infers_for_plan_and_lead(self):
    slices = {
      'plan': slice(1576, 2566),  # 990
      'lead': slice(917, 1061),   # 144
    }
    cfg = infer_mhp_for_outputs(slices, ModelConstants)
    assert cfg == {'plan_mhp_n': 1, 'plan_mhp_selection': 0,
                   'lead_mhp_n': 3, 'lead_mhp_selection': 0}

  def test_legacy_falls_back_to_constants(self):
    # Legacy sizes: 4955 plan, 102 lead -> both match Priority 1.
    slices = {
      'plan': slice(0, 4955),
      'lead': slice(4955, 5057),
    }
    cfg = infer_mhp_for_outputs(slices, ModelConstants)
    assert cfg == {'plan_mhp_n': ModelConstants.PLAN_MHP_N,
                   'plan_mhp_selection': ModelConstants.PLAN_MHP_SELECTION,
                   'lead_mhp_n': ModelConstants.LEAD_MHP_N,
                   'lead_mhp_selection': ModelConstants.LEAD_MHP_SELECTION}

  def test_missing_outputs_are_skipped(self):
    cfg = infer_mhp_for_outputs({}, ModelConstants)
    assert cfg == {}


# -- CombinedParser ---------------------------------------------------------

def _synth_outputs(in_n_plan=5, out_n_plan=1, in_n_lead=2, out_n_lead=3,
                   n_plan=ModelConstants.IDX_N * ModelConstants.PLAN_WIDTH,
                   n_lead=ModelConstants.LEAD_TRAJ_LEN * ModelConstants.LEAD_WIDTH):
  """Synthesize a flat-output dict with the right per-head sizes."""
  plan_size = in_n_plan * (2 * n_plan + out_n_plan)
  lead_size = in_n_lead * (2 * n_lead + out_n_lead)
  return {
    'plan': np.random.RandomState(0).randn(1, plan_size).astype(np.float32),
    'lead': np.random.RandomState(1).randn(1, lead_size).astype(np.float32),
    # Other outputs that parse_outputs() consumes:
    'lane_lines':     np.random.RandomState(2).randn(1, 528).astype(np.float32),
    'road_edges':     np.random.RandomState(3).randn(1, 264).astype(np.float32),
    'pose':           np.random.RandomState(4).randn(1, 12).astype(np.float32),
    'road_transform': np.random.RandomState(5).randn(1, 12).astype(np.float32),
    'wide_from_device_euler': np.random.RandomState(6).randn(1, 6).astype(np.float32),
    'lead_prob':      np.random.RandomState(7).randn(1, 3).astype(np.float32),
    'lane_lines_prob':np.random.RandomState(8).randn(1, 8).astype(np.float32),
    'meta':           np.random.RandomState(9).randn(1, 55).astype(np.float32),
    'desire_state':   np.random.RandomState(10).randn(1, 8).astype(np.float32),
    'desire_pred':    np.random.RandomState(11).randn(1, 32).astype(np.float32),
  }


class TestCombinedParser:
  def test_legacy_keeps_existing_shape(self):
    p = CombinedParser()  # empty mhp -> legacy constants
    out = p.parse_outputs(_synth_outputs(5, 1, 2, 3))
    assert out['plan'].shape == (1, 33, 15)
    assert out['plan_stds'].shape == (1, 33, 15)
    # Lead primary output collapses to LEAD_MHP_SELECTION=3 selections per
    # ``parse_mdn``; raw hypotheses survive as ``lead_hypotheses``.
    assert out['lead'].shape == (1, 3, 6, 4)
    assert out['lead_stds'].shape == (1, 3, 6, 4)
    assert out['plan_hypotheses'].shape == (1, 5, 33, 15)
    assert out['lead_hypotheses'].shape == (1, 2, 6, 4)

  def test_new_supercombo_plan_and_lead_parse(self):
    p = CombinedParser(mhp_config={
      'plan_mhp_n': 1, 'plan_mhp_selection': 0,
      'lead_mhp_n': 3, 'lead_mhp_selection': 0,
    })
    out = p.parse_outputs(_synth_outputs(1, 0, 3, 0))
    assert out['plan'].shape == (1, 33, 15)
    assert out['plan_stds'].shape == (1, 33, 15)
    assert out['lead'].shape == (1, 3, 6, 4)
    assert out['lead_stds'].shape == (1, 3, 6, 4)
    # MHP-without-weights keeps every hypothesis as ``*_hypotheses``
    assert out['lead_hypotheses'].shape == (1, 3, 6, 4)
    # Plan with a single hypothesis takes the in_N<=1 branch, which
    # (matching legacy behavior) does not emit ``plan_hypotheses``.
    assert 'plan_hypotheses' not in out


class TestSplitParser:
  def test_default_uses_is_mhp_heuristic(self):
    # No mhp_config -> falls back to inspecting the raw tensor's last axis.
    # The legacy 102-element lead pack fits the "MHP branch" path.
    n = SplitParser()
    outs = {'lead': np.zeros((1, 102), dtype=np.float32)}
    n.parse_dynamic_outputs(outs)
    assert outs['lead'].shape == (1, 3, 6, 4)
    assert outs['lead_hypotheses'].shape == (1, 2, 6, 4)

  def test_explicit_mhp_overrides_is_mhp(self):
    n = SplitParser(mhp_config={'lead_mhp_n': 3, 'lead_mhp_selection': 0})
    outs = {'lead': np.zeros((1, 144), dtype=np.float32)}
    n.parse_dynamic_outputs(outs)
    assert outs['lead'].shape == (1, 3, 6, 4)


if __name__ == '__main__':
  pytest.main([__file__, '-v'])
