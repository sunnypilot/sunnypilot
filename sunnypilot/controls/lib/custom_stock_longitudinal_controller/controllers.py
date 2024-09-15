from abc import abstractmethod, ABC

from cereal import car, custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_controller import ACTIVE_STATES
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.states import InactiveState, \
  AcceleratingState, DeceleratingState, HoldingState, ResettingState, LoadingState
from openpilot.sunnypilot.controls.lib.custom_stock_longitudinal_controller.helpers import get_set_point, \
  speed_hysteresis, update_manual_button_timers

ButtonType = car.CarState.ButtonEvent.Type
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
    self.is_ready_prev = False
    self.cruise_button = None
    self.speed_steady = 0

    self.accel_button = None
    self.decel_button = None
    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0}

    self.button_states = {
      ButtonControlState.inactive: InactiveState(self),
      ButtonControlState.loading: LoadingState(self),
      ButtonControlState.accelerating: AcceleratingState(self),
      ButtonControlState.decelerating: DeceleratingState(self),
      ButtonControlState.holding: HoldingState(self),
      ButtonControlState.resetting: ResettingState(self),
    }

  @abstractmethod
  def create_mock_button_messages(self) -> list[SendCan]:
    pass

  def state_publish(self) -> custom.CarControlSP.CustomStockLongitudinalControl:
    customStockLongitudinalControl = custom.CarControlSP.CustomStockLongitudinalControl.new_message()
    customStockLongitudinalControl.state = self.button_state
    customStockLongitudinalControl.cruiseButton = 0 if self.cruise_button is None else int(self.cruise_button)
    customStockLongitudinalControl.finalSpeedKph = float(self.final_speed_kph)
    customStockLongitudinalControl.targetSpeed = float(self.target_speed)
    customStockLongitudinalControl.vCruise = float(self.v_cruise)
    return customStockLongitudinalControl

  def update_msgs(self) -> None:
    if self.car.sm.updated['longitudinalPlanSP']:
      self.v_tsc_state = self.car.sm['longitudinalPlanSP'].visionTurnControllerState
      self.slc_state = self.car.sm['longitudinalPlanSP'].speedLimitControlState
      self.m_tsc_state = self.car.sm['longitudinalPlanSP'].turnSpeedControlState
      self.v_tsc = self.car.sm['longitudinalPlanSP'].visionTurnSpeed

      speed_limit = self.car.sm['longitudinalPlanSP'].speedLimit
      speed_limit_offset = self.car.sm['longitudinalPlanSP'].speedLimitOffset
      self.speed_limit_offseted = speed_limit + speed_limit_offset

      self.m_tsc = self.car.sm['longitudinalPlanSP'].turnSpeed

  def update_calculations(self, CS: car.CarState, CC: car.CarControl) -> None:
    is_metric = self.car_state.params_list.is_metric
    self.v_cruise_min = get_set_point(is_metric)

    v_target = {'cruise': CC.vCruise}

    if self.v_tsc_state != VisionTurnControllerState.disabled:
      v_target['v_tsc'] = self.v_tsc * CV.MS_TO_KPH

    if self.slc_state in ACTIVE_STATES:
      v_target['slc'] = self.speed_limit_offseted * CV.MS_TO_KPH

    if self.m_tsc_state > TurnSpeedControlState.tempInactive:
      v_target['m_tsc'] = self.m_tsc * CV.MS_TO_KPH

    source = min(v_target, key=v_target.get)

    speed_filtered = speed_hysteresis(self, v_target[source], self.speed_steady, 1.5 * (1 if is_metric else CV.MPH_TO_KPH))

    self.final_speed_kph = min(speed_filtered, CC.vCruise)

    self.target_speed = round(self.final_speed_kph * (1 if is_metric else CV.KPH_TO_MPH))
    self.v_cruise = round(CS.cruiseState.speed * (CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH))

  def update_state(self, CS: car.CarState, CC: car.CarControl) -> None:
    update_manual_button_timers(CS, self.cruise_buttons)

    ready = CS.cruiseState.enabled and not CC.cruiseControl.cancel and not CC.cruiseControl.resume
    button_pressed = any(self.cruise_buttons[k] > 0 for k in CS.buttonEvents)

    self.is_ready = ready and not button_pressed

    self.cruise_button = self.button_states[self.button_state]()

    self.is_ready_prev = self.is_ready

  def update(self, CS: car.CarState, CC: car.CarControl) -> list[SendCan]:
    can_sends = []

    self.update_msgs()

    self.update_calculations(CS, CC)

    self.update_state(CS, CC)

    can_sends.extend(self.create_mock_button_messages())

    return can_sends
