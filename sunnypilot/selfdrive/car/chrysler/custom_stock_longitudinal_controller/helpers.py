def create_cruise_buttons(packer, frame, bus, buttons=0):

  values = {
    "ACC_Accel": 1 if buttons == 1 else 0,
    "ACC_Decel": 1 if buttons == 2 else 0,
    "COUNTER": frame % 0x10,
  }

  return packer.make_can_msg("CRUISE_BUTTONS", bus, values)
