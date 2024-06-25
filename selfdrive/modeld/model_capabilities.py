from enum import IntFlag, auto


class ModelCapabilities(IntFlag):
  """Model capabilities for different generations of models."""

  Default = auto()
  """Default capability, used for the prebuilt model."""

  NoO = auto()
  """Navigation on Openpilot capability, used for models support navigation."""

  LateralPlannerSolution = auto()
  """LateralPlannerSolution capability, used for models that support the lateral planner solution."""

  DesiredCurvatureV1 = auto()
  """
  DesiredCurvatureV1 capability: This capability is used for models that support the desired curvature.
  In this version, 'prev_desired_curvs' is used as the input for the 'desired_curvature' output.
  """

  DesiredCurvatureV2 = auto()
  """
  DesiredCurvatureV2 capability: This capability is used for models that support the desired curvature.
  In V2, 'prev_desired_curv' (no plural) is used as the input for the same 'desired_curvature' output.
  """

  @staticmethod
  def get_by_gen(gen):
    """Returns the model capabilities for a given generation."""
    if gen == 1:
      return ModelCapabilities.Default | ModelCapabilities.LateralPlannerSolution | ModelCapabilities.NoO
    elif gen == 2:
      return ModelCapabilities.Default | ModelCapabilities.DesiredCurvatureV1 | ModelCapabilities.NoO
    elif gen == 3:
      return ModelCapabilities.Default | ModelCapabilities.DesiredCurvatureV2 | ModelCapabilities.NoO
    elif gen == 4:
      return ModelCapabilities.Default | ModelCapabilities.DesiredCurvatureV2
    else:
      # Default model is meant to represent the capabilities of the prebuilt model.
      return ModelCapabilities.Default
