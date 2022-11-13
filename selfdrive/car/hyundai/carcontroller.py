from cereal import car, log
import cereal.messaging as messaging
from common.conversions import Conversions as CV
from common.numpy_fast import clip
from common.params import Params
from common.realtime import DT_CTRL
from opendbc.can.packer import CANPacker
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai import hyundaicanfd, hyundaican
from selfdrive.car.hyundai.values import HyundaiFlags, Buttons, CarControllerParams, CANFD_CAR, CAR

VisualAlert = car.CarControl.HUDControl.VisualAlert
LongCtrlState = car.CarControl.Actuators.LongControlState

# EPS faults if you apply torque while the steering angle is above 90 degrees for more than 1 second
# All slightly below EPS thresholds to avoid fault
MAX_ANGLE = 85
MAX_ANGLE_FRAMES = 89
MAX_ANGLE_CONSECUTIVE_FRAMES = 2


def process_hud_alert(enabled, fingerprint, hud_control):
  sys_warning = (hud_control.visualAlert in (VisualAlert.steerRequired, VisualAlert.ldw))

  # initialize to no line visible
  # TODO: this is not accurate for all cars
  sys_state = 1
  if hud_control.leftLaneVisible and hud_control.rightLaneVisible or sys_warning:  # HUD alert only display when LKAS status is active
    sys_state = 3 if enabled or sys_warning else 4
  elif hud_control.leftLaneVisible:
    sys_state = 5
  elif hud_control.rightLaneVisible:
    sys_state = 6

  # initialize to no warnings
  left_lane_warning = 0
  right_lane_warning = 0
  if hud_control.leftLaneDepart:
    left_lane_warning = 1 if fingerprint in (CAR.GENESIS_G90, CAR.GENESIS_G80) else 2
  if hud_control.rightLaneDepart:
    right_lane_warning = 1 if fingerprint in (CAR.GENESIS_G90, CAR.GENESIS_G80) else 2

  return sys_warning, sys_state, left_lane_warning, right_lane_warning


