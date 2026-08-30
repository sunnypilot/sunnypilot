"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.common.parameterized import parameterized

import openpilot.sunnypilot.models.helpers as helpers
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.modeld import _find_driving_pkl
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, ARCHETYPES, CAM_W, CAM_H, \
  SPLIT_VISION_INPUT_SHAPES, SPLIT_POLICY_INPUT_SHAPES
from openpilot.common.test import OpenpilotTestCase

# resolved by name from this module when a test asks for them
tmp_path = tests_helpers.tmp_path
patch_modeld = tests_helpers.patch_modeld
model_state_factory = tests_helpers.model_state_factory

ModelState = modeld_module.ModelState


# Pkl discovery

class TestFindDrivingPkl(OpenpilotTestCase):
  def test_returns_none_when_no_bundle(self):
    assert _find_driving_pkl(None) is None

  def test_returns_none_when_no_models(self):
    bundle = DummyBundle(models=[])
    assert _find_driving_pkl(bundle) is None

  def test_returns_none_when_pkl_not_on_disk(self):
    bundle = DummyBundle(models=[
      DummyModel('vision', 'driving_fof_tinygrad.pkl'),
      DummyModel('policy', 'driving_fof_tinygrad.pkl'),
    ])
    assert _find_driving_pkl(bundle) is None

  def test_finds_pkl_by_artifact_name(self, tmp_path, monkeypatch):
    (tmp_path / 'driving_fof_tinygrad.pkl').write_bytes(b'fake')
    from openpilot.common.hardware import hw
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))

    bundle = DummyBundle(models=[
      DummyModel('vision', 'driving_fof_tinygrad.pkl'),
      DummyModel('policy', 'driving_fof_tinygrad.pkl'),
    ])
    result = _find_driving_pkl(bundle)
    assert result is not None
    assert 'driving_fof_tinygrad.pkl' in result


# Init — assertion guard

class TestModelStateCombinedInit(OpenpilotTestCase):
  def test_asserts_when_no_pkl(self, monkeypatch):
    bundle = DummyBundle(models=[], is_20hz=True)
    monkeypatch.setattr(helpers, 'get_active_bundle', lambda params=None, *, chestnut=None: bundle)
    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: bundle)
    with self.assertRaisesRegex(AssertionError, "No driving pkl found"):
      ModelState(cam_w=CAM_W, cam_h=CAM_H)


class TestStockEquivalence(OpenpilotTestCase):

  def test_split_queue_keys_match_stock(self, model_state_factory):
    from openpilot.selfdrive.modeld.compile_modeld import make_input_queues
    from openpilot.sunnypilot.modeld_v2.compile_modeld import derive_frame_skip

    state = model_state_factory(ARCHETYPES['vision_policy_split'])

    frame_skip = derive_frame_skip(SPLIT_VISION_INPUT_SHAPES, SPLIT_POLICY_INPUT_SHAPES)
    stock_shapes = {**SPLIT_VISION_INPUT_SHAPES, **SPLIT_POLICY_INPUT_SHAPES, 'action_t': (1, 2)}
    stock_queues, stock_npy = make_input_queues(stock_shapes, frame_skip, device='NPY')

    assert set(state.input_queues.keys()) == set(stock_queues.keys())
    assert {'desire', 'traffic_convention'} <= set(state.numpy_inputs.keys())
    assert set(state.numpy_inputs.keys()) == set(stock_npy.keys()) - {'action_t', 'prev_feat'}

  def test_split_queue_keys_work_with_desire_key(self, model_state_factory):
    from openpilot.sunnypilot.modeld_v2.compile_modeld import derive_frame_skip, make_split_input_queues

    policy_shapes_desire = {'features_buffer': (1, 25, 512), 'desire': (1, 25, 8), 'traffic_convention': (1, 2)}
    frame_skip = derive_frame_skip(SPLIT_VISION_INPUT_SHAPES, policy_shapes_desire)
    queues, npy = make_split_input_queues(SPLIT_VISION_INPUT_SHAPES, policy_shapes_desire, frame_skip, device='NPY')

    assert 'desire_q' in queues
    assert 'desire' in npy
    assert 'img_q' in queues
    assert 'feat_q' in queues

  def test_split_vision_input_names_match_stock(self, model_state_factory):
    state = model_state_factory(ARCHETYPES['vision_policy_split'])
    assert state.vision_input_names == ['img', 'big_img']

  def test_split_output_slices_preserved(self, model_state_factory):
    arch = ARCHETYPES['vision_policy_split']
    state = model_state_factory(arch)
    assert state.vision_output_slices == arch.metadata_structure['vision']['output_slices']
    assert state.policy_output_slices == arch.metadata_structure['policy']['output_slices']


