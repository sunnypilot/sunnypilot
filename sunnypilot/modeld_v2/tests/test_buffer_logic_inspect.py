import numpy as np
import pytest
from typing import Any

import openpilot.sunnypilot.models.helpers as helpers
import openpilot.sunnypilot.models.runners.helpers as runner_helpers
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module

class DummyOverride:
  def __init__(self, key: str, value: str) -> None:
    self.key = key
    self.value = value

class DummyBundle:
  def __init__(self) -> None:
    self.overrides = [DummyOverride('lat', '.1'), DummyOverride('long', '.3')]
    self.generation = 11  # For mlsim property

class DummyModelRunner:
  def __init__(self, input_shapes: dict[str, tuple[int, int, int]], constants: Any = None) -> None:
    self.input_shapes = input_shapes
    self.constants = constants or type('C', (), {
      'FULL_HISTORY_BUFFER_LEN': 100,
      'FEATURE_LEN': 512,
      'DESIRE_LEN': 8,
      'PREV_DESIRED_CURV_LEN': 1,
      'INPUT_HISTORY_BUFFER_LEN': 25,
      'TEMPORAL_SKIP': 4,
    })()
    self.vision_input_names: list[str] = []
    # Set flags based on shapes for correct buffer logic
    shape = input_shapes.get('desire', (1, 0, 0))
    if shape[1] == 25:
      self.is_20hz_3d = True
      self.is_20hz = False
    elif shape[1] == 24:
      self.is_20hz_3d = False
      self.is_20hz = True
    else:
      self.is_20hz_3d = False
      self.is_20hz = False

ModelState = modeld_module.ModelState
@pytest.fixture
def shapes(request):
  """Return the parametrized shapes dict (indirect param). """
  return request.param

@pytest.fixture
def bundle() -> DummyBundle:
  """Fixture that creates a model bundle instance for the darn test."""
  return DummyBundle()

@pytest.fixture
def runner(shapes) -> DummyModelRunner:
  """Fixture that constructs a model runner for the shapes."""
  return DummyModelRunner(shapes)

@pytest.fixture
def apply_patches(monkeypatch: pytest.MonkeyPatch, bundle: DummyBundle, runner: DummyModelRunner):
  monkeypatch.setattr(helpers, 'get_active_bundle', lambda params=None: bundle, raising=False)
  monkeypatch.setattr(runner_helpers, 'get_model_runner', lambda: runner, raising=False)
  monkeypatch.setattr(modeld_module, 'get_model_runner', lambda: runner, raising=False)
  monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None: bundle, raising=False)

# These are expected shapes and indices based on the time the model was presented
def get_expected_indices(shape, constants, mode, key=None):
  if mode == 'split':
    # split model: negative slice logic
    start = -1 - (constants.TEMPORAL_SKIP * (constants.INPUT_HISTORY_BUFFER_LEN - 1))
    arr = np.arange(constants.FULL_HISTORY_BUFFER_LEN)
    idxs = arr[start::constants.TEMPORAL_SKIP]
    return idxs
  elif mode == '20hz':
    num_elements = shape[1]
    step_size = int(-100 / num_elements)
    idxs = np.arange(step_size, step_size * (num_elements + 1), step_size)[::-1]
    return idxs
  elif mode == 'non20hz':
    # non-20hz: full range for temporal inputs
    if key and shape[1] == constants.FULL_HISTORY_BUFFER_LEN:
      return np.arange(constants.FULL_HISTORY_BUFFER_LEN)
    return None

# This is the extracted shapes directly from the model onnx
@pytest.mark.parametrize("shapes,mode", [
  ({'desire': (1, 25, 8), 'features_buffer': (1, 25, 512), 'prev_desired_curv': (1, 25, 1)}, 'split'),
  ({'desire': (1, 25, 8), 'features_buffer': (1, 24, 512), 'prev_desired_curv': (1, 25, 1)}, '20hz'),
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), 'prev_desired_curv': (1, 100, 1)}, 'non20hz'),
], indirect=["shapes"])

def test_buffer_shapes_and_indices(shapes, mode, apply_patches):
  state = ModelState(None)
  constants = DummyModelRunner(shapes).constants # because you can't run the dang thing locally
  for key in shapes:
    buf = getattr(state, f"full_{key}", None)
    idxs = getattr(state, f"{key}_idxs", None)
    # Buffer shape logic
    if mode == 'split':
      expected_shape = (1, constants.FULL_HISTORY_BUFFER_LEN, shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, 'split', key)
    elif mode == '20hz':
      expected_shape = (1, constants.FULL_HISTORY_BUFFER_LEN, shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, '20hz', key)
    elif mode == 'non20hz':
      if key == 'features_buffer':
        expected_shape = (1, shapes[key][1]*4, shapes[key][2])
      else:
        expected_shape = (1, shapes[key][1], shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, 'non20hz', key)

    assert buf is not None, f"{key}: buffer not found"
    assert buf.shape == expected_shape, f"{key}: buffer shape {buf.shape} != expected {expected_shape}"
    if expected_idxs is not None:
      assert np.all(idxs == expected_idxs), f"{key}: buffer idxs {idxs} != expected {expected_idxs}"
    else:
      assert idxs is None or idxs.size == 0, f"{key}: buffer idxs should be None or empty"
