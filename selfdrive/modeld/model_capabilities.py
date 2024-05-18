from enum import IntEnum, auto


class ModelCapabilities(IntEnum):
  Default = auto()
  NoO = auto()
  LateralPlannerSolution = auto()
  DesiredCurvature = auto()

  @staticmethod
  def get_by_gen(gen):
    if gen == 1:
      return ModelCapabilities.Default | ModelCapabilities.LateralPlannerSolution | ModelCapabilities.NoO
    elif gen in (2, 3):
      return ModelCapabilities.Default | ModelCapabilities.DesiredCurvature | ModelCapabilities.NoO
    elif gen == 4:
      return ModelCapabilities.Default | ModelCapabilities.DesiredCurvature
    else:
      return ModelCapabilities.Default
