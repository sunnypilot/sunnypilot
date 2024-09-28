from enum import IntFlag
import os, sys

from cereal import custom
from openpilot.common.params import Params

SIMULATION = "SIMULATION" in os.environ

ModelGeneration = custom.ModelGeneration


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

  PlanTemporalPose = 2 ** 5

  ModelOutputSlicesV1 = 2 ** 6


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
    return int(self.params.get('DrivingModelGeneration') or ModelGeneration.default)

  def get_model_capabilities(self) -> ModelCapabilities:
    """Returns the model capabilities for a given generation."""
    if self.generation == ModelGeneration.seven:
      return ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.PlanTemporalPose | \
             ModelCapabilities.ModelOutputSlicesV1
    elif self.generation == ModelGeneration.six:
      return ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.PlanTemporalPose
    elif self.generation == ModelGeneration.five:
      return ModelCapabilities.DesiredCurvatureV2
    elif self.generation == ModelGeneration.four:
      return ModelCapabilities.DesiredCurvatureV2
    elif self.generation == ModelGeneration.three:
      return ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.NoO
    elif self.generation == ModelGeneration.two:
      return ModelCapabilities.DesiredCurvatureV1 | ModelCapabilities.NoO
    elif self.generation == ModelGeneration.one:
      return ModelCapabilities.LateralPlannerSolution | ModelCapabilities.NoO
    else:
      # Default model is meant to represent the capabilities of the prebuilt model
      return ModelCapabilities.Default

  def custom_meta(self):
    if self.capabilities & ModelCapabilities.ModelOutputSlicesV1:
      class Meta:
        ENGAGED = slice(0, 1)
        # next 2, 4, 6, 8, 10 seconds
        GAS_DISENGAGE = slice(1, 41, 8)
        BRAKE_DISENGAGE = slice(2, 41, 8)
        STEER_OVERRIDE = slice(3, 41, 8)
        HARD_BRAKE_3 = slice(4, 41, 8)
        HARD_BRAKE_4 = slice(5, 41, 8)
        HARD_BRAKE_5 = slice(6, 41, 8)
        GAS_PRESS = slice(7, 41, 8)
        BRAKE_PRESS = slice(8, 41, 8)
        # next 0, 2, 4, 6, 8, 10 seconds
        LEFT_BLINKER = slice(41, 53, 2)
        RIGHT_BLINKER = slice(42, 53, 2)

      sys.modules['constants'].Meta = Meta