ARCHETYPE_NAMES = list(ARCHETYPES.keys())


class TestModelTypeDetection(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_combined_model_type(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert state._combined_model_type == arch.expected_model_type, \
      f"{arch.name}: got {state._combined_model_type}, expected {arch.expected_model_type}"


class TestConstantsSelection(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_constants_class(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert type(state.constants) is arch.expected_constants_class, \
      f"{arch.name}: got {type(state.constants).__name__}, expected {arch.expected_constants_class.__name__}"


class TestParserSelection(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_parser_module(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    parser_module = type(state.parser).__module__
    assert parser_module.endswith(arch.expected_parser_module), \
      f"{arch.name}: parser from {parser_module}, expected module ending with {arch.expected_parser_module}"


class TestDesireKeyDetection(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_desire_key(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert state.desire_key == arch.expected_desire_key, \
      f"{arch.name}: got {state.desire_key}, expected {arch.expected_desire_key}"


class TestVisionInputNames(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_vision_names_contain_img(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert len(state.vision_input_names) >= 1
    for name in state.vision_input_names:
      assert 'img' in name, f"{arch.name}: vision input name '{name}' missing 'img'"


class TestOutputSlices(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_vision_slices_populated(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert len(state.vision_output_slices) > 0, f"{arch.name}: vision_output_slices empty"

  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_policy_slices_match_type(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    if arch.expected_model_type == 'supercombo':
      assert state.policy_output_slices == {}, f"{arch.name}: supercombo should have empty policy slices"
    else:
      assert len(state.policy_output_slices) > 0, f"{arch.name}: split/multi should have policy slices"


class TestInputQueueCreation(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_queues_not_empty(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert len(state.input_queues) > 0, f"{arch.name}: input_queues empty"

  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_npy_contains_transforms(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert 'tfm' in state.numpy_inputs, f"{arch.name}: 'tfm' missing from npy"
    assert 'big_tfm' in state.numpy_inputs, f"{arch.name}: 'big_tfm' missing from npy"
    assert state.numpy_inputs['tfm'].shape == (3, 3)
    assert state.numpy_inputs['big_tfm'].shape == (3, 3)

  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_npy_contains_desire(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert arch.expected_desire_key in state.numpy_inputs, \
      f"{arch.name}: '{arch.expected_desire_key}' missing from npy"


class TestFrameBufferParams(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_frame_buf_params_per_vision_input(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    for name in state.vision_input_names:
      assert name in state.frame_buf_params, f"{arch.name}: frame_buf_params missing '{name}'"
      nv12_info = state.frame_buf_params[name]
      assert len(nv12_info) >= 4, f"{arch.name}: nv12_info for '{name}' too short"


class TestBundleOverrides(OpenpilotTestCase):
  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_smoothing_params_from_overrides(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert state.LAT_SMOOTH_SECONDS == 0.1
    assert state.LONG_SMOOTH_SECONDS == 0.3

  @parameterized.expand(ARCHETYPE_NAMES, names=["archetype_name"])
  def test_generation_from_bundle(self, archetype_name, model_state_factory):
    arch = ARCHETYPES[archetype_name]
    state = model_state_factory(arch)
    assert state.generation == 10


class TestMlsimProperty(OpenpilotTestCase):
  def test_mlsim_false_for_gen10(self, model_state_factory):
    state = model_state_factory(ARCHETYPES['supercombo_non20hz'])
    assert state.mlsim is False

  def test_mlsim_true_for_gen11(self, tmp_path, monkeypatch, patch_modeld):
    from openpilot.common.hardware import hw
    from openpilot.sunnypilot.modeld_v2.tests.helpers import write_pkl, ARCHETYPES as A

    arch = A['supercombo_non20hz']
    write_pkl(tmp_path, arch)
    bundle = DummyBundle(models=arch.model_stubs, is_20hz=arch.is_20hz, generation=11)
    patch_modeld(bundle)
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))

    state = ModelState(cam_w=CAM_W, cam_h=CAM_H)
    assert state.mlsim is True


class TestCrossArchetypeMismatch(OpenpilotTestCase):
  def test_wrong_is_20hz_changes_constants(self, tmp_path, monkeypatch, patch_modeld):
    from openpilot.common.hardware import hw
    from openpilot.sunnypilot.modeld_v2.tests.helpers import write_pkl
    from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

    arch = ARCHETYPES['vision_policy_split']
    write_pkl(tmp_path, arch)
    bundle = DummyBundle(models=arch.model_stubs, is_20hz=False)
    patch_modeld(bundle)
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))

    state = ModelState(cam_w=CAM_W, cam_h=CAM_H)
    assert type(state.constants) is ModelConstants, \
      "Wrong is_20hz should produce wrong constants class"
