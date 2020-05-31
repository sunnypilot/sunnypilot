from cereal import car
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.volkswagen import volkswagencan
from selfdrive.car.volkswagen.values import DBC_FILES, CANBUS, MQB_LDW_MESSAGES, BUTTON_STATES, CarControllerParams as P
from opendbc.can.packer import CANPacker
from common.realtime import DT_CTRL
from common.conversions import Conversions as CV
from common.params import Params
import cereal.messaging as messaging

VisualAlert = car.CarControl.HUDControl.VisualAlert

class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.apply_steer_last = 0
    self.CP = CP

    self.packer_pt = CANPacker(DBC_FILES.mqb)

    self.hcaSameTorqueCount = 0
    self.hcaEnabledFrameCount = 0
    self.graButtonStatesToSend = None
    self.graMsgSentCount = 0
    self.graMsgStartFramePrev = 0
    self.graMsgBusCounterPrev = 0

    self.steer_rate_limited = False

    self.signal_last = 0.
    self.disengage_blink = 0.
    self.lat_active = False
    self.standstill_status = 0
    self.standstill_status_timer = 0

    self.sm = messaging.SubMaster(['liveMapData', 'controlsState', 'longitudinalPlan'])
    self.param_s = Params()
    self.speed_limit_control_enabled = self.param_s.get_bool("SpeedLimitControl")
    self.vision_turn_speed_control = self.param_s.get_bool("VisionTurnSpeedControl")
    self.map_turn_speed_control = self.param_s.get_bool("MapTurnSpeedControl")
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
    self.button_type = 0
    self.button_select = 0
    self.button_count = 0
    self.target_speed = 0
    self.resume_count = 0
    self.t_interval = 7
    self.sl_force_active_timer = 0
    self.slc_state = 0
    self.slc_active_stock = False
    self.acc_type = int(Params().get("VwAccType"))

  def update(self, c, CS, frame, ext_bus, actuators, visual_alert, left_lane_visible, right_lane_visible, left_lane_depart, right_lane_depart):
    """ Controls thread """

    self.sm.update(0)
    self.speed_limit_control_enabled = self.param_s.get_bool("SpeedLimitControl")
    self.vision_turn_speed_control = self.param_s.get_bool("VisionTurnSpeedControl")
    self.map_turn_speed_control = self.param_s.get_bool("MapTurnSpeedControl")
    self.last_speed_limit_sign_tap = self.param_s.get_bool("LastSpeedLimitSignTap")
    self.slc_state = self.sm['longitudinalPlan'].speedLimitControlState
    self.is_metric = self.param_s.get_bool("IsMetric")
    self.speed_limit_perc_offset = self.param_s.get_bool("SpeedLimitPercOffset")
    self.speed_limit_value_offset = int(self.param_s.get("SpeedLimitValueOffset"))
    self.v_cruise_kph_prev = self.sm['controlsState'].vCruise
    self.get_speed_limit()
    self.acc_type = int(Params().get("VwAccType"))

    cur_time = frame * DT_CTRL
    if CS.leftBlinkerOn or CS.rightBlinkerOn:
      self.signal_last = cur_time

    lat_active = c.latActive and (not CS.belowLaneChangeSpeed or
                   (not ((cur_time - self.signal_last) < 1.0) and not (CS.leftBlinkerOn or CS.rightBlinkerOn)))

    can_sends = []

    # **** Steering Controls ************************************************ #

    if frame % P.HCA_STEP == 0:
      # Logic to avoid HCA state 4 "refused":
      #   * Don't steer unless HCA is in state 3 "ready" or 5 "active"
      #   * Don't steer at standstill
      #   * Don't send > 3.00 Newton-meters torque
      #   * Don't send the same torque for > 6 seconds
      #   * Don't send uninterrupted steering for > 360 seconds
      # One frame of HCA disabled is enough to reset the timer, without zeroing the
      # torque value. Do that anytime we happen to have 0 torque, or failing that,
      # when exceeding ~1/3 the 360 second timer.

      if lat_active:
        new_steer = int(round(actuators.steer * P.STEER_MAX))
        apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, P)
        self.steer_rate_limited = new_steer != apply_steer
        if apply_steer == 0:
          hcaEnabled = False
          self.hcaEnabledFrameCount = 0
        else:
          self.hcaEnabledFrameCount += 1
          if self.hcaEnabledFrameCount >= 118 * (100 / P.HCA_STEP):  # 118s
            hcaEnabled = False
            self.hcaEnabledFrameCount = 0
          else:
            hcaEnabled = True
            if self.apply_steer_last == apply_steer:
              self.hcaSameTorqueCount += 1
              if self.hcaSameTorqueCount > 1.9 * (100 / P.HCA_STEP):  # 1.9s
                apply_steer -= (1, -1)[apply_steer < 0]
                self.hcaSameTorqueCount = 0
            else:
              self.hcaSameTorqueCount = 0
      else:
        hcaEnabled = False
        apply_steer = 0

      self.apply_steer_last = apply_steer
      idx = (frame / P.HCA_STEP) % 16
      can_sends.append(volkswagencan.create_mqb_steering_control(self.packer_pt, CANBUS.pt, apply_steer,
                                                                 idx, hcaEnabled))

    # **** HUD Controls ***************************************************** #

    if frame % P.LDW_STEP == 0:
      if visual_alert in (VisualAlert.steerRequired, VisualAlert.ldw):
        hud_alert = MQB_LDW_MESSAGES["laneAssistTakeOverSilent"]
      else:
        hud_alert = MQB_LDW_MESSAGES["none"]

      can_sends.append(volkswagencan.create_mqb_hud_control(self.packer_pt, CANBUS.pt, c.enabled, lat_active,
                                                            CS.out.steeringPressed, hud_alert, left_lane_visible,
                                                            right_lane_visible, CS.ldw_stock_values,
                                                            left_lane_depart, right_lane_depart))

    self.lat_active = lat_active

    if self.last_speed_limit_sign_tap:
      self.sl_force_active_timer = cur_time

    sl_force_active = self.speed_limit_control_enabled and (cur_time < self.sl_force_active_timer + 2.0)
    sl_inactive = not sl_force_active and (not self.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
    sl_temp_inactive = not sl_force_active and (self.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active

    # **** ACC Button Controls ********************************************** #

    # FIXME: this entire section is in desperate need of refactoring

    if self.CP.pcmCruise:
      if c.cruiseControl.cancel or (c.enabled and CS.out.cruiseState.standstill):
        if frame > self.graMsgStartFramePrev + P.GRA_VBP_STEP:
          if c.cruiseControl.cancel:
            # Cancel ACC if it's engaged with OP disengaged.
            self.graButtonStatesToSend = BUTTON_STATES.copy()
            self.graButtonStatesToSend["cancel"] = True
          elif c.enabled and CS.out.cruiseState.standstill:
            self.standstill_status = 1
            # Blip the Resume button if we're engaged at standstill.
            # FIXME: This is a naive implementation, improve with visiond or radar input.
            self.graButtonStatesToSend = BUTTON_STATES.copy()
            self.graButtonStatesToSend["resumeCruise"] = True

        if CS.graMsgBusCounter != self.graMsgBusCounterPrev:
          self.graMsgBusCounterPrev = CS.graMsgBusCounter
          if self.graButtonStatesToSend is not None:
            if self.graMsgSentCount == 0:
              self.graMsgStartFramePrev = frame
            idx = (CS.graMsgBusCounter + 1) % 16
            can_sends.append(volkswagencan.create_mqb_acc_buttons_control(self.packer_pt, ext_bus, self.graButtonStatesToSend, CS, idx))
            self.graMsgSentCount += 1
            if self.graMsgSentCount >= P.GRA_VBP_COUNT:
              self.graButtonStatesToSend = None
              self.graMsgSentCount = 0

      elif not CS.out.cruiseState.standstill:
        if frame > self.graMsgStartFramePrev:
          if CS.out.cruiseState.enabled and not CS.out.gasPressed:
            cruise_button = self.get_cruise_buttons(CS, self.v_cruise_kph_prev)
            if cruise_button is not None:
              if self.acc_type == 0:
                if cruise_button == 1:
                  self.graButtonStatesToSend = BUTTON_STATES.copy()
                  self.graButtonStatesToSend["accelCruise"] = True
                elif cruise_button == 2:
                  self.graButtonStatesToSend = BUTTON_STATES.copy()
                  self.graButtonStatesToSend["decelCruise"] = True
              elif self.acc_type == 1:
                if cruise_button == 1:
                  self.graButtonStatesToSend = BUTTON_STATES.copy()
                  self.graButtonStatesToSend["resumeCruise"] = True
                elif cruise_button == 2:
                  self.graButtonStatesToSend = BUTTON_STATES.copy()
                  self.graButtonStatesToSend["setCruise"] = True

        if CS.graMsgBusCounter != self.graMsgBusCounterPrev:
          self.graMsgBusCounterPrev = CS.graMsgBusCounter
          if self.graButtonStatesToSend is not None:
            if self.graMsgSentCount == 0:
              self.graMsgStartFramePrev = frame
            idx = (CS.graMsgBusCounter + 1) % 16
            can_sends.append(volkswagencan.create_mqb_acc_buttons_control(self.packer_pt, ext_bus, self.graButtonStatesToSend, CS, idx))
            self.graMsgSentCount += 1
            if self.graMsgSentCount >= 3:
              self.graButtonStatesToSend = None
              self.graMsgSentCount = 0

    if CS.out.brakeLights and CS.out.vEgo < 0.1:
      self.standstill_status = 1
      self.standstill_status_timer += 1
      if self.standstill_status_timer > 200:
        self.standstill_status = 1
        self.standstill_status_timer = 0
    if self.standstill_status == 1 and CS.out.vEgo > 1:
      self.standstill_status = 0

    new_actuators = actuators.copy()
    new_actuators.steer = self.apply_steer_last / P.STEER_MAX

    return new_actuators, can_sends

  def get_speed_limit(self):
    self.speed_limit = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0)
    return self.speed_limit

  # multikyd methods, sunnyhaibin logic
  def get_cruise_buttons_status(self, CS):
    if not CS.out.cruiseState.enabled or CS.buttonStates["accelCruise"] or CS.buttonStates["decelCruise"] or CS.buttonStates["setCruise"] or CS.buttonStates["resumeCruise"]:
      self.timer = 40
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
    speed_diff = round(self.target_speed - self.v_set_dis)
    if speed_diff > 0:
      self.button_type = 1
    elif speed_diff < 0:
      self.button_type = 2
    return None

  def type_1(self):
    cruise_button = None
    self.button_count += 1
    if self.target_speed == self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 10:
      cruise_button = 1
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_2(self):
    cruise_button = None
    self.button_count += 1
    if self.target_speed == self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 10:
      cruise_button = 2
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
