import os
from abc import abstractmethod, ABC

import numpy as np
from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.system.hardware import TICI
from openpilot.sunnypilot.models.runners.constants import NumpyDict, ShapeDict, CLMemDict, FrameDict, Model, SliceDict, SEND_RAW_PRED
from openpilot.system.hardware.hw import Paths
import pickle

CUSTOM_MODEL_PATH = Paths.model_root()


# Set QCOM environment variable for TICI devices, potentially enabling hardware acceleration
USBGPU = "USBGPU" in os.environ
if USBGPU:
  os.environ['AMD'] = '1'
  os.environ['AMD_IFACE'] = 'USB'
elif TICI:
  os.environ['QCOM'] = '1'
else:
  os.environ['LLVM'] = '1'
  os.environ['JIT'] = '2'  # TODO: This may cause issues


class ModelData:
  """
  Stores metadata and configuration for a specific machine learning model.

  This class loads model metadata (like input shapes and output slices)
  from a pickle file associated with a model instance.

  :param model: The machine learning model object containing metadata.
  """
  def __init__(self, model: Model):
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


class ModularRunner(ABC):
  """
  Represents a modular runner for handling and slicing model outputs.

  This abstract base class is designed to provide an interface for modular
  parsing and processing of model outputs. Classes inheriting from it must
  implement the specified abstract methods, defining how model outputs
  should be handled and stored. The primary goal is to enable structured
  parsing of outputs through a dictionary-based method mapping.

  :ivar parser_method_dict: Mapping dictionary containing parser methods
      for handling specific types of outputs.
  :type parser_method_dict: dict
  """

  @property
  @abstractmethod
  def parser_method_dict(self) -> dict:
    pass

  @parser_method_dict.setter
  @abstractmethod
  def parser_method_dict(self, value: dict) -> None:
    pass

  @abstractmethod
  def _slice_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    pass


class ModelRunner(ModularRunner):
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
    self.is_20hz_3d: bool | None = None
    self.models: dict[int, ModelData] = {}
    self._model_data: ModelData | None = None  # Active model data for current operation
    self._parser_method_dict: dict = {}
    self.inputs: dict = {}
    self._parser = None
    self._load_models()
    self._constants = None

  @property
  def constants(self):
    return self._constants

  @property
  def parser_method_dict(self) -> dict:
    """Returns the dictionary mapping model types to their respective parsing methods."""
    return self._parser_method_dict

  @parser_method_dict.setter
  def parser_method_dict(self, value: dict) -> None:
    """Sets the dictionary mapping model types to their respective parsing methods."""
    self._parser_method_dict = value

  def _load_models(self) -> None:
    """Loads the active model bundle configuration and sets up ModelData."""
    bundle = get_active_bundle()
    if not bundle:
      raise ValueError("No active model bundle found, why are we being executed?")

    self.models = {model.type.raw: ModelData(model) for model in bundle.models}
    self.is_20hz = bundle.is20hz
    self.is_20hz_3d = False

  @property
  def input_shapes(self) -> ShapeDict:
    """Returns the input shapes for the currently active model."""
    if self._model_data:
      return self._model_data.input_shapes
    raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

  @property
  def output_slices(self) -> SliceDict:
    """Returns the output slices for the currently active model."""
    if self._model_data:
      return self._model_data.output_slices
    raise ValueError("Model data is not available. Ensure the model is loaded correctly.")

  @property
  def vision_input_names(self) -> list[str]:
    """Returns the list of vision input names from the input shapes."""
    if self._model_data:
      return list(self._model_data.input_shapes.keys())
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
      sliced_outputs['raw_pred'] = model_outputs.copy()  # Optionally include the full raw output
    return sliced_outputs

  def run_model(self) -> NumpyDict:
    """
    Executes the model inference pipeline: runs the model and parses outputs.

    :return: Dictionary containing the final parsed model outputs.
    """
    return self._run_model()  # Parsing is handled within specific runner implementations
