from abc import abstractmethod, ABC

from cereal import car, custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.states import InactiveState, \
  AcceleratingState, DeceleratingState, HoldingState, ResettingState, LoadingState
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.helpers import get_set_point
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_controller import ACTIVE_STATES

ButtonControlState = custom.CarControlSP.CustomStockLongitudinalControl.ButtonControlState
SpeedLimitControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
TurnSpeedControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
VisionTurnControllerState = custom.LongitudinalPlanSP.VisionTurnControllerState

SendCan = tuple[int, bytes, int]


class CustomStockLongitudinalControllerBase(ABC):
  def __init__(self, car, car_controller, car_state, CP):
    self.car = car
    self.car_controller = car_controller
    self.car_state = car_state
    self.CP = CP

    self.params = Params()
    self.timer = 0
    self.final_speed_kph = 0
    self.target_speed = 0
    self.v_cruise = 0
    self.v_cruise_min = 0
    self.button_state = ButtonControlState.inactive

    self.v_tsc_state = VisionTurnControllerState.disabled
    self.slc_state = SpeedLimitControlState.inactive
    self.m_tsc_state = TurnSpeedControlState.inactive
    self.v_tsc = 0
    self.speed_limit_offseted = 0
    self.m_tsc = 0

    self.is_ready = False
    self.cruise_button = None
    self.steady_speed = 0

    self.accel_button = None
    self.decel_button = None
    self.set_speed_buttons = None

    self.button_states = {
      ButtonControlState.inactive: InactiveState(),
      ButtonControlState.accelerating: AcceleratingState(),
      ButtonControlState.decelerating: DeceleratingState(),
      ButtonControlState.holding: HoldingState(),
      ButtonControlState.resetting: ResettingState(),
      ButtonControlState.loading: LoadingState(),
    }

  @abstractmethod
  def create_mock_button_messages(self) -> list[SendCan]:
    pass

  def state_publish(self):
    customStockLongitudinalControl = custom.CarControlSP.CustomStockLongitudinalControl.new_message()
    customStockLongitudinalControl.state = self.button_state
    customStockLongitudinalControl.cruiseButton = 0 if self.cruise_button is None else int(self.cruise_button)
    customStockLongitudinalControl.finalSpeedKph = float(self.final_speed_kph)
    customStockLongitudinalControl.targetSpeed = float(self.target_speed)
    customStockLongitudinalControl.vCruise = float(self.v_cruise)
    return customStockLongitudinalControl

  def get_v_target(self, CC: car.CarControl) -> float:
    v_tsc_target = self.v_tsc * CV.MS_TO_KPH if self.v_tsc_state != VisionTurnControllerState.disabled else 255
    slc_target = self.speed_limit_offseted * CV.MS_TO_KPH if self.slc_state in ACTIVE_STATES else 255
    m_tsc_target = self.m_tsc * CV.MS_TO_KPH if self.m_tsc_state > TurnSpeedControlState.tempInactive else 255
    tsc_target = self.curve_speed_hysteresis(min(v_tsc_target, m_tsc_target) + 2 * CV.MPH_TO_KPH)

    return min(CC.vCruise, slc_target, tsc_target)

  def curve_speed_hysteresis(self, cur_speed: float, hyst: float = (0.75 * CV.MPH_TO_KPH)) -> float:
    if cur_speed > self.steady_speed:
      self.steady_speed = cur_speed
    elif cur_speed < self.steady_speed - hyst:
      self.steady_speed = cur_speed
    return self.steady_speed

  def ready_state_update(self, CS: car.CarState, CC: car.CarControl) -> None:
    ready = CS.cruiseState.enabled and not CC.cruiseControl.cancel and not CC.cruiseControl.resume
    button_pressed = any(be.type in self.set_speed_buttons for be in CS.buttonEvents)

    self.is_ready = ready and not button_pressed

  def get_cruise_button(self, CS: car.CarState) -> None:
    self.target_speed = round(self.final_speed_kph * (CV.KPH_TO_MPH if not self.car_state.params_list.is_metric else 1))
    self.v_cruise = round(CS.cruiseState.speed * (CV.MS_TO_MPH if not self.car_state.params_list.is_metric else CV.MS_TO_KPH))

    self.cruise_button = self.button_states[self.button_state](self)

  def update(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    can_sends = []
    if self.car.sm.updated['longitudinalPlanSP']:
      self.v_tsc_state = self.car.sm['longitudinalPlanSP'].visionTurnControllerState
      self.slc_state = self.car.sm['longitudinalPlanSP'].speedLimitControlState
      self.m_tsc_state = self.car.sm['longitudinalPlanSP'].turnSpeedControlState
      self.v_tsc = self.car.sm['longitudinalPlanSP'].visionTurnSpeed
      self.speed_limit_offseted = self.car.sm['longitudinalPlanSP'].speedLimit + self.car.sm['longitudinalPlanSP'].speedLimitOffset
      self.m_tsc = self.car.sm['longitudinalPlanSP'].turnSpeed

    self.v_cruise_min = get_set_point(self.car_state.params_list.is_metric)

    self.final_speed_kph = self.get_v_target(CC)

    self.ready_state_update(CS, CC)

    self.get_cruise_button(CS)

    can_sends.extend(self.create_mock_button_messages())

    return can_sends
