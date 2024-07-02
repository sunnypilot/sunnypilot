from cereal import custom, car

DEBUG = False
PARAMS_UPDATE_PERIOD = 2.  # secs. Time between parameter updates.
TEMP_INACTIVE_GUARD_PERIOD = 1.  # secs. Time to wait after activation before considering temp deactivation signal.

# Lookup table for speed limit percent offset depending on speed.
LIMIT_PERC_OFFSET_V = [0.1, 0.05, 0.038]  # 55, 105, 135 km/h
LIMIT_PERC_OFFSET_BP = [13.9, 27.8, 36.1]  # 50, 100, 130 km/h

SpeedLimitControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
EventName = car.CarEvent.EventName

