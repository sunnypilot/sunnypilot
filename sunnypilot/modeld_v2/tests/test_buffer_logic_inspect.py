import numpy as np
import pytest
from typing import Any

import openpilot.sunnypilot.models.helpers as helpers
import openpilot.sunnypilot.models.runners.helpers as runner_helpers
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module

ModelState = modeld_module.ModelState

# These are the shapes extracted/loaded from the model onnx
SHAPE_MODE_PARAMS = [
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), "nav_features": (1, 256), "nav_instructions": (1, 150)}, 'non20hz'), # Optimus Prime
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), "lat_planner_state": (1, 4),}, 'non20hz'), # farmville
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), "lateral_control_params": (1, 2), "prev_desired_curv": (1, 100, 1)}, 'non20hz'), # wd40
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), 'prev_desired_curv': (1, 100, 1), "lateral_control_params": (1, 2),}, 'non20hz'), # NTS
  ({'desire': (1, 25, 8), 'features_buffer': (1, 24, 512)}, '20hz'), # NPR
  ({'desire': (1, 100, 8), 'features_buffer': (1, 99, 512), 'prev_desired_curv': (1, 100, 1), "lateral_control_params": (1, 2),}, 'non20hz'), # NTS
  ({'desire': (1, 25, 8), 'features_buffer': (1, 25, 512)}, 'split'), # Steam Powered v2
  ({'desire_pulse': (1, 25, 8), 'features_buffer': (1, 25, 512)}, 'split'), # desire rename
]


# This creates a dummy runner, override, and bundle instance for the tests to run, without actually trying to load a physical model.
class DummyOverride:
  def __init__(self, key: str, value: str) -> None:
    self.key = key
    self.value = value


class DummyBundle:
  def __init__(self) -> None:
    self.overrides = [DummyOverride('lat', '.1'), DummyOverride('long', '.3')]
    self.generation = 10  # default to non-mlsim for buffer-update tests, as raising to 11 here will zero curvature buffer


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
    shape = input_shapes.get('desire', (1, 0, 0)) # [batch, history, features]
    if shape[1] == 25:
      self.is_20hz = True
    else:
      self.is_20hz = False

  # Minimal prepare/run methods so ModelState can be run without actually running the model
  def prepare_inputs(self, imgs_cl, numpy_inputs, frames):
    return None

  def run_model(self):
    return {
      'hidden_state': np.zeros((1, self.constants.FEATURE_LEN), dtype=np.float32),
      'desired_curvature': np.zeros((1, 1), dtype=np.float32),
    }


@pytest.fixture
def shapes(request):
  return request.param


@pytest.fixture
def bundle() -> DummyBundle:
  return DummyBundle()


@pytest.fixture
def runner(shapes) -> DummyModelRunner:
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
    return np.arange(shape[1])
  return None


@pytest.mark.parametrize("shapes,mode", SHAPE_MODE_PARAMS, indirect=["shapes"])
def test_buffer_shapes_and_indices(shapes, mode, apply_patches):
  state = ModelState(None)
  constants = DummyModelRunner(shapes).constants
  for key in shapes:
    buf = state.temporal_buffers.get(key, None)
    idxs = state.temporal_idxs_map.get(key, None)
    if buf is None:
      continue    # not all shapes are 3D, and the non-3D ones are not buffered
    # Buffer shape logic
    if mode == 'split':
      expected_shape = (1, constants.FULL_HISTORY_BUFFER_LEN, shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, 'split', key)
    elif mode == '20hz':
      expected_shape = (1, constants.FULL_HISTORY_BUFFER_LEN, shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, '20hz', key)
    elif mode == 'non20hz':
      expected_shape = (1, shapes[key][1], shapes[key][2])
      expected_idxs = get_expected_indices(shapes[key], constants, 'non20hz', key)

    assert buf is not None, f"{key}: buffer not found"
    assert buf.shape == expected_shape, f"{key}: buffer shape {buf.shape} != expected {expected_shape}"
    if expected_idxs is not None:
      assert np.all(idxs == expected_idxs), f"{key}: buffer idxs {idxs} != expected {expected_idxs}"
    else:
      assert idxs is None or idxs.size == 0, f"{key}: buffer idxs should be None or empty"


