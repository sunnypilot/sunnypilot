class ModelConstantsV1:
  HISTORY_BUFFER_LEN = 99
  PREV_DESIRED_CURVS_LEN = 20
  NAV_FEATURE_LEN = 256
  NAV_INSTRUCTION_LEN = 150
  DRIVING_STYLE_LEN = 12


class MetaV1:
  ENGAGED = slice(0, 1)
  # next 2, 4, 6, 8, 10 seconds
  GAS_DISENGAGE = slice(1, 41, 8)
  BRAKE_DISENGAGE = slice(2, 41, 8)
  STEER_OVERRIDE = slice(3, 41, 8)
  HARD_BRAKE_3 = slice(4, 41, 8)
  HARD_BRAKE_4 = slice(5, 41, 8)
  HARD_BRAKE_5 = slice(6, 41, 8)
  GAS_PRESS = slice(7, 41, 8)
  BRAKE_PRESS = slice(8, 41, 8)
  # next 0, 2, 4, 6, 8, 10 seconds
  LEFT_BLINKER = slice(41, 53, 2)
  RIGHT_BLINKER = slice(42, 53, 2)


class ModelMeta:
  def __init__(self, meta):
    self.ENGAGED = meta.ENGAGED
    self.GAS_DISENGAGE = meta.GAS_DISENGAGE
    self.BRAKE_DISENGAGE = meta.BRAKE_DISENGAGE
    self.STEER_OVERRIDE = meta.STEER_OVERRIDE
    self.HARD_BRAKE_3 = meta.HARD_BRAKE_3
    self.HARD_BRAKE_4 = meta.HARD_BRAKE_4
    self.HARD_BRAKE_5 = meta.HARD_BRAKE_5
    self.GAS_PRESS = meta.GAS_PRESS
    self.BRAKE_PRESS = meta.BRAKE_PRESS
    self.LEFT_BLINKER = meta.LEFT_BLINKER
    self.RIGHT_BLINKER = meta.RIGHT_BLINKER
