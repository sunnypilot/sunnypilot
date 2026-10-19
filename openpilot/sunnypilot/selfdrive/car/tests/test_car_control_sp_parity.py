"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


def test_convert_car_control_sp_accepts_every_capnp_field():
  # card converts the capnp CarControlSP into the opendbc structs dataclass via
  # **kwargs on every frame. Any field added to the capnp schema without a
  # mirrored dataclass field crashes card at runtime (TypeError), taking down
  # CAN output with it. to_dict() exposes every schema field, so converting a
  # default-initialized message is sufficient to catch a missing mirror.
  from openpilot.cereal import messaging
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  dat = messaging.new_message('carControlSP')
  converted = convert_carControlSP(dat.carControlSP)
  assert converted.leadCoastMinDistance == 0.
  assert converted.longitudinalIdle is False


def test_convert_car_control_sp_preserves_saved_coast_gaps():
  from openpilot.cereal import messaging
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  dat = messaging.new_message('carControlSP')
  dat.carControlSP.longitudinalIdle = True
  # Preserve the exact boundary through serialization and the card conversion.
  gaps = [2.1234567890123, 0.]
  dat.carControlSP.leadCoastTimeGaps = gaps
  restored = messaging.log_from_bytes(dat.to_bytes())
  converted = convert_carControlSP(restored.carControlSP)
  assert converted.leadCoastTimeGaps == gaps
