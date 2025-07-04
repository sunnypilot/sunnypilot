from cereal import custom

DEBUG = True
PARAMS_UPDATE_PERIOD = 2.  # secs. Time between parameter updates.
TEMP_INACTIVE_GUARD_PERIOD = 1.  # secs. Time to wait after activation before considering temp deactivation signal.

# Lookup table for speed limit percent offset depending on speed.
LIMIT_PERC_OFFSET_V = [0.1, 0.05, 0.038]  # 55, 105, 135 km/h
LIMIT_PERC_OFFSET_BP = [13.9, 27.8, 36.1]  # 50, 100, 130 km/h

# Constants for Limit controllers.
LIMIT_ADAPT_ACC = -1.  # m/s^2 Ideal acceleration for the adapting (braking) phase when approaching speed limits.
LIMIT_MIN_ACC = -1.5  # m/s^2 Maximum deceleration allowed for limit controllers to provide.
LIMIT_MAX_ACC = 1.0   # m/s^2 Maximum acceleration allowed for limit controllers to provide while active.
LIMIT_MIN_SPEED = 8.33  # m/s, Minimum speed limit to provide as solution on limit controllers.
LIMIT_SPEED_OFFSET_TH = -1.  # m/s Maximum offset between speed limit and current speed for adapting state.
LIMIT_MAX_MAP_DATA_AGE = 10.  # s Maximum time to hold to map data, then consider it invalid inside limits controllers.

SpeedLimitControlState = custom.LongitudinalPlanSP.SpeedLimitControlState
