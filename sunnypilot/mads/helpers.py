from panda import ALTERNATIVE_EXPERIENCE

from openpilot.common.params import Params


class MadsParams:
  def __init__(self):
    self.params = Params()

  def read_param(self, key: str):
    return self.params.get_bool(key)

  def set_alternative_experience(self, CP):
    enabled = self.read_param("Mads")
    disengage_lateral_on_brake = self.read_param("MadsDisengageLateralOnBrake")

    if enabled:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS

      if not disengage_lateral_on_brake:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.DISABLE_DISENGAGE_LATERAL_ON_BRAKE
