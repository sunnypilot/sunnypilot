from cereal import car, log
from common.realtime import DT_CTRL
from common.numpy_fast import clip, interp
from selfdrive.config import Conversions as CV
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai.hyundaican import create_lkas11, create_clu11, create_lfahda_mfc, create_acc_commands, create_acc_opt, create_frt_radar_opt
from selfdrive.car.hyundai.values import Buttons, CarControllerParams, CAR
from opendbc.can.packer import CANPacker
from common.params import Params
import cereal.messaging as messaging
from random import randint
from selfdrive.controls.lib.speed_limit_controller import SpeedLimitController

VisualAlert = car.CarControl.HUDControl.VisualAlert
LongCtrlState = car.CarControl.Actuators.LongControlState
SpeedLimitControlState = log.LongitudinalPlan.SpeedLimitControlState


def process_hud_alert(enabled, fingerprint, visual_alert, left_lane,
                      right_lane, left_lane_depart, right_lane_depart):
  sys_warning = (visual_alert in [VisualAlert.steerRequired, VisualAlert.ldw])

  # initialize to no line visible
  sys_state = 1
  if left_lane and right_lane or sys_warning:  # HUD alert only display when LKAS status is active
    sys_state = 3 if enabled or sys_warning else 4
  elif left_lane:
    sys_state = 5
  elif right_lane:
    sys_state = 6

  # initialize to no warnings
  left_lane_warning = 0
  right_lane_warning = 0
  if left_lane_depart:
    left_lane_warning = 1 if fingerprint in [CAR.GENESIS_G90, CAR.GENESIS_G80] else 2
  if right_lane_depart:
    right_lane_warning = 1 if fingerprint in [CAR.GENESIS_G90, CAR.GENESIS_G80] else 2

  return sys_warning, sys_state, left_lane_warning, right_lane_warning


