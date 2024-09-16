def create_acc_buttons_control(packer, bus, gra_stock_values, buttons=0):
  values = {s: gra_stock_values[s] for s in [
    "GRA_Hauptschalter",           # ACC button, on/off
    "GRA_Typ_Hauptschalter",       # ACC main button type
    "GRA_Codierung",               # ACC button configuration/coding
    "GRA_Tip_Stufe_2",             # unknown related to stalk type
    "GRA_ButtonTypeInfo",          # unknown related to stalk type
  ]}

  values.update({
    "COUNTER": (gra_stock_values["COUNTER"] + 1) % 16,
    "GRA_Tip_Wiederaufnahme": 1 if buttons == 3 else 0,
    "GRA_Tip_Setzen": 1 if buttons == 4 else 0,
    "GRA_Tip_Runter": 1 if buttons == 2 else 0,
    "GRA_Tip_Hoch": 1 if buttons == 1 else 0,
  })

  return packer.make_can_msg("GRA_ACC_01", bus, values)
