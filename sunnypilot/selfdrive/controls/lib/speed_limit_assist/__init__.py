from cereal import custom

SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimitAssistState

PARAMS_UPDATE_PERIOD = 3.  # secs. Time between parameter updates.
DISABLED_GUARD_PERIOD = 2  # secs.
PRE_ACTIVE_GUARD_PERIOD = 5  # secs. Time to wait after activation before considering temp deactivation signal.

# Constants for Limit controllers.
LIMIT_ADAPT_ACC = -1.  # m/s^2 Ideal acceleration for the adapting (braking) phase when approaching speed limits.
LIMIT_MIN_ACC = -1.5  # m/s^2 Maximum deceleration allowed for limit controllers to provide.
LIMIT_MAX_ACC = 1.0   # m/s^2 Maximum acceleration allowed for limit controllers to provide while active.
LIMIT_MIN_SPEED = 8.33  # m/s, Minimum speed limit to provide as solution on limit controllers.
LIMIT_SPEED_OFFSET_TH = -1.  # m/s Maximum offset between speed limit and current speed for adapting state.
LIMIT_MAX_MAP_DATA_AGE = 10.  # s Maximum time to hold to map data, then consider it invalid inside limits controllers.

# Speed Limit Assist Auto mode constants
REQUIRED_INITIAL_MAX_SET_SPEED = 35.7632  # m/s 80 MPH  # TODO-SP: customizable with params
CRUISE_SPEED_TOLERANCE = 0.44704  # m/s ±1 MPH tolerance  # TODO-SP: metric vs imperial
FALLBACK_CRUISE_SPEED = 255.0  # m/s fallback when no speed limit available
