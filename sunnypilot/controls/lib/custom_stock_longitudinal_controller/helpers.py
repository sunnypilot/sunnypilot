from openpilot.common.conversions import Conversions as CV


def get_set_point(is_metric: bool) -> float:
  return 30 if is_metric else int(20 * CV.MPH_TO_KPH)


def speed_hysteresis(speed: float, speed_steady: float, hyst: float) -> float:
  if speed > speed_steady + hyst:
    speed_steady = speed - hyst
  elif speed < speed_steady - hyst:
    speed_steady = speed + hyst
  return speed_steady
