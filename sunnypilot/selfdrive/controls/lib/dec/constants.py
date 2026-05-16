class WMACConstants:
  # lead
  LEAD_WINDOW_SIZE = 6
  LEAD_PROB = 0.45

  # slow down
  SLOW_DOWN_WINDOW_SIZE = 5
  SLOW_DOWN_PROB = 0.42
  SLOW_DOWN_BP = [0., 10., 20., 30., 40., 50., 60., 80., 100., 120.]
  SLOW_DOWN_DIST = [22., 36., 50., 68., 90., 112., 145., 195., 245., 300.]
  # endpoint must be below this fraction of expected_distance for shortage to count;
  # gives a deadband so routine city traj (intersection turn, short visibility) doesn't trigger
  SLOW_DOWN_DEADBAND_RATIO = 0.75

  # predicted stop (modelV2.velocity)
  V_STOP_THRESH = 0.5
  T_STOP_HORIZON = 8.0
  V_STOP_URGENCY_CAP = 0.9
  V_STOP_MIN_T = 1.0          # ignore stops predicted within 1s (=current-state continuation)
  V_STOP_MIN_D = 5.0          # ignore stops predicted <5m ahead
  V_STOP_MIN_VEGO_KPH = 10.8  # skip when already creeping (<3 m/s); standstill path handles it

  # model brake-prob curves (modelV2.meta.disengagePredictions)
  # brakePressProbs sits in ~0.4-0.7 during normal driving — must spike above baseline to count
  BRAKE_PRESS_PROB_THRESH = 0.7
  BRAKE_PRESS_PEAK_RATIO = 1.5   # peak must exceed mean × this to trigger
  HARD_BRAKE_3MS2_PROB_THRESH = 0.25
  HARD_BRAKE_5MS2_PROB_THRESH = 0.15

  # slowness
  SLOWNESS_WINDOW_SIZE = 10
  SLOWNESS_PROB = 0.55
  SLOWNESS_CRUISE_OFFSET = 1.025
