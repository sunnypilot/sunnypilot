import json
import math
import time
from cereal import custom
from openpilot.common.params import Params

R = 6373000.0  # approximate radius of earth in meters
TO_RADIANS = math.pi / 180
TO_DEGREES = 180 / math.pi
TARGET_JERK = -0.6  # m/s^3 There's some jounce limits that are not consistent so we're fudging this some
TARGET_ACCEL = -1.2  # m/s^2 should match up with the long planner limit
TARGET_OFFSET = 1.0  # seconds - This controls how soon before the curve you reach the target velocity. It also helps
                     # reach the target velocity when innacuracies in the distance modeling logic would cause overshoot.
                     # The value is multiplied against the target velocity to determine the additional distance. This is
                     # done to keep the distance calculations consistent but results in the offset actually being less
                     # time than specified depending on how much of a speed diffrential there is between v_ego and the
                     # target velocity.


def calculate_accel(t, target_jerk, a_ego):
  return a_ego + target_jerk * t


def calculate_velocity(t, target_jerk, a_ego, v_ego):
  return v_ego + a_ego * t + target_jerk/2 * (t ** 2)


def calculate_distance(t, target_jerk, a_ego, v_ego):
  return t * v_ego + a_ego/2 * (t ** 2) + target_jerk/6 * (t ** 3)


PARAMS_UPDATE_PERIOD = 5.

TurnSpeedControlState = custom.LongitudinalPlanSP.SpeedLimitControlState


# points should be in radians
# output is meters
def distance_to_point(ax, ay, bx, by):
  a = math.sin((bx-ax)/2)*math.sin((bx-ax)/2) + math.cos(ax) * math.cos(bx)*math.sin((by-ay)/2)*math.sin((by-ay)/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

  return R * c  # in meters


class TurnSpeedController:
  def __init__(self):
    self.params = Params()
    self.mem_params = Params("/dev/shm/params")
    self.enabled = self.params.get_bool("TurnSpeedControl")
    self.last_params_update = 0
    self._op_enabled = False
    self._gas_pressed = False
    self._state = TurnSpeedControlState.inactive
    self._v_cruise = 0
    self._min_v = 0
    self.target_lat = 0.0
    self.target_lon = 0.0
    self.target_v = 0.0

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    self._state = value

  @property
  def is_active(self):
    return self.state > TurnSpeedControlState.tempInactive and self.enabled

  @property
  def v_target(self):
    return self._min_v

  def update_params(self):
    t = time.monotonic()
    if t > self.last_params_update + PARAMS_UPDATE_PERIOD:
      self.enabled = self.params.get_bool("TurnSpeedControl")
      self.last_params_update = t

  def target_speed(self, v_ego, a_ego) -> float:
    if not self.enabled:
      return 0.0

    lat = 0.0
    lon = 0.0
    try:
      position = json.loads(self.mem_params.get("LastGPSPosition"))
      lat = position["latitude"]
      lon = position["longitude"]
    except: return 0.0

    try:
      target_velocities = json.loads(self.mem_params.get("MapTargetVelocities"))
    except: return 0.0

    min_dist = 1000
    min_idx = 0
    distances = []

    # find our location in the path
    for i in range(len(target_velocities)):
      target_velocity = target_velocities[i]
      tlat = target_velocity["latitude"]
      tlon = target_velocity["longitude"]
      d = distance_to_point(lat * TO_RADIANS, lon * TO_RADIANS, tlat * TO_RADIANS, tlon * TO_RADIANS)
      distances.append(d)
      if d < min_dist:
        min_dist = d
        min_idx = i

    # only look at values from our current position forward
    forward_points = target_velocities[min_idx:]
    forward_distances = distances[min_idx:]

    # find velocities that we are within the distance we need to adjust for
    valid_velocities = []
    for i in range(len(forward_points)):
      target_velocity = forward_points[i]
      tlat = target_velocity["latitude"]
      tlon = target_velocity["longitude"]
      tv = target_velocity["velocity"]
      if tv > v_ego:
        continue

      d = forward_distances[i]

      a_diff = (a_ego - TARGET_ACCEL)
      accel_t = abs(a_diff / TARGET_JERK)
      min_accel_v = calculate_velocity(accel_t, TARGET_JERK, a_ego, v_ego)

      max_d = 0
      if tv > min_accel_v:
        # calculate time needed based on target jerk
        a = 0.5 * TARGET_JERK
        b = a_ego
        c = v_ego - tv
        t_a = -1 * ((b**2 - 4 * a * c) ** 0.5 + b) / 2 * a
        t_b = ((b**2 - 4 * a * c) ** 0.5 - b) / 2 * a
        if not isinstance(t_a, complex) and t_a > 0:
          t = t_a
        else:
          t = t_b
        if isinstance(t, complex):
          continue

        max_d = max_d + calculate_distance(t, TARGET_JERK, a_ego, v_ego)
      else:
        t = accel_t
        max_d = calculate_distance(t, TARGET_JERK, a_ego, v_ego)

        # calculate additional time needed based on target accel
        t = abs((min_accel_v - tv) / TARGET_ACCEL)
        max_d += calculate_distance(t, 0, TARGET_ACCEL, min_accel_v)

      if d < max_d + tv * TARGET_OFFSET:
        valid_velocities.append((float(tv), tlat, tlon))

    # Find the smallest velocity we need to adjust for
    min_v = 100.0
    target_lat = 0.0
    target_lon = 0.0
    for tv, lat, lon in valid_velocities:
      if tv < min_v:
        min_v = tv
        target_lat = lat
        target_lon = lon

    if self.target_v < min_v and not (self.target_lat == 0 and self.target_lon == 0):
      for i in range(len(forward_points)):
        target_velocity = forward_points[i]
        tlat = target_velocity["latitude"]
        tlon = target_velocity["longitude"]
        tv = target_velocity["velocity"]
        if tv > v_ego:
          continue

        if tlat == self.target_lat and tlon == self.target_lon and tv == self.target_v:
          return float(self.target_v)
      # not found so lets reset
      self.target_v = 0.0
      self.target_lat = 0.0
      self.target_lon = 0.0

    self.target_v = min_v
    self.target_lat = target_lat
    self.target_lon = target_lon

    return min_v

  def _state_transition(self):
    if not self._op_enabled or not self.enabled:
      self.state = TurnSpeedControlState.inactive
      return

    if self._gas_pressed:
      self.state = TurnSpeedControlState.tempInactive
      return

    # INACTIVE
    if self.state == TurnSpeedControlState.inactive:
      if self._v_cruise > self._min_v != 0:
        self.state = TurnSpeedControlState.active

    # TEMP INACTIVE
    elif self.state == TurnSpeedControlState.tempInactive:
      if self._v_cruise > self._min_v != 0:
        self.state = TurnSpeedControlState.active
      else:
        self.state = TurnSpeedControlState.inactive

    # ACTIVE
    elif self.state == TurnSpeedControlState.active:
      if not (self._v_cruise > self._min_v != 0):
        self.state = TurnSpeedControlState.inactive

  def update(self, op_enabled, v_ego, sm, v_cruise):
    self.update_params()
    self._op_enabled = op_enabled
    self._gas_pressed = sm['carState'].gasPressed
    self._v_cruise = v_cruise
    self._min_v = self.target_speed(v_ego, sm['carState'].aEgo)

    self._state_transition()
