from enum import IntEnum


class Source(IntEnum):
  none = 0
  car_state = 1
  map_data = 2
  nav = 3


class Policy(IntEnum):
  nav_only = 0
  map_data_only = 1
  car_state_only = 2
  nav_priority = 3
  map_data_priority = 4
  car_state_priority = 5
  combined = 6


class Engage(IntEnum):
  auto = 0
  user_confirm = 1


class OffsetType(IntEnum):
  default = 0
  fixed = 1
  percentage = 2
