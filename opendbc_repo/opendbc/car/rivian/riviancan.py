def checksum(data, poly, xor_output):
  crc = 0
  for byte in data:
    crc ^= byte
    for _ in range(8):
      if crc & 0x80:
        crc = (crc << 1) ^ poly
      else:
        crc <<= 1
      crc &= 0xFF
  return crc ^ xor_output


def create_lka_steering(packer, frame, acm_lka_hba_cmd, apply_torque, enabled, active, mads):
  # forward auto high beam and speed limit status and nothing else
  values = {s: acm_lka_hba_cmd[s] for s in (
    "ACM_hbaSysState",
    "ACM_hbaLamp",
    "ACM_hbaOnOffState",
    "ACM_slifOnOffState",
  )}

  values |= {
    "ACM_lkaHbaCmd_Counter": frame % 15,
    "ACM_lkaStrToqReq": apply_torque,
    "ACM_lkaActToi": mads.lat_active,

    "ACM_lkaLaneRecogState": 3 if mads.lka_icon_states else 0,
    "ACM_lkaSymbolState": 3 if mads.lka_icon_states else 0,

    # static values
    "ACM_lkaElkRequest": 0,
    "ACM_ldwlkaOnOffState": 2,  # 2=LKAS+LDW on
    "ACM_elkOnOffState": 1,  # 1=LKAS on
    # TODO: what are these used for?
    "ACM_ldwWarnTypeState": 2,  # always 2
    "ACM_ldwWarnTimingState": 1,  # always 1
    #"ACM_lkaHandsoffDisplayWarning": 1,  # TODO: we can send this when openpilot wants you to pay attention
  }

  data = packer.make_can_msg("ACM_lkaHbaCmd", 0, values)[1]
  values["ACM_lkaHbaCmd_Checksum"] = checksum(data[1:], 0x1D, 0x63)
  return packer.make_can_msg("ACM_lkaHbaCmd", 0, values)


def create_wheel_touch(packer, sccm_wheel_touch, enabled):
  values = {s: sccm_wheel_touch[s] for s in (
    "SCCM_WheelTouch_Counter",
    "SCCM_WheelTouch_HandsOn",
    "SCCM_WheelTouch_CapacitiveValue",
    "SETME_X52",
  )}

  # When only using ACC without lateral, the ACM warns the driver to hold the steering wheel on engagement
  # Tell the ACM that the user is holding the wheel to avoid this warning
  if enabled:
    values["SCCM_WheelTouch_HandsOn"] = 1
    values["SCCM_WheelTouch_CapacitiveValue"] = 100  # only need to send this value, but both are set for consistency

  data = packer.make_can_msg("SCCM_WheelTouch", 2, values)[1]
  values["SCCM_WheelTouch_Checksum"] = checksum(data[1:], 0x1D, 0x97)
  return packer.make_can_msg("SCCM_WheelTouch", 2, values)


def create_longitudinal(packer, frame, accel, enabled):
  values = {
    "ACM_longitudinalRequest_Counter": frame % 15,
    "ACM_AccelerationRequest": accel,
    "ACM_PrndRequest": 0,
    "ACM_longInterfaceEnable": 1 if enabled else 0,  # 0=INIT when not engaged, 1=ENABLE when engaged
    "ACM_VehicleHoldRequest": 0,
  }

  data = packer.make_can_msg("ACM_longitudinalRequest", 0, values)[1]
  values["ACM_longitudinalRequest_Checksum"] = checksum(data[1:], 0x1D, 0x12)
  return packer.make_can_msg("ACM_longitudinalRequest", 0, values)