def legacy_buffer_update(buf, new_val, mode, key, constants, idxs, input_shape, prev_desire=None):
  # This is what we compare the new dynamic logic to, to ensure it does the same thing
  if mode == 'split':
    if key == 'desire' or key.startswith('desire'):
      buf[0,:-1] = buf[0,1:]
      buf[0,-1] = new_val
      return buf.reshape((1, constants.INPUT_HISTORY_BUFFER_LEN, constants.TEMPORAL_SKIP, -1)).max(axis=2)
    elif key == 'features_buffer':
      buf[0,:-1] = buf[0,1:]
      buf[0,-1] = new_val
      return buf[0, idxs]
    elif key == 'prev_desired_curv':
      buf[0,:-1] = buf[0,1:]
      buf[0,-1,:] = new_val
      return buf[0, idxs]
  elif mode == '20hz':
    if key == 'desire':
      buf[:-1] = buf[1:]
      buf[-1] = new_val
      reshape_dims = (1, buf.shape[1], -1, buf.shape[2])
      reshaped = buf.reshape(reshape_dims).max(axis=2)
      # Slice to last shape[1] elements to match model input shape
      input_len = reshaped.shape[1]
      model_input_len = 25  # For 20hz mode, desire shape[1] is 25
      if input_len > model_input_len:
        reshaped = reshaped[:, -model_input_len:, :]
      return reshaped
    elif key == 'features_buffer':
      buffer_history_len = buf.shape[1]
      legacy_buf = np.zeros((buffer_history_len, buf.shape[2]), dtype=np.float32)
      legacy_buf[:] = buf[0]
      legacy_buf[:-1] = legacy_buf[1:]
      legacy_buf[-1] = new_val
      return legacy_buf[idxs]
    elif key == 'prev_desired_curv':
      buffer_history_len = buf.shape[1]
      legacy_buf = np.zeros((buffer_history_len, buf.shape[2]), dtype=np.float32)
      legacy_buf[:] = buf[0]
      legacy_buf[:-1] = legacy_buf[1:]
      legacy_buf[-1,:] = new_val
      return legacy_buf[idxs]
  elif mode == 'non20hz':
    if key == 'desire':
      desire_len = constants.DESIRE_LEN
      if prev_desire is None:
        prev_desire = np.zeros(desire_len, dtype=np.float32)
      # Set first element to zero
      new_val = new_val.copy()
      new_val[0] = 0
      # Shift buffer by desire len
      buf[0][:-desire_len] = buf[0][desire_len:]
      # Only insert new desire if rising edge
      buf[0][-desire_len:] = np.where(new_val - prev_desire > 0.99, new_val, 0)
      prev_desire[:] = new_val
      return buf[0]
    elif key == 'features_buffer':
      buf[0, :-1] = buf[0, 1:]
      buf[0, -1] = new_val
      return buf[0, -input_shape[1]:]  # (99, 512)
    elif key == 'prev_desired_curv':
      length = new_val.shape[0]
      buf[0,:-length,0] = buf[0,length:,0]
      buf[0,-length:,0] = new_val[:length]
      return buf[0]
  return None


def dynamic_buffer_update(state, key, new_val, mode):
  if key == 'desire' or key.startswith('desire'):
    inputs = {k: np.zeros(v[2], dtype=np.float32) if len(v) == 3 else np.zeros(v[1], dtype=np.float32)
              for k, v in state.model_runner.input_shapes.items() if k != key}
    inputs[key] = new_val.copy()
    # ModelState.run expects desire as a pulse, so we zero the first element.
    inputs[key][0] = 0
    state.run({}, {}, inputs, prepare_only=False)
    return state.numpy_inputs[key]

  if key == 'features_buffer':
    inputs = {k: np.zeros(v[2], dtype=np.float32) if len(v) == 3 else np.zeros(v[1], dtype=np.float32)
              for k, v in state.model_runner.input_shapes.items() if k != 'features_buffer'}
    def run_model_stub():
      return {
        'hidden_state': np.asarray(new_val, dtype=np.float32).reshape(1, -1),
      }
    state.model_runner.run_model = run_model_stub
    state.run({}, {}, inputs, prepare_only=False)
    return state.numpy_inputs['features_buffer'][0]

  if key == 'prev_desired_curv':
    inputs = {k: np.zeros(v[2], dtype=np.float32) if len(v) == 3 else np.zeros(v[1], dtype=np.float32)
              for k, v in state.model_runner.input_shapes.items() if k != 'prev_desired_curv'}
    def run_model_stub():
      return {
        'hidden_state': np.zeros((1, state.constants.FEATURE_LEN), dtype=np.float32),
        'desired_curvature': np.asarray(new_val, dtype=np.float32).reshape(1, -1),
      }
    state.model_runner.run_model = run_model_stub
    state.run({}, {}, inputs, prepare_only=False)
    return state.numpy_inputs['prev_desired_curv'][0]
  return None


@pytest.mark.parametrize("shapes,mode", SHAPE_MODE_PARAMS, indirect=["shapes"])
@pytest.mark.parametrize("key", ["desire", "features_buffer", "prev_desired_curv"])
def test_buffer_update_equivalence(shapes, mode, key, apply_patches):
  state = ModelState(None)
  if key == "desire":
    desire_keys = [k for k in shapes.keys() if k.startswith('desire')]
    if desire_keys:
      actual_key = desire_keys[0]  # Use the first (and likely only) desire key
  else:
    actual_key = key

  if actual_key not in state.numpy_inputs:
    pytest.skip()

  constants = DummyModelRunner(shapes).constants
  buf = state.temporal_buffers.get(actual_key, None)
  idxs = state.temporal_idxs_map.get(actual_key, None)
  input_shape = shapes[actual_key]
  prev_desire = np.zeros(constants.DESIRE_LEN, dtype=np.float32) if key == 'desire' else None

  for step in range(20):    # multiple steps to ensure history is built up
    new_val = np.full((input_shape[2],), step, dtype=np.float32)
    expected = legacy_buffer_update(buf, new_val, mode, actual_key, constants, idxs, input_shape, prev_desire)
    actual = dynamic_buffer_update(state, actual_key, new_val, mode)
    if expected is not None and actual is not None and expected.shape != actual.shape:
      if expected.ndim == 2 and actual.ndim == 2 and expected.shape[1] == actual.shape[1]:
        expected = expected[-actual.shape[0]:]
    assert np.allclose(actual, expected), f"{mode} {actual_key}: dynamic buffer update does not match legacy logic"
