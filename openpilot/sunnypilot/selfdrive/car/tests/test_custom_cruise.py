from opendbc.can.parser import CANParser
from opendbc.car import create_button_events
from opendbc.car.structs import car
from opendbc.car.toyota.carstate import get_virtual_cruise_button, VIRTUAL_CRUISE_BUTTONS
from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.common.parameterized import parameterized, parameterized_class
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.car.cruise import TOYOTA_VIRTUAL_CRUISE_LONG_PRESS, VCruiseHelper, V_CRUISE_INITIAL, V_CRUISE_UNSET
from openpilot.selfdrive.car.tests.test_cruise_speed import TestVCruiseHelper
from openpilot.sunnypilot.selfdrive.car.interfaces import initialize_params

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type


class TestToyotaParamsHandoff(OpenpilotTestCase):
  def test_tss2_long_tuning_param_is_forwarded_to_opendbc(self):
    keys = {next(iter(entry)) for entry in initialize_params(Params())}
    assert "ToyotaTSS2Long" in keys


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
    self.enable(V_CRUISE_INITIAL * CV.KPH_TO_MS, False, False)

    initial_speed = self.v_cruise_helper.v_cruise_kph

    # Short press should increment by 1 (default)
    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 1

  @parameterized.expand((1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
  def test_custom_short_press_increments(self, increment):
    """Test custom short press increments (1-10)"""
    self.set_custom_increments(enabled=True, short_inc=increment, long_inc=5)
    self.enable(50 * CV.KPH_TO_MS, False, False)

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
    self.enable(50 * CV.KPH_TO_MS, False, False)

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
    self.enable(50 * CV.KPH_TO_MS, False, False)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_short(button_type)

    expected_change = 3 if button_type == ButtonType.accelCruise else -3
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + expected_change

  def test_rounding_behavior(self):
    """Test rounding behavior for 5 and 10 increments"""
    test_cases = [
      (47, 5, 50),  # 47 -> 50 (round up to next 5)
      (45, 5, 50),  # 45 -> 50 (already at 5, increment by 5)
      (43, 10, 50),  # 43 -> 50 (round up to next 10)
      (40, 10, 50),  # 40 -> 50 (already at 10, increment by 10)
    ]

    for initial, increment, expected in test_cases:
      self.set_custom_increments(enabled=True, short_inc=increment, long_inc=increment)
      self.reset_cruise_speed_state()
      self.enable(initial * CV.KPH_TO_MS, False, False)

      self.press_button_short(ButtonType.accelCruise)
      assert self.v_cruise_helper.v_cruise_kph == expected

  def test_invalid_values_fallback(self):
    """Test that invalid values fallback to safe defaults"""
    # Test invalid short increment
    self.set_custom_increments(enabled=True, short_inc=-1, long_inc=5)
    self.enable(50 * CV.KPH_TO_MS, False, False)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_short(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 1  # Should fallback to 1

    # Test invalid long increment
    self.reset_cruise_speed_state()
    self.set_custom_increments(enabled=True, short_inc=1, long_inc=99)
    self.enable(50 * CV.KPH_TO_MS, False, False)

    initial_speed = self.v_cruise_helper.v_cruise_kph
    self.press_button_long(ButtonType.accelCruise)
    assert self.v_cruise_helper.v_cruise_kph == initial_speed + 10  # Should fallback to 10


class TestToyotaVirtualCruiseSpeed(OpenpilotTestCase):
  def setup_method(self):
    self.params = Params()
    self.params.put_bool("CustomAccIncrementsEnabled", True, block=True)
    self.params.put("CustomAccShortPressIncrement", 5, block=True)
    self.params.put("CustomAccLongPressIncrement", 5, block=True)

    CP = car.CarParams(brand="toyota", pcmCruise=True, openpilotLongitudinalControl=True)
    CP_SP = custom.CarParamsSP(pcmCruiseSpeed=False)
    self.v_cruise_helper = VCruiseHelper(CP, CP_SP)
    self.v_cruise_helper.read_custom_set_speed_params()
    self.route_parser = CANParser("toyota_nodsu_pt_generated", [("CLUTCH", 16)], 0)
    self.route_button = 0

  @staticmethod
  def car_state(canonical_kph, cluster_kph, *, available=True, standstill=False, gas_pressed=False, v_ego_kph=0.0, button_events=None):
    CS = car.CarState(
      gasPressed=gas_pressed,
      vEgo=v_ego_kph * CV.KPH_TO_MS,
      cruiseState={
        "available": available,
        "speed": canonical_kph * CV.KPH_TO_MS,
        "speedCluster": cluster_kph * CV.KPH_TO_MS,
        "standstill": standstill,
      },
    )
    CS.buttonEvents = button_events or []
    return CS

  def seed_enabled(self, canonical_kph, cluster_kph, *, is_metric=True):
    CS = self.car_state(canonical_kph, cluster_kph)
    self.v_cruise_helper.update_v_cruise(CS, enabled=False, is_metric=is_metric)
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=is_metric)
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=is_metric)
    assert self.v_cruise_helper.v_cruise_kph == canonical_kph
    assert self.v_cruise_helper.v_cruise_cluster_kph == cluster_kph

  def press(self, button_type, canonical_kph, cluster_kph, hold_frames=0, *, standstill=False, gas_pressed=False, v_ego_kph=0.0, is_metric=True):
    pressed = [ButtonEvent(type=button_type, pressed=True)]
    self.v_cruise_helper.update_v_cruise(
      self.car_state(canonical_kph, cluster_kph, standstill=standstill, gas_pressed=gas_pressed, v_ego_kph=v_ego_kph, button_events=pressed),
      enabled=True,
      is_metric=is_metric,
    )
    for _ in range(hold_frames):
      self.v_cruise_helper.update_v_cruise(
        self.car_state(canonical_kph, cluster_kph, standstill=standstill, gas_pressed=gas_pressed, v_ego_kph=v_ego_kph),
        enabled=True,
        is_metric=is_metric,
      )
    released = [ButtonEvent(type=button_type, pressed=False)]
    self.v_cruise_helper.update_v_cruise(
      self.car_state(canonical_kph, cluster_kph, standstill=standstill, gas_pressed=gas_pressed, v_ego_kph=v_ego_kph, button_events=released),
      enabled=True,
      is_metric=is_metric,
    )

  def set_increments(self, short_increment, long_increment):
    self.params.put("CustomAccShortPressIncrement", short_increment, block=True)
    self.params.put("CustomAccLongPressIncrement", long_increment, block=True)
    self.v_cruise_helper.read_custom_set_speed_params()

  def assert_kph_almost_equal(self, actual, expected):
    self.assertAlmostEqual(actual, expected, delta=abs(expected) * 1e-6)

  def route_button_events(self, payload):
    self.route_parser.update((1, [(0x361, bytes.fromhex(payload), 0)]))
    current = get_virtual_cruise_button(
      self.route_parser.vl["CLUTCH"]["CRUISE_RES"],
      self.route_parser.vl["CLUTCH"]["CRUISE_SET"],
    )
    events = create_button_events(current, self.route_button, VIRTUAL_CRUISE_BUTTONS)
    self.route_button = current
    return events

  def test_short_press_rounds_display_target_and_preserves_offset(self):
    self.seed_enabled(27, 31)
    self.press(ButtonType.accelCruise, 28, 32)

    assert self.v_cruise_helper.v_cruise_kph == 31
    assert self.v_cruise_helper.v_cruise_cluster_kph == 35

  def test_decel_at_display_minimum_does_not_increase_target(self):
    self.seed_enabled(26, 30)
    self.press(ButtonType.decelCruise, 25, 29)

    assert self.v_cruise_helper.v_cruise_kph == 26
    assert self.v_cruise_helper.v_cruise_cluster_kph == 30

  @parameterized.expand((52, TOYOTA_VIRTUAL_CRUISE_LONG_PRESS - 1))
  def test_route_length_short_press_is_not_a_long_press(self, hold_frames):
    self.set_increments(short_increment=2, long_increment=5)
    self.seed_enabled(27, 31)
    self.press(ButtonType.accelCruise, 28, 32, hold_frames=hold_frames)

    assert self.v_cruise_helper.v_cruise_kph == 29
    assert self.v_cruise_helper.v_cruise_cluster_kph == 33

  def test_toyota_long_press_uses_route_validated_cadence_and_suppresses_release(self):
    self.set_increments(short_increment=2, long_increment=5)
    self.seed_enabled(27, 31)

    pressed = [ButtonEvent(type=ButtonType.accelCruise, pressed=True)]
    self.v_cruise_helper.update_v_cruise(self.car_state(31, 35, button_events=pressed), enabled=True, is_metric=True)
    for _ in range(TOYOTA_VIRTUAL_CRUISE_LONG_PRESS):
      self.v_cruise_helper.update_v_cruise(self.car_state(31, 35), enabled=True, is_metric=True)

    assert self.v_cruise_helper.v_cruise_kph == 31
    assert self.v_cruise_helper.v_cruise_cluster_kph == 35

    released = [ButtonEvent(type=ButtonType.accelCruise, pressed=False)]
    self.v_cruise_helper.update_v_cruise(self.car_state(31, 35, button_events=released), enabled=True, is_metric=True)
    assert self.v_cruise_helper.v_cruise_kph == 31
    assert self.v_cruise_helper.v_cruise_cluster_kph == 35

  def test_route_4_32_second_hold_repeats_six_times(self):
    self.seed_enabled(26, 30)
    self.press(ButtonType.accelCruise, 30, 34, hold_frames=432)

    assert self.v_cruise_helper.v_cruise_kph == 56
    assert self.v_cruise_helper.v_cruise_cluster_kph == 60

  def test_maximum_boundary_caps_pair_and_preserves_offset(self):
    self.seed_enabled(141, 145)
    self.press(ButtonType.accelCruise, 142, 146)

    assert self.v_cruise_helper.v_cruise_kph == 141
    assert self.v_cruise_helper.v_cruise_cluster_kph == 145

    self.press(ButtonType.accelCruise, 143, 147)
    assert self.v_cruise_helper.v_cruise_kph == 141
    assert self.v_cruise_helper.v_cruise_cluster_kph == 145

  @parameterized.expand(
    (
      (25, 29, ButtonType.decelCruise),
      (141, 147, ButtonType.accelCruise),
    )
  )
  def test_out_of_range_raw_pair_is_not_moved_in_opposite_direction(self, canonical_kph, cluster_kph, button_type):
    self.seed_enabled(canonical_kph, cluster_kph)
    self.press(button_type, canonical_kph, cluster_kph)

    assert self.v_cruise_helper.v_cruise_kph == canonical_kph
    assert self.v_cruise_helper.v_cruise_cluster_kph == cluster_kph

  def test_imperial_increment_preserves_canonical_cluster_pair(self):
    self.seed_enabled(45, 50, is_metric=False)
    self.press(ButtonType.accelCruise, 46, 51, is_metric=False)

    assert self.v_cruise_helper.v_cruise_kph == 51
    assert self.v_cruise_helper.v_cruise_cluster_kph == 56

  def test_engagement_button_held_does_not_change_target(self):
    initial = self.car_state(27, 31)
    self.v_cruise_helper.update_v_cruise(initial, enabled=False, is_metric=True)

    pressed = [ButtonEvent(type=ButtonType.decelCruise, pressed=True)]
    self.v_cruise_helper.update_v_cruise(self.car_state(27, 31, button_events=pressed), enabled=False, is_metric=True)
    for _ in range(TOYOTA_VIRTUAL_CRUISE_LONG_PRESS + 10):
      self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)

    released = [ButtonEvent(type=ButtonType.decelCruise, pressed=False)]
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32, button_events=released), enabled=True, is_metric=True)
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)

    assert self.v_cruise_helper.v_cruise_kph == 28
    assert self.v_cruise_helper.v_cruise_cluster_kph == 32

  def test_delayed_pcm_target_seeds_before_software_ownership(self):
    invalid = self.car_state(0, 0)
    self.v_cruise_helper.update_v_cruise(invalid, enabled=False, is_metric=True)

    release = [ButtonEvent(type=ButtonType.decelCruise, pressed=False)]
    for _ in range(4):
      self.v_cruise_helper.update_v_cruise(self.car_state(0, 0, button_events=release), enabled=True, is_metric=True)
      assert self.v_cruise_helper.v_cruise_kph == V_CRUISE_UNSET
      assert self.v_cruise_helper.v_cruise_cluster_kph == V_CRUISE_UNSET

    self.v_cruise_helper.update_v_cruise(self.car_state(27, 31), enabled=True, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 27)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 31)

    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 27)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 31)

  def test_route_payload_short_press_drives_virtual_target(self):
    self.seed_enabled(27, 31)

    pressed = self.route_button_events("a61a0000561a1a81")
    self.v_cruise_helper.update_v_cruise(self.car_state(27, 31, button_events=pressed), enabled=True, is_metric=True)
    for _ in range(52):
      self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)

    released = self.route_button_events("861a0000561b1a81")
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32, button_events=released), enabled=True, is_metric=True)
    assert self.v_cruise_helper.v_cruise_kph == 31
    assert self.v_cruise_helper.v_cruise_cluster_kph == 35

  def test_prius_route_payload_short_set_drives_virtual_target(self):
    self.seed_enabled(31, 35)

    pressed = self.route_button_events("965f000056666585")
    self.v_cruise_helper.update_v_cruise(self.car_state(31, 35, button_events=pressed), enabled=True, is_metric=True)
    for _ in range(45):
      self.v_cruise_helper.update_v_cruise(self.car_state(30, 34), enabled=True, is_metric=True)

    released = self.route_button_events("865f000056666585")
    self.v_cruise_helper.update_v_cruise(self.car_state(30, 34, button_events=released), enabled=True, is_metric=True)
    assert self.v_cruise_helper.v_cruise_kph == 26
    assert self.v_cruise_helper.v_cruise_cluster_kph == 30

  def test_prius_route_payload_standstill_res_does_not_change_target(self):
    self.seed_enabled(27, 31)

    pressed = self.route_button_events("a61b0000561c1c80")
    self.v_cruise_helper.update_v_cruise(
      self.car_state(27, 31, standstill=True, button_events=pressed),
      enabled=True,
      is_metric=True,
    )
    for _ in range(TOYOTA_VIRTUAL_CRUISE_LONG_PRESS):
      self.v_cruise_helper.update_v_cruise(self.car_state(27, 31, standstill=True), enabled=True, is_metric=True)

    released = self.route_button_events("865f000056666585")
    self.v_cruise_helper.update_v_cruise(
      self.car_state(27, 31, standstill=True, button_events=released),
      enabled=True,
      is_metric=True,
    )
    assert self.v_cruise_helper.v_cruise_kph == 27
    assert self.v_cruise_helper.v_cruise_cluster_kph == 31

  def test_route_payload_disengage_mid_hold_clears_pending_action(self):
    self.seed_enabled(27, 31)

    pressed = self.route_button_events("a61a0000561a1a81")
    self.v_cruise_helper.update_v_cruise(self.car_state(27, 31, button_events=pressed), enabled=True, is_metric=True)
    for _ in range(30):
      self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)

    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=False, is_metric=True)
    released = self.route_button_events("861a0000561b1a81")
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32, available=False, button_events=released), enabled=False, is_metric=True)

    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=False, is_metric=True)
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)
    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=True, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 28)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 32)

  def test_standstill_resume_does_not_change_target(self):
    self.seed_enabled(27, 31)
    self.press(ButtonType.accelCruise, 27, 31, standstill=True)

    assert self.v_cruise_helper.v_cruise_kph == 27
    assert self.v_cruise_helper.v_cruise_cluster_kph == 31

  def test_disengagement_discards_virtual_target_and_reseeds_raw_pair(self):
    self.seed_enabled(27, 31)
    self.press(ButtonType.accelCruise, 28, 32)
    assert self.v_cruise_helper.v_cruise_kph == 31

    raw = self.car_state(28, 32)
    self.v_cruise_helper.update_v_cruise(raw, enabled=False, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 28)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 32)

    self.v_cruise_helper.update_v_cruise(raw, enabled=True, is_metric=True)
    self.v_cruise_helper.update_v_cruise(raw, enabled=True, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 28)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 32)

  def test_unavailable_and_mads_handback_discard_virtual_target(self):
    self.seed_enabled(27, 31)
    self.press(ButtonType.accelCruise, 28, 32)
    assert self.v_cruise_helper.v_cruise_kph == 31

    self.v_cruise_helper.update_v_cruise(self.car_state(28, 32), enabled=False, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 28)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 32)

    self.v_cruise_helper.update_v_cruise(self.car_state(0, 0, available=False), enabled=False, is_metric=True)
    assert self.v_cruise_helper.v_cruise_kph == V_CRUISE_UNSET
    assert self.v_cruise_helper.v_cruise_cluster_kph == V_CRUISE_UNSET

    self.v_cruise_helper.update_v_cruise(self.car_state(29, 33), enabled=False, is_metric=True)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_kph, 29)
    self.assert_kph_almost_equal(self.v_cruise_helper.v_cruise_cluster_kph, 33)

  def test_set_during_gas_override_clips_target_to_ego_speed(self):
    self.seed_enabled(27, 31)
    self.press(ButtonType.decelCruise, 26, 30, gas_pressed=True, v_ego_kph=50)

    assert self.v_cruise_helper.v_cruise_kph == 50
    assert self.v_cruise_helper.v_cruise_cluster_kph == 54
