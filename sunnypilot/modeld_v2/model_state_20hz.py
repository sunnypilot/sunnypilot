from abc import abstractmethod, ABC

import numpy as np
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.modeld.models.commonmodel_pyx import DrivingModelFrame


class ModelState20Hz(ABC):
  def __init__(self, context):
    self.is_20hz = False
    self._context = context
    self.desire_20Hz = None
    self.full_features_20Hz = None
    self.frames = None
    self.prev_desire = None
    if self.is_20hz:
      self.initialize_20hz_buffers()

  def initialize_20hz_buffers(self):
    self.full_features_20Hz = np.zeros((ModelConstants.FULL_HISTORY_BUFFER_LEN, ModelConstants.FEATURE_LEN), dtype=np.float32)
    self.desire_20Hz = np.zeros((ModelConstants.FULL_HISTORY_BUFFER_LEN + 1, ModelConstants.DESIRE_LEN), dtype=np.float32)
    self.frames = {'input_imgs': DrivingModelFrame(self._context, self.buffer_length), 'big_input_imgs': DrivingModelFrame(self._context, self.buffer_length)}
    self.prev_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)

  @property
  def frames(self):
    return self._frames

  @frames.setter
  def frames(self, value):
    self._frames = value

  @property
  def prev_desire(self):
    return self._prev_desire

  @prev_desire.setter
  def prev_desire(self, value):
    self._prev_desire = value

  @property
  def buffer_length(self):
    return 5 if self.is_20hz else 2
