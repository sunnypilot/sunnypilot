import pytest
import itertools

from sunnypilot.selfdrive.car.vcruise_helper import VCruiseHelperSP as VCruiseHelper, IMPERIAL_INCREMENT
from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type

class TestAdjustCustomAccIncrements:
  def setup_method(self):
    self.CP = car.CarParams()
    self.params = Params()
    self.v_cruise_helper = VCruiseHelper(self.CP)
    self.reset_cruise_speed_state()

  def reset_cruise_speed_state(self):
    # Two resets previous cruise speed
    for _ in range(2):
      self.v_cruise_helper.update_v_cruise(car.CarState(cruiseState={"available": False}), enabled=False, is_metric=False)

  def enable(self, v_ego, experimental_mode, dynamic_experimental_control):
    # Simulates user pressing set with a current speed
    self.v_cruise_helper.initialize_v_cruise(car.CarState(vEgo=v_ego), experimental_mode, dynamic_experimental_control)

  @pytest.mark.parametrize(
    ("custom_acc_enabled", "short_inc", "metric", "init_norm"),
    itertools.product([True, False], [-1, 1, 4, 7, 5, 10, 99], [False, True], [40, 35, 50, 25])
  )
  def test_short_press_only(self, custom_acc_enabled, short_inc, metric, init_norm):
    """
    Single (short) press:
      – uses `short_inc` if custom enabled
      – otherwise defaults to 1
    """
    base = init_norm if metric else init_norm * IMPERIAL_INCREMENT
    self.enable(base * CV.KPH_TO_MS, False, False)

    self.params.put_bool("CustomAccIncrementsEnabled", custom_acc_enabled)
    self.params.put("CustomAccShortPressIncrement", str(short_inc))
    self.params.put("CustomAccLongPressIncrement", "10" if metric else "5")
    self.params.put_bool("IsMetric", metric)

    short_inc = short_inc if custom_acc_enabled and 1 <= short_inc <= 10 else 1

    for btn in (ButtonType.accelCruise, ButtonType.decelCruise):
      CS = car.CarState(cruiseState={"available": True})
      prev = self.v_cruise_helper.v_cruise_kph if metric else round(self.v_cruise_helper.v_cruise_kph / IMPERIAL_INCREMENT)

      # simulate short-press
      CS.buttonEvents = [ButtonEvent(type=btn, pressed=True)]
      self.v_cruise_helper.update_v_cruise(CS, True, metric)
      CS.buttonEvents = [ButtonEvent(type=btn, pressed=False)]
      self.v_cruise_helper.update_v_cruise(CS, True, metric)

      curr = self.v_cruise_helper.v_cruise_kph if metric else round(self.v_cruise_helper.v_cruise_kph / IMPERIAL_INCREMENT)
      diff = curr - prev

      if (short_inc in [5,10]):
        remainder = prev % short_inc
        exp = (short_inc - remainder) if btn == ButtonType.accelCruise else -remainder
        if remainder == 0:
          exp = short_inc if btn == ButtonType.accelCruise else -short_inc
      else:
        exp = short_inc if custom_acc_enabled else 1
        if btn == ButtonType.decelCruise:
          exp *= -1

      assert diff == exp, (
              f"SHORT press – {'metric' if metric else 'imperial'} {'decel' if btn == ButtonType.decelCruise else 'accel'}: " +
              f"expected {exp}, got {diff}"
      )

  @pytest.mark.parametrize(
    ("custom_acc_enabled", "long_inc", "metric", "init_norm"),
    itertools.product([True, False], [-1, 1, 4, 7, 5, 10, 99], [False, True], [40, 35, 50, 25])
  )
  def test_long_press_only(self, custom_acc_enabled, long_inc, metric, init_norm):
    """
    True "long press" (holding):
      – uses `long_inc` if custom enabled
      – otherwise defaults to 10 (metric) or 5 (imperial)
    """
    base = init_norm if metric else init_norm * IMPERIAL_INCREMENT
    self.enable(base * CV.KPH_TO_MS, False, False)

    self.params.put_bool("CustomAccIncrementsEnabled", custom_acc_enabled)
    self.params.put("CustomAccShortPressIncrement", "1")
    self.params.put("CustomAccLongPressIncrement", str(long_inc))
    self.params.put_bool("IsMetric", metric)

    long_inc = long_inc if custom_acc_enabled and 1 <= long_inc <= 10 else 10 if metric else 5

    for btn in (ButtonType.accelCruise, ButtonType.decelCruise):
      CS = car.CarState(cruiseState={"available": True})
      prev = self.v_cruise_helper.v_cruise_kph if metric else round(self.v_cruise_helper.v_cruise_kph / IMPERIAL_INCREMENT)

      for i in range(51):
        CS.buttonEvents = [ButtonEvent(type=btn, pressed=True)] if i == 0 else []
        self.v_cruise_helper.update_v_cruise(CS, True, metric)

      CS.buttonEvents = [ButtonEvent(type=btn, pressed=False)]
      self.v_cruise_helper.update_v_cruise(CS, True, metric)

      curr = self.v_cruise_helper.v_cruise_kph if metric else round(self.v_cruise_helper.v_cruise_kph / IMPERIAL_INCREMENT)
      diff = curr - prev

      if (long_inc in [5, 10]):
        remainder = prev % long_inc
        exp = (long_inc - remainder) if btn == ButtonType.accelCruise else -remainder
        if remainder == 0:
          exp = long_inc if btn == ButtonType.accelCruise else -long_inc
      else:
        exp = long_inc if custom_acc_enabled else 10 if metric else 5
        if btn == ButtonType.decelCruise:
          exp *= -1

      assert diff == exp, (
              f"LONG press – {'metric' if metric else 'imperial'} {'decel' if btn == ButtonType.decelCruise else 'accel'}: " +
              f"expected {exp}, got {diff} (prev: {prev}, curr: {curr})"
      )
