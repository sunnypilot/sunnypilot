import os
import pickle
from abc import abstractmethod
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
ModelManager = custom.ModelManagerSP


class ModelData:
  def __init__(self, model=None):
    self.model = model
    self.metadata = model.metadata if model else None
    self.input_shapes = {}
    self.output_slices = {}

    if self.metadata:
      self._load_metadata()

  def _load_metadata(self):
    metadata_path = f"{CUSTOM_MODEL_PATH}/{self.metadata.fileName}"
    with open(metadata_path, 'rb') as f:
      model_metadata = pickle.load(f)
    self.input_shapes = model_metadata.get('input_shapes', {})
    self.output_slices = model_metadata.get('output_slices', {})


class ModelRunner:
  def __init__(self):
    """Initialize the model runner with paths to model and metadata files."""
    self.is_20hz = None
    self.models = {}
    self._model_data = None
    bundle = get_active_bundle()

    if bundle:
      bundle_models = {model.type.raw: model for model in bundle.models}

      drive_model = bundle_models.get(ModelManager.Model.Type.supercombo)
      policy_model = bundle_models.get(ModelManager.Model.Type.policy)
      vision_model = bundle_models.get(ModelManager.Model.Type.vision)

      if drive_model:
        self.models[ModelManager.Model.Type.supercombo] = ModelData(model=drive_model)
      elif policy_model and vision_model:
        self.models[ModelManager.Model.Type.policy] = ModelData(model=policy_model)
        self.models[ModelManager.Model.Type.vision] = ModelData(model=vision_model)

      self.is_20hz = bundle.is20hz

    self.inputs: dict = {}
    self.parser = Parser()

  @property
  @abstractmethod
  def input_shapes(self) -> dict[str, tuple[int]]:
    return self._model_data.input_shapes

  @abstractmethod
  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    """Prepare inputs for model inference."""
    raise NotImplementedError

  @abstractmethod
  def _run_model(self):
    """Run model inference with prepared inputs."""
    raise NotImplementedError("This method should be implemented in subclasses.")

  def _slice_outputs(self, model_outputs: np.ndarray) -> dict:
    """Slice model outputs according to metadata configuration."""
    if not self._model_data:
      raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

    sliced_outputs = {k: model_outputs[np.newaxis, v] for k, v in self._model_data.output_slices.items()}
    if SEND_RAW_PRED:
      sliced_outputs['raw_pred'] = model_outputs.copy()
    return sliced_outputs

  @abstractmethod
  def _parse_outputs(self, model_outputs: dict[str, np.ndarray]) -> dict:
    """Parse model outputs into a dictionary."""
    raise NotImplementedError("This method should be implemented in subclasses.")

  def run_model(self) -> dict[str, np.ndarray]:
    """Run model inference with prepared inputs and parse outputs."""
    parsed_result: dict[str, np.ndarray] = self._parse_outputs(self._run_model())
    return parsed_result


