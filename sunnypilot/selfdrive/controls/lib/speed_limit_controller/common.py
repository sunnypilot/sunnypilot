from enum import IntEnum


class Source(IntEnum):
  none = 0
  car_state = 1
  map_data = 2


class Policy(IntEnum):
  map_data_only = 0
  car_state_only = 1
  map_data_priority = 2
  car_state_priority = 3
  combined = 4


class Engage(IntEnum):
  auto = 0
  user_confirm = 1


class OffsetType(IntEnum):
  default = 0
  fixed = 1
  percentage = 2
