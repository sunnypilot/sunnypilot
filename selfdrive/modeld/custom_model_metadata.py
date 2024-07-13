from enum import IntFlag, IntEnum
import os

from openpilot.common.params import Params

SIMULATION = "SIMULATION" in os.environ


class ModelGeneration(IntEnum):
  DEFAULT = 0
  ONE = 1
  TWO = 2
  THREE = 3
  FOUR = 4
  FIVE = 5


class ModelCapabilities(IntFlag):
  """Model capabilities for different generations of models."""

  Default = 1
  """Default capability, used for the prebuilt model."""

  NoO = 2
  """Navigation on Openpilot capability, used for models support navigation."""

  LateralPlannerSolution = 2 ** 2
  """LateralPlannerSolution capability, used for models that support the lateral planner solution."""

  DesiredCurvatureV1 = 2 ** 3
  """
  DesiredCurvatureV1 capability: This capability is used for models that support the desired curvature.
  In this version, 'prev_desired_curvs' is used as the input for the 'desired_curvature' output.
  """

  DesiredCurvatureV2 = 2 ** 4
  """
  DesiredCurvatureV2 capability: This capability is used for models that support the desired curvature.
  In V2, 'prev_desired_curv' (no plural) is used as the input for the same 'desired_curvature' output.
  """


class CustomModelMetadata:
  def __init__(self, params=None, init_only=False) -> None:
    # TODO: Handle this with cereal
    if not init_only:
      raise RuntimeError("cannot be used in a loop, this should only be used on init")

    self.params: Params = params
    self.generation: ModelGeneration = self.read_model_generation_param()
    self.capabilities: ModelCapabilities = self.get_model_capabilities()
    self.valid: bool = self.params.get_bool("CustomDrivingModel") and not SIMULATION and \
                       self.capabilities != ModelCapabilities.Default

  def read_model_generation_param(self) -> ModelGeneration:
    return ModelGeneration(int(self.params.get("DrivingModelGeneration", encoding='utf8')) or ModelGeneration.DEFAULT)

  def get_model_capabilities(self) -> ModelCapabilities:
    """Returns the model capabilities for a given generation."""
    if self.generation == ModelGeneration.FIVE:
      return ModelCapabilities.DesiredCurvatureV2
    elif self.generation == ModelGeneration.FOUR:
      return ModelCapabilities.DesiredCurvatureV2
    elif self.generation == ModelGeneration.THREE:
      return ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.NoO
    elif self.generation == ModelGeneration.TWO:
      return ModelCapabilities.DesiredCurvatureV1 | ModelCapabilities.NoO
    elif self.generation == ModelGeneration.ONE:
      return ModelCapabilities.LateralPlannerSolution | ModelCapabilities.NoO
    else:
      # Default model is meant to represent the capabilities of the prebuilt model
      return ModelCapabilities.Default
