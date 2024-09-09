from openpilot.common.conversions import Conversions as CV

FCA_V_CRUISE_MIN = {
  True: 30,
  False: int(20 * CV.MPH_TO_KPH),
}
HONDA_V_CRUISE_MIN = {
  True: 40,
  False: int(25 * CV.MPH_TO_KPH),
}
MAZDA_V_CRUISE_MIN = {
  True: 30,
  False: int(20 * CV.MPH_TO_KPH),
}
VOLKSWAGEN_V_CRUISE_MIN = {
  True: 30,
  False: int(20 * CV.MPH_TO_KPH),
}


class MinimumSetPoint:
  def __init__(self, CP):
    self.CP = CP

    self.set_point: float = 0
    self.is_metric_prev: bool | None = None

  def get_set_point(self, is_metric: bool) -> float:
    if is_metric != self.is_metric_prev:
      if self.CP.carName == "honda":
        self.set_point = HONDA_V_CRUISE_MIN[is_metric]
      elif self.CP.carName == "chrysler":
        self.set_point = FCA_V_CRUISE_MIN[is_metric]
      elif self.CP.carName == "mazda":
        self.set_point = MAZDA_V_CRUISE_MIN[is_metric]
      elif self.CP.carName == "volkswagen":
        self.set_point = VOLKSWAGEN_V_CRUISE_MIN[is_metric]
    self.is_metric_prev = is_metric

    return self.set_point
