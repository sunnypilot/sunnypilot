from abc import abstractmethod, ABC

from cereal import car, custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.states import InactiveState, \
  AcceleratingState, DeceleratingState, HoldingState, ResettingState
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_controller import ACTIVE_STATES

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState
SpeedLimitControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
TurnSpeedControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
VisionTurnControllerState = custom.LongitudinalPlanSP.VisionTurnControllerState

SendCan = tuple[int, bytes, int]


class CustomStockLongitudinalControllerBase(ABC):
  def __init__(self, car, car_controller, CP):
    self.car = car
    self.car_controller = car_controller
    self.CP = CP

    self.params = Params()
    self.last_speed_limit_sign_tap_prev = False
    self.timer = 0
    self.final_speed_kph = 0
    self.target_speed = 0
    self.current_speed = 0
    self.v_cruise = 0
    self.v_cruise_min = 0
    self.button_state = ButtonControlState.inactive
    self.slc_active_stock = False
    self.sl_force_active_timer = 0

    self.v_tsc_state = VisionTurnControllerState.disabled
    self.slc_state = SpeedLimitControlState.inactive
    self.m_tsc_state = TurnSpeedControlState.inactive
    self.v_tsc = 0
    self.speed_limit_offseted = 0
    self.m_tsc = 0

    self.cruise_button = None
    self.steady_speed = 0

    self.button_mapping = {}
    self.accel_button = None
    self.decel_button = None
    self.initialize_button_mapping()

    self.set_speed_buttons = None

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

  def initialize_button_mapping(self) -> None:
    self.button_mapping = {
      'accelerating': self.accel_button,
      'decelerating': self.decel_button,
    }

  def get_set_speed_buttons(self, CS: car.CarState) -> bool:
    return any(be.type in self.set_speed_buttons for be in CS.out.buttonEvents)

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

  def get_v_target(self, v_cruise_kph_prev: float):
    v_tsc_target = self.v_tsc * CV.MS_TO_KPH if self.v_tsc_state != VisionTurnControllerState.disabled else 255
    slc_target = self.speed_limit_offseted * CV.MS_TO_KPH if self.slc_state in ACTIVE_STATES else 255
    m_tsc_target = self.m_tsc * CV.MS_TO_KPH if self.m_tsc_state > TurnSpeedControlState.tempInactive else 255
    tsc_target = self.curve_speed_hysteresis(min(v_tsc_target, m_tsc_target) + 2 * CV.MPH_TO_KPH)

    return min(v_cruise_kph_prev, slc_target, tsc_target)

  def curve_speed_hysteresis(self, cur_speed: float, hyst: float = (0.75 * CV.MPH_TO_KPH)) -> float:
    if cur_speed > self.steady_speed:
      self.steady_speed = cur_speed
    elif cur_speed < self.steady_speed - hyst:
      self.steady_speed = cur_speed
    return self.steady_speed

  def get_button_control(self, CS: car.CarState, final_speed: float) -> int:
    self.target_speed = round(final_speed * (CV.KPH_TO_MPH if not CS.params_list.is_metric else 1))
    self.v_cruise = round(CS.out.cruiseState.speed * (CV.MS_TO_MPH if not CS.params_list.is_metric else CV.MS_TO_KPH))
    cruise_button = self.handle_button_state()
    return cruise_button

  def get_cruise_buttons(self, CS: car.CarState, v_cruise_kph_prev: float) -> int | None:
    cruise_button = None
    if not self.get_cruise_buttons_status(CS):
      pass
    elif CS.out.cruiseState.enabled:
      self.final_speed_kph = self.get_v_target(v_cruise_kph_prev)
      cruise_button = self.get_button_control(CS, self.final_speed_kph)  # MPH/KPH based button presses
    return cruise_button

  @staticmethod
  def get_set_point(is_metric: bool) -> float:
    return 30 if is_metric else int(20 * CV.MPH_TO_KPH)

  @abstractmethod
  def create_mock_button_messages(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    pass

  def update(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    if self.car.sm.updated['longitudinalPlanSP']:
      self.v_tsc_state = self.car.sm['longitudinalPlanSP'].visionTurnControllerState
      self.slc_state = self.car.sm['longitudinalPlanSP'].speedLimitControlState
      self.m_tsc_state = self.car.sm['longitudinalPlanSP'].turnSpeedControlState
      self.v_tsc = self.car.sm['longitudinalPlanSP'].visionTurnSpeed
      self.speed_limit_offseted = self.car.sm['longitudinalPlanSP'].speedLimitOffseted
      self.m_tsc = self.car.sm['longitudinalPlanSP'].turnSpeed

    self.v_cruise_min = self.get_set_point(CS.params_list.is_metric)

    can_sends = self.create_mock_button_messages(CS, CC)

    return can_sends