def create_adas_status(packer, vdm_adas_status, interface_status, enabled):
  values = {s: vdm_adas_status[s] for s in (
    "VDM_AdasStatus_Checksum",
    "VDM_AdasStatus_Counter",
    "VDM_AdasDecelLimit",
    "VDM_AdasDriverAccelPriorityStatus",
    "VDM_AdasFaultStatus",
    "VDM_AdasAccelLimit",
    "VDM_AdasDriverModeStatus",
    "VDM_AdasUnkown1",
    "VDM_AdasInterfaceStatus",
    "VDM_AdasVehicleHoldStatus",
    "VDM_UserAdasRequest",
  )}

  # Override interface_status if provided (for cancel logic), otherwise use enabled state
  if interface_status is not None:
    values["VDM_AdasInterfaceStatus"] = interface_status
  else:
    # 0=Unavailable when not engaged, 1=Available when engaged
    values["VDM_AdasInterfaceStatus"] = 1 if enabled else 0

  # 0=Human when not engaged, 1=Adas when engaged
  values["VDM_AdasDriverModeStatus"] = 1 if enabled else 0

  # 0 when not engaged, 129 when engaged
  values["VDM_AdasUnkown1"] = 129 if enabled else 0

  # 0 when not engaged, 4 when engaged
  values["VDM_UserAdasRequest"] = 4 if enabled else 0

  data = packer.make_can_msg("VDM_AdasSts", 2, values)[1]
  values["VDM_AdasStatus_Checksum"] = checksum(data[1:], 0x1D, 0xD1)
  return packer.make_can_msg("VDM_AdasSts", 2, values)


def create_epas_status(packer, frame, enabled):
  # EPAS_Ecu2EacSts values: 0=Inhibited, 1=Available, 2=Active, 3=Fault, 7=Sna
  values = {
    "EPASS_Ecu2Status_Counter": frame % 15,
    "EPAS_Ecu2EacSts": 7 if enabled else 1,  # 7=Sna when engaged, 1=Available when not
    "EPAS_Ecu2PowerMode": 1,  # 1=Normal
    "EPASS_Ecu2Role": 0,
    "EPASS_Ecu2State": 0,
  }

  data = packer.make_can_msg("EPASS_Status", 0, values)[1]
  values["EPASS_Ecu2Status_Checksum"] = checksum(data[1:], 0x1D, 0x00)  # TODO: verify XOR value
  return packer.make_can_msg("EPASS_Status", 0, values)


def create_steering_control(packer, frame, apply_angle, enabled):
  # ACM_EacEnabled values: 0=None, 1=Enabled, 2=Reserved
  values = {
    "ACM_SteeringControl_Counter": frame % 15,
    "ACM_EacEnabled": 1 if enabled else 0,  # 0=None when not engaged, 1=Enabled when engaged
    "ACM_HapticRequired": 0,
    "ACM_SteeringAngleRequest": apply_angle,  # Steering angle in degrees
  }

  data = packer.make_can_msg("ACM_SteeringControl", 0, values)[1]
  values["ACM_SteeringControl_Checksum"] = checksum(data[1:], 0x1D, 0x00)  # TODO: verify XOR value
  return packer.make_can_msg("ACM_SteeringControl", 0, values)


def create_longitudinal_interface(packer, frame, enabled):
  # Send longitudinal interface enable on bus 0
  values = {
    "ACM_longitudinalRequest_Counter": frame % 15,
    "ACM_AccelerationRequest": 0,
    "ACM_PrndRequest": 0,
    "ACM_longInterfaceEnable": 1 if enabled else 0,  # 0=INIT when not engaged, 1=ENABLE when engaged
    "ACM_VehicleHoldRequest": 0,
  }

  data = packer.make_can_msg("ACM_longitudinalRequest", 0, values)[1]
  values["ACM_longitudinalRequest_Checksum"] = checksum(data[1:], 0x1D, 0x12)
  return packer.make_can_msg("ACM_longitudinalRequest", 0, values)


def create_epas_adas_status(packer, frame, enabled):
  # EPAS_EacStatus values: 0=Inhibited, 1=Available, 2=Active, 3=Standby, 4=Fault, 5=Sna
  values = {
    "EPAS_AdasStatus_Counter": frame % 15,
    "EPAS_EacStatus": 2 if enabled else 1,  # 1=Available when not engaged, 2=Active when engaged
    "EPAS_EacErrorCode": 0,  # 0=No error
    "EPAS_SteeringAngleSpeed": 0,
    "EPAS_InternalSas": 0,
    "EPAS_InternalSasQ": 0,
  }

  data = packer.make_can_msg("EPAS_AdasStatus", 0, values)[1]
  values["EPAS_AdasStatus_Checksum"] = checksum(data[1:], 0x1D, 0x00)  # TODO: verify XOR value
  return packer.make_can_msg("EPAS_AdasStatus", 0, values)