"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import pickle
import pytest

import openpilot.sunnypilot.models.helpers as helpers
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
from openpilot.sunnypilot.models.split_model_constants import SplitModelConstants


class DummyOverride:
  def __init__(self, key, value):
    self.key = key
    self.value = value


class DummyArtifact:
  def __init__(self, file_name):
    self.fileName = file_name


class DummyModelType:
  def __init__(self, raw):
    self.raw = raw


class DummyModel:
  def __init__(self, type_str, artifact_file):
    self.type = DummyModelType(type_str)
    self.artifact = DummyArtifact(artifact_file)


class DummyBundle:
  def __init__(self, is_20hz=False, models=None, generation=10):
    self.overrides = [DummyOverride('lat', '.1'), DummyOverride('long', '.3')]
    self.generation = generation
    self.is20hz = is_20hz
    self.models = models or []


class Archetype:
  def __init__(self, name, metadata_structure, model_stubs, is_20hz,
               expected_model_type, expected_constants_class, expected_parser_module,
               expected_desire_key):
    self.name = name
    self.metadata_structure = metadata_structure
    self.model_stubs = model_stubs
    self.is_20hz = is_20hz
    self.expected_model_type = expected_model_type
    self.expected_constants_class = expected_constants_class
    self.expected_parser_module = expected_parser_module
    self.expected_desire_key = expected_desire_key


def _noop_jit(**kwargs):
  pass


def _make_vision_policy_metadata(vision_input_shapes, policy_input_shapes,
                                 vision_output_slices, policy_output_slices):
  return {
    'vision': {'input_shapes': vision_input_shapes, 'output_slices': vision_output_slices},
    'policy': {'input_shapes': policy_input_shapes, 'output_slices': policy_output_slices},
  }


def _make_multi_policy_metadata(vision_input_shapes, policy_input_shapes,
                                vision_output_slices, policy_output_slices):
  return {
    'vision': {'input_shapes': vision_input_shapes, 'output_slices': vision_output_slices},
    'offPolicy': {'input_shapes': policy_input_shapes, 'output_slices': policy_output_slices},
  }


def _make_tri_policy_metadata(vision_input_shapes, policy_input_shapes,
                              vision_output_slices, policy_output_slices):
  return {
    'vision': {'input_shapes': vision_input_shapes, 'output_slices': vision_output_slices},
    'onPolicy': {'input_shapes': policy_input_shapes, 'output_slices': policy_output_slices},
    'offPolicy': {'input_shapes': policy_input_shapes, 'output_slices': policy_output_slices},
  }


def _make_supercombo_metadata(input_shapes, output_slices):
  return {'model': {'input_shapes': input_shapes, 'output_slices': output_slices}}


SPLIT_VISION_INPUT_SHAPES = {'img': (1, 12, 128, 256), 'big_img': (1, 12, 128, 256)}
SPLIT_POLICY_INPUT_SHAPES = {'features_buffer': (1, 25, 512), 'desire_pulse': (1, 25, 8), 'traffic_convention': (1, 2)}
SPLIT_VISION_SLICES = {'hidden_state': slice(0, 512), 'pose': slice(512, 524)}
SPLIT_POLICY_SLICES = {'plan': slice(0, 495), 'meta': slice(495, 550)}

SUPERCOMBO_INPUT_SHAPES = {
  'img': (1, 12, 128, 256), 'big_img': (1, 12, 128, 256),
  'desire': (1, 100, 8), 'features_buffer': (1, 99, 512),
  'lateral_control_params': (1, 2), 'prev_desired_curv': (1, 100, 1),
  'traffic_convention': (1, 2),
}
SUPERCOMBO_SLICES = {'plan': slice(0, 495), 'hidden_state': slice(495, 1007), 'meta': slice(1007, 1062)}

CAM_W, CAM_H = 1928, 1208

ARCHETYPES = {
  'vision_policy_split': Archetype(
    name='vision_policy_split',
    metadata_structure=_make_vision_policy_metadata(
      SPLIT_VISION_INPUT_SHAPES, SPLIT_POLICY_INPUT_SHAPES,
      SPLIT_VISION_SLICES, SPLIT_POLICY_SLICES),
    model_stubs=[DummyModel('vision', 'driving_test_tinygrad.pkl'),
                 DummyModel('policy', 'driving_test_tinygrad.pkl')],
    is_20hz=True,
    expected_model_type='split',
    expected_constants_class=SplitModelConstants,
    expected_parser_module='parse_model_outputs_split',
    expected_desire_key='desire',
  ),
  'vision_multi_policy': Archetype(
    name='vision_multi_policy',
    metadata_structure=_make_multi_policy_metadata(
      SPLIT_VISION_INPUT_SHAPES, SPLIT_POLICY_INPUT_SHAPES,
      SPLIT_VISION_SLICES, SPLIT_POLICY_SLICES),
    model_stubs=[DummyModel('vision', 'driving_test_tinygrad.pkl'),
                 DummyModel('offPolicy', 'driving_test_tinygrad.pkl')],
    is_20hz=True,
    expected_model_type='multi_policy',
    expected_constants_class=SplitModelConstants,
    expected_parser_module='parse_model_outputs_split',
    expected_desire_key='desire',
  ),
  'tri_policy': Archetype(
    name='tri_policy',
    metadata_structure=_make_tri_policy_metadata(
      SPLIT_VISION_INPUT_SHAPES, SPLIT_POLICY_INPUT_SHAPES,
      SPLIT_VISION_SLICES, SPLIT_POLICY_SLICES),
    model_stubs=[DummyModel('vision', 'driving_test_tinygrad.pkl'),
                 DummyModel('onPolicy', 'driving_test_tinygrad.pkl'),
                 DummyModel('offPolicy', 'driving_test_tinygrad.pkl')],
    is_20hz=True,
    expected_model_type='multi_policy',
    expected_constants_class=SplitModelConstants,
    expected_parser_module='parse_model_outputs_split',
    expected_desire_key='desire',
  ),
  'supercombo_non20hz': Archetype(
    name='supercombo_non20hz',
    metadata_structure=_make_supercombo_metadata(SUPERCOMBO_INPUT_SHAPES, SUPERCOMBO_SLICES),
    model_stubs=[DummyModel('supercombo', 'driving_test_tinygrad.pkl')],
    is_20hz=False,
    expected_model_type='supercombo',
    expected_constants_class=ModelConstants,
    expected_parser_module='parse_model_outputs',
    expected_desire_key='desire',
  ),
}


def make_pkl_data(archetype):
  return {
    'metadata': archetype.metadata_structure,
    (CAM_W, CAM_H): {'run_policy': _noop_jit, 'warp_enqueue': _noop_jit},
  }


def write_pkl(tmp_path, archetype):
  pkl_path = tmp_path / 'driving_test_tinygrad.pkl'
  with open(pkl_path, 'wb') as f:
    pickle.dump(make_pkl_data(archetype), f)
  return pkl_path


def make_bundle(archetype):
  return DummyBundle(
    models=archetype.model_stubs,
    is_20hz=archetype.is_20hz,
  )


@pytest.fixture
def patch_modeld(monkeypatch):
  def _patch(bundle):
    monkeypatch.setattr(helpers, 'get_active_bundle', lambda params=None: bundle, raising=False)
    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None: bundle, raising=False)

  return _patch


@pytest.fixture
def model_state_factory(tmp_path, monkeypatch, patch_modeld):
  from openpilot.system.hardware import hw

  def _create(archetype):
    write_pkl(tmp_path, archetype)
    bundle = make_bundle(archetype)
    patch_modeld(bundle)
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    return modeld_module.ModelState(cam_w=CAM_W, cam_h=CAM_H)

  return _create
