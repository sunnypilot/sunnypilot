from cereal import car, log
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.volkswagen import volkswagencan
from selfdrive.car.volkswagen.values import DBC_FILES, CANBUS, MQB_LDW_MESSAGES, BUTTON_STATES, CarControllerParams as P
from opendbc.can.packer import CANPacker
from selfdrive.config import Conversions as CV
from common.realtime import DT_CTRL
from common.params import Params
import cereal.messaging as messaging

VisualAlert = car.CarControl.HUDControl.VisualAlert
SpeedLimitControlState = log.LongitudinalPlan.SpeedLimitControlState

class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.apply_steer_last = 0

    self.packer_pt = CANPacker(DBC_FILES.mqb)

    self.sm = messaging.SubMaster(['liveMapData', 'controlsState', 'longitudinalPlan'])

    self.signal_last = 0.
    self.disengage_blink = 0.
    self.hcaSameTorqueCount = 0
    self.hcaEnabledFrameCount = 0
    self.graButtonStatesToSend = None
    self.graMsgSentCount = 0
    self.graMsgStartFramePrev = 0
    self.graMsgBusCounterPrev = 0

    self.steer_rate_limited = False

    self.standstill_fault_reduce_timer = 0
    self.standstill_status = 0
    self.standstill_status_timer = 0

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

  def update(self, enabled, CS, frame, ext_bus, actuators, visual_alert, left_lane_visible, right_lane_visible, left_lane_depart, right_lane_depart):
    """ Controls thread """

    self.sm.update(0)

    cur_time = frame * DT_CTRL
    if CS.leftBlinkerOn or CS.rightBlinkerOn:
      self.signal_last = cur_time

    can_sends = []

    lkas_active = enabled and CS.out.vEgo > CS.CP.minSteerSpeed and not (CS.out.standstill or CS.out.steerError or CS.out.steerWarning) and CS.accMainEnabled and ((CS.automaticLaneChange and not CS.belowLaneChangeSpeed) or ((not ((cur_time - self.signal_last) < 1) or not CS.belowLaneChangeSpeed) and not (CS.leftBlinkerOn or CS.rightBlinkerOn)))

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

      if enabled and CS.out.vEgo > CS.CP.minSteerSpeed and not (CS.out.standstill or CS.out.steerError or CS.out.steerWarning) and CS.accMainEnabled and ((CS.automaticLaneChange and not CS.belowLaneChangeSpeed) or ((not ((cur_time - self.signal_last) < 1) or not CS.belowLaneChangeSpeed) and not (CS.leftBlinkerOn or CS.rightBlinkerOn))):
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
      if visual_alert in [VisualAlert.steerRequired, VisualAlert.ldw]:
        hud_alert = MQB_LDW_MESSAGES["laneAssistTakeOverSilent"]
      else:
        hud_alert = MQB_LDW_MESSAGES["none"]

      can_sends.append(volkswagencan.create_mqb_hud_control(self.packer_pt, CANBUS.pt, enabled, lkas_active,
                                                            CS.out.steeringPressed, hud_alert, left_lane_visible,
                                                            right_lane_visible, CS.ldw_stock_values,
                                                            left_lane_depart, right_lane_depart))

    speed_limit_control_enabled = Params().get_bool("SpeedLimitControl")
    last_speed_limit_sign_tap = Params().get_bool("LastSpeedLimitSignTap")

    speed_limit = self.get_speed_limit_osm()
    speed_limit_offset = self.get_speed_limit_offset_osm()
    speed_limit_offsetted = int(speed_limit + speed_limit_offset)

    if last_speed_limit_sign_tap:
      self.sl_force_active_timer = cur_time

    sl_force_active = speed_limit_control_enabled and (cur_time < self.sl_force_active_timer + 2.0)
    sl_inactive = not sl_force_active and (not speed_limit_control_enabled or (True if self.get_slc_state() == 0 else False))
    sl_temp_inactive = not sl_force_active and (speed_limit_control_enabled and (True if self.get_slc_state() == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active

    # **** ACC Button Controls ********************************************** #

    # FIXME: this entire section is in desperate need of refactoring

    if CS.CP.pcmCruise:
      if frame > self.graMsgStartFramePrev + P.GRA_VBP_STEP:
        if not enabled and CS.out.cruiseState.enabled:
          # Cancel ACC if it's engaged with OP disengaged.
          self.graButtonStatesToSend = BUTTON_STATES.copy()
          self.graButtonStatesToSend["cancel"] = True
        elif enabled and CS.esp_hold_confirmation:
          self.standstill_status = 1
          # Blip the Resume button if we're engaged at standstill.
          # FIXME: This is a naive implementation, improve with visiond or radar input.
          self.graButtonStatesToSend = BUTTON_STATES.copy()
          self.graButtonStatesToSend["resumeCruise"] = True
      if frame > self.graMsgStartFramePrev + P.GRA_VBP_STEP:
        if not (enabled and CS.esp_hold_confirmation) and (enabled and CS.cruise_active):
          cruise_button = self.get_cruise_buttons(CS)
          if cruise_button is not None and self.graMsgSentCount == 0:
            if cruise_button == 1:
              self.graButtonStatesToSend = BUTTON_STATES.copy()
              self.graButtonStatesToSend["accelCruise"] = True
            elif cruise_button == 2:
              self.graButtonStatesToSend = BUTTON_STATES.copy()
              self.graButtonStatesToSend["decelCruise"] = True
            print("self.get_cruise_buttons(CS) = " + str(cruise_button))
            print("SPAMMING")

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

    if CS.out.brakeLights and CS.out.vEgo < 0.1:
      self.standstill_status = 1
      self.standstill_status_timer += 1
      if self.standstill_status_timer > 200:
        self.standstill_status = 1
        self.standstill_status_timer = 0
    if self.standstill_status == 1 and CS.out.vEgo > 1:
      self.standstill_status = 0
      self.standstill_fault_reduce_timer = 0

    return can_sends

  def get_speed_limit_osm(self):
    is_metric = Params().get_bool("IsMetric")
    speed_limit_osm = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) * (CV.MS_TO_MPH if not is_metric else CV.MS_TO_KPH)
    return speed_limit_osm

  def get_speed_limit_offset_osm(self):
    speed_limit_perc_offset = Params().get_bool("SpeedLimitPercOffset")
    speed_limit_value_offset = int(Params().get("SpeedLimitValueOffset"))
    is_metric = Params().get_bool("IsMetric")
    if speed_limit_perc_offset:
      speed_limit_offset = float(self.sm['longitudinalPlan'].speedLimitOffset) * (CV.MS_TO_MPH if not is_metric else CV.MS_TO_KPH)
    else:
      speed_limit_offset = float(speed_limit_value_offset)
    return speed_limit_offset

  def get_slc_state(self):
    self.slc_state = self.sm['longitudinalPlan'].speedLimitControlState
    return self.slc_state

  # multikyd methods, sunnyhaibin logic
  def get_cruise_buttons_status(self, CS):
    if not CS.cruise_active or CS.buttonStates["accelCruise"] or CS.buttonStates["decelCruise"] or CS.buttonStates["setCruise"] or CS.buttonStates["resumeCruise"]:
      self.timer = 80
    elif self.timer:
      self.timer -= 1
    else:
      return 1
    return 0

  def get_target_speed(self, v_cruise_kph_prev):
    speed_limit_perc_offset = Params().get_bool("SpeedLimitPercOffset")
    speed_limit_value_offset = int(Params().get("SpeedLimitValueOffset"))
    is_metric = Params().get_bool("IsMetric")
    v_cruise_kph = v_cruise_kph_prev
    if Params().get_bool("SpeedLimitControl") and (float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) != 0.0):
      target_v_cruise_kph = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) * CV.MS_TO_KPH
      if speed_limit_perc_offset:
        v_cruise_kph = target_v_cruise_kph + float(float(self.sm['longitudinalPlan'].speedLimitOffset) * CV.MS_TO_KPH)
      else:
        v_cruise_kph = target_v_cruise_kph + (float(speed_limit_value_offset * CV.MPH_TO_KPH) if not is_metric else speed_limit_value_offset)
      if not self.slc_active_stock:
        v_cruise_kph = v_cruise_kph_prev

    print('v_cruise_kph={}'.format(v_cruise_kph))
    self.t_interval = 10 if not is_metric else 7
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

  def get_curve_speed(self, target_speed_kph):
    v_cruise_kph_prev = self.sm['controlsState'].vCruise
    if Params().get_bool("TurnVisionControl"):
      vision_v_cruise_kph = float(float(self.sm['longitudinalPlan'].visionTurnSpeed) * CV.MS_TO_KPH)
      if int(vision_v_cruise_kph) == int(v_cruise_kph_prev):
        vision_v_cruise_kph = 255
      vision_v_cruise_kph = min(target_speed_kph, vision_v_cruise_kph)
    else:
      vision_v_cruise_kph = 255
    if Params().get_bool("TurnSpeedControl"):
      map_v_cruise_kph = float(float(self.sm['longitudinalPlan'].turnSpeed) * CV.MS_TO_KPH)
      if int(map_v_cruise_kph) == 0.0:
        map_v_cruise_kph = 255
      map_v_cruise_kph = min(target_speed_kph, map_v_cruise_kph)
    else:
      map_v_cruise_kph = 255
    print('vision_v_cruise_kph={}  map_v_cruise_kph={}'.format(vision_v_cruise_kph, map_v_cruise_kph))
    return min(target_speed_kph, vision_v_cruise_kph, map_v_cruise_kph)

  def get_button_control(self, CS, final_speed):
    is_metric = Params().get_bool("IsMetric")
    v_cruise_kph_max = self.sm['controlsState'].vCruise
    self.init_speed = round(min(final_speed, v_cruise_kph_max) * CV.KPH_TO_MPH) if not is_metric else round(min(final_speed, v_cruise_kph_max))
    self.v_set_dis = round(CS.out.cruiseState.speed * CV.MS_TO_MPH) if not is_metric else round(CS.out.cruiseState.speed * CV.MS_TO_KPH)
    cruise_button = self.get_button_type(self.button_type)
    return cruise_button

  def get_cruise_buttons(self, CS):
    cruise_button = None
    if not self.get_cruise_buttons_status(CS):
      pass
    elif CS.cruise_active:
      v_cruise_kph_prev = self.sm['controlsState'].vCruise
      set_speed_kph = self.get_target_speed(v_cruise_kph_prev)
      if Params().get_bool("SpeedLimitControl"):
        target_speed_kph = set_speed_kph
      else:
        target_speed_kph = min(v_cruise_kph_prev, set_speed_kph)
      if Params().get_bool("TurnVisionControl") or Params().get_bool("TurnSpeedControl"):
        self.final_speed_kph = self.get_curve_speed(target_speed_kph)
      else:
        self.final_speed_kph = target_speed_kph

      print('self.final_speed_kph={}  v_cruise_kph_prev={}'.format(self.final_speed_kph, v_cruise_kph_prev))

      cruise_button = self.get_button_control(CS, self.final_speed_kph) # MPH/KPH based button presses
    return cruise_button