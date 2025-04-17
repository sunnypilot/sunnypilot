import pytest
import itertools
import numpy as np
from time import sleep

from parameterized import parameterized_class
from cereal import log
from openpilot.selfdrive.car.cruise import VCruiseHelper, V_CRUISE_MIN, V_CRUISE_MAX, V_CRUISE_INITIAL, IMPERIAL_INCREMENT
from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver
from openpilot.common.params import Params

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type


def run_cruise_simulation(cruise, e2e, personality, t_end=20.):
  man = Maneuver(
    '',
    duration=t_end,
    initial_speed=max(cruise - 1., 0.0),
    lead_relevancy=True,
    initial_distance_lead=100,
    cruise_values=[cruise],
    prob_lead_values=[0.0],
    breakpoints=[0.],
    e2e=e2e,
    personality=personality,
  )
  valid, output = man.evaluate()
  assert valid
  return output[-1, 3]


@parameterized_class(("e2e", "personality", "speed"), itertools.product(
                      [True, False], # e2e
                      log.LongitudinalPersonality.schema.enumerants, # personality
                      [5,35])) # speed
class TestCruiseSpeed:
  def test_cruise_speed(self):
    print(f'Testing {self.speed} m/s')
    cruise_speed = float(self.speed)

    simulation_steady_state = run_cruise_simulation(cruise_speed, self.e2e, self.personality)
    assert simulation_steady_state == pytest.approx(cruise_speed, abs=.01), f'Did not reach {self.speed} m/s'


