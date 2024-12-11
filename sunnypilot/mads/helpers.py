"""
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
"""

from panda import Panda, ALTERNATIVE_EXPERIENCE

from openpilot.common.params import Params

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

      if CP.carName == "hyundai":
        if (CP.sunnypilotFlags & HyundaiFlagsSP.HAS_LFA_BUTTON) or (CP.flags & HyundaiFlags.CANFD):
          CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ALWAYS_ALLOW_MADS_BUTTON

  def set_car_specific_params(self, CP):
    if CP.carName == "hyundai":
      # TODO-SP: This should be separated from MADS module for future implementations
      hyundai_cruise_main_toggleable = self.read_param("HyundaiLongitudinalMainCruiseToggleable")
      if hyundai_cruise_main_toggleable:
        CP.sunnypilotFlags |= HyundaiFlagsSP.LONGITUDINAL_MAIN_CRUISE_TOGGLEABLE.value
        CP.safetyConfigs[-1].safetyParam |= Panda.FLAG_HYUNDAI_LONG_MAIN_CRUISE_TOGGLEABLE
