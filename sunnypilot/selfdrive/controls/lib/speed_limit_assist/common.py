from enum import IntEnum


class Policy(IntEnum):
  map_data_only = 0
  car_state_only = 1
  map_data_priority = 2
  car_state_priority = 3
  combined = 4


class OffsetType(IntEnum):
  off = 0
  fixed = 1
  percentage = 2
