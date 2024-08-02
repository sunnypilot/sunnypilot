from cereal import car
import cereal.messaging as messaging
from openpilot.common.conversions import Conversions as CV
from openpilot.common.numpy_fast import clip
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car import apply_driver_steer_torque_limits, common_fault_avoidance
from openpilot.selfdrive.car.hyundai import hyundaicanfd, hyundaican
from openpilot.selfdrive.car.hyundai.hyundaicanfd import CanBus
from openpilot.selfdrive.car.hyundai.values import HyundaiFlags, HyundaiFlagsSP, Buttons, CarControllerParams, CANFD_CAR, CAR, CAMERA_SCC_CAR, LEGACY_SAFETY_MODE_CAR
from openpilot.selfdrive.car.interfaces import CarControllerBase
from openpilot.selfdrive.controls.lib.drive_helpers import HYUNDAI_V_CRUISE_MIN

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


class CarController(CarControllerBase):
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    self.CAN = CanBus(CP)
    self.params = CarControllerParams(CP)
    self.packer = CANPacker(dbc_name)
    self.angle_limit_counter = 0
    self.frame = 0

    self.accel_last = 0
    self.apply_steer_last = 0
    self.car_fingerprint = CP.carFingerprint
    self.last_button_frame = 0

    self.disengage_blink = 0.
    self.lat_disengage_init = False
    self.lat_active_last = False

    sub_services = ['longitudinalPlanSP']
    if CP.openpilotLongitudinalControl:
      sub_services.append('radarState')
    # TODO: Always true, prep for future conditional refactoring
    if sub_services:
      self.sm = messaging.SubMaster(sub_services)

    self.param_s = Params()
    self.is_metric = self.param_s.get_bool("IsMetric")
    self.speed_limit_control_enabled = False
    self.last_speed_limit_sign_tap = False
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
    self.hkg_can_smooth_stop = self.param_s.get_bool("HkgSmoothStop")
    self.lead_distance = 0

  def calculate_lead_distance(self, hud_control: car.CarControl.HUDControl) -> float:
    lead_one = self.sm["radarState"].leadOne
    lead_two = self.sm["radarState"].leadTwo

    if lead_one.status and (not lead_two.status or lead_one.dRel < lead_two.dRel):
      return lead_one.dRel
    if lead_two.status:
      return lead_two.dRel

    return 19 if hud_control.leadVisible else 0

  def update(self, CC, CS, now_nanos):
    if not self.CP.pcmCruiseSpeed or (self.CP.openpilotLongitudinalControl and self.frame % 5 == 0):
      self.sm.update(0)

    if not self.CP.pcmCruiseSpeed:
      if self.sm.updated['longitudinalPlanSP']:
        self.v_tsc_state = self.sm['longitudinalPlanSP'].visionTurnControllerState
        self.slc_state = self.sm['longitudinalPlanSP'].speedLimitControlState
        self.m_tsc_state = self.sm['longitudinalPlanSP'].turnSpeedControlState
        self.speed_limit = self.sm['longitudinalPlanSP'].speedLimit
        self.speed_limit_offset = self.sm['longitudinalPlanSP'].speedLimitOffset
        self.v_tsc = self.sm['longitudinalPlanSP'].visionTurnSpeed
        self.m_tsc = self.sm['longitudinalPlanSP'].turnSpeed

      if self.frame % 200 == 0:
        self.speed_limit_control_enabled = self.param_s.get_bool("EnableSlc")
        self.is_metric = self.param_s.get_bool("IsMetric")
      self.last_speed_limit_sign_tap = self.param_s.get_bool("LastSpeedLimitSignTap")
      self.v_cruise_min = HYUNDAI_V_CRUISE_MIN[self.is_metric] * (CV.KPH_TO_MPH if not self.is_metric else 1)

    actuators = CC.actuators
    hud_control = CC.hudControl

    # steering torque
    new_steer = int(round(actuators.steer * self.params.STEER_MAX))
    apply_steer = apply_driver_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque, self.params)

    # >90 degree steering fault prevention
    self.angle_limit_counter, apply_steer_req = common_fault_avoidance(abs(CS.out.steeringAngleDeg) >= MAX_ANGLE, CC.latActive,
                                                                       self.angle_limit_counter, MAX_ANGLE_FRAMES,
                                                                       MAX_ANGLE_CONSECUTIVE_FRAMES)

    if not CC.latActive:
      apply_steer = 0

    # Hold torque with induced temporary fault when cutting the actuation bit
    torque_fault = CC.latActive and not apply_steer_req

    self.apply_steer_last = apply_steer

    # accel + longitudinal
    accel = clip(actuators.accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX)
    stopping = actuators.longControlState == LongCtrlState.stopping
    set_speed_in_units = hud_control.setSpeed * (CV.MS_TO_KPH if CS.is_metric else CV.MS_TO_MPH)

    # HUD messages
    sys_warning, sys_state, left_lane_warning, right_lane_warning = process_hud_alert(CC.enabled, self.car_fingerprint,
                                                                                      hud_control)

    # show LFA "white_wheel" and LKAS "White car + lanes" when not CC.latActive
    lateral_paused = CS.madsEnabled and not CC.latActive
    if CC.latActive:
      self.lat_disengage_init = False
    elif self.lat_active_last:
      self.lat_disengage_init = True

    if not self.lat_disengage_init:
      self.disengage_blink = self.frame

    blinking_icon = (self.frame - self.disengage_blink) * DT_CTRL < 1.0 if self.lat_disengage_init else False

    if not self.CP.pcmCruiseSpeed:
      if not self.last_speed_limit_sign_tap_prev and self.last_speed_limit_sign_tap:
        self.sl_force_active_timer = self.frame
        self.param_s.put_bool_nonblocking("LastSpeedLimitSignTap", False)
      self.last_speed_limit_sign_tap_prev = self.last_speed_limit_sign_tap

      sl_force_active = self.speed_limit_control_enabled and (self.frame < (self.sl_force_active_timer * DT_CTRL + 2.0))
      sl_inactive = not sl_force_active and (not self.speed_limit_control_enabled or (True if self.slc_state == 0 else False))
      sl_temp_inactive = not sl_force_active and (self.speed_limit_control_enabled and (True if self.slc_state == 1 else False))
      slc_active = not sl_inactive and not sl_temp_inactive

      self.slc_active_stock = slc_active

    self.lat_active_last = CC.latActive

    escc = self.CP.spFlags & HyundaiFlagsSP.SP_ENHANCED_SCC.value

    can_sends = []

    # *** common hyundai stuff ***

    # tester present - w/ no response (keeps relevant ECU disabled)
    if self.frame % 100 == 0 and not ((self.CP.flags & HyundaiFlags.CANFD_CAMERA_SCC.value) or escc) and \
      self.CP.carFingerprint not in CAMERA_SCC_CAR and self.CP.openpilotLongitudinalControl:
      # for longitudinal control, either radar or ADAS driving ECU
      addr, bus = 0x7d0, 0
      if self.CP.flags & HyundaiFlags.CANFD_HDA2.value:
        addr, bus = 0x730, self.CAN.ECAN
      can_sends.append([addr, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", bus])

      # for blinkers
      if self.CP.flags & HyundaiFlags.ENABLE_BLINKERS:
        can_sends.append([0x7b1, 0, b"\x02\x3E\x80\x00\x00\x00\x00\x00", self.CAN.ECAN])

    # CAN-FD platforms
    if self.CP.carFingerprint in CANFD_CAR:
      hda2 = self.CP.flags & HyundaiFlags.CANFD_HDA2
      hda2_long = hda2 and self.CP.openpilotLongitudinalControl

      # steering control
      can_sends.extend(hyundaicanfd.create_steering_messages(self.packer, self.CP, self.CAN, CC.enabled, apply_steer_req, apply_steer,
                                                             lateral_paused, blinking_icon))

      # prevent LFA from activating on HDA2 by sending "no lane lines detected" to ADAS ECU
      if self.frame % 5 == 0 and hda2:
        can_sends.append(hyundaicanfd.create_suppress_lfa(self.packer, self.CAN, CS.hda2_lfa_block_msg,
                                                          self.CP.flags & HyundaiFlags.CANFD_HDA2_ALT_STEERING))

      # LFA and HDA icons
      if self.frame % 5 == 0 and (not hda2 or hda2_long):
        can_sends.append(hyundaicanfd.create_lfahda_cluster(self.packer, self.CAN, CC.enabled and CS.out.cruiseState.enabled, CC.latActive,
                                                            lateral_paused, blinking_icon))

      # blinkers
      if hda2 and self.CP.flags & HyundaiFlags.ENABLE_BLINKERS:
        can_sends.extend(hyundaicanfd.create_spas_messages(self.packer, self.CAN, self.frame, CC.leftBlinker, CC.rightBlinker))

      if self.CP.openpilotLongitudinalControl:
        if hda2:
          can_sends.extend(hyundaicanfd.create_adrv_messages(self.packer, self.CAN, self.frame))
        if self.frame % 2 == 0:
          can_sends.append(hyundaicanfd.create_acc_control(self.packer, self.CAN, CC.enabled and CS.out.cruiseState.enabled, self.accel_last, accel, stopping, CC.cruiseControl.override,
                                                           set_speed_in_units, hud_control))
          self.accel_last = accel
      else:
        # button presses
        can_sends.extend(self.create_button_messages(CC, CS, use_clu11=False))
        if not (CC.cruiseControl.cancel or CC.cruiseControl.resume) and CS.out.cruiseState.enabled and not self.CP.pcmCruiseSpeed:
          if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
            # TODO: resume for alt button cars
            pass
          else:
            self.cruise_button = self.get_cruise_buttons(CS, CC.vCruise)
            if self.cruise_button is not None:
              if self.frame % 2 == 0:
                can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, self.CAN, ((self.frame // 2) + 1) % 0x10, self.cruise_button))
    else:
      can_sends.append(hyundaican.create_lkas11(self.packer, self.frame, self.CP, apply_steer, apply_steer_req,
                                                torque_fault, CS.lkas11, sys_warning, sys_state, CC.enabled,
                                                hud_control.leftLaneVisible, hud_control.rightLaneVisible,
                                                left_lane_warning, right_lane_warning,
                                                lateral_paused, blinking_icon))

      if not self.CP.openpilotLongitudinalControl:
        can_sends.extend(self.create_button_messages(CC, CS, use_clu11=True))
        if not (CC.cruiseControl.cancel or CC.cruiseControl.resume) and CS.out.cruiseState.enabled and not self.CP.pcmCruiseSpeed:
          self.cruise_button = self.get_cruise_buttons(CS, CC.vCruise)
          if self.cruise_button is not None:
            if self.CP.carFingerprint in LEGACY_SAFETY_MODE_CAR:
              send_freq = 1
              if not (self.v_tsc_state != 0 or self.m_tsc_state > 1) and abs(self.target_speed - self.v_set_dis) <= 2:
                send_freq = 5
              # send resume at a max freq of 10Hz
              if (self.frame - self.last_button_frame) * DT_CTRL > 0.1 * send_freq:
                # send 25 messages at a time to increases the likelihood of cruise buttons being accepted
                can_sends.extend([hyundaican.create_clu11(self.packer, self.frame, CS.clu11, self.cruise_button, self.CP)] * 25)
                if (self.frame - self.last_button_frame) * DT_CTRL >= 0.15 * send_freq:
                  self.last_button_frame = self.frame
            elif self.frame % 2 == 0:
              can_sends.extend([hyundaican.create_clu11(self.packer, (self.frame // 2) + 1, CS.clu11, self.cruise_button, self.CP)] * 25)

      # Parse lead distance from radarState and display the corresponding distance in the car's cluster
      if self.CP.openpilotLongitudinalControl and self.sm.updated['radarState'] and self.frame % 5 == 0:
        self.lead_distance = self.calculate_lead_distance(hud_control)

      if self.frame % 2 == 0 and self.CP.openpilotLongitudinalControl:
        if self.hkg_can_smooth_stop:
          stopping = stopping and CS.out.vEgoRaw < 0.05

        # TODO: unclear if this is needed
        jerk = 3.0 if actuators.longControlState == LongCtrlState.pid else 1.0
        use_fca = self.CP.flags & HyundaiFlags.USE_FCA.value
        can_sends.extend(hyundaican.create_acc_commands(self.packer, CC.enabled and CS.out.cruiseState.enabled, accel, jerk, int(self.frame / 2),
                                                        hud_control, set_speed_in_units, stopping,
                                                        CC.cruiseControl.override, use_fca, CS, escc, self.CP, self.lead_distance))

      # 20 Hz LFA MFA message
      if self.frame % 5 == 0 and self.CP.flags & HyundaiFlags.SEND_LFA.value:
        can_sends.append(hyundaican.create_lfahda_mfc(self.packer, CC.enabled, CC.latActive, lateral_paused, blinking_icon))

      # 5 Hz ACC options
      if self.frame % 20 == 0 and self.CP.openpilotLongitudinalControl:
        can_sends.extend(hyundaican.create_acc_opt(self.packer, escc, CS, self.CP))

      # 2 Hz front radar options
      if self.frame % 50 == 0 and self.CP.openpilotLongitudinalControl and not escc:
        can_sends.append(hyundaican.create_frt_radar_opt(self.packer))

    new_actuators = actuators.as_builder()
    new_actuators.steer = apply_steer / self.params.STEER_MAX
    new_actuators.steerOutputCan = apply_steer
    new_actuators.accel = accel

    self.frame += 1
    return new_actuators, can_sends

  def create_button_messages(self, CC: car.CarControl, CS: car.CarState, use_clu11: bool):
    can_sends = []
    if use_clu11:
      if CC.cruiseControl.cancel:
        can_sends.append(hyundaican.create_clu11(self.packer, self.frame, CS.clu11, Buttons.CANCEL, self.CP))
      elif CC.cruiseControl.resume:
        # send resume at a max freq of 10Hz
        if (self.frame - self.last_button_frame) * DT_CTRL > 0.1:
          # send 25 messages at a time to increases the likelihood of resume being accepted
          can_sends.extend([hyundaican.create_clu11(self.packer, self.frame, CS.clu11, Buttons.RES_ACCEL, self.CP)] * 25)
          if (self.frame - self.last_button_frame) * DT_CTRL >= 0.15:
            self.last_button_frame = self.frame
    else:
      if (self.frame - self.last_button_frame) * DT_CTRL > 0.25:
        # cruise cancel
        if CC.cruiseControl.cancel:
          if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
            can_sends.append(hyundaicanfd.create_acc_cancel(self.packer, self.CP, self.CAN, CS.cruise_info))
            self.last_button_frame = self.frame
          else:
            for _ in range(20):
              can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, self.CAN, CS.buttons_counter+1, Buttons.CANCEL))
            self.last_button_frame = self.frame

        # cruise standstill resume
        elif CC.cruiseControl.resume:
          if self.CP.flags & HyundaiFlags.CANFD_ALT_BUTTONS:
            # TODO: resume for alt button cars
            pass
          else:
            for _ in range(20):
              can_sends.append(hyundaicanfd.create_buttons(self.packer, self.CP, self.CAN, CS.buttons_counter+1, Buttons.RES_ACCEL))
            self.last_button_frame = self.frame

    return can_sends

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
    cruise_button = Buttons.RES_ACCEL
    self.button_count += 1
    if self.target_speed <= self.v_set_dis:
      self.button_count = 0
      self.button_type = 3
    elif self.button_count > 5:
      self.button_count = 0
      self.button_type = 3
    return cruise_button

  def type_2(self):
    cruise_button = Buttons.SET_DECEL
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
    self.init_speed = round(min(final_speed, v_cruise_kph_prev) * (CV.KPH_TO_MPH if not self.is_metric else 1))
    self.v_set_dis = round(CS.out.cruiseState.speed * (CV.MS_TO_MPH if not self.is_metric else CV.MS_TO_KPH))
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
    return cruise_button
