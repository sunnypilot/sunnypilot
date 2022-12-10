from cereal import car
import cereal.messaging as messaging
from opendbc.can.packer import CANPacker
from common.numpy_fast import clip
from common.params import Params
from common.realtime import DT_CTRL
from common.conversions import Conversions as CV
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.volkswagen import mqbcan, pqcan
from selfdrive.car.volkswagen.values import CANBUS, PQ_CARS, CarControllerParams, BUTTON_STATES

VisualAlert = car.CarControl.HUDControl.VisualAlert
LongCtrlState = car.CarControl.Actuators.LongControlState


class CarController:
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    self.CCP = CarControllerParams(CP)
    self.CCS = pqcan if CP.carFingerprint in PQ_CARS else mqbcan
    self.packer_pt = CANPacker(dbc_name)

    self.apply_steer_last = 0
    self.gra_acc_counter_last = None
    self.frame = 0
    self.hcaSameTorqueCount = 0
    self.hcaEnabledFrameCount = 0
    self.graButtonStatesToSend = None
    self.graMsgSentCount = 0
    self.graMsgStartFramePrev = 0
    self.last_button_frame = 0

    self.sm = messaging.SubMaster(['liveMapData', 'controlsState', 'longitudinalPlan'])
    self.param_s = Params()
    self.speed_limit_control_enabled = self.param_s.get_bool("SpeedLimitControl")
    self.vision_turn_speed_control = self.param_s.get_bool("TurnVisionControl")
    self.map_turn_speed_control = self.param_s.get_bool("TurnSpeedControl")
    self.last_speed_limit_sign_tap = self.param_s.get_bool("LastSpeedLimitSignTap")
    self.speed_limit = 0.
    self.is_metric = self.param_s.get_bool("IsMetric")
    self.speed_limit_perc_offset = self.param_s.get_bool("SpeedLimitPercOffset")
    self.speed_limit_value_offset = int(self.param_s.get("SpeedLimitValueOffset"))
    self.v_cruise_kph_prev = self.sm['controlsState'].vCruise
    self.timer = 0
    self.final_speed_kph = 0
    self.init_speed = 0
    self.current_speed = 0
    self.v_set_dis = 0
    self.v_set_dis_prev = 0
    self.button_type = 0
    self.button_select = 0
    self.button_count = 0
    self.target_speed = 0
    self.resume_count = 0
    self.t_interval = 7
    self.sl_force_active_timer = 0
    self.slc_state = 0
    self.slc_active_stock = False
    self.acc_type = int(self.param_s.get("VwAccType"))
    self.read_params_count = 0
    self.cruise_button = None
    self.speed_diff = 0

  def update(self, CC, CS, ext_bus):
    self.sm.update(0)
    self.speed_limit_control_enabled = self.param_s.get_bool("SpeedLimitControl")
    self.vision_turn_speed_control = self.param_s.get_bool("TurnVisionControl")
    self.map_turn_speed_control = self.param_s.get_bool("TurnSpeedControl")
    self.last_speed_limit_sign_tap = self.param_s.get_bool("LastSpeedLimitSignTap")
    self.slc_state = self.sm['longitudinalPlan'].speedLimitControlState
    self.is_metric = self.param_s.get_bool("IsMetric")
    self.speed_limit_perc_offset = self.param_s.get_bool("SpeedLimitPercOffset")
    self.speed_limit_value_offset = int(self.param_s.get("SpeedLimitValueOffset"))
    self.v_cruise_kph_prev = self.sm['controlsState'].vCruise
    self.get_speed_limit()

    actuators = CC.actuators
    hud_control = CC.hudControl
    can_sends = []

    if self.read_params_count % 50 == 0:
      self.acc_type = int(self.param_s.get("VwAccType"))
    self.read_params_count += 1

    # **** Steering Controls ************************************************ #

    if self.frame % self.CCP.HCA_STEP == 0:
      # Logic to avoid HCA state 4 "refused":
      #   * Don't steer unless HCA is in state 3 "ready" or 5 "active"
      #   * Don't steer at standstill
      #   * Don't send > 3.00 Newton-meters torque
      #   * Don't send the same torque for > 6 seconds
      #   * Don't send uninterrupted steering for > 360 seconds
      # One frame of HCA disabled is enough to reset the timer, without zeroing the
      # torque value. Do that anytime we happen to have 0 torque, or failing that,
      # when exceeding ~1/3 the 360 second timer.

      if CC.latActive:
        new_steer = int(round(actuators.steer * self.CCP.STEER_MAX))
        apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.CCP)
        if apply_steer == 0:
          hcaEnabled = False
          self.hcaEnabledFrameCount = 0
        else:
          self.hcaEnabledFrameCount += 1
          if self.hcaEnabledFrameCount >= 118 * (100 / self.CCP.HCA_STEP):  # 118s
            hcaEnabled = False
            self.hcaEnabledFrameCount = 0
          else:
            hcaEnabled = True
            if self.apply_steer_last == apply_steer:
              self.hcaSameTorqueCount += 1
              if self.hcaSameTorqueCount > 1.9 * (100 / self.CCP.HCA_STEP):  # 1.9s
                apply_steer -= (1, -1)[apply_steer < 0]
                self.hcaSameTorqueCount = 0
            else:
              self.hcaSameTorqueCount = 0
      else:
        hcaEnabled = False
        apply_steer = 0

      self.apply_steer_last = apply_steer
      can_sends.append(self.CCS.create_steering_control(self.packer_pt, CANBUS.pt, apply_steer, hcaEnabled))

    # **** Acceleration Controls ******************************************** #

    if self.frame % self.CCP.ACC_CONTROL_STEP == 0 and self.CP.openpilotLongitudinalControl:
      acc_control = self.CCS.acc_control_value(CS.out.cruiseState.available, CS.out.accFaulted, CC.longActive)
      accel = clip(actuators.accel, self.CCP.ACCEL_MIN, self.CCP.ACCEL_MAX) if CC.longActive else 0
      stopping = actuators.longControlState == LongCtrlState.stopping
      starting = actuators.longControlState == LongCtrlState.starting
      can_sends.extend(self.CCS.create_acc_accel_control(self.packer_pt, CANBUS.pt, CS.acc_type, CC.longActive, accel,
                                                         acc_control, stopping, starting, CS.esp_hold_confirmation))

    # **** HUD Controls ***************************************************** #

    if self.frame % self.CCP.LDW_STEP == 0:
      hud_alert = 0
      if hud_control.visualAlert in (VisualAlert.steerRequired, VisualAlert.ldw):
        hud_alert = self.CCP.LDW_MESSAGES["laneAssistTakeOver"]
      can_sends.append(self.CCS.create_lka_hud_control(self.packer_pt, CANBUS.pt, CS.ldw_stock_values, CC.enabled, CC.latActive,
                                                       CS.out.steeringPressed, hud_alert, hud_control))

    if self.frame % self.CCP.ACC_HUD_STEP == 0 and self.CP.openpilotLongitudinalControl:
      acc_hud_status = self.CCS.acc_hud_status_value(CS.out.cruiseState.available, CS.out.accFaulted, CC.longActive)
      set_speed = hud_control.setSpeed * CV.MS_TO_KPH  # FIXME: follow the recent displayed-speed updates, also use mph_kmh toggle to fix display rounding problem?
      can_sends.append(self.CCS.create_acc_hud_control(self.packer_pt, CANBUS.pt, acc_hud_status, set_speed,
                                                       hud_control.leadVisible))

    # **** Stock ACC Button Controls **************************************** #

    gra_send_ready = self.CP.pcmCruise and CS.gra_stock_values["COUNTER"] != self.gra_acc_counter_last
    if gra_send_ready and (CC.cruiseControl.cancel or CC.cruiseControl.resume):
      counter = (CS.gra_stock_values["COUNTER"] + 1) % 16
      can_sends.append(self.CCS.create_acc_buttons_control(self.packer_pt, ext_bus, CS.gra_stock_values, counter, self.graButtonStatesToSend,
                                                           cancel=CC.cruiseControl.cancel, resume=CC.cruiseControl.resume))

    cur_time = self.frame * DT_CTRL

    if self.last_speed_limit_sign_tap:
      self.sl_force_active_timer = cur_time

    sl_force_active = self.speed_limit_control_enabled and (cur_time < self.sl_force_active_timer + 2.0)
    sl_inactive = not sl_force_active and (not self.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
    sl_temp_inactive = not sl_force_active and (self.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active

    if not CC.cruiseControl.resume and CS.out.cruiseState.enabled and not CS.out.gasPressed and not self.CP.pcmCruiseSpeed:
      if self.frame > self.graMsgStartFramePrev + 10:
        if CS.out.cruiseState.enabled:
          self.cruise_button = self.get_cruise_buttons(CS, self.v_cruise_kph_prev)
          if self.cruise_button is not None and self.graMsgSentCount == 0:
            if self.acc_type == 0:
              if self.cruise_button == 1:
                self.graButtonStatesToSend = BUTTON_STATES.copy()
                self.graButtonStatesToSend["accelCruise"] = True
              elif self.cruise_button == 2:
                self.graButtonStatesToSend = BUTTON_STATES.copy()
                self.graButtonStatesToSend["decelCruise"] = True
            elif self.acc_type == 1:
              if self.cruise_button == 1:
                self.graButtonStatesToSend = BUTTON_STATES.copy()
                self.graButtonStatesToSend["resumeCruise"] = True
              elif self.cruise_button == 2:
                self.graButtonStatesToSend = BUTTON_STATES.copy()
                self.graButtonStatesToSend["setCruise"] = True
      if CS.gra_stock_values["COUNTER"] != self.gra_acc_counter_last:
        if self.graButtonStatesToSend is not None and (self.frame - self.last_button_frame) * DT_CTRL > 0.1:
          if self.graMsgSentCount == 0:
            self.graMsgStartFramePrev = self.frame
          counter = (CS.gra_stock_values["COUNTER"] + 1) % 16
          can_sends.append(self.CCS.create_acc_buttons_control(self.packer_pt, ext_bus, CS.gra_stock_values, counter, self.graButtonStatesToSend))
          self.last_button_frame = self.frame
          self.graMsgSentCount += 1
          if self.graMsgSentCount >= 3:
            self.graButtonStatesToSend = None
            self.graMsgSentCount = 0

    new_actuators = actuators.copy()
    new_actuators.steer = self.apply_steer_last / self.CCP.STEER_MAX

    self.gra_acc_counter_last = CS.gra_stock_values["COUNTER"]
    self.frame += 1
    return new_actuators, can_sends

  def get_speed_limit(self):
    self.speed_limit = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0)
    return self.speed_limit

  # multikyd methods, sunnyhaibin logic
  def get_cruise_buttons_status(self, CS):
    if not CS.out.cruiseState.enabled:
      if CS.buttonStates["accelCruise"] or CS.buttonStates["decelCruise"] or CS.buttonStates["setCruise"] or CS.buttonStates["resumeCruise"]:
        self.timer = 40
      elif CS.buttonStates["gapAdjustCruise"]:
        self.timer = 300
    elif self.timer:
      self.timer -= 1
    else:
      return 1
    return 0

  def get_target_speed(self, v_cruise_kph_prev):
    v_cruise_kph = v_cruise_kph_prev
    if self.speed_limit_control_enabled and self.speed_limit != 0.0:
      target_v_cruise_kph = self.speed_limit * CV.MS_TO_KPH
      if self.speed_limit_perc_offset:
        v_cruise_kph = target_v_cruise_kph + float(float(self.sm['longitudinalPlan'].speedLimitOffset) * CV.MS_TO_KPH)
      else:
        v_cruise_kph = target_v_cruise_kph + (float(self.speed_limit_value_offset * CV.MPH_TO_KPH) if not self.is_metric else self.speed_limit_value_offset)
      if not self.slc_active_stock:
        v_cruise_kph = v_cruise_kph_prev

    return v_cruise_kph

  def get_button_type(self, button_type):
    self.type_status = "type_" + str(button_type)
    self.button_picker = getattr(self, self.type_status, lambda:"default")
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
    self.speed_diff = round(self.target_speed - self.v_set_dis)
    if self.speed_diff > 0:
      self.button_type = 1
    elif self.speed_diff < 0:
      self.button_type = 2
    return None

  def type_1(self):
    cruise_button = 1
    self.button_count += 1
    if self.target_speed == self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 5:
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_2(self):
    cruise_button = 2
    self.button_count += 1
    if self.target_speed == self.v_set_dis:
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
    if self.vision_turn_speed_control:
      vision_v_cruise_kph = float(float(self.sm['longitudinalPlan'].visionTurnSpeed) * CV.MS_TO_KPH)
      if int(vision_v_cruise_kph) == int(v_cruise_kph_prev):
        vision_v_cruise_kph = 255
    else:
      vision_v_cruise_kph = 255
    if self.map_turn_speed_control:
      map_v_cruise_kph = float(float(self.sm['longitudinalPlan'].turnSpeed) * CV.MS_TO_KPH)
      if int(map_v_cruise_kph) == 0.0:
        map_v_cruise_kph = 255
    else:
      map_v_cruise_kph = 255
    return min(target_speed_kph, vision_v_cruise_kph, map_v_cruise_kph)

  def get_button_control(self, CS, final_speed, v_cruise_kph_prev):
    self.init_speed = round(min(final_speed, v_cruise_kph_prev) * CV.KPH_TO_MPH) if not self.is_metric else round(min(final_speed, v_cruise_kph_prev))
    self.v_set_dis = round(CS.out.cruiseState.speed * CV.MS_TO_MPH) if not self.is_metric else round(CS.out.cruiseState.speed * CV.MS_TO_KPH)
    cruise_button = self.get_button_type(self.button_type)
    return cruise_button

  def get_cruise_buttons(self, CS, v_cruise_kph_prev):
    cruise_button = None
    if not self.get_cruise_buttons_status(CS):
      pass
    elif CS.out.cruiseState.enabled:
      set_speed_kph = self.get_target_speed(v_cruise_kph_prev)
      if self.speed_limit_control_enabled:
        target_speed_kph = set_speed_kph
      else:
        target_speed_kph = min(v_cruise_kph_prev, set_speed_kph)
      if self.vision_turn_speed_control or self.map_turn_speed_control:
        self.final_speed_kph = self.get_curve_speed(target_speed_kph, v_cruise_kph_prev)
      else:
        self.final_speed_kph = target_speed_kph

      cruise_button = self.get_button_control(CS, self.final_speed_kph, v_cruise_kph_prev) # MPH/KPH based button presses
    return cruise_button
