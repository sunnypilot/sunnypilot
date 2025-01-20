import pickle
from abc import abstractmethod, ABC

import numpy as np


class ModelSmartInput(ABC):
  def __init__(self, METADATA_PATH):
    self.using_smart_input = True
    self.desire_reshape_dims = None
    self.output = None
    self.full_features_20Hz_idxs = None
    self._output_slices = None
    self._input_shapes = None
    self._numpy_inputs = {}

    if self.using_smart_input:
      self.initialize_smart_input(METADATA_PATH)

  def initialize_smart_input(self, METADATA_PATH):
    with open(METADATA_PATH, 'rb') as f:
      model_metadata = pickle.load(f)

    self._input_shapes = model_metadata['input_shapes']
    self._output_slices = model_metadata['output_slices']

    for key, shape in self.input_shapes.items():
      if key not in ['input_imgs', 'big_input_imgs']:  # Managed by opencl
        self._numpy_inputs[key] = np.zeros(shape, dtype=np.float32)

    net_output_size = model_metadata['output_shapes']['outputs'][1]
    self.output = np.zeros(net_output_size, dtype=np.float32)

    num_elements = self.numpy_inputs['features_buffer'].shape[1]
    step_size = int(-100 / num_elements)
    self.full_features_20Hz_idxs = np.arange(step_size, step_size * (num_elements + 1), step_size)[::-1]
    self.desire_reshape_dims = (self.numpy_inputs['desire'].shape[0], self.numpy_inputs['desire'].shape[1], -1, self.numpy_inputs['desire'].shape[2])

  def process_outputs_smart(self, outputs):
    if "desired_curvature" in outputs:
      input_name_prev = None

      if "prev_desired_curvs" in self.numpy_inputs.keys():
        input_name_prev = 'prev_desired_curvs'
      elif "prev_desired_curv" in self.numpy_inputs.keys():
        input_name_prev = 'prev_desired_curv'

      if input_name_prev is not None:
        length = outputs['desired_curvature'][0].size
        self.numpy_inputs[input_name_prev][0, :-length, 0] = self.numpy_inputs[input_name_prev][0, length:, 0]
        self.numpy_inputs[input_name_prev][0, -length:, 0] = outputs['desired_curvature'][0]

  @property
  def input_shapes(self):
    return self._input_shapes

  @input_shapes.setter
  def input_shapes(self, value):
    if not self._input_shapes:
      self._input_shapes = value
    print("Waring: ignoring input_shapes setter because ModelSmartInput is in use.")

  @property
  def output_slices(self):
    return self._output_slices

  @output_slices.setter
  def output_slices(self, value):
    if not self._output_slices:
      self._output_slices = value
    print("Waring: ignoring output_slices setter because ModelSmartInput is in use.")

  @property
  @abstractmethod
  def frames(self):
    raise NotImplementedError

  @property
  def numpy_inputs(self):
    return self._numpy_inputs

  @numpy_inputs.setter
  def numpy_inputs(self, value):
    if not self._numpy_inputs:
      self._numpy_inputs = value
    print("Waring: ignoring numpy_inputs setter because ModelSmartInput is in use.")
