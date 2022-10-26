def create_steering_control(packer, bus, apply_steer, lkas_enabled):
  values = {
    "SET_ME_0X3": 0x3,
    "Assist_Torque": abs(apply_steer),
    "Assist_Requested": lkas_enabled,
    "Assist_VZ": 1 if apply_steer < 0 else 0,
    "HCA_Available": 1,
    "HCA_Standby": not lkas_enabled,
    "HCA_Active": lkas_enabled,
    "SET_ME_0XFE": 0xFE,
    "SET_ME_0X07": 0x07,
  }
  return packer.make_can_msg("HCA_01", bus, values)


def create_lka_hud_control(packer, bus, ldw_stock_values, enabled, lat_active, steering_pressed, hud_alert, hud_control):
  values = ldw_stock_values.copy()

  values.update({
    "LDW_Status_LED_gelb": 1 if lat_active and steering_pressed else 0,
    "LDW_Status_LED_gruen": 1 if lat_active and not steering_pressed else 0,
    "LDW_Lernmodus_links": 3 if hud_control.leftLaneDepart else 1 + hud_control.leftLaneVisible,
    "LDW_Lernmodus_rechts": 3 if hud_control.rightLaneDepart else 1 + hud_control.rightLaneVisible,
    "LDW_Texte": hud_alert,
  })
  return packer.make_can_msg("LDW_02", bus, values)


def create_acc_buttons_control(packer, bus, gra_stock_values, counter, buttonStatesToSend, cancel=False, resume=False):
  values = gra_stock_values.copy()

  values.update({
    "COUNTER": counter,
    "GRA_Abbrechen": cancel,
    "GRA_Tip_Wiederaufnahme": resume,
  })

  if buttonStatesToSend is not None and not (cancel or resume):
    values.update({
      "GRA_Abbrechen": buttonStatesToSend["cancel"],
      "GRA_Tip_Setzen": buttonStatesToSend["setCruise"],
      "GRA_Tip_Hoch": buttonStatesToSend["accelCruise"],
      "GRA_Tip_Runter": buttonStatesToSend["decelCruise"],
      "GRA_Tip_Wiederaufnahme": buttonStatesToSend["resumeCruise"],
      "GRA_Verstellung_Zeitluecke": 3 if buttonStatesToSend["gapAdjustCruise"] else 0
    })

  return packer.make_can_msg("GRA_ACC_01", bus, values)
