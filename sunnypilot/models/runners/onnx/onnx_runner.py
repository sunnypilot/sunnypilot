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

from sunnypilot.modeld_v2.model_runner import VisionTinygrad
from sunnypilot.models.runners.modular_runner import ModularRunner
from sunnypilot.models.runners.split_runner import PolicyTinygrad
from sunnypilot.models.runners.supercombo_runner import SupercomboTinygrad
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
