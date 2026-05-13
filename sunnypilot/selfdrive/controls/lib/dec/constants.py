class WMACConstants:
  # lead
  LEAD_WINDOW_SIZE = 6
  LEAD_PROB = 0.45

  # slow down
  SLOW_DOWN_WINDOW_SIZE = 5
  SLOW_DOWN_PROB = 0.5
  SLOW_DOWN_BP = [0., 10., 20., 30., 40., 50., 60., 80., 100., 120.]
  SLOW_DOWN_DIST = [32., 46., 64., 86., 108., 130., 165., 210., 260., 310.]

  # predicted stop (modelV2.velocity)
  V_STOP_THRESH = 0.5
  T_STOP_HORIZON = 8.0
  V_STOP_URGENCY_CAP = 0.9

  # model brake-prob curves (modelV2.meta.disengagePredictions)
  BRAKE_PRESS_PROB_THRESH = 0.35
  HARD_BRAKE_3MS2_PROB_THRESH = 0.25
  HARD_BRAKE_5MS2_PROB_THRESH = 0.15

  # slowness
  SLOWNESS_WINDOW_SIZE = 10
  SLOWNESS_PROB = 0.55
  SLOWNESS_CRUISE_OFFSET = 1.025