class TinygradRunner(ModelRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def __init__(self, model_type: ModelManager.Model.Type = ModelManager.Model.Type.supercombo):
    super().__init__()

    self._model_data = self.models.get(model_type)
    assert self._model_data.model.artifact.fileName.endswith('_tinygrad.pkl'), f"Invalid model file {self._model_data.model.artifact.fileName} for TinygradRunner"

    model_pkl_path = f"{CUSTOM_MODEL_PATH}/{self._model_data.model.artifact.fileName}"

    # Load Tinygrad model
    with open(model_pkl_path, "rb") as f:
      try:
        self.model_run = pickle.load(f)
      except FileNotFoundError as e:
        assert "/dev/kgsl-3d0" not in str(e), "Model was built on C3 or C3X, but is being loaded on PC"
        raise

    self.input_to_dtype = {}
    self.input_to_device = {}

    for idx, name in enumerate(self.model_run.captured.expected_names):
      self.input_to_dtype[name] = self.model_run.captured.expected_st_vars_dtype_device[idx][2]  # dtype
      self.input_to_device[name] = self.model_run.captured.expected_st_vars_dtype_device[idx][3]  # device

  def prepare_vision_inputs(self, imgs_cl: dict[str, CLMem], frames: dict[str, DrivingModelFrame]) -> dict:
    for key in imgs_cl:
      if TICI and key not in self.inputs:
        self.inputs[key] = qcom_tensor_from_opencl_address(imgs_cl[key].mem_address, self._model_data.input_shapes[key], dtype=self.input_to_dtype[key])
      elif not TICI:
        shape = frames[key].buffer_from_cl(imgs_cl[key]).reshape(self._model_data.input_shapes[key])
        self.inputs[key] = Tensor(shape, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

  def prepare_policy_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray]) -> dict:
    for key, value in numpy_inputs.items():
      if key not in imgs_cl:
        self.inputs[key] = Tensor(value, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

    return self.inputs

  @abstractmethod
  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    self.prepare_vision_inputs(imgs_cl, frames)
    self.prepare_policy_inputs(imgs_cl, numpy_inputs)
    return self.inputs

  def _run_model(self):
    return self.model_run(**self.inputs).numpy().flatten()
  
  @abstractmethod
  def _parse_outputs(self, model_outputs: np.ndarray) -> dict:
    """Parse model outputs into a dictionary."""
    return self.parser.parse_outputs(self._slice_outputs(model_outputs))


class TinygradVisionRunner(TinygradRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def __init__(self):
    super().__init__(ModelManager.Model.Type.vision)
    self.parser = SplitParser()

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    raise NotImplementedError("TinygradVisionRunner does not implement prepare_inputs method. you must call prepare_vision_inputs instead.")

  def _parse_outputs(self, model_outputs: np.ndarray) -> dict:
    """Parse model outputs into a dictionary."""
    return self.parser.parse_vision_outputs(self._slice_outputs(model_outputs))

class TinygradPolicyRunner(TinygradRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def __init__(self):
    super().__init__(ModelManager.Model.Type.policy)
    self.parser = SplitParser()

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    raise NotImplementedError("TinygradPolicyRunner does not implement prepare_inputs method. you must call prepare_policy_inputs instead.")

  def _parse_outputs(self, model_outputs: np.ndarray) -> dict:
    """Parse model outputs into a dictionary."""
    return self.parser.parse_policy_outputs(self._slice_outputs(model_outputs))

class TinygradSplitRunner(ModelRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def _run_model(self):
    policy_output = self.policy_runner.run_model()
    vision_output = self.vision_runner.run_model()
    return { **policy_output, **vision_output }

  def __init__(self):
    super().__init__()
    self.policy_runner = TinygradPolicyRunner()
    self.vision_runner = TinygradVisionRunner()
  
  @property
  def input_shapes(self) -> dict[str, tuple[int]]:
    """Get the input shapes for the model."""
    return { **self.policy_runner.input_shapes, **self.vision_runner.input_shapes }

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    self.policy_runner.prepare_policy_inputs(imgs_cl, numpy_inputs)
    self.vision_runner.prepare_vision_inputs(imgs_cl, frames)
    return { **self.policy_runner.inputs, **self.vision_runner.inputs }

class ONNXRunner(ModelRunner):
  """ONNX implementation of model runner for non-TICI hardware."""

  def __init__(self):
    super().__init__()
    self.runner = make_onnx_cpu_runner(MODEL_PATH)

    self.input_to_nptype = {
      model_input.name: ORT_TYPES_TO_NP_TYPES[model_input.type]
      for model_input in self.runner.get_inputs()
    }

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    self.inputs = numpy_inputs
    for key in imgs_cl:
      self.inputs[key] = frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key]).astype(dtype=self.input_to_nptype[key])
    return self.inputs

  def _run_model(self):
    return self.runner.run(None, self.inputs)[0].flatten()

def get_model_runner() -> ModelRunner:
  """Get the appropriate model runner based on the hardware and model types."""
  if not TICI:
    return ONNXRunner()

  bundle = get_active_bundle()
  if bundle and bundle.models:
    types = {m.type.raw for m in bundle.models}
    if ModelManager.Model.Type.vision in types or ModelManager.Model.Type.policy in types:
      return TinygradSplitRunner()
    return TinygradRunner(bundle.models[0].type.raw)

  return TinygradRunner()
