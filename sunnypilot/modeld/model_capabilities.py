from enum import IntFlag


class ModelCapabilities(IntFlag):
  """Model capabilities for different generations of models."""

  Default = 1
  """Default, used for the prebuilt model."""

  NavigateOnOpenpilot = 2
  """Navigation on openpilot, used for models support navigation."""

  LateralPlannerSolution = 2 ** 2
  """LateralPlannerSolution, used for models that support the lateral planner solution."""

  DesiredCurvatureV1 = 2 ** 3
  """
  DesiredCurvatureV1, used for models that support the desired curvature.
  In this version, 'prev_desired_curvs' is used as the input for the 'desired_curvature' output.
  """

  DesiredCurvatureV2 = 2 ** 4
  """
  DesiredCurvatureV2, used for models that support the desired curvature.
  In V2, 'prev_desired_curv' (no plural) is used as the input for the same 'desired_curvature' output.
  """

  MLSIM = 2 ** 5
  """MLSIM, used for models that support the MLSIM trained models."""

  Meta_V1 = 2 ** 6
  """Meta_V1, used for models that require the older meta cosntants."""

  SIM_POSE = 2 ** 7
  """SIM_POSE, used for models that support the SIM_POSE input."""