class CarController:
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    self.params = CarControllerParams(CP)
    self.packer = CANPacker(dbc_name)
    self.angle_limit_counter = 0
    self.frame = 0

    self.accel_last = 0
    self.apply_steer_last = 0
    self.car_fingerprint = CP.carFingerprint
    self.last_button_frame = 0
    self.resume_count = 0

    self.disengage_blink = 0.

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
    self.cruise_button = None
    self.speed_diff = 0

  def update(self, CC, CS):
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

    # steering torque
    steer = actuators.steer
    if self.CP.carFingerprint in (CAR.KONA, CAR.KONA_EV, CAR.KONA_HEV, CAR.KONA_EV_2022):
      # these cars have significantly more torque than most HKG; limit to 70% of max
      steer = clip(steer, -0.7, 0.7)
    new_steer = int(round(steer * self.params.STEER_MAX))
    apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.params)

    if not CC.latActive:
      apply_steer = 0

    self.apply_steer_last = apply_steer

    # accel + longitudinal
    accel = clip(actuators.accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX)
    stopping = actuators.longControlState == LongCtrlState.stopping and CS.out.standstill
    set_speed_in_units = hud_control.setSpeed * (CV.MS_TO_KPH if CS.is_metric else CV.MS_TO_MPH)

    # HUD messages
    sys_warning, sys_state, left_lane_warning, right_lane_warning = process_hud_alert(CC.enabled, self.car_fingerprint,
                                                                                      hud_control)

    cur_time = self.frame * DT_CTRL

    # show LFA "white_wheel" and LKAS "White car + lanes" when disengageFromBrakes
    disengage_from_brakes = CS.madsEnabled and not CC.latActive

    # show LFA "white_wheel" and LKAS "White car + lanes" when belowLaneChangeSpeed and (leftBlinkerOn or rightBlinkerOn)
    below_lane_change_speed = CS.madsEnabled and CS.belowLaneChangeSpeed and\
                              (CS.leftBlinkerOn or CS.rightBlinkerOn)

    if not (disengage_from_brakes or below_lane_change_speed):
      self.disengage_blink = cur_time

    disengage_blinking_icon = (disengage_from_brakes or below_lane_change_speed) and not\
                              ((cur_time - self.disengage_blink) > 1)

    if self.last_speed_limit_sign_tap:
      self.sl_force_active_timer = cur_time

    sl_force_active = self.speed_limit_control_enabled and (cur_time < self.sl_force_active_timer + 2.0)
    sl_inactive = not sl_force_active and (not self.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
    sl_temp_inactive = not sl_force_active and (self.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
    slc_active = not sl_inactive and not sl_temp_inactive

    self.slc_active_stock = slc_active

    if not slc_active:
      self.switching_to_hda_timer = cur_time

    switching_to_hda = slc_active and CS.out.cruiseState.enabled and not ((cur_time - self.switching_to_hda_timer) > 0.5)

    if self.speed_limit_prev == self.speed_limit:
      self.speed_limit_changed_timer = cur_time

    speed_limit_changed = self.speed_limit_prev != self.speed_limit and not ((cur_time - self.speed_limit_changed_timer) > 1)
    if not speed_limit_changed:
      self.speed_limit_prev = self.speed_limit

    enhanced_scc = self.CP.flags & HyundaiFlags.SP_ENHANCED_SCC

    can_sends = []

    # *** common hyundai stuff ***

    # tester present - w/ no response (keeps relevant ECU disabled)
    if self.frame % 100 == 0 and self.CP.openpilotLongitudinalControl:
      addr, bus = 0x00, 0
      if not enhanced_scc:
        addr, bus = 0x7d0, 0
      if self.CP.flags & HyundaiFlags.CANFD_HDA2.value:
        addr, bus = 0x730, 5
      can_sends.append([addr, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", bus])

    # >90 degree steering fault prevention
    # Count up to MAX_ANGLE_FRAMES, at which point we need to cut torque to avoid a steering fault
    if CC.latActive and abs(CS.out.steeringAngleDeg) >= MAX_ANGLE:
      self.angle_limit_counter += 1
    else:
      self.angle_limit_counter = 0

    # Cut steer actuation bit for two frames and hold torque with induced temporary fault
    torque_fault = CC.latActive and self.angle_limit_counter > MAX_ANGLE_FRAMES
    lat_active = CC.latActive and not torque_fault

    if self.angle_limit_counter >= MAX_ANGLE_FRAMES + MAX_ANGLE_CONSECUTIVE_FRAMES:
      self.angle_limit_counter = 0

    # CAN-FD platforms
    if self.CP.carFingerprint in CANFD_CAR:
      hda2 = self.CP.flags & HyundaiFlags.CANFD_HDA2
      hda2_long = hda2 and self.CP.openpilotLongitudinalControl

      # steering control
      can_sends.extend(hyundaicanfd.create_steering_messages(self.packer, self.CP, CC.enabled, lat_active, apply_steer))

      # disable LFA on HDA2
      if self.frame % 5 == 0 and hda2:
        can_sends.append(hyundaicanfd.create_cam_0x2a4(self.packer, CS.cam_0x2a4))

      # LFA and HDA icons
      if self.frame % 5 == 0 and (not hda2 or hda2_long):
        can_sends.append(hyundaicanfd.create_lfahda_cluster(self.packer, self.CP, CC.enabled and CS.out.cruiseState.enabled, CC.latActive, CS.madsEnabled))

      if self.CP.openpilotLongitudinalControl:
        can_sends.extend(hyundaicanfd.create_adrv_messages(self.packer, self.frame))
        if self.frame % 2 == 0:
          can_sends.append(hyundaicanfd.create_acc_control(self.packer, self.CP, CC.enabled and CS.out.cruiseState.enabled, self.accel_last, accel, stopping, CC.cruiseControl.override,
                                                           set_speed_in_units))
          self.accel_last = accel
      else:
        # button presses
        if (self.frame - self.last_button_frame) * DT_CTRL > 0.25:
          # cruise cancel
          if CC.cruiseControl.cancel:
            if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
              can_sends.append(hyundaicanfd.create_acc_cancel(self.packer, self.CP, CS.cruise_info))
              self.last_button_frame = self.frame
            else:
              for _ in range(20):
                can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, CS.buttons_counter+1, Buttons.CANCEL))
              self.last_button_frame = self.frame

          # cruise standstill resume
          elif CC.cruiseControl.resume:
            if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
              # TODO: resume for alt button cars
              pass
            else:
              for _ in range(20):
                can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, CS.buttons_counter+1, Buttons.RES_ACCEL))
              self.last_button_frame = self.frame
        if not CC.cruiseControl.resume and CS.out.cruiseState.enabled and not CS.out.gasPressed and not self.CP.pcmCruiseSpeed:
          self.cruise_button = self.get_cruise_buttons(CS, self.v_cruise_kph_prev)
          if self.cruise_button is not None:
            for _ in range(20):
              can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, CS.buttons_counter+self.resume_count, self.cruise_button))
              self.resume_count += 1
          else:
            self.resume_count = 0
    else:
      can_sends.append(hyundaican.create_lkas11(self.packer, self.frame, self.car_fingerprint, apply_steer, lat_active,
                                                torque_fault, CS.lkas11, sys_warning, sys_state, CC.enabled,
                                                hud_control.leftLaneVisible, hud_control.rightLaneVisible,
                                                left_lane_warning, right_lane_warning,
                                                disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon))

      if not self.CP.openpilotLongitudinalControl:
        if CC.cruiseControl.cancel:
          can_sends.append(hyundaican.create_clu11(self.packer, self.frame, CS.clu11, Buttons.CANCEL, self.CP.carFingerprint))
        elif CC.cruiseControl.resume:
          # send resume at a max freq of 20Hz
          if (self.frame - self.last_button_frame) * DT_CTRL > 0.05:
            # send 25 messages at a time to increases the likelihood of resume being accepted
            can_sends.extend([hyundaican.create_clu11(self.packer, self.resume_count, CS.clu11, Buttons.RES_ACCEL, self.CP.carFingerprint)] * 25)
            self.resume_count += 1
            if self.resume_count > 5:
              self.last_button_frame = self.frame
              self.resume_count = 0
        if not CC.cruiseControl.resume and CS.out.cruiseState.enabled and not CS.out.gasPressed and not self.CP.pcmCruiseSpeed:
          self.cruise_button = self.get_cruise_buttons(CS, self.v_cruise_kph_prev)
          if self.cruise_button is not None:
            can_sends.append(hyundaican.create_clu11(self.packer, self.resume_count, CS.clu11, self.cruise_button, self.CP.carFingerprint))
            self.resume_count += 1
          else:
            self.resume_count = 0

      if self.frame % 2 == 0 and self.CP.openpilotLongitudinalControl:
        tau_gap_set = CS.gap_adjust_cruise_tr
        # TODO: unclear if this is needed
        jerk = 3.0 if actuators.longControlState == LongCtrlState.pid else 1.0
        can_sends.extend(hyundaican.create_acc_commands(self.packer, CC.enabled and CS.out.cruiseState.enabled and CS.mainEnabled, accel, jerk, int(self.frame / 2),
                                                        hud_control.leadVisible, set_speed_in_units, stopping, CC.cruiseControl.override, CS.mainEnabled, enhanced_scc, tau_gap_set, CS))

      # 20 Hz LFA MFA message
      if self.frame % 5 == 0 and self.car_fingerprint in (CAR.SONATA, CAR.PALISADE, CAR.IONIQ, CAR.KIA_NIRO_EV, CAR.KIA_NIRO_HEV_2021,
                                                          CAR.IONIQ_EV_2020, CAR.IONIQ_PHEV, CAR.KIA_CEED, CAR.KIA_SELTOS, CAR.KONA_EV, CAR.KONA_EV_2022,
                                                          CAR.ELANTRA_2021, CAR.ELANTRA_HEV_2021, CAR.SONATA_HYBRID, CAR.KONA_HEV, CAR.SANTA_FE_2022,
                                                          CAR.KIA_K5_2021, CAR.IONIQ_HEV_2022, CAR.SANTA_FE_HEV_2022, CAR.GENESIS_G70_2020, CAR.SANTA_FE_PHEV_2022, CAR.ELANTRA_2022_NON_SCC):
        can_sends.append(hyundaican.create_lfahda_mfc(self.packer, CC.latActive, disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon, slc_active, round(self.speed_limit * CV.MS_TO_KPH), speed_limit_changed, switching_to_hda))

      # 5 Hz ACC options
      if self.frame % 20 == 0 and self.CP.openpilotLongitudinalControl:
        can_sends.extend(hyundaican.create_acc_opt(self.packer, enhanced_scc))

      # 2 Hz front radar options
      if self.frame % 50 == 0 and self.CP.openpilotLongitudinalControl and not enhanced_scc:
        can_sends.append(hyundaican.create_frt_radar_opt(self.packer))

    new_actuators = actuators.copy()
    new_actuators.steer = apply_steer / self.params.STEER_MAX
    new_actuators.accel = accel

    self.frame += 1
    return new_actuators, can_sends

  def get_speed_limit(self):
    self.speed_limit = float(self.sm['longitudinalPlan'].speedLimit if self.sm['longitudinalPlan'].speedLimit is not None else 0.0)
    return self.speed_limit

  # multikyd methods, sunnyhaibin logic
  def get_cruise_buttons_status(self, CS):
    if not CS.out.cruiseState.enabled or CS.cruise_buttons[-1] != Buttons.NONE:
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
    self.speed_diff = round(self.target_speed - self.v_set_dis)
    if self.speed_diff > 0:
      self.button_type = 1
    elif self.speed_diff < 0:
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
