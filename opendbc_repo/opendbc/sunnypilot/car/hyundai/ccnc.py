"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.crc import CRC8J1850, mk_crc8_fun
from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

cruise_buttons_checksum = mk_crc8_fun(CRC8J1850, init_crc=0x97, xor_out=0x97)  # mk_crc8_fun xors init with xor_out: register starts at 0

MAIN_PRESS_FRAMES = 12  # 120 ms


def create_ccnc_mdps(packer, CAN, mdps):
  values = mdps.copy()

  values.update({
    "MDPS_LkaToiActvSta": 0,
    "MDPS_LkaToiUnblSta": 1,
  })

  return packer.make_can_msg("MDPS", CAN.CAM, values)


def create_ccnc_0x161(packer, CAN, msg_161, enabled, lat_active, paused, long_enabled,
                      main_cruise_enabled, hud_control, set_speed):
  values = msg_161.copy()

  values.update({
    "LKA_ICON": 4 if lat_active else 3,
    "LFA_ICON": 2 if lat_active else 1 if paused else 0,
    "LANELINE_LEFT": 6 if lat_active else 0,
    "LANELINE_RIGHT": 6 if lat_active else 0,
    "CENTERLINE": 1 if lat_active else 0,
    "DAW_ICON": 0,
  })

  if long_enabled:
    state = 0 if not main_cruise_enabled else 2 if enabled else 1
    lead = 2 if enabled and hud_control.leadVisible else 0

    values.update({
      "SETSPEED": (0, 1, 3)[state],
      "SETSPEED_HUD": state,
      "SETSPEED_SPEED": set_speed if main_cruise_enabled else 255,
      "DISTANCE": hud_control.leadDistanceBars if main_cruise_enabled else 0,
      "DISTANCE_SPACING": 1 if enabled else 0,
      "DISTANCE_LEAD": lead,
      "DISTANCE_CAR": state,
      "HDA_ICON": 0,
      "SLA_ICON": 0,
      "NAV_ICON": 0,
      "TARGET": 0,
    })

  return packer.make_can_msg("CCNC_0x161", CAN.ECAN, values)


def create_ccnc_0x162(packer, CAN, msg_162, enabled, long_enabled, hud_control, lead_distance):
  values = msg_162.copy()

  if long_enabled:
    values.update({
      "LEAD": 2 if enabled and hud_control.leadVisible else 0,
      "LEAD_DISTANCE": lead_distance,
    })

  return packer.make_can_msg("CCNC_0x162", CAN.ECAN, values)


def create_ccnc_buttons(packer, CAN, cruise_buttons_msg, main_btn):
  values = cruise_buttons_msg.copy()

  values.update({
    "ADAPTIVE_CRUISE_MAIN_BTN": 1 if main_btn else 0,
    "NORMAL_CRUISE_MAIN_BTN": 0,
  })

  dat = packer.make_can_msg("CRUISE_BUTTONS", CAN.CAM, values)[1]
  values["_CHECKSUM"] = cruise_buttons_checksum(dat[1:])

  return packer.make_can_msg("CRUISE_BUTTONS", CAN.CAM, values)


class CcncCarController:
  def __init__(self, CP, CP_SP):
    self.ccnc_lfa_steering = bool(CP_SP.flags & HyundaiFlagsSP.CCNC and not (CP.flags & HyundaiFlags.CANFD_LKA_STEER_MSG))

  @staticmethod
  def _get_set_speed(v_cruise_cluster, is_metric):
    unit_conv = 1 if is_metric else CV.KPH_TO_MPH
    max_speed = 145 if is_metric else 90
    min_speed = 40 if is_metric else 25
    set_speed = round(v_cruise_cluster * unit_conv)
    return min_speed if set_speed > max_speed else set_speed

  def update(self, CS, CC):
    can_sends = []

    if not self.ccnc_lfa_steering:
      return can_sends

    can_sends.append(create_ccnc_mdps(self.packer, self.CAN, CS.mdps))

    if self.frame % 2 == 0 and self.CP.openpilotLongitudinalControl and self.CP.flags & HyundaiFlags.CANFD_CAMERA_SCC:
      press_main = CS.cruise_info["MainMode_ACC"] and self.frame % (2 * MAIN_PRESS_FRAMES) < MAIN_PRESS_FRAMES
      can_sends.append(create_ccnc_buttons(self.packer, self.CAN, CS.cruise_buttons_msg, press_main))

    if self.frame % 5 == 0:
      lat_active = self.mads.lat_active if self.mads.enable_mads else CC.enabled
      paused = self.mads.enable_mads and self.mads.paused
      set_speed = self._get_set_speed(CS.out.vCruiseCluster, CS.is_metric)
      can_sends.append(create_ccnc_0x161(self.packer, self.CAN, CS.msg_161, CC.enabled, lat_active, paused,
                                         self.CP.openpilotLongitudinalControl, CS.main_cruise_enabled,
                                         CC.hudControl, set_speed))
      can_sends.append(create_ccnc_0x162(self.packer, self.CAN, CS.msg_162, CC.enabled,
                                         self.CP.openpilotLongitudinalControl, CC.hudControl, self.lead_distance))

    return can_sends
