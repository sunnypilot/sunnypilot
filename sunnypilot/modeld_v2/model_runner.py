import os
import pickle
from abc import ABC, abstractmethod
import numpy as np

from cereal import custom
from openpilot.sunnypilot.modeld_v2 import MODEL_PATH, METADATA_PATH
from openpilot.sunnypilot.modeld.runners.run_helpers_new import get_model_path
from openpilot.sunnypilot.modeld_v2.models.commonmodel_pyx import DrivingModelFrame, CLMem
from openpilot.sunnypilot.modeld_v2.runners.ort_helpers import make_onnx_cpu_runner, ORT_TYPES_TO_NP_TYPES
from openpilot.sunnypilot.modeld.runners import ModelRunner as V1Runner
from openpilot.system.hardware import TICI
from openpilot.system.hardware.hw import Paths

from openpilot.sunnypilot.models.helpers import get_active_bundle

if TICI:
  os.environ['QCOM'] = '1'

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
CUSTOM_MODEL_PATH = Paths.model_root()
ModelManager = custom.ModelManagerSP


class ModelRunner(ABC):
  """Abstract base class for model runners that defines the interface for running ML models."""

  def __init__(self):
    """Initialize the model runner with paths to model and metadata files."""
    metadata_path = METADATA_PATH
    self.is_20hz = None
    self._drive_model = None
    self._metadata_model = None

    if bundle := get_active_bundle():
      bundle_models = {model.type.raw: model for model in bundle.models}
      self._drive_model = bundle_models.get(ModelManager.Type.drive)
      self._metadata_model = bundle_models.get(ModelManager.Type.metadata)
      self.is_20hz = bundle.is20hz

    # Override the metadata path if a metadata model is found in the active bundle
    if self._metadata_model:
      metadata_path = f"{CUSTOM_MODEL_PATH}/{self._metadata_model.fileName}"

    with open(metadata_path, 'rb') as f:
      self.model_metadata = pickle.load(f)

    self.input_shapes = self.model_metadata['input_shapes']
    self.output_slices = self.model_metadata['output_slices']
    self.inputs: dict = {}

  @abstractmethod
  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    """Prepare inputs for model inference."""
    raise NotImplementedError

  @abstractmethod
  def run_model(self):
    """Run model inference with prepared inputs."""

  def slice_outputs(self, model_outputs: np.ndarray) -> dict:
    """Slice model outputs according to metadata configuration."""
    parsed_outputs = {k: model_outputs[np.newaxis, v] for k, v in self.output_slices.items()}
    if SEND_RAW_PRED:
      parsed_outputs['raw_pred'] = model_outputs.copy()
    return parsed_outputs


class SNPERunner(ModelRunner):
  """Use v1 Thneed/SNPE backends via run_helpers."""
  def __init__(self):
    super().__init__()
    paths = get_model_path()
    self.runner = V1Runner(paths)
    # infer dtypes if needed (v1 runner handles its own casts)
    # inputs will be numpy arrays

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray], frames: dict[str, DrivingModelFrame]) -> dict:
    # merge numpy_inputs + image buffers
    inputs = dict(numpy_inputs)
    for key, cl in imgs_cl.items():
      arr = frames[key].buffer_from_cl(cl).reshape(self.input_shapes[key]).astype(np.float32)
      inputs[key] = arr
    self.inputs = inputs
    return self.inputs

  def run_model(self):
    # v1 SNPEModel/ThneedModel exposes run(…) similar to ONNXSession
    outputs = self.runner.run(None, self.inputs)
    return outputs[0].flatten()


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

  def run_model(self):
    return self.runner.run(None, self.inputs)[0].flatten()
