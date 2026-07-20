from opendbc.car import structs
from opendbc.car.structs import car
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP
from openpilot.cereal import custom
from openpilot.selfdrive.controls.radard import radar_point_eligible_for_fusion


def radar_point(motion_state: int):
  point = car.RadarData.RadarPoint.new_message()
  point.motionState = motion_state
  return point


def test_hyundai_full_radar_fuses_only_classified_points():
  CP = structs.CarParams(brand="hyundai")
  CP_SP = custom.CarParamsSP.new_message()
  CP_SP.flags = HyundaiFlagsSP.RADAR_FULL_RADAR.value

  assert radar_point_eligible_for_fusion(CP, CP_SP, radar_point(1))
  assert radar_point_eligible_for_fusion(CP, CP_SP, radar_point(2))
  assert not radar_point_eligible_for_fusion(CP, CP_SP, radar_point(0))
  assert not radar_point_eligible_for_fusion(CP, CP_SP, radar_point(255))


def test_radar_motion_filter_does_not_affect_other_modes_or_brands():
  CP_SP = custom.CarParamsSP.new_message()

  assert radar_point_eligible_for_fusion(structs.CarParams(brand="hyundai"), CP_SP, radar_point(0))
  assert radar_point_eligible_for_fusion(structs.CarParams(brand="toyota"), CP_SP, radar_point(0))
