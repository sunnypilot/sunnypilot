"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
LIMIT_ADAPT_ACC = -1.  # m/s^2 Ideal acceleration for the adapting (braking) phase when approaching speed limits.
LIMIT_MAX_MAP_DATA_AGE = 10.  # s Maximum time to hold to map data, then consider it invalid inside limits controllers.

# Speed Limit Assist Auto mode constants
REQUIRED_INITIAL_MAX_SET_SPEED = 35.7632  # m/s 80 MPH  # TODO-SP: customizable with params
CRUISE_SPEED_TOLERANCE = 0.44704  # m/s ±1 MPH tolerance  # TODO-SP: metric vs imperial
