def create_acc_buttons_control(packer, bus, gra_stock_values, buttons=0):
  values = {s: gra_stock_values[s] for s in [
    "GRA_Hauptschalt",      # ACC button, on/off
    "GRA_Typ_Hauptschalt",  # ACC button, momentary vs latching
    "GRA_Kodierinfo",       # ACC button, configuration
    "GRA_Sender",           # ACC button, CAN message originator
  ]}

  values.update({
    "COUNTER": (gra_stock_values["COUNTER"] + 1) % 16,
    "GRA_Recall": 1 if buttons == 3 else 0,
    "GRA_Neu_Setzen": 1 if buttons == 4 else 0,
    "GRA_Down_kurz": 1 if buttons == 2 else 0,
    "GRA_Up_kurz": 1 if buttons == 1 else 0,
  })

  return packer.make_can_msg("GRA_Neu", bus, values)
