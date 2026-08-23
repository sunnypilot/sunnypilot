from openpilot.cereal import custom
from opendbc.car.structs import car
from openpilot.common.constants import CV
from openpilot.common.parameterized import parameterized, parameterized_class
from openpilot.common.params import Params
from openpilot.selfdrive.car.cruise import V_CRUISE_INITIAL
from openpilot.selfdrive.car.tests.test_cruise_speed import TestVCruiseHelper
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode as SpeedLimitMode

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type
SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState


# TODO: test pcmCruise and pcmCruiseSpeed
@parameterized_class(('pcm_cruise', 'pcm_cruise_speed'), [(False, True)])
class TestCustomAccIncrements(TestVCruiseHelper):
  def setup_method(self):
    TestVCruiseHelper.openpilot_setup_method(self)
    self.params = Params()
    self.reset_custom_params()

  def reset_custom_params(self) -> None:
    """Reset to default custom ACC parameters"""
    self.params.put_bool("CustomAccIncrementsEnabled", False, block=True)
    self.params.put("CustomAccShortPressIncrement", 1, block=True)
    self.params.put("CustomAccLongPressIncrement", 5, block=True)
    self.v_cruise_helper.read_custom_set_speed_params()

  def press_button_short(self, button_type: car.CarState.ButtonEvent.Type) -> None:
    """Simulate a short button press (press + release)"""
    CS = car.CarState(cruiseState={"available": True})
    CS.buttonEvents = [ButtonEvent(type=button_type, pressed=True)]
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=True)

    CS.buttonEvents = [ButtonEvent(type=button_type, pressed=False)]
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=True)

  def press_button_long(self, button_type: car.CarState.ButtonEvent.Type) -> None:
    """Simulate a long button press (50+ frames)"""
    CS = car.CarState(cruiseState={"available": True})
    CS.buttonEvents = [ButtonEvent(type=button_type, pressed=True)]
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=True)

    # Hold for 50 frames to trigger long press
    CS.buttonEvents = []
    for _ in range(50):
      self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=True)

    CS.buttonEvents = [ButtonEvent(type=button_type, pressed=False)]
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=True)

  def set_custom_increments(self, enabled: bool, short_inc: int, long_inc: int) -> None:
    """Set custom ACC increment parameters"""
    self.params.put_bool("CustomAccIncrementsEnabled", enabled, block=True)
    self.params.put("CustomAccShortPressIncrement", short_inc, block=True)
    self.params.put("CustomAccLongPressIncrement", long_inc, block=True)
    self.v_cruise_helper.read_custom_set_speed_params()

  def test_default_behavior_when_disabled(self):
    """Test that default increments are used when custom ACC is disabled"""
    self.set_custom_increments(enabled=False, short_inc=5, long_inc=10)
    self.enable(V_CRUISE_INITIAL * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph

    # Short press should increment by 1 (default)
    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 1

  @parameterized.expand((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
  def test_custom_short_press_increments(self, increment):
    """Test custom short press increments (1-10)"""
    self.set_custom_increments(enabled=True, short_inc=increment, long_inc=5)
    self.enable(50 * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_short(ButtonType.accelCruise)

    if increment in (5, 10):
      # Should round to nearest increment
      expected_speed = ((initial_speed // increment) + 1) * increment
    else:
      expected_speed = initial_speed + increment

    assert self.v_cruise_helper.v_cruise_kph == expected_speed

  @parameterized.expand((1, 5, 10))
  def test_custom_long_press_increments(self, increment):
    """Test custom long press increments (1, 5, 10)"""
    self.set_custom_increments(enabled=True, short_inc=1, long_inc=increment)
    self.enable(50 * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_long(ButtonType.accelCruise)

    if increment in (5, 10):
      # Should round to nearest increment
      expected_speed = ((initial_speed // increment) + 1) * increment
    else:
      expected_speed = initial_speed + increment

    assert self.v_cruise_helper.v_cruise_kph == expected_speed

  @parameterized.expand([ButtonType.accelCruise, ButtonType.decelCruise])
  def test_accel_decel_symmetry(self, button_type):
    """Test that acceleration and deceleration work symmetrically"""
    self.set_custom_increments(enabled=True, short_inc=3, long_inc=5)
    self.enable(50 * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_short(button_type)

    expected_change = 3 if button_type == ButtonType.accelCruise else -3
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + expected_change

  def test_snap_to_slc_only_when_assist_enabled(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.warning), block=True)
    self.enable(60 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 55
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.disabled
    self.v_cruise_helper.prev_sla_state = SpeedLimitAssistState.disabled

    self.press_button_short(ButtonType.decelCruise)

    assert self.v_cruise_helper.v_cruise_kph == 50

  def test_snap_to_slc_when_inactive_after_manual_adjustment(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(40 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 52
    self.v_cruise_helper.prev_speed_limit_final_last_kph = 52
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.inactive
    self.v_cruise_helper.prev_sla_state = SpeedLimitAssistState.inactive

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 52

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 60

  def test_snap_to_slc_when_planner_state_disabled_but_assist_mode_enabled(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(40 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 30.9
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.disabled

    self.press_button_short(ButtonType.decelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 30.9

  def test_snap_to_slc_once_when_crossing_target(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(60 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 53
    self.v_cruise_helper.prev_speed_limit_final_last_kph = 53
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active
    self.v_cruise_helper.prev_sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.decelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 53

    self.press_button_short(ButtonType.decelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 50

    self.press_button_short(ButtonType.decelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 40

  def test_snap_to_slc_once_when_crossing_target_from_below(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(40 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 53
    self.v_cruise_helper.prev_speed_limit_final_last_kph = 53
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active
    self.v_cruise_helper.prev_sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 53

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 60

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 70

  def test_snap_to_slc_before_crossing_only_when_within_third_step(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(40 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 56
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 50

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 56

  def test_snap_to_slc_before_crossing_when_close_to_next_step(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(40 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 52
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == 52

  @parameterized.expand([
    (56, 40, ButtonType.accelCruise, [40, 50, 56, 60, 70]),
    (56, 70, ButtonType.decelCruise, [70, 60, 56, 50, 40]),
    (58, 40, ButtonType.accelCruise, [40, 50, 58, 70]),
    (58, 80, ButtonType.decelCruise, [80, 70, 58, 50]),
    (62, 40, ButtonType.accelCruise, [40, 50, 62, 70]),
    (62, 80, ButtonType.decelCruise, [80, 70, 62, 50]),
  ])
  def test_snap_to_slc_offset_sequences(self, slc_target, initial_speed, button_type, expected):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(initial_speed * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = slc_target
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active

    actual = [self.v_cruise_helper.v_cruise_kph]
    for _ in range(len(expected) - 1):
      self.press_button_short(button_type)
      actual.append(self.v_cruise_helper.v_cruise_kph)

    assert actual == expected

  def test_snap_to_slc_from_just_below_target(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(50 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.v_cruise_kph = 54.5
    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 55
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.accelCruise)

    assert self.v_cruise_helper.v_cruise_kph == 55

  def test_snap_to_slc_from_just_above_target(self):
    self.set_custom_increments(enabled=True, short_inc=10, long_inc=10)
    self.params.put("SpeedLimitMode", int(SpeedLimitMode.assist), block=True)
    self.enable(60 * CV.KPH_TO_MS, False, False)

    self.v_cruise_helper.v_cruise_kph = 53.5
    self.v_cruise_helper.has_speed_limit = True
    self.v_cruise_helper.speed_limit_final_last_kph = 53
    self.v_cruise_helper.sla_state = SpeedLimitAssistState.active

    self.press_button_short(ButtonType.decelCruise)

    assert self.v_cruise_helper.v_cruise_kph == 53

  def test_rounding_behavior(self):
    """Test rounding behavior for 5 and 10 increments"""
    test_cases = [
      (47, 5, 50),   # 47 -> 50 (round up to next 5)
      (45, 5, 50),   # 45 -> 50 (already at 5, increment by 5)
      (43, 10, 50),  # 43 -> 50 (round up to next 10)
      (40, 10, 50),  # 40 -> 50 (already at 10, increment by 10)
    ]

    for initial, increment, expected in test_cases:
      self.set_custom_increments(enabled=True, short_inc=increment, long_inc=increment)
      self.reset_cruise_speed_state()
      self.enable(initial * CV.KPH_TO_MS)

      self.press_button_short(ButtonType.accelCruise)
      assert self.v_cruise_helper.v_cruise_kph == expected

  def test_invalid_values_fallback(self):
    """Test that invalid values fallback to safe defaults"""
    # Test invalid short increment
    self.set_custom_increments(enabled=True, short_inc=-1, long_inc=5)
    self.enable(50 * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 1  # Should fallback to 1

    # Test invalid long increment
    self.reset_cruise_speed_state()
    self.set_custom_increments(enabled=True, short_inc=1, long_inc=99)
    self.enable(50 * CV.KPH_TO_MS)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_long(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 10  # Should fallback to 10
