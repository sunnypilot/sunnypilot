from enum import IntEnum


class Source(IntEnum):
  none = 0
  car_state = 1
  map_data = 2
  nav = 3


class Policy(IntEnum):
  car_state_only = 0
  map_data_only = 1
  car_state_priority = 2
  map_data_priority = 3
  combined = 4
  nav_only = 5
  nav_priority = 6
