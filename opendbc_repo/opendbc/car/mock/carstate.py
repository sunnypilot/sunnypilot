from opendbc.car import structs
from opendbc.car.interfaces import CarStateBase


class CarState(CarStateBase):
  def update(self, can_parsers) -> tuple[structs.CarState, structs.CarStateSP]:
    return structs.CarState(), structs.CarStateSP()
