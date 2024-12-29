import os
from openpilot.system.hardware import TICI

#
if TICI:
  from tinygrad.tensor import Tensor
  from tinygrad.dtype import dtypes
  from openpilot.selfdrive.modeld.runners.tinygrad_helpers import qcom_tensor_from_opencl_address

  os.environ['QCOM'] = '1'
else:
  from openpilot.selfdrive.modeld.runners.ort_helpers import make_onnx_cpu_runner
import pickle
import numpy as np
from pathlib import Path
from abc import ABC, abstractmethod
from openpilot.selfdrive.modeld.models.commonmodel_pyx import DrivingModelFrame, CLContext

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')


class ModelRunner(ABC):
  """Abstract base class for model runners that defines the interface for running ML models."""

  def __init__(self, model_path: Path, metadata_path: Path, frames: dict[str, DrivingModelFrame]):
    """Initialize the model runner with paths to model and metadata files."""
    self.model_path = model_path
    self.frames = frames
    with open(metadata_path, 'rb') as f:
      self.model_metadata = pickle.load(f)
    self.input_shapes = self.model_metadata['input_shapes']
    self.output_slices = self.model_metadata['output_slices']

  @abstractmethod
  def prepare_inputs(self, imgs_cl: dict[str, any], numpy_inputs: dict[str, np.ndarray]) -> dict[str, any]:
    """Prepare inputs for model inference."""
    pass

  @abstractmethod
  def run_model(self, inputs: dict[str, any]) -> np.ndarray:
    """Run model inference with prepared inputs."""
    pass

  def slice_outputs(self, model_outputs: np.ndarray) -> dict[str, np.ndarray]:
    """Slice model outputs according to metadata configuration."""
    parsed_outputs = {k: model_outputs[np.newaxis, v] for k, v in self.output_slices.items()}
    if SEND_RAW_PRED:
      parsed_outputs['raw_pred'] = model_outputs.copy()
    return parsed_outputs


class TinyGradRunner(ModelRunner):
  """TinyGrad implementation of model runner for TICI hardware."""

  def __init__(self, model_path: Path, metadata_path: Path, frames: dict[str, DrivingModelFrame]):
    super().__init__(model_path, metadata_path, frames)
    # Load TinyGrad model
    with open(model_path, "rb") as f:
      self.model_run = pickle.load(f)
    self.tensor_inputs = {}

  def prepare_inputs(self, imgs_cl: dict[str, any], numpy_inputs: dict[str, np.ndarray]) -> dict[str, any]:
    # Initialize image tensors if not already done
    for key in imgs_cl:
      if key not in self.tensor_inputs:
        self.tensor_inputs[key] = qcom_tensor_from_opencl_address(imgs_cl[key].mem_address, self.input_shapes[key], dtype=dtypes.uint8)

    # Update numpy inputs
    for k, v in numpy_inputs.items():
      if k not in self.tensor_inputs:
        self.tensor_inputs[k] = Tensor(v, device='NPY').realize()
      else:
        self.tensor_inputs[k].assign(v)

    return self.tensor_inputs

  def run_model(self, inputs: dict[str, any]) -> np.ndarray:
    return self.model_run(**inputs).flatten()


class ONNXRunner(ModelRunner):
  """ONNX implementation of model runner for non-TICI hardware."""

  def __init__(self, model_path: Path, metadata_path: Path, frames: dict[str, DrivingModelFrame]):
    super().__init__(model_path, metadata_path, frames)
    self.runner = make_onnx_cpu_runner(model_path)

  def prepare_inputs(self, imgs_cl: dict[str, any], numpy_inputs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    for key in imgs_cl:
      numpy_inputs[key] = self.frames[key].buffer_from_cl(imgs_cl[key]).reshape(self.input_shapes[key])
    return numpy_inputs

  def run_model(self, inputs: dict[str, any]) -> np.ndarray:
    return self.runner.run(None, inputs)[0].flatten()


def create_model_runner(model_path: Path, metadata_path: Path, frames: dict[str, DrivingModelFrame], tinygrad_path: Path | None = None,
                        is_tici: bool = False) -> ModelRunner:
  """Factory function to create appropriate model runner based on hardware."""
  if is_tici:
    return TinyGradRunner(tinygrad_path or model_path, metadata_path, frames)
  return ONNXRunner(model_path, metadata_path, frames)
