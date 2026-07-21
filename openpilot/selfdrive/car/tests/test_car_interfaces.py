import os
import hypothesis.strategies as st
from hypothesis import Phase, given, settings
from openpilot.common.parameterized import parameterized

from openpilot.cereal import custom
from opendbc.car.structs import car
from opendbc.car import DT_CTRL, structs
from opendbc.car.structs import CarParams
from opendbc.car.tests.test_car_interfaces import get_fuzzy_car_interface
from opendbc.car.mock.values import CAR as MOCK
from opendbc.car.values import PLATFORMS
from openpilot.selfdrive.car.helpers import convert_carControlSP
from openpilot.selfdrive.controls.lib.latcontrol_angle import LatControlAngle
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.controls.lib.longcontrol import LongControl
from openpilot.selfdrive.test.fuzzy_generation import FuzzyGenerator

from openpilot.sunnypilot.selfdrive.car import interfaces as sunnypilot_interfaces

MAX_EXAMPLES = int(os.environ.get('MAX_EXAMPLES', '60'))


def legacy_convert_car_control_sp(struct):
  def remove_deprecated(values):
    return {k: v for k, v in values.items() if not k.endswith('DEPRECATED')}

  struct_dict = struct.to_dict()
  result = structs.CarControlSP(**remove_deprecated(struct_dict))
  result.mads = structs.ModularAssistiveDrivingSystem(**remove_deprecated(struct_dict.get('mads', {})))
  result.leadOne = structs.LeadData(**remove_deprecated(struct_dict.get('leadOne', {})))
  result.leadTwo = structs.LeadData(**remove_deprecated(struct_dict.get('leadTwo', {})))
  result.radarTracks = [structs.CarControlSP.RadarTrack(**track) for track in struct_dict.get('radarTracks', [])]
  result.intelligentCruiseButtonManagement = structs.IntelligentCruiseButtonManagement(
    **remove_deprecated(struct_dict.get('intelligentCruiseButtonManagement', {}))
  )
  return result


def test_convert_car_control_sp_matches_legacy_conversion():
  msg = custom.CarControlSP.new_message(
    mads={"state": "enabled", "enabled": True, "active": True, "available": True},
    params=[{"key": "test", "type": "int", "value": b"42"}],
    leadOne={
      "dRel": 12.5, "yRel": -0.25, "vRel": -1.5, "aRel": 0.1, "vLead": 20.0,
      "dPath": 0.5, "vLat": 0.2, "vLeadK": 20.1, "aLeadK": 0.05, "fcw": True,
      "status": True, "aLeadTau": 1.5, "modelProb": 0.9, "radar": True, "radarTrackId": 7,
    },
    leadTwo={"dRel": 25.0, "status": True, "radarTrackId": 9},
    intelligentCruiseButtonManagement={"state": "holding", "sendButton": "increase", "vTarget": 27.0},
    radarTracks=[
      {"trackId": 7, "dRel": 12.5, "yRel": -0.25, "vRel": -1.5, "motionState": 2, "age": 4},
      {"trackId": 9, "dRel": 25.0, "yRel": 3.0, "vRel": 0.5, "motionState": 1, "age": 8},
    ],
    radarTracksActive=True,
  ).as_reader()

  assert convert_carControlSP(msg) == legacy_convert_car_control_sp(msg)
  default_msg = custom.CarControlSP.new_message().as_reader()
  assert convert_carControlSP(default_msg) == legacy_convert_car_control_sp(default_msg)


class TestCarInterfaces:
  # FIXME: Due to the lists used in carParams, Phase.target is very slow and will cause
  #  many generated examples to overrun when max_examples > ~20, don't use it
  @parameterized.expand([(car,) for car in sorted(PLATFORMS)] + [MOCK.MOCK])
  @settings(max_examples=MAX_EXAMPLES, deadline=None,
            phases=(Phase.reuse, Phase.generate, Phase.shrink))
  @given(data=st.data())
  def test_car_interfaces(self, car_name, data):
    car_interface = get_fuzzy_car_interface(car_name, data.draw)
    car_params = car_interface.CP.as_reader()
    car_params_sp = car_interface.CP_SP
    sunnypilot_interfaces.setup_interfaces(car_interface)

    cc_msg = FuzzyGenerator.get_random_msg(data.draw, car.CarControl, real_floats=True)
    cc_sp_msg = FuzzyGenerator.get_random_msg(data.draw, custom.CarControlSP, real_floats=True)
    # Run car interface
    now_nanos = 0
    CC = car.CarControl.new_message(**cc_msg)
    CC = CC.as_reader()
    CC_SP = custom.CarControlSP.new_message(**cc_sp_msg)
    CC_SP = convert_carControlSP(CC_SP.as_reader())
    for _ in range(10):
      car_interface.update([])
      car_interface.apply(CC, CC_SP, now_nanos)
      now_nanos += DT_CTRL * 1e9  # 10 ms

    CC = car.CarControl.new_message(**cc_msg)
    CC.enabled = True
    CC.latActive = True
    CC.longActive = True
    CC = CC.as_reader()
    for _ in range(10):
      car_interface.update([])
      car_interface.apply(CC, CC_SP, now_nanos)
      now_nanos += DT_CTRL * 1e9  # 10ms

    # Test controller initialization
    # TODO: wait until card refactor is merged to run controller a few times,
    #  hypothesis also slows down significantly with just one more message draw
    LongControl(car_params, car_params_sp)
    if car_params.steerControlType == CarParams.SteerControlType.angle:
      LatControlAngle(car_params, car_params_sp, car_interface, DT_CTRL)
    elif car_params.lateralTuning.which() == 'pid':
      LatControlPID(car_params, car_params_sp, car_interface, DT_CTRL)
    elif car_params.lateralTuning.which() == 'torque':
      LatControlTorque(car_params, car_params_sp, car_interface, DT_CTRL)