# TODO: test pcmCruise
@parameterized_class(('pcm_cruise',), [(False,)])
class TestVCruiseHelper:
  def setup_method(self):
    self.CP = car.CarParams(pcmCruise=self.pcm_cruise)
    self.v_cruise_helper = VCruiseHelper(self.CP)
    self.reset_cruise_speed_state()

  def reset_cruise_speed_state(self):
    # Two resets previous cruise speed
    for _ in range(2):
      self.v_cruise_helper.update_v_cruise(car.CarState(cruiseState={"available": False}), enabled=False, is_metric=False)

  def enable(self, v_ego, experimental_mode, dynamic_experimental_control):
    # Simulates user pressing set with a current speed
    self.v_cruise_helper.initialize_v_cruise(car.CarState(vEgo=v_ego), experimental_mode, dynamic_experimental_control)

  def test_adjust_speed(self):
    """
    Asserts speed changes on falling edges of buttons.
    """

    self.enable(V_CRUISE_INITIAL * CV.KPH_TO_MS, False, False)

    for btn in (ButtonType.accelCruise, ButtonType.decelCruise):
      for pressed in (True, False):
        CS = car.CarState(cruiseState={"available": True})
        CS.buttonEvents = [ButtonEvent(type=btn, pressed=pressed)]

        self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)
        assert pressed == (self.v_cruise_helper.v_cruise_kph == self.v_cruise_helper.v_cruise_kph_last)


  @pytest.mark.parametrize(("custom_acc_increments_enabled, short_inc, long_inc, long_press, metric, init_kph_or_mph"),
                       itertools.product([True, False], [1, 5, 10], [1, 5, 10], [False], [False, True], [40, 35, 50, 25]))
  def test_adjust_custom_acc_increments(self, custom_acc_increments_enabled, short_inc, long_inc, long_press, metric, init_kph_or_mph):
    """
    Asserts speed changes behavior with custom increments
    """
    self.enable((init_kph_or_mph if metric else init_kph_or_mph * IMPERIAL_INCREMENT) * CV.KPH_TO_MS, False, False)

    # Set custom increment parameters
    Params().put_bool("CustomAccIncrementsEnabled", custom_acc_increments_enabled)
    Params().put("CustomAccShortPressIncrement", str(short_inc))
    Params().put("CustomAccLongPressIncrement", str(long_inc))

    # Determine expected increment based on parameters
    expected_increment = long_inc if custom_acc_increments_enabled and long_press else short_inc if custom_acc_increments_enabled else 5 if long_press else 1

    for btn in (ButtonType.accelCruise, ButtonType.decelCruise):

        expected_increment *= -1 if btn==ButtonType.decelCruise else 1

        # Test button press and release cycle
        CS = car.CarState(cruiseState={"available": True})

        # Press button
        CS.buttonEvents = [ButtonEvent(type=btn, pressed=True)]
        prev_kph = self.v_cruise_helper.v_cruise_kph
        prev_mph = round(prev_kph / IMPERIAL_INCREMENT)
        prev_normalized = prev_kph if metric else prev_mph
        self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=metric)

        # TODO: Add test for long_press

        # Release button
        CS.buttonEvents = [ButtonEvent(type=btn, pressed=False)]
        self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=metric)

        # Check the difference based on reverse_acc setting
        new_kph = self.v_cruise_helper.v_cruise_kph
        new_mph = round(new_kph / IMPERIAL_INCREMENT)
        new_normalized = new_kph if metric else new_mph

        diff = new_normalized - prev_normalized

        print("Testing..\nbutton:", btn,
               "\ncustom:",custom_acc_increments_enabled,
                "\nis_metric:",metric,
                 "\nshort_inc:",short_inc, "\nlong_inc:",long_inc)
        if metric:
          print("\nprev_kph:",prev_kph, "\nnew_kph:",new_kph)
        else:
          print("\nprev_mph:", prev_mph, "\nnew_mph:", new_mph)
        print("\n--------------")

        assert diff == expected_increment, f"expected {expected_increment}, got {diff}"

  def test_rising_edge_enable(self):
    """
    Some car interfaces may enable on rising edge of a button,
    ensure we don't adjust speed if enabled changes mid-press.
    """

    # NOTE: enabled is always one frame behind the result from button press in controlsd
    for enabled, pressed in ((False, False),
                             (False, True),
                             (True, False)):
      CS = car.CarState(cruiseState={"available": True})
      CS.buttonEvents = [ButtonEvent(type=ButtonType.decelCruise, pressed=pressed)]
      self.v_cruise_helper.update_v_cruise(CS, enabled=enabled, is_metric=False)
      if pressed:
        self.enable(V_CRUISE_INITIAL * CV.KPH_TO_MS, False, False)

      # Expected diff on enabling. Speed should not change on falling edge of pressed
      assert not pressed == self.v_cruise_helper.v_cruise_kph == self.v_cruise_helper.v_cruise_kph_last

  def test_resume_in_standstill(self):
    """
    Asserts we don't increment set speed if user presses resume/accel to exit cruise standstill.
    """

    self.enable(0, False, False)

    for standstill in (True, False):
      for pressed in (True, False):
        CS = car.CarState(cruiseState={"available": True, "standstill": standstill})
        CS.buttonEvents = [ButtonEvent(type=ButtonType.accelCruise, pressed=pressed)]
        self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

        # speed should only update if not at standstill and button falling edge
        should_equal = standstill or pressed
        assert should_equal == (self.v_cruise_helper.v_cruise_kph == self.v_cruise_helper.v_cruise_kph_last)

  def test_set_gas_pressed(self):
    """
    Asserts pressing set while enabled with gas pressed sets
    the speed to the maximum of vEgo and current cruise speed.
    """

    for v_ego in np.linspace(0, 100, 101):
      self.reset_cruise_speed_state()
      self.enable(V_CRUISE_INITIAL * CV.KPH_TO_MS, False, False)

      # first decrement speed, then perform gas pressed logic
      expected_v_cruise_kph = self.v_cruise_helper.v_cruise_kph - IMPERIAL_INCREMENT
      expected_v_cruise_kph = max(expected_v_cruise_kph, v_ego * CV.MS_TO_KPH)  # clip to min of vEgo
      expected_v_cruise_kph = float(np.clip(round(expected_v_cruise_kph, 1), V_CRUISE_MIN, V_CRUISE_MAX))

      CS = car.CarState(vEgo=float(v_ego), gasPressed=True, cruiseState={"available": True})
      CS.buttonEvents = [ButtonEvent(type=ButtonType.decelCruise, pressed=False)]
      self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

      # TODO: fix skipping first run due to enabled on rising edge exception
      if v_ego == 0.0:
        continue
      assert expected_v_cruise_kph == self.v_cruise_helper.v_cruise_kph

  def test_initialize_v_cruise(self):
    """
    Asserts allowed cruise speeds on enabling with SET.
    """

    for experimental_mode in (True, False):
      for dynamic_experimental_control in (True, False):
        for v_ego in np.linspace(0, 100, 101):
          self.reset_cruise_speed_state()
          assert not self.v_cruise_helper.v_cruise_initialized

          self.enable(float(v_ego), experimental_mode, dynamic_experimental_control)
          assert V_CRUISE_INITIAL <= self.v_cruise_helper.v_cruise_kph <= V_CRUISE_MAX
          assert self.v_cruise_helper.v_cruise_initialized
