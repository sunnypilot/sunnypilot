from panda import Panda, ALTERNATIVE_EXPERIENCE

from openpilot.common.params import Params

from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP


class MadsParams:
  def __init__(self):
    self.params = Params()
    self.allow_always = False

  def read_param(self, key: str):
    return self.params.get_bool(key)

  def set_alternative_experience(self, CP):
    enabled = self.read_param("Mads")
    disengage_lateral_on_brake = self.read_param("MadsDisengageLateralOnBrake")
    main_cruise = self.read_param("MadsMainCruiseAllowed")
    unified_engagement_mode = self.read_param("MadsUnifiedEngagementMode")

    if enabled:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS

      if not disengage_lateral_on_brake:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.DISABLE_DISENGAGE_LATERAL_ON_BRAKE

      if main_cruise:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.MAIN_CRUISE_ALLOWED

      if unified_engagement_mode:
        CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.UNIFIED_ENGAGEMENT_MODE

  def set_car_specific_params(self, CP):
    if CP.carName == "hyundai":
      if (CP.sunnypilotFlags & HyundaiFlagsSP.HAS_LFA_BUTTON) or (CP.flags & HyundaiFlags.CANFD):
        self.allow_always = True
        CP.safetyConfig[-1].safetyParam |= Panda.FLAG_HYUNDAI_MADS_BUTTON_ALLOWED

      # TODO-SP: This should be separated from MADS module for future implementations
      hyundai_cruise_main_toggleable = self.read_param("HyundaiLongitudinalMainCruiseToggleable")
      if hyundai_cruise_main_toggleable:
        CP.sunnypilotFlags |= HyundaiFlagsSP.LONGITUDINAL_MAIN_CRUISE_TOGGLEABLE.value
        CP.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_LONG_MAIN_CRUISE_TOGGLEABLE
