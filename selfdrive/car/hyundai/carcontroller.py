from cereal import car, log
from common.realtime import DT_CTRL
from common.numpy_fast import clip
from common.conversions import Conversions as CV
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai.hyundaican import create_lkas11, create_clu11, create_lfahda_mfc, create_acc_commands, create_acc_opt, create_frt_radar_opt
from selfdrive.car.hyundai.values import Buttons, CarControllerParams, CAR
from opendbc.can.packer import CANPacker
from common.params import Params
import cereal.messaging as messaging

VisualAlert = car.CarControl.HUDControl.VisualAlert
LongCtrlState = car.CarControl.Actuators.LongControlState
SpeedLimitControlState = log.LongitudinalPlan.SpeedLimitControlState

STEER_FAULT_MAX_ANGLE = 85  # EPS max is 90
STEER_FAULT_MAX_FRAMES = 90  # EPS counter is 95


def process_hud_alert(enabled, fingerprint, hud_control):
  sys_warning = (hud_control.visualAlert in (VisualAlert.steerRequired, VisualAlert.ldw))

  # initialize to no line visible
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
    self.cut_steer_frames = 0
    self.cut_steer = False
    self.frame = 0

    self.apply_steer_last = 0
    self.car_fingerprint = CP.carFingerprint
    self.steer_rate_limited = False
    self.last_resume_frame = 0
    self.accel = 0

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
    self.switching_to_hda_timer = 0.
    self.speed_limit_changed_timer = 0
    self.speed_limit_prev = 0.
    self.slc_active_stock = False

  def update(self, CC, CS):
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

    actuators = CC.actuators
    hud_control = CC.hudControl
    pcm_cancel_cmd = CC.cruiseControl.cancel

    # Steering Torque
    new_steer = int(round(actuators.steer * self.params.STEER_MAX))
    apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.params)
    self.steer_rate_limited = new_steer != apply_steer

    cur_time = self.frame * DT_CTRL
    if CS.leftBlinkerOn or CS.rightBlinkerOn:
      self.signal_last = cur_time

    lat_active = CC.latActive and (not CS.belowLaneChangeSpeed or
                   (not ((cur_time - self.signal_last) < 1.0) and not (CS.leftBlinkerOn or CS.rightBlinkerOn)))

    if not lat_active:
      apply_steer = 0

    self.apply_steer_last = apply_steer

    sys_warning, sys_state, left_lane_warning, right_lane_warning = process_hud_alert(CC.enabled, self.car_fingerprint,
                                                                                      hud_control)

    # show LFA "white_wheel" and LKAS "White car + lanes" when disengageFromBrakes
    disengage_from_brakes = CS.madsEnabled and not lat_active

    # show LFA "white_wheel" and LKAS "White car + lanes" when belowLaneChangeSpeed
    # and (leftBlinkerOn or rightBlinkerOn)
    below_lane_change_speed = CS.madsEnabled and CS.belowLaneChangeSpeed and\
                              (CS.leftBlinkerOn or CS.rightBlinkerOn)

    if not (disengage_from_brakes or below_lane_change_speed):
      self.disengage_blink = cur_time

    disengage_blinking_icon = (disengage_from_brakes or below_lane_change_speed) and not\
                              ((cur_time - self.disengage_blink) > 1)

    escc = self.CP.enhancedScc

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

    can_sends = []

    # tester present - w/ no response (keeps radar disabled)
    if self.CP.openpilotLongitudinalControl and not escc:
      if self.frame % 100 == 0:
        can_sends.append([0x7D0, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", 0])

    if lat_active and abs(CS.out.steeringAngleDeg) > STEER_FAULT_MAX_ANGLE:
      self.angle_limit_counter += 1
    else:
      self.angle_limit_counter = 0

    # stop requesting torque to avoid 90 degree fault and hold torque with induced temporary fault
    # two cycles avoids race conditions every few minutes
    if self.angle_limit_counter > STEER_FAULT_MAX_FRAMES:
      self.cut_steer = True
    elif self.cut_steer_frames > 1:
      self.cut_steer_frames = 0
      self.cut_steer = False

    cut_steer_temp = False
    if self.cut_steer:
      cut_steer_temp = True
      self.angle_limit_counter = 0
      self.cut_steer_frames += 1

    can_sends.append(create_lkas11(self.packer, self.frame, self.car_fingerprint, apply_steer, lat_active,
                                   cut_steer_temp, CS.lkas11, sys_warning, sys_state, lat_active,
                                   hud_control.leftLaneVisible, hud_control.rightLaneVisible,
                                   left_lane_warning, right_lane_warning,
                                   disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon))

    if not self.CP.openpilotLongitudinalControl:
      if pcm_cancel_cmd:
        can_sends.append(create_clu11(self.packer, self.frame, CS.clu11, Buttons.CANCEL))
      elif CS.out.cruiseState.standstill:
        self.standstill_status = 1
        # send resume at a max freq of 10Hz
        if (self.frame - self.last_resume_frame) * DT_CTRL > 0.1:
          # send 25 messages at a time to increases the likelihood of resume being accepted
          can_sends.extend([create_clu11(self.packer, self.frame, CS.clu11, Buttons.RES_ACCEL)] * 25)
          self.last_resume_frame = self.frame
      if not CS.out.cruiseState.standstill and CS.out.cruiseState.enabled and not CS.out.gasPressed:
        cruise_button = self.get_cruise_buttons(CS, self.v_cruise_kph_prev)
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

    if self.frame % 2 == 0 and self.CP.openpilotLongitudinalControl:
      tau_gap_set = CS.gap_adjust_cruise_tr
      pid_control = (actuators.longControlState == LongCtrlState.pid)
      stopping = (actuators.longControlState == LongCtrlState.stopping)
      accel = actuators.accel
      # TODO: aEgo lags when jerk is high, use smoothed ACCEL_REF_ACC instead?
      accel_error = accel - CS.out.aEgo if CC.longActive else 0
      # TODO: jerk upper would probably be better from longitudinal planner desired jerk?
      jerk_upper = clip(2.0 * accel_error, 0.0, 2.0) # zero when error is negative to keep decel control tight
      jerk_lower = 12.7 # always max value to keep decel control tight

      if CC.longActive:
        if pid_control and CS.out.standstill and CS.brake_control_active and accel > 0.0:
          # brake controller needs to wind up internally until it reaches a threshold where the brakes release
          # larger values cause faster windup (too small and you never start moving)
          # larger values get vehicle moving quicker but can cause sharp negative jerk transitioning back to plan
          # larger values also cause more overshoot and therefore it takes longer to stop once moving
          accel = 1.0
          jerk_upper = 1.0

      accel = clip(accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX)

      set_speed_in_units = hud_control.setSpeed * (CV.MS_TO_MPH if CS.clu11["CF_Clu_SPEED_UNIT"] == 1 else CV.MS_TO_KPH)
      can_sends.extend(create_acc_commands(self.packer, CC.enabled and CS.out.cruiseState.enabled and CS.mainEnabled, accel, jerk_upper, jerk_lower, int(self.frame / 2), hud_control.leadVisible,
                                           set_speed_in_units, stopping, CS.out.gasPressed, CS.mainEnabled, tau_gap_set, escc))
      self.accel = accel

    # 20 Hz LFA MFA message
    if self.frame % 5 == 0 and self.car_fingerprint in (CAR.SONATA, CAR.PALISADE, CAR.IONIQ, CAR.KIA_NIRO_EV, CAR.KIA_NIRO_HEV_2021,
                                                        CAR.IONIQ_EV_2020, CAR.IONIQ_PHEV, CAR.KIA_CEED, CAR.KIA_SELTOS, CAR.KONA_EV,
                                                        CAR.ELANTRA_2021, CAR.ELANTRA_HEV_2021, CAR.SONATA_HYBRID, CAR.KONA_HEV, CAR.SANTA_FE_2022,
                                                        CAR.KIA_K5_2021, CAR.IONIQ_HEV_2022, CAR.SANTA_FE_HEV_2022, CAR.GENESIS_G70_2020, CAR.SANTA_FE_PHEV_2022):
      can_sends.append(create_lfahda_mfc(self.packer, CS.out.cruiseState.enabled, lat_active, disengage_from_brakes, below_lane_change_speed, disengage_blinking_icon,
                                         slc_active, round(self.speed_limit * CV.MS_TO_KPH), speed_limit_changed, switching_to_hda))

    self.lat_active = lat_active

    # 5 Hz ACC options
    if self.frame % 20 == 0 and self.CP.openpilotLongitudinalControl:
      can_sends.extend(create_acc_opt(self.packer, escc))

    # 2 Hz front radar options
    if self.frame % 50 == 0 and self.CP.openpilotLongitudinalControl:
      can_sends.append(create_frt_radar_opt(self.packer))

    new_actuators = actuators.copy()
    new_actuators.steer = apply_steer / self.params.STEER_MAX
    new_actuators.accel = self.accel

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
