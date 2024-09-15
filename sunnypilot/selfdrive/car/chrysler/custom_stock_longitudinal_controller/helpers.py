def create_cruise_buttons(packer, frame, bus, CP, buttons=0):

  acc_accel = 1 if buttons == 1 else 0
  acc_decel = 1 if buttons == 2 else 0

  values = {
    "ACC_Accel": acc_accel,
    "ACC_Decel": acc_decel,
    "COUNTER": frame % 0x10,
  }

  if buttons == 0 and not (cancel or resume) and CP.carFingerprint in RAM_CARS:
    values = cruise_buttons_msg.copy()
  return packer.make_can_msg("CRUISE_BUTTONS", bus, values)
