import os
import pickle
from abc import abstractmethod, ABC
import numpy as np

from cereal import custom
from openpilot.sunnypilot.modeld_v2 import MODEL_PATH
from openpilot.sunnypilot.modeld_v2.models.commonmodel_pyx import DrivingModelFrame, CLMem
from openpilot.sunnypilot.modeld_v2.runners.ort_helpers import make_onnx_cpu_runner, ORT_TYPES_TO_NP_TYPES
from openpilot.sunnypilot.modeld_v2.runners.tinygrad_helpers import qcom_tensor_from_opencl_address
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser
from openpilot.sunnypilot.modeld_v2.parse_model_outputs_split import Parser as SplitParser
from openpilot.system.hardware import TICI
from openpilot.system.hardware.hw import Paths

from openpilot.sunnypilot.models.helpers import get_active_bundle
from tinygrad.tensor import Tensor

if TICI:
  os.environ['QCOM'] = '1'

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
CUSTOM_MODEL_PATH = Paths.model_root()
ModelType = custom.ModelManagerSP.Model.Type

# Type definitions
NumpyDict = dict[str, np.ndarray]
ShapeDict = dict[str, tuple[int, ...]]
SliceDict = dict[str, slice]
CLMemDict = dict[str, CLMem]
FrameDict = dict[str, DrivingModelFrame]


class ModelData:
  """Container for model metadata and inference configuration."""

  def __init__(self, model = None):
    self.model = model
    self.metadata = model.metadata if model else None
    self.input_shapes: ShapeDict = {}
    self.output_slices: SliceDict = {}

    if self.metadata:
      self._load_metadata()

  def _load_metadata(self) -> None:
    """Load model metadata from pickle file."""
    metadata_path = f"{CUSTOM_MODEL_PATH}/{self.metadata.fileName}"
    with open(metadata_path, 'rb') as f:
      model_metadata = pickle.load(f)
    self.input_shapes = model_metadata.get('input_shapes', {})
    self.output_slices = model_metadata.get('output_slices', {})


class ModelRunner(ABC):
  """Abstract base class for model runners."""

  def __init__(self):
    """Initialize the model runner."""
    self.is_20hz: bool | None = None
    self.models: dict[int, ModelData] = {}
    self._model_data: ModelData | None = None
    self.inputs: dict = {}
    self.parser = Parser()

    # Load active model bundle
    self._load_models()

  def _load_models(self) -> None:
    """Load active model bundle."""
    bundle = get_active_bundle()
    if not bundle:
      return

    # Map of model types to model objects
    bundle_models = {model.type.raw: model for model in bundle.models}

    # Load either supercombo or policy+vision models
    drive_model = bundle_models.get(ModelType.supercombo)
    policy_model = bundle_models.get(ModelType.policy)
    vision_model = bundle_models.get(ModelType.vision)

    if drive_model:
      self.models[ModelType.supercombo] = ModelData(model=drive_model)
    elif policy_model and vision_model:
      self.models[ModelType.policy] = ModelData(model=policy_model)
      self.models[ModelType.vision] = ModelData(model=vision_model)

    self.is_20hz = bundle.is20hz

  @property
  def input_shapes(self) -> ShapeDict:
    """Get model input shapes."""
    if self._model_data:
      return self._model_data.input_shapes
    raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

  @abstractmethod
  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepare inputs for model inference."""
    raise NotImplementedError

  @abstractmethod
  def _run_model(self) -> NumpyDict:
    """Run model inference with prepared inputs."""
    raise NotImplementedError

  def _slice_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Slice model outputs according to metadata configuration."""
    if not self._model_data:
      raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

    sliced_outputs = {k: model_outputs[np.newaxis, v] for k, v in self._model_data.output_slices.items()}
    if SEND_RAW_PRED:
      sliced_outputs['raw_pred'] = model_outputs.copy()
    return sliced_outputs

  def run_model(self) -> NumpyDict:
    """Run model inference with prepared inputs and parse outputs."""
    return self._run_model()


class TinygradRunner(ModelRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def __init__(self, model_type: int = ModelType.supercombo):
    super().__init__()

    self._model_data = self.models.get(model_type)
    if not self._model_data or not self._model_data.model:
      raise ValueError(f"Model data for type {model_type} not available.")

    artifact_filename = self._model_data.model.artifact.fileName
    assert artifact_filename.endswith('_tinygrad.pkl'), \
      f"Invalid model file {artifact_filename} for TinygradRunner"

    # Load Tinygrad model
    model_pkl_path = f"{CUSTOM_MODEL_PATH}/{artifact_filename}"
    with open(model_pkl_path, "rb") as f:
      try:
        self.model_run = pickle.load(f)
      except FileNotFoundError as e:
        assert "/dev/kgsl-3d0" not in str(e), "Model was built on C3 or C3X, but is being loaded on PC"
        raise

    # Map input names to their required dtype and device
    self.input_to_dtype = {}
    self.input_to_device = {}

    for idx, name in enumerate(self.model_run.captured.expected_names):
      info = self.model_run.captured.expected_st_vars_dtype_device[idx]
      self.input_to_dtype[name] = info[2]  # dtype
      self.input_to_device[name] = info[3]  # device

  def prepare_vision_inputs(self, imgs_cl: CLMemDict, frames: FrameDict):
    for key in imgs_cl:
      if TICI and key not in self.inputs:
        self.inputs[key] = qcom_tensor_from_opencl_address(imgs_cl[key].mem_address, self.input_shapes[key], dtype=self.input_to_dtype[key])
      elif not TICI:
        shape = frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key])
        self.inputs[key] = Tensor(shape, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

  def prepare_policy_inputs(self, numpy_inputs: NumpyDict):
    for key, value in numpy_inputs.items():
        self.inputs[key] = Tensor(value, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepare all inputs for the model."""
    self.prepare_vision_inputs(imgs_cl, frames)
    self.prepare_policy_inputs(numpy_inputs)
    return self.inputs

  def _run_model(self) -> NumpyDict:
    """Run model inference and parse outputs."""
    outputs = self.model_run(**self.inputs).numpy().flatten()
    return self._parse_outputs(outputs)

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parse model outputs into a dictionary."""
    result: NumpyDict = self.parser.parse_outputs(self._slice_outputs(model_outputs))
    return result


class TinygradVisionRunner(TinygradRunner):
  """Tinygrad runner for vision model."""

  def __init__(self):
    super().__init__(ModelType.vision)
    self.parser = SplitParser()

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parse vision outputs."""
    result: NumpyDict = self.parser.parse_vision_outputs(self._slice_outputs(model_outputs))
    return result


class TinygradPolicyRunner(TinygradRunner):
  """Tinygrad runner for policy model."""

  def __init__(self):
    super().__init__(ModelType.policy)
    self.parser = SplitParser()

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parse policy outputs."""
    result: NumpyDict = self.parser.parse_policy_outputs(self._slice_outputs(model_outputs))
    return result


class TinygradSplitRunner(ModelRunner):
  """Combined runner for split vision and policy models."""

  def __init__(self):
    super().__init__()
    self.vision_runner = TinygradVisionRunner()
    self.policy_runner = TinygradPolicyRunner()

  def _run_model(self) -> NumpyDict:
    """Run both vision and policy models and combine outputs."""
    policy_output = self.policy_runner.run_model()
    vision_output = self.vision_runner.run_model()
    return {**policy_output, **vision_output}

  @property
  def input_shapes(self) -> ShapeDict:
    """Get combined input shapes from both models."""
    return {**self.policy_runner.input_shapes, **self.vision_runner.input_shapes}

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepare inputs for both models."""
    self.policy_runner.prepare_policy_inputs(numpy_inputs)
    self.vision_runner.prepare_vision_inputs(imgs_cl, frames)
    return {**self.policy_runner.inputs, **self.vision_runner.inputs}


class ONNXRunner(ModelRunner):
  """ONNX implementation of model runner for non-TICI hardware."""

  def __init__(self):
    super().__init__()
    self.runner = make_onnx_cpu_runner(MODEL_PATH)

    self.input_to_nptype = {
      model_input.name: ORT_TYPES_TO_NP_TYPES[model_input.type]
      for model_input in self.runner.get_inputs()
    }

  @property
  def input_shapes(self) -> ShapeDict:
    """Get input shapes for ONNX model."""
    # For ONNX, we use the shape from the model definition
    return {runner_input.name: runner_input.shape for runner_input in self.runner.get_inputs()}

  def prepare_inputs(self, imgs_cl: CLMemDict, numpy_inputs: NumpyDict, frames: FrameDict) -> dict:
    """Prepare inputs for ONNX model."""
    self.inputs = numpy_inputs

    # Process images from OpenCL memory
    for key in imgs_cl:
      self.inputs[key] = frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key]).astype(dtype=self.input_to_nptype[key])
    return self.inputs

  def _parse_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parse model outputs into a dictionary."""
    result: NumpyDict = self.parser.parse_outputs(self._slice_outputs(model_outputs))
    return result

  def _run_model(self) -> NumpyDict:
    """Run ONNX model inference."""
    outputs = self.runner.run(None, self.inputs)[0].flatten()
    return self._parse_outputs(outputs)


def get_model_runner() -> ModelRunner:
  """Get the appropriate model runner based on the hardware and available models."""
  # Use ONNX runner for non-TICI platforms
  if not TICI:
    return ONNXRunner()

  # Find available models in the active bundle
  bundle = get_active_bundle()
  if bundle and bundle.models:
    model_types = {m.type.raw for m in bundle.models}

    # Use split runner if we have separate vision and policy models
    if ModelType.vision in model_types or ModelType.policy in model_types:
      return TinygradSplitRunner()

    # Otherwise use the single model runner
    return TinygradRunner(bundle.models[0].type.raw)

  # Default to supercombo model
  return TinygradRunner()
