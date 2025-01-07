import os
from openpilot.system.hardware import TICI

from openpilot.sunnypilot.modeld.run_helpers import get_custom_model_paths
#
from tinygrad.tensor import Tensor, dtypes
from openpilot.selfdrive.modeld.runners.tinygrad_helpers import qcom_tensor_from_opencl_address
from openpilot.selfdrive.modeld.runners.ort_helpers import make_onnx_cpu_runner, ORT_TYPES_TO_NP_TYPES
import pickle
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod
from openpilot.selfdrive.modeld.models.commonmodel_pyx import DrivingModelFrame, CLMem
from openpilot.system.hardware import PC

if TICI:
  os.environ['QCOM'] = '1'

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
MODEL_PATH = Path(__file__).parent / '../models/supercombo.onnx'
MODEL_PKL_PATH = Path(__file__).parent / '../models/supercombo_tinygrad.pkl'
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'
USE_ONNX = os.getenv('USE_ONNX', PC)


class ModelRunner(ABC):
  """Abstract base class for model runners that defines the interface for running ML models."""

  def __init__(self):
    """Initialize the model runner with paths to model and metadata files."""
    self.model_paths = ({"model": MODEL_PATH, "metadata": METADATA_PATH} if USE_ONNX else
                        get_custom_model_paths() or {"model": MODEL_PKL_PATH, "metadata": METADATA_PATH})

    with open(self.model_paths["metadata"], 'rb') as f:
      self.model_metadata = pickle.load(f)

    self.input_shapes = self.model_metadata['input_shapes']
    self.output_slices = self.model_metadata['output_slices']
    self.inputs: dict = {}

  @abstractmethod
  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray]) -> dict:
    """Prepare inputs for model inference."""

  @abstractmethod
  def run_model(self):
    """Run model inference with prepared inputs."""

  def slice_outputs(self, model_outputs: np.ndarray) -> dict:
    """Slice model outputs according to metadata configuration."""
    parsed_outputs = {k: model_outputs[np.newaxis, v] for k, v in self.output_slices.items()}
    if SEND_RAW_PRED:
      parsed_outputs['raw_pred'] = model_outputs.copy()
    return parsed_outputs


class TinygradRunner(ModelRunner):
  """Tinygrad implementation of model runner for TICI hardware."""

  def __init__(self, frames: dict[str, DrivingModelFrame] | None = None):
    super().__init__()
    if not str(self.model_paths["model"]).endswith("_tinygrad.pkl"):
      raise ValueError(f"Tinygrad model must be a _tinygrad.pkl file, we got {self.model_paths['model']}")

    # Load Tinygrad model
    with open(self.model_paths["model"], "rb") as f:
      self.model_run = pickle.load(f)

    self.input_to_dtype = {}
    self.input_to_device = {}

    for idx, name in enumerate(self.model_run.captured.expected_names):
      self.input_to_dtype[name] = self.model_run.captured.expected_st_vars_dtype_device[idx][2]  # 2 is the dtype
      self.input_to_device[name] = self.model_run.captured.expected_st_vars_dtype_device[idx][3]  # 3 is the device

    assert TICI or frames is not None, "TinygradRunner requires frames for non-TICI hardware"
    self.frames = frames
    self.is_memory_model = None  # Use None to indicate that it hasn't been determined yet

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray]) -> dict:
    # Initialize image tensors if not already done
    for key in imgs_cl:
      if TICI and key not in self.inputs:
        self.inputs[key] = qcom_tensor_from_opencl_address(imgs_cl[key].mem_address, self.input_shapes[key], dtype=dtypes.uint8)
      elif not TICI:
        shape = self.frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key])
        self.inputs[key] = Tensor(shape, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

    # Update numpy inputs
    for key, value in numpy_inputs.items():
      if key not in imgs_cl:
        self.inputs[key] = Tensor(value, device=self.input_to_device[key], dtype=self.input_to_dtype[key]).realize()

    return self.inputs

  def run_model(self):
    return self.model_run(**self.inputs).numpy().flatten()


class ONNXRunner(ModelRunner):
  """ONNX implementation of model runner for non-TICI hardware."""

  def __init__(self, frames: dict[str, DrivingModelFrame]):
    super().__init__()
    self.runner = make_onnx_cpu_runner(self.model_paths["model"])
    self.frames = frames

    self.input_to_nptype = {
      model_input.name: ORT_TYPES_TO_NP_TYPES[model_input.type]
      for model_input in self.runner.get_inputs()
    }

  def prepare_inputs(self, imgs_cl: dict[str, CLMem], numpy_inputs: dict[str, np.ndarray]) -> dict:
    self.inputs = numpy_inputs.copy()
    for key in imgs_cl:
      self.inputs[key] = self.frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key]).astype(dtype=np.float32)
    return self.inputs

  def run_model(self):
    return self.runner.run(None, self.inputs)[0].flatten()
