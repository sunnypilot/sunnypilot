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
