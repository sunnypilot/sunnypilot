import os

from cereal import custom
from openpilot.common.params import Params

from openpilot.sunnypilot.modeld.model_capabilities import ModelCapabilities

SIMULATION = "SIMULATION" in os.environ

ModelGeneration = custom.ModelGeneration


class CustomModelMetadata:
  def __init__(self, params=None, init_only=False):
    if not init_only:
      raise RuntimeError("cannot be used in a loop, this should only be used on init")

    self.params: Params = params
    self.generation = self.read_model_generation_param()
    self.capabilities = self.get_model_capabilities()
    self.valid = self.params.get_bool("CustomDrivingModel") and not SIMULATION and \
                 self.capabilities != ModelCapabilities.Default

  def read_model_generation_param(self):
    try:
      return int(self.params.get("DrivingModelGeneration"))
    except (ValueError, TypeError):
      return ModelGeneration.default

  def get_model_generation(self):
    return self.generation

  def get_model_capabilities(self):
    capabilities = {
      ModelGeneration.eight: ModelCapabilities.MLSIM,
      ModelGeneration.five: ModelCapabilities.DesiredCurvatureV2,
      ModelGeneration.four: ModelCapabilities.DesiredCurvatureV2,
      ModelGeneration.three: ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.NoO,
      ModelGeneration.two: ModelCapabilities.DesiredCurvatureV1 | ModelCapabilities.NoO,
      ModelGeneration.one: ModelCapabilities.LateralPlannerSolution | ModelCapabilities.NoO,
      ModelGeneration.default: ModelCapabilities.Default,
    }

    # Default model is meant to represent the capabilities of the prebuilt model
    return capabilities.get(self.generation, ModelCapabilities.Default)
