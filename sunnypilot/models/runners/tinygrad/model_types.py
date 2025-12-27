import os
from abc import ABC

import numpy as np
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser as CombinedParser
from openpilot.sunnypilot.modeld_v2.parse_model_outputs_split import Parser as SplitParser
from openpilot.sunnypilot.models.runners.constants import ModelType, NumpyDict
from openpilot.sunnypilot.models.runners.model_runner import ModularRunner
from openpilot.system.hardware.hw import Paths


SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
CUSTOM_MODEL_PATH = Paths.model_root()


class PolicyTinygrad(ModularRunner, ABC):
  """
  A TinygradRunner specialized for policy-only models.

  Uses a SplitParser to handle outputs specific to the policy part of a split model setup.
  """
  def __init__(self):
    self._policy_parser = SplitParser()
    self.parser_method_dict[ModelType.policy] = self._parse_policy_outputs

  def _parse_policy_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses policy model outputs using SplitParser."""
    result: NumpyDict = self._policy_parser.parse_policy_outputs(self._slice_outputs(model_outputs))
    return result

class VisionTinygrad(ModularRunner, ABC):
  """
  A TinygradRunner specialized for vision-only models.

  Uses a SplitParser to handle outputs specific to the vision part of a split model setup.
  """
  def __init__(self):
    self._vision_parser = SplitParser()
    self.parser_method_dict[ModelType.vision] = self._parse_vision_outputs

  def _parse_vision_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses vision model outputs using SplitParser."""
    result: NumpyDict = self._vision_parser.parse_vision_outputs(self._slice_outputs(model_outputs))
    return result

class SupercomboTinygrad(ModularRunner, ABC):
  """
  A TinygradRunner specialized for vision-only models.

  Uses a SplitParser to handle outputs specific to the vision part of a split model setup.
  """
  def __init__(self):
    self._supercombo_parser = CombinedParser()
    self.parser_method_dict[ModelType.supercombo] = self._parse_supercombo_outputs

  def _parse_supercombo_outputs(self, model_outputs: np.ndarray) -> NumpyDict:
    """Parses vision model outputs using SplitParser."""
    result: NumpyDict = self._supercombo_parser.parse_outputs(self._slice_outputs(model_outputs))
    return result
