import os
import pickle
from abc import abstractmethod, ABC
import numpy as np

from cereal import custom
from openpilot.sunnypilot.modeld_v2 import MODEL_PATH
from openpilot.sunnypilot.modeld_v2.models.commonmodel_pyx import DrivingModelFrame, CLMem
from openpilot.sunnypilot.modeld_v2.runners.ort_helpers import make_onnx_cpu_runner, ORT_TYPES_TO_NP_TYPES
from openpilot.sunnypilot.modeld_v2.runners.tinygrad_helpers import qcom_tensor_from_opencl_address
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser as CombinedParser
from openpilot.sunnypilot.modeld_v2.parse_model_outputs_split import Parser as SplitParser
from openpilot.system.hardware import TICI
from openpilot.system.hardware.hw import Paths

from openpilot.sunnypilot.models.helpers import get_active_bundle
from tinygrad.tensor import Tensor

# Set QCOM environment variable for TICI devices, potentially enabling hardware acceleration
if TICI:
  os.environ['QCOM'] = '1'

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
CUSTOM_MODEL_PATH = Paths.model_root()
ModelType = custom.ModelManagerSP.Model.Type

# Type definitions for clarity
NumpyDict = dict[str, np.ndarray]
ShapeDict = dict[str, tuple[int, ...]]
SliceDict = dict[str, slice]
CLMemDict = dict[str, CLMem]
FrameDict = dict[str, DrivingModelFrame]

class ModelData:
  """
  Stores metadata and configuration for a specific machine learning model.

  This class loads model metadata (like input shapes and output slices)
  from a pickle file associated with a model instance.

  :param model: The machine learning model object containing metadata.
  """
  def __init__(self, model: custom.ModelManagerSP.Model):
    self.model = model
    self.metadata = model.metadata
    self.input_shapes: ShapeDict = {}
    self.output_slices: SliceDict = {}
    if self.metadata:
      self._load_metadata()

  def _load_metadata(self) -> None:
    """Loads input shapes and output slices from the model's metadata pickle file."""
    metadata_path = f"{CUSTOM_MODEL_PATH}/{self.metadata.fileName}"
    with open(metadata_path, 'rb') as f:
      model_metadata = pickle.load(f)
    self.input_shapes = model_metadata.get('input_shapes', {})
    self.output_slices = model_metadata.get('output_slices', {})


class ModelRunner(ABC):
  """
  Abstract base class for managing and executing machine learning models.

  Provides a common interface for loading models, preparing inputs, running
  inference, and slicing/parsing outputs based on model metadata. Derived
  classes implement the specifics of input preparation and model execution
  for different frameworks (e.g., Tinygrad, ONNX).
  """
  def __init__(self):
    """Initializes the model runner, loading the active model bundle."""
    self.is_20hz: bool | None = None
    self.models: dict[int, ModelData] = {}
    self._model_data: ModelData | None = None # Active model data for current operation
    self.inputs: dict = {}
    self.parser = CombinedParser()
    self._load_models()

  def _load_models(self) -> None:
    """Loads the active model bundle configuration and sets up ModelData."""
    bundle = get_active_bundle()
    if not bundle:
      raise ValueError("No active model bundle found, why are we being executed?")

    self.models = {model.type.raw: ModelData(model) for model in bundle.models}
    self.is_20hz = bundle.is20hz

  @property
  def input_shapes(self) -> ShapeDict:
    """Returns the input shapes for the currently active model."""
    if self._model_data:
      return self._model_data.input_shapes
    raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

  @abstractmethod
  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """
    Abstract method to prepare inputs for model inference.

    :param imgs_cl: Dictionary of OpenCL memory objects for image inputs.
    :param numpy_inputs: Dictionary of numpy arrays for non-image inputs.
    :param frames: Dictionary of DrivingModelFrame objects for context.
    :return: Dictionary of prepared inputs ready for the model.
    """
    raise NotImplementedError

  @abstractmethod
  def _run_model(self) -> NumpyDict:
    """
    Abstract method to execute model inference with prepared inputs.

    :return: Dictionary containing the model's raw output arrays.
    """
    raise NotImplementedError

  def _slice_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """
    Slices the raw model output array based on the output_slices metadata.

    :param model_outputs: The raw numpy array output from the model.
    :return: A dictionary where keys are output names and values are sliced numpy arrays.
    """
    if not self._model_data:
      raise ValueError("Model data is not available. Ensure the model is loaded correctly.")
    sliced_outputs = {k: model_outputs[np.newaxis, v] for k, v in self._model_data.output_slices.items()}
    if SEND_RAW_PRED:
      sliced_outputs['raw_pred'] = model_outputs.copy() # Optionally include the full raw output
    return sliced_outputs

  def run_model(self) -> NumpyDict:
    """
    Executes the model inference pipeline: runs the model and parses outputs.

    :return: Dictionary containing the final parsed model outputs.
    """
    return self._run_model() # Parsing is handled within specific runner implementations

class TinygradRunner(ModelRunner):
  """
  A ModelRunner implementation for executing Tinygrad models.

  Handles loading Tinygrad model artifacts (.pkl), preparing inputs as Tinygrad
  Tensors (potentially using QCOM extensions on TICI), running inference,
  and parsing the outputs.

  :param model_type: The type of model (e.g., supercombo) to load and run.
  """
  def __init__(self, model_type: int = ModelType.supercombo):
    super().__init__()
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
    outputs = self.model_run(**self.inputs).numpy().flatten()
    return self._parse_outputs(outputs)

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses the raw model outputs using the standard Parser."""
    result: NumpyDict = self.parser.parse_outputs(self._slice_outputs(model_outputs))
    return result

class TinygradVisionRunner(TinygradRunner):
  """
  A TinygradRunner specialized for vision-only models.

  Uses a SplitParser to handle outputs specific to the vision part of a split model setup.
  """
  def __init__(self):
    super().__init__(ModelType.vision)
    self.parser = SplitParser() # Use SplitParser for vision-specific outputs

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses vision model outputs using SplitParser."""
    result: NumpyDict = self.parser.parse_vision_outputs(self._slice_outputs(model_outputs))
    return result

