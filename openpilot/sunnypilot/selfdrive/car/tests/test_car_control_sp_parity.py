"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


def test_convert_car_control_sp_ignores_fields_missing_from_opendbc():
  # The capnp schema and the independently versioned opendbc dataclass can
  # temporarily differ. Conversion must keep card running while the pinned
  # submodule remains authoritative for the CAN-facing fields.
  from openpilot.cereal import messaging
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  dat = messaging.new_message('carControlSP')
  converted = convert_carControlSP(dat.carControlSP)
  assert converted.mads is not None


def test_convert_car_control_sp_accepts_saved_coast_gaps():
  from openpilot.cereal import messaging
  from openpilot.selfdrive.car.helpers import convert_carControlSP

  dat = messaging.new_message('carControlSP')
  dat.carControlSP.longitudinalIdle = True
  # Preserve the exact boundary through serialization and the card conversion.
  gaps = [2.1234567890123, 0.]
  dat.carControlSP.leadCoastTimeGaps = gaps
  restored = messaging.log_from_bytes(dat.to_bytes())
  converted = convert_carControlSP(restored.carControlSP)
  assert converted.mads is not None
