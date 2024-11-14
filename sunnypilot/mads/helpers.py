from panda import ALTERNATIVE_EXPERIENCE

from openpilot.common.params import Params


class MadsParams:
  @staticmethod
  def read_param(key: str, params=None):
    if params is None:
      params = Params()

    return params.get_bool(key)

  def set_alternative_experience(self, CP, params):
    enabled = self.read_param("Mads", params)
    disengage_lateral_on_brake = self.read_param("MadsDisengageLateralOnBrake", params)

    if enabled:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS

      if not disengage_lateral_on_brake:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.DISABLE_DISENGAGE_LATERAL_ON_BRAKE
