from openpilot.common.conversions import Conversions as CV


def get_set_point(is_metric: bool) -> float:
  return 30 if is_metric else int(20 * CV.MPH_TO_KPH)
