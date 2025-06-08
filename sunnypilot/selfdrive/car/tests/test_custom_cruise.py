import pytest
import itertools

from openpilot.selfdrive.car.cruise import VCruiseHelper, IMPERIAL_INCREMENT
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
    self.v_cruise_helper.custom_acc_enabled = False
    self.v_cruise_helper.short_increment = 1
    self.v_cruise_helper.long_increment = 5
    for _ in range(2):
      self.v_cruise_helper.update_v_cruise(car.CarState(cruiseState={"available": False}), enabled=False, is_metric=False)

  def enable(self, v_ego, experimental_mode, dynamic_experimental_control):
    # Simulates user pressing set with a current speed
    self.v_cruise_helper.initialize_v_cruise(car.CarState(vEgo=v_ego), experimental_mode, dynamic_experimental_control)

  @pytest.mark.parametrize(
    ("custom_acc_enabled", "long_press", "acc_inc", "metric", "init_norm"),
    itertools.product([True, False], [True, False], [1, 4, 10, 99], [False, True], [40, 35, 50])
  )
  def test_acc_changes(self, custom_acc_enabled, long_press, acc_inc, metric, init_norm):

    self.params.put_bool("CustomAccIncrementsEnabled", custom_acc_enabled)
    self.params.put("CustomAccShortPressIncrement", str(acc_inc))
    self.params.put("CustomAccLongPressIncrement", str(acc_inc))
    self.params.put_bool("IsMetric", metric)
    self.v_cruise_helper.read_custom_set_speed_params()

    base = init_norm if metric else init_norm * IMPERIAL_INCREMENT
    self.enable(base * CV.KPH_TO_MS, False, False)

    if long_press:
      long_inc = acc_inc if custom_acc_enabled and 1 <= acc_inc <= 10 else 10 if metric else 5

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

        if long_inc in [5, 10]:
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
    else:
      short_inc = acc_inc if custom_acc_enabled and 1 <= acc_inc <= 10 else 1

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

        if short_inc in [5, 10]:
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
