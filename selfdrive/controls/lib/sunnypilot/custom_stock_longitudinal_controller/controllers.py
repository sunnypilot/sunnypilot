from abc import abstractmethod, ABC
from dataclasses import dataclass

from cereal import car
import cereal.messaging as messaging
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.car import DT_CTRL
from openpilot.selfdrive.controls.lib.sunnypilot.custom_stock_longitudinal_controller.definitions import MinimumSetPoint

SendCan = tuple[int, bytes, int]


@dataclass
class Service:
  long_plan_sp: str = 'longitudinalPlanSP'


class CustomStockLongitudinalControllerBase(ABC):
  def __init__(self, car_controller, CP):
    self.car_controller = car_controller
    self.CP = CP

    self.long_plan_sp = Service.long_plan_sp
    if hasattr(car_controller, 'sm'):
      new_services = self.car_controller.sm.data.keys() | {self.long_plan_sp}
      self.car_controller.sm = messaging.SubMaster(list(new_services))
    else:
      self.car_controller.sm = messaging.SubMaster([self.long_plan_sp])

    self.min_set_point = MinimumSetPoint(CP)

    self.params = Params()
    self.last_speed_limit_sign_tap_prev = False
    self.speed_limit = 0.
    self.speed_limit_offset = 0
    self.timer = 0
    self.final_speed_kph = 0
    self.init_speed = 0
    self.current_speed = 0
    self.v_set_dis = 0
    self.v_cruise_min = 0
    self.button_type = 0
    self.button_select = 0
    self.button_count = 0
    self.target_speed = 0
    self.t_interval = 7
    self.slc_active_stock = False
    self.sl_force_active_timer = 0
    self.v_tsc_state = 0
    self.slc_state = 0
    self.m_tsc_state = 0
    self.cruise_button = None
    self.speed_diff = 0
    self.v_tsc = 0
    self.m_tsc = 0
    self.steady_speed = 0

    self.button_mappings = self.get_button_mappings()

  # copy for logs in interface update
  def update_logs(self):
    self.car_controller.cruise_button = self.cruise_button
    self.car_controller.final_speed_kph = self.final_speed_kph
    self.car_controller.target_speed = self.target_speed
    self.car_controller.v_set_dis = self.v_set_dis
    self.car_controller.speed_diff = self.speed_diff
    self.car_controller.button_type = self.button_type

  # multikyd methods, sunnypilot logic
  def get_cruise_buttons_status(self, CS):
    if not CS.out.cruiseState.enabled or self.get_set_speed_buttons(CS):
      self.timer = 40
    elif self.timer:
      self.timer -= 1
    else:
      return 1
    return 0

  def get_target_speed(self, v_cruise_kph_prev):
    v_cruise_kph = v_cruise_kph_prev
    if self.slc_state > 1:
      v_cruise_kph = (self.speed_limit + self.speed_limit_offset) * CV.MS_TO_KPH
      if not self.slc_active_stock:
        v_cruise_kph = v_cruise_kph_prev
    return v_cruise_kph

  def get_button_type(self, button_type):
    self.type_status = "type_" + str(button_type)
    self.button_picker = getattr(self, self.type_status, lambda: "default")
    return self.button_picker()

  def reset_button(self):
    if self.button_type != 3:
      self.button_type = 0

  def type_default(self):
    self.button_type = 0
    return None

  def type_0(self):
    self.button_count = 0
    self.target_speed = self.init_speed
    self.speed_diff = self.target_speed - self.v_set_dis
    if self.target_speed > self.v_set_dis:
      self.button_type = 1
    elif self.target_speed < self.v_set_dis and self.v_set_dis > self.v_cruise_min:
      self.button_type = 2
    return None

  def type_1(self):
    cruise_button = self.button_mappings['type_1']
    self.button_count += 1
    if self.target_speed <= self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 5:
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_2(self):
    cruise_button = self.button_mappings['type_2']
    self.button_count += 1
    if self.target_speed >= self.v_set_dis or self.v_set_dis <= self.v_cruise_min:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 5:
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_3(self):
    cruise_button = None
    self.button_count += 1
    if self.button_count > self.t_interval:
      self.button_type = 0
    return cruise_button

  def get_curve_speed(self, target_speed_kph, v_cruise_kph_prev):
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

  def get_button_control(self, CS, final_speed, v_cruise_kph_prev):
    self.init_speed = round(min(final_speed, v_cruise_kph_prev) * (CV.KPH_TO_MPH if not CS.params_list.is_metric else 1))
    self.v_set_dis = round(CS.out.cruiseState.speed * (CV.MS_TO_MPH if not CS.params_list.is_metric else CV.MS_TO_KPH))
    cruise_button = self.get_button_type(self.button_type)
    return cruise_button

  def curve_speed_hysteresis(self, cur_speed: float, hyst=(0.75 * CV.MPH_TO_KPH)):
    if cur_speed > self.steady_speed:
      self.steady_speed = cur_speed
    elif cur_speed < self.steady_speed - hyst:
      self.steady_speed = cur_speed
    return self.steady_speed

  def get_cruise_buttons(self, CS, v_cruise_kph_prev):
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

    self.update_logs()

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

  def update(self, CS: car.CarState) -> None:
    self.car_controller.sm.update(0)

    if self.car_controller.sm.updated[self.long_plan_sp]:
      self.v_tsc_state = self.car_controller.sm[self.long_plan_sp].visionTurnControllerState
      self.slc_state = self.car_controller.sm[self.long_plan_sp].speedLimitControlState
      self.m_tsc_state = self.car_controller.sm[self.long_plan_sp].turnSpeedControlState
      self.speed_limit = self.car_controller.sm[self.long_plan_sp].speedLimit
      self.speed_limit_offset = self.car_controller.sm[self.long_plan_sp].speedLimitOffset
      self.v_tsc = self.car_controller.sm[self.long_plan_sp].visionTurnSpeed
      self.m_tsc = self.car_controller.sm[self.long_plan_sp].turnSpeed

    self.v_cruise_min = self.min_set_point.get_set_point(CS.params_list.is_metric)

    if not self.last_speed_limit_sign_tap_prev and CS.params_list.last_speed_limit_sign_tap:
      self.sl_force_active_timer = self.car_controller.frame
      self.params.put_bool_nonblocking("LastSpeedLimitSignTap", False)
    self.last_speed_limit_sign_tap_prev = CS.params_list.last_speed_limit_sign_tap

    sl_force_active = CS.params_list.speed_limit_control_enabled and (self.car_controller.frame < (self.sl_force_active_timer * DT_CTRL + 2.0))
    sl_inactive = not sl_force_active and (not CS.params_list.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
    sl_temp_inactive = not sl_force_active and (CS.params_list.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active