class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.p = CarControllerParams(CP)
    self.packer = CANPacker(dbc_name)

    self.sm = messaging.SubMaster(['liveMapData', 'controlsState', 'longitudinalPlan'])

    self.signal_last = 0.
    self.disengage_blink = 0.
    self.apply_steer_last = 0
    self.car_fingerprint = CP.carFingerprint
    self.steer_rate_limited = False
    self.last_resume_frame = 0
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
    self.switching_to_hda_timer = 0.
    self.speed_limit_changed_timer = 0
    self.speed_limit_prev = 0.
    self.slc_active_stock = False
    self.last_lead_distance = 0

  def update(self, enabled, CS, frame, actuators, pcm_cancel_cmd, visual_alert, hud_speed,
             left_lane, right_lane, left_lane_depart, right_lane_depart, lead_visible):
    # Steering Torque
    new_steer = int(round(actuators.steer * self.p.STEER_MAX))
    apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.p)
    self.steer_rate_limited = new_steer != apply_steer

    cur_time = frame * DT_CTRL
    if CS.leftBlinkerOn or CS.rightBlinkerOn:
      self.signal_last = cur_time

    # disable when temp fault is active, or below LKA minimum speed
    lkas_active = enabled and not CS.out.steerWarning and CS.out.vEgo >= CS.CP.minSteerSpeed and\
                  (CS.lfaEnabled or CS.accMainEnabled) and ((CS.automaticLaneChange and not CS.belowLaneChangeSpeed) or
                  ((not ((cur_time - self.signal_last) < 1) or not CS.belowLaneChangeSpeed) and not
                  (CS.leftBlinkerOn or CS.rightBlinkerOn)))

    if not lkas_active:
      apply_steer = 0

    self.apply_steer_last = apply_steer

    sys_warning, sys_state, left_lane_warning, right_lane_warning = \
      process_hud_alert(enabled, self.car_fingerprint, visual_alert,
                        left_lane, right_lane, left_lane_depart, right_lane_depart)

    can_sends = []

    # show LFA "white_wheel" and LKAS "White car + lanes" when disengageFromBrakes
    disengage_from_brakes = (CS.lfaEnabled or CS.accMainEnabled) and not lkas_active

    # show LFA "white_wheel" and LKAS "White car + lanes" when belowLaneChangeSpeed and (leftBlinkerOn or rightBlinkerOn)
    below_lane_change_speed = (CS.lfaEnabled or CS.accMainEnabled) and CS.belowLaneChangeSpeed and\
                              (CS.leftBlinkerOn or CS.rightBlinkerOn)

    if not (disengage_from_brakes or below_lane_change_speed):
      self.disengage_blink = cur_time

    disengage_blinking_icon = (disengage_from_brakes or below_lane_change_speed) and not\
                              ((cur_time - self.disengage_blink) > 1)

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

    if not slc_active:
      self.switching_to_hda_timer = cur_time

    switching_to_hda = slc_active and CS.out.cruiseState.enabled and not ((cur_time - self.switching_to_hda_timer) > 0.5)

    if self.speed_limit_prev == speed_limit:
      self.speed_limit_changed_timer = cur_time

    speed_limit_changed = self.speed_limit_prev != speed_limit and not ((cur_time - self.speed_limit_changed_timer) > 1)
    if not speed_limit_changed:
      self.speed_limit_prev = speed_limit


    # tester present - w/ no response (keeps radar disabled)
    if CS.CP.openpilotLongitudinalControl:
      if (frame % 100) == 0:
        can_sends.append([0x7D0, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", 0])

    can_sends.append(create_lkas11(self.packer, frame, self.car_fingerprint, apply_steer, lkas_active,
                                   CS.lkas11, sys_warning, sys_state, enabled,
                                   lkas_active, disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon,
                                   left_lane, right_lane,
                                   left_lane_warning, right_lane_warning))

    if not CS.CP.openpilotLongitudinalControl:
      if pcm_cancel_cmd:
        can_sends.append(create_clu11(self.packer, frame, CS.clu11, Buttons.CANCEL))
      elif CS.out.cruiseState.standstill:
        self.standstill_status = 1
        if Params().get_bool("StockResumeAlt"):
          if self.last_lead_distance == 0:
            self.last_lead_distance = CS.lead_distance
            self.resume_count = 0
          elif CS.lead_distance != self.last_lead_distance and (frame - self.last_resume_frame) > 5:
            can_sends.append(create_clu11(self.packer, self.resume_count, CS.clu11, Buttons.RES_ACCEL))
            self.resume_count += 1
            if self.resume_count > 5:
              self.last_resume_frame = frame
              self.resume_count = 0
        else:
          # send resume at a max freq of 10Hz
          if (frame - self.last_resume_frame) * DT_CTRL > 0.1:
            # send 25 messages at a time to increases the likelihood of resume being accepted
            can_sends.extend([create_clu11(self.packer, frame, CS.clu11, Buttons.RES_ACCEL)] * 25)
            self.last_resume_frame = frame
      elif self.last_lead_distance != 0:
        self.last_lead_distance = 0
      if not CS.out.cruiseState.standstill and (enabled and CS.acc_active):
        cruise_button = self.get_cruise_buttons(CS)
        if cruise_button is not None:
          can_sends.append(create_clu11(self.packer, self.resume_count, CS.clu11, cruise_button))
          self.resume_count += 1
        else:
          self.resume_count = 0

    if CS.out.brakeLights and CS.out.vEgo < 0.1:
      self.standstill_status = 1
      self.standstill_status_timer += 1
      if self.standstill_status_timer > 200:
        self.standstill_status = 1
        self.standstill_status_timer = 0
    if self.standstill_status == 1 and CS.out.vEgo > 1:
      self.standstill_status = 0
      self.standstill_fault_reduce_timer = 0

    zero_vego = True if CS.out.vEgo < 0.1 and (CS.lfaEnabled or CS.accMainEnabled) else False

    if frame % 2 == 0 and CS.CP.openpilotLongitudinalControl:
      accel = actuators.accel if enabled and CS.out.cruiseState.enabled else 0

      jerk = clip(2.0 * (accel - CS.out.aEgo), -12.7, 12.7)

      if accel < 0:
        accel = interp(accel - CS.out.aEgo, [-1.0, -0.5], [2 * accel, accel])

      accel = clip(accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX)

      stopping = (actuators.longControlState == LongCtrlState.stopping)
      set_speed_in_units = hud_speed * (CV.MS_TO_MPH if CS.clu11["CF_Clu_SPEED_UNIT"] == 1 else CV.MS_TO_KPH)
      can_sends.extend(create_acc_commands(self.packer, enabled and CS.out.cruiseState.enabled, accel, jerk, int(frame / 2), lead_visible, set_speed_in_units, stopping))

    # 20 Hz LFA MFA message
    if frame % 5 == 0 and self.car_fingerprint in [CAR.SONATA, CAR.PALISADE, CAR.IONIQ, CAR.KIA_NIRO_EV, CAR.KIA_NIRO_HEV_2021,
                                                   CAR.IONIQ_EV_2020, CAR.IONIQ_PHEV, CAR.KIA_CEED, CAR.KIA_SELTOS, CAR.KONA_EV,
                                                   CAR.ELANTRA_2021, CAR.ELANTRA_HEV_2021, CAR.SONATA_HYBRID, CAR.KONA_HEV, CAR.SANTA_FE_2022,
                                                   CAR.KIA_K5_2021, CAR.IONIQ_HEV_2022, CAR.SANTA_FE_HEV_2022, CAR.GENESIS_G70_2020]:
      can_sends.append(create_lfahda_mfc(self.packer, enabled, lkas_active, disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon, slc_active, speed_limit, speed_limit_changed, switching_to_hda, zero_vego))

    # 5 Hz ACC options
    if frame % 20 == 0 and CS.CP.openpilotLongitudinalControl:
      can_sends.extend(create_acc_opt(self.packer))

    # 2 Hz front radar options
    if frame % 50 == 0 and CS.CP.openpilotLongitudinalControl:
      can_sends.append(create_frt_radar_opt(self.packer))

    return can_sends

  def get_speed_limit_osm(self):
    is_metric = Params().get_bool("IsMetric")
    self.sm.update(0)
    speed_limit_osm = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) * (CV.MS_TO_MPH if not is_metric else CV.MS_TO_KPH)
    return speed_limit_osm

  def get_speed_limit_offset_osm(self):
    speed_limit_perc_offset = Params().get_bool("SpeedLimitPercOffset")
    speed_limit_value_offset = int(Params().get("SpeedLimitValueOffset"))
    is_metric = Params().get_bool("IsMetric")
    if speed_limit_perc_offset:
      self.sm.update(0)
      speed_limit_offset = float(self.sm['longitudinalPlan'].speedLimitOffset) * (CV.MS_TO_MPH if not is_metric else CV.MS_TO_KPH)
    else:
      speed_limit_offset = float(speed_limit_value_offset)
    return speed_limit_offset

  def get_slc_state(self):
    self.sm.update(0)
    self.slc_state = self.sm['longitudinalPlan'].speedLimitControlState
    return self.slc_state

  # multikyd methods, sunnyhaibin logic
  def get_cruise_buttons_status(self, CS):
    if not CS.cruise_active or CS.cruise_buttons != Buttons.NONE:
      self.timer = 40
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
    self.sm.update(0)
    if Params().get_bool("SpeedLimitControl") and (float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) != 0.0):
      self.sm.update(0)
      target_v_cruise_kph = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0) * CV.MS_TO_KPH
      if speed_limit_perc_offset:
        self.sm.update(0)
        v_cruise_kph = target_v_cruise_kph + float(float(self.sm['longitudinalPlan'].speedLimitOffset) * CV.MS_TO_KPH)
      else:
        v_cruise_kph = target_v_cruise_kph + (float(speed_limit_value_offset * CV.MPH_TO_KPH) if not is_metric else speed_limit_value_offset)
      if not self.slc_active_stock:
        v_cruise_kph = v_cruise_kph_prev

    print('v_cruise_kph={}'.format(v_cruise_kph))

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
    cruise_button = Buttons.RES_ACCEL
    self.button_count += 1
    if self.target_speed == self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 5:
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_2(self):
    cruise_button = Buttons.SET_DECEL
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
      self.sm.update(0)
      vision_v_cruise_kph = float(float(self.sm['longitudinalPlan'].visionTurnSpeed) * CV.MS_TO_KPH)
      if int(vision_v_cruise_kph) == int(v_cruise_kph_prev):
        vision_v_cruise_kph = 255
      vision_v_cruise_kph = min(target_speed_kph, vision_v_cruise_kph)
    else:
      vision_v_cruise_kph = 255
    if Params().get_bool("TurnSpeedControl"):
      self.sm.update(0)
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
    self.sm.update(0)
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
      self.sm.update(0)
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