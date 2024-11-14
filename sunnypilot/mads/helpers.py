from panda import ALTERNATIVE_EXPERIENCE

from openpilot.common.params import Params


class MadsParams:
  @staticmethod
  def init_params(params):
    if params is None:
      return Params()
    return params

  def read_enabled_param(self, params=None):
    params = self.init_params(params)
    return params.get_bool("Mads")

  def read_main_enabled_param(self, params=None):
    params = self.init_params(params)
    return params.get_bool("MadsCruiseMain")

  def read_disengage_lateral_on_brake_param(self, params=None):
    params = self.init_params(params)
    return params.get_bool("MadsDisengageLateralOnBrake")

  def read_unified_engagement_mode_param(self, params=None):
    params = self.init_params(params)
    return params.get_bool("MadsUnifiedEngagementMode")

  def set_alternative_experience(self, CP, params):
    enabled = self.read_enabled_param(params)
    disengage_lateral_on_brake = self.read_disengage_lateral_on_brake_param(params)

    if enabled:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS

      if not disengage_lateral_on_brake:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.DISABLE_DISENGAGE_LATERAL_ON_BRAKE