class TinygradPolicyRunner(TinygradRunner):
  """
  A TinygradRunner specialized for policy-only models.

  Uses a SplitParser to handle outputs specific to the policy part of a split model setup.
  """
  def __init__(self):
    super().__init__(ModelType.policy)
    self.parser = SplitParser() # Use SplitParser for policy-specific outputs

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses policy model outputs using SplitParser."""
    result: NumpyDict = self.parser.parse_policy_outputs(self._slice_outputs(model_outputs))
    return result

class TinygradSplitRunner(ModelRunner):
  """
  A ModelRunner that coordinates separate TinygradVisionRunner and TinygradPolicyRunner instances.

  Manages the execution of split vision and policy models, combining their inputs and outputs.
  """
  def __init__(self):
    super().__init__()
    self.vision_runner = TinygradVisionRunner()
    self.policy_runner = TinygradPolicyRunner()

  def _run_model(self) -> NumpyDict:
    """Runs both vision and policy models and merges their parsed outputs."""
    policy_output = self.policy_runner.run_model()
    vision_output = self.vision_runner.run_model()
    return {**policy_output, **vision_output} # Combine results

  @property
  def input_shapes(self) -> ShapeDict:
    """Returns the combined input shapes from both vision and policy models."""
    return {**self.policy_runner.input_shapes, **self.vision_runner.input_shapes}

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepares inputs for both vision and policy models."""
    # Policy inputs only depend on numpy_inputs
    self.policy_runner.prepare_policy_inputs(numpy_inputs)
    # Vision inputs depend on imgs_cl and frames
    self.vision_runner.prepare_vision_inputs(imgs_cl, frames)
    # Return combined inputs (though they are stored within respective runners)
    return {**self.policy_runner.inputs, **self.vision_runner.inputs}

class ONNXRunner(ModelRunner):
  """
  A ModelRunner implementation for executing ONNX models using ONNX Runtime CPU.

  Handles loading the ONNX model, preparing inputs as numpy arrays, running
  inference, and parsing outputs. This runner is typically used on non-TICI platforms.
  """
  def __init__(self):
    super().__init__()
    # Initialize ONNX Runtime session for the model at MODEL_PATH
    self.runner = make_onnx_cpu_runner(MODEL_PATH)
    # Map expected input names to numpy dtypes
    self.input_to_nptype = {
      model_input.name: ORT_TYPES_TO_NP_TYPES[model_input.type]
      for model_input in self.runner.get_inputs()
    }
    # For ONNX, _model_data isn't strictly necessary as shapes/types come from the runner
    # However, we might still need output_slices if custom models define them.
    # We assume supercombo type for potentially loading output_slices metadata if available.
    self._model_data = self.models.get(ModelType.supercombo)


  @property
  def input_shapes(self) -> ShapeDict:
    """Returns the input shapes defined in the ONNX model."""
    # ONNX shapes are derived directly from the model definition via the runner
    return {runner_input.name: runner_input.shape for runner_input in self.runner.get_inputs()}

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepares inputs for the ONNX model as numpy arrays."""
    self.inputs = numpy_inputs # Start with non-image numpy inputs
    # Convert image inputs from OpenCL buffers to numpy arrays
    for key in imgs_cl:
      buffer = frames[key].buffer_from_cl(imgs_cl[key])
      reshaped_buffer = buffer.reshape(self.input_shapes[key])
      self.inputs[key] = reshaped_buffer.astype(dtype=self.input_to_nptype[key])
    return self.inputs

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses the raw ONNX model outputs using the standard Parser."""
    # Use slicing if metadata is available, otherwise pass raw outputs
    outputs_to_parse = self._slice_outputs(model_outputs) if self._model_data else {'raw_pred': model_outputs}
    result: NumpyDict = self.parser.parse_outputs(outputs_to_parse)
    return result

  def _run_model(self) -> NumpyDict:
    """Runs the ONNX model inference and parses the outputs."""
    # Execute the ONNX Runtime session
    outputs = self.runner.run(None, self.inputs)[0].flatten()
    return self._parse_outputs(outputs)

def get_model_runner() -> ModelRunner:
  """
  Factory function to create and return the appropriate ModelRunner instance.

  Selects between ONNXRunner (for non-TICI platforms) and TinygradRunner
  (for TICI platforms), choosing TinygradSplitRunner if separate vision/policy
  models are detected in the active bundle.

  :return: An instance of a ModelRunner subclass (ONNXRunner, TinygradRunner, or TinygradSplitRunner).
  """
  if not TICI:
    return ONNXRunner()

  # On TICI platforms, use Tinygrad runners
  bundle = get_active_bundle()
  if bundle and bundle.models:
    model_types = {m.type.raw for m in bundle.models}
    # Check if the bundle uses separate vision and policy models
    if ModelType.vision in model_types or ModelType.policy in model_types:
      return TinygradSplitRunner()
    # Otherwise, assume a single model (likely supercombo)
    if bundle.models:
      return TinygradRunner(bundle.models[0].type.raw)

  # Default fallback to TinygradRunner with the supercombo type if bundle info is missing/incomplete
  return TinygradRunner(ModelType.supercombo)
