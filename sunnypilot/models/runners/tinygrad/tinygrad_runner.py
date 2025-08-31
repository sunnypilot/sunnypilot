import pickle

import numpy as np
from openpilot.sunnypilot.modeld_v2.runners.tinygrad_helpers import qcom_tensor_from_opencl_address
from openpilot.sunnypilot.models.runners.constants import CLMemDict, FrameDict, NumpyDict, ModelType, ShapeDict, CUSTOM_MODEL_PATH, SliceDict
from openpilot.sunnypilot.models.runners.model_runner import ModelRunner
from openpilot.sunnypilot.models.runners.tinygrad.model_types import PolicyTinygrad, VisionTinygrad, SupercomboTinygrad
from openpilot.system.hardware import TICI
from openpilot.sunnypilot.models.split_model_constants import SplitModelConstants
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants

from tinygrad.tensor import Tensor


class TinygradRunner(ModelRunner, SupercomboTinygrad, PolicyTinygrad, VisionTinygrad):
  """
  A ModelRunner implementation for executing Tinygrad models.

  Handles loading Tinygrad model artifacts (.pkl), preparing inputs as Tinygrad
  Tensors (potentially using QCOM extensions on TICI), running inference,
  and parsing the outputs.

  :param model_type: The type of model (e.g., supercombo) to load and run.
  """
  def __init__(self, model_type: int = ModelType.supercombo):
    ModelRunner.__init__(self)
    SupercomboTinygrad.__init__(self)
    PolicyTinygrad.__init__(self)
    VisionTinygrad.__init__(self)
    self._constants = ModelConstants
    self._model_data = self.models.get(model_type)
    if not self._model_data or not self._model_data.model:
      raise ValueError(f"Model data for type {model_type} not available.")

    artifact_filename = self._model_data.model.artifact.fileName
    assert artifact_filename.endswith('_tinygrad.pkl'), \
      f"Invalid model file {artifact_filename} for TinygradRunner"

    model_pkl_path = f"{CUSTOM_MODEL_PATH}/{artifact_filename}"
    with open(model_pkl_path, "rb") as f:
      try:
        # Load the compiled Tinygrad model runner function
        self.model_run = pickle.load(f)
      except FileNotFoundError as e:
        # Provide a helpful error message if the model was built for a different platform
        assert "/dev/kgsl-3d0" not in str(e), "Model was built on C3 or C3X, but is being loaded on PC"
        raise

    # Map input names to their required dtype and device from the loaded model
    self.input_to_dtype = {}
    self.input_to_device = {}
    for idx, name in enumerate(self.model_run.captured.expected_names):
      info = self.model_run.captured.expected_st_vars_dtype_device[idx]
      self.input_to_dtype[name] = info[2]  # dtype
      self.input_to_device[name] = info[3]  # device

  @property
  def vision_input_names(self) -> list[str]:
    """Returns the list of vision input names from the input shapes."""
    return [name for name in self.input_shapes.keys() if 'img' in name]

  def prepare_vision_inputs(self, imgs_cl: CLMemDict, frames: FrameDict):
    """Prepares vision (image) inputs as Tinygrad Tensors."""
    for key in imgs_cl:
      if TICI and key not in self.inputs:
        # On TICI, directly use OpenCL memory address for efficiency via QCOM extensions
        self.inputs[key] = qcom_tensor_from_opencl_address(imgs_cl[key].mem_address, self.input_shapes[key], dtype=self.input_to_dtype[key])
      elif not TICI:
        # On other platforms, copy data from CL buffer to a numpy array first
        shape = frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key])
        self.inputs[key] = Tensor(shape, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

  def prepare_policy_inputs(self, numpy_inputs: NumpyDict):
    """Prepares non-image (policy) inputs as Tinygrad Tensors."""
    for key, value in numpy_inputs.items():
      self.inputs[key] = Tensor(value, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepares all vision and policy inputs for the model."""
    self.prepare_vision_inputs(imgs_cl, frames)
    self.prepare_policy_inputs(numpy_inputs)
    return self.inputs

  def _run_model(self) -> NumpyDict:
    """Runs the Tinygrad model inference and parses the outputs."""
    outputs = self.model_run(**self.inputs).contiguous().realize().uop.base.buffer.numpy()
    return self._parse_outputs(outputs)

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses the raw model outputs using the standard Parser."""
    if self._model_data is None:
      raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

    result: NumpyDict = self.parser_method_dict[self._model_data.model.type.raw](model_outputs)
    return result


class TinygradSplitRunner(ModelRunner):
  """
  A ModelRunner that coordinates separate TinygradVisionRunner and TinygradPolicyRunner instances.

  Manages the execution of split vision and policy models, combining their inputs and outputs.
  """
  def __init__(self):
    super().__init__()
    self.is_20hz_3d = True
    self.vision_runner = TinygradRunner(ModelType.vision)
    self.policy_runner = TinygradRunner(ModelType.policy)
    self._constants = SplitModelConstants

  def _run_model(self) -> NumpyDict:
    """Runs both vision and policy models and merges their parsed outputs."""
    policy_output = self.policy_runner.run_model()
    vision_output = self.vision_runner.run_model()
    return {**policy_output, **vision_output} # Combine results

  @property
  def vision_input_names(self) -> list[str]:
    """Returns the list of vision input names from the vision runner."""
    return list(self.vision_runner.vision_input_names)

  @property
  def input_shapes(self) -> ShapeDict:
    """Returns the combined input shapes from both vision and policy models."""
    return {**self.policy_runner.input_shapes, **self.vision_runner.input_shapes}

  @property
  def output_slices(self) -> SliceDict:
    """Returns the combined output slices from both vision and policy models."""
    return {**self.policy_runner.output_slices, **self.vision_runner.output_slices}

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepares inputs for both vision and policy models."""
    # Policy inputs only depend on numpy_inputs
    self.policy_runner.prepare_policy_inputs(numpy_inputs)
    # Vision inputs depend on imgs_cl and frames
    self.vision_runner.prepare_vision_inputs(imgs_cl, frames)
    # Return combined inputs (though they are stored within respective runners)
    return {**self.policy_runner.inputs, **self.vision_runner.inputs}
