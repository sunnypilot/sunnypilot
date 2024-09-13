from abc import abstractmethod, ABC

from cereal import car, custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.car import DT_CTRL
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.states import InactiveState, \
  AcceleratingState, DeceleratingState, HoldingState, ResettingState

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState

SendCan = tuple[int, bytes, int]


class CustomStockLongitudinalControllerBase(ABC):
  def __init__(self, car, car_controller, CP):
    self.car = car
    self.car_controller = car_controller
    self.CP = CP

    self.params = Params()
    self.last_speed_limit_sign_tap_prev = False
    self.speed_limit = 0.
    self.speed_limit_offset = 0
    self.timer = 0
    self.final_speed_kph = 0
    self.target_speed = 0
    self.current_speed = 0
    self.v_set_dis = 0
    self.v_cruise_min = 0
    self.button_state = ButtonControlState.inactive
    self.button_select = 0
    self.slc_active_stock = False
    self.sl_force_active_timer = 0
    self.v_tsc_state = 0
    self.slc_state = 0
    self.m_tsc_state = 0
    self.cruise_button = None
    self.v_tsc = 0
    self.m_tsc = 0
    self.steady_speed = 0

    self.button_mappings = self.get_button_mappings()

    inactive_state = InactiveState()
    accelerating_state = AcceleratingState()
    decelerating_state = DeceleratingState()
    holding_state = HoldingState()
    resetting_state = ResettingState()

    self.button_states = {
      ButtonControlState.inactive: inactive_state,
      ButtonControlState.accelerating: accelerating_state,
      ButtonControlState.decelerating: decelerating_state,
      ButtonControlState.holding: holding_state,
      ButtonControlState.resetting: resetting_state,
    }

  def handle_button_state(self) -> int | None:
    state = self.button_states.get(self.button_state)
    if state:
      return state.handle(self)
    else:
      raise ValueError(f"Unhandled button state: {self.button_state}")

  # multikyd methods, sunnypilot logic
  def get_cruise_buttons_status(self, CS: car.CarState) -> bool:
    if not CS.out.cruiseState.enabled or self.get_set_speed_buttons(CS):
      self.timer = 40
    elif self.timer:
      self.timer -= 1
    else:
      return True
    return False

  def get_target_speed(self, v_cruise_kph_prev: float) -> float:
    v_cruise_kph = v_cruise_kph_prev
    if self.slc_state > 1:
      v_cruise_kph = (self.speed_limit + self.speed_limit_offset) * CV.MS_TO_KPH
      if not self.slc_active_stock:
        v_cruise_kph = v_cruise_kph_prev
    return v_cruise_kph

  def get_curve_speed(self, target_speed_kph: float, v_cruise_kph_prev: float) -> float:
    if self.v_tsc_state != 0:
      vision_v_cruise_kph = self.v_tsc * CV.MS_TO_KPH
      if int(vision_v_cruise_kph) == int(v_cruise_kph_prev):
        vision_v_cruise_kph = 255
    else:
      vision_v_cruise_kph = 255
    if self.m_tsc_state > 1:
      map_v_cruise_kph = self.m_tsc * CV.MS_TO_KPH
      if int(map_v_cruise_kph) == 0.0:
        map_v_cruise_kph = 255
    else:
      map_v_cruise_kph = 255
    curve_speed = self.curve_speed_hysteresis(min(vision_v_cruise_kph, map_v_cruise_kph) + 2 * CV.MPH_TO_KPH)
    return min(target_speed_kph, curve_speed)

  def get_button_control(self, CS: car.CarState, final_speed: float, v_cruise_kph_prev: float) -> int:
    self.target_speed = round(min(final_speed, v_cruise_kph_prev) * (CV.KPH_TO_MPH if not CS.params_list.is_metric else 1))
    self.v_set_dis = round(CS.out.cruiseState.speed * (CV.MS_TO_MPH if not CS.params_list.is_metric else CV.MS_TO_KPH))
    cruise_button = self.handle_button_state()

    return cruise_button

  def curve_speed_hysteresis(self, cur_speed: float, hyst: float = (0.75 * CV.MPH_TO_KPH)) -> float:
    if cur_speed > self.steady_speed:
      self.steady_speed = cur_speed
    elif cur_speed < self.steady_speed - hyst:
      self.steady_speed = cur_speed
    return self.steady_speed

  def get_cruise_buttons(self, CS: car.CarState, v_cruise_kph_prev: float) -> int | None:
    cruise_button = None
    if not self.get_cruise_buttons_status(CS):
      pass
    elif CS.out.cruiseState.enabled:
      set_speed_kph = self.get_target_speed(v_cruise_kph_prev)
      if self.slc_state > 1:
        target_speed_kph = set_speed_kph
      else:
        target_speed_kph = min(v_cruise_kph_prev, set_speed_kph)
      if self.v_tsc_state != 0 or self.m_tsc_state > 1:
        self.final_speed_kph = self.get_curve_speed(target_speed_kph, v_cruise_kph_prev)
      else:
        self.final_speed_kph = target_speed_kph

      cruise_button = self.get_button_control(CS, self.final_speed_kph, v_cruise_kph_prev)  # MPH/KPH based button presses

    return cruise_button

  @abstractmethod
  def get_set_speed_buttons(self, CS: car.CarState) -> bool:
    pass

  @abstractmethod
  def get_button_mappings(self) -> dict[str, int]:
    pass

  @abstractmethod
  def create_mock_button_messages(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    pass

  @abstractmethod
  def get_set_point(self, is_metric: bool) -> float:
    pass

  def update(self, CS: car.CarState) -> None:
    if self.car.sm.updated['longitudinalPlanSP']:
      self.v_tsc_state = self.car.sm['longitudinalPlanSP'].visionTurnControllerState
      self.slc_state = self.car.sm['longitudinalPlanSP'].speedLimitControlState
      self.m_tsc_state = self.car.sm['longitudinalPlanSP'].turnSpeedControlState
      self.speed_limit = self.car.sm['longitudinalPlanSP'].speedLimit
      self.speed_limit_offset = self.car.sm['longitudinalPlanSP'].speedLimitOffset
      self.v_tsc = self.car.sm['longitudinalPlanSP'].visionTurnSpeed
      self.m_tsc = self.car.sm['longitudinalPlanSP'].turnSpeed

    self.v_cruise_min = self.get_set_point(CS.params_list.is_metric)

    if not self.last_speed_limit_sign_tap_prev and CS.params_list.last_speed_limit_sign_tap:
      self.sl_force_active_timer = self.car.sm.frame
      self.params.put_bool_nonblocking("LastSpeedLimitSignTap", False)
    self.last_speed_limit_sign_tap_prev = CS.params_list.last_speed_limit_sign_tap

    sl_force_active = CS.params_list.speed_limit_control_enabled and (self.car.sm.frame < (self.sl_force_active_timer * DT_CTRL + 2.0))
    sl_inactive = not sl_force_active and (not CS.params_list.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
    sl_temp_inactive = not sl_force_active and (CS.params_list.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active
