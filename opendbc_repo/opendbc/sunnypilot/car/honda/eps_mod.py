"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car import structs
from opendbc.car.honda.values import CAR
from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP

# Modified EPS firmware accepts larger requests than stock; the lookup maps them back to the EPS output range.
# Modified EPS cars not listed here use the stock linear STEER_MAX.
EPS_MOD_TORQUE_LOOKUP = {
  # stock request input values:     0x0000, 0x00DE, 0x014D, 0x01EF, 0x0290, 0x0377, 0x0454, 0x0610, 0x06EE
  # stock request output values:    0x0000, 0x0917, 0x0DC5, 0x1017, 0x119F, 0x140B, 0x1680, 0x1680, 0x1680
  # modified request output values: 0x0000, 0x0917, 0x0DC5, 0x1017, 0x119F, 0x140B, 0x1680, 0x2880, 0x3180
  # stock filter output values:     0x009F, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108
  # modified filter output values:  0x009F, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108, 0x0108, 0x0400, 0x0480
  # note: max request allowed is 4096, but request is capped at 3840 in firmware, so modifications result in 2x max
  CAR.HONDA_CIVIC: ([0, 2560, 8000], [0, 2560, 3840]),
  CAR.HONDA_CIVIC_BOSCH: ([0, 2564, 8000], [0, 2564, 3840]),
  CAR.HONDA_CIVIC_BOSCH_DIESEL: ([0, 2564, 8000], [0, 2564, 3840]),
  CAR.HONDA_CIVIC_2022: ([0, 2564, 8000], [0, 2564, 3840]),
  # stock request input values:     0x0000, 0x00DB, 0x01BB, 0x0296, 0x0377, 0x0454, 0x0532, 0x0610, 0x067F
  # stock request output values:    0x0000, 0x0500, 0x0A15, 0x0E6D, 0x1100, 0x1200, 0x129A, 0x134D, 0x1400
  # modified request output values: 0x0000, 0x0500, 0x0A15, 0x0E6D, 0x1100, 0x1200, 0x1ACD, 0x239A, 0x2800
  CAR.HONDA_CRV_5G: ([0, 2560, 10000], [0, 2560, 3840]),
}


def get_eps_mod_torque_lookup(CP: structs.CarParams, CP_SP: structs.CarParamsSP) -> tuple[list[int], list[int]] | None:
  if not CP_SP.flags & HondaFlagsSP.EPS_MODIFIED:
    return None

  if CP.carFingerprint == CAR.HONDA_CLARITY:
    eps_fw = next((fw.fwVersion for fw in CP.carFw if fw.ecu == "eps"), b"")
    bp, v = ([0, 5760, 10240] if b"-" in eps_fw else [0, 5760, 15360]), [0, 2560, 3840]
  elif CP.carFingerprint in EPS_MOD_TORQUE_LOOKUP:
    bp, v = EPS_MOD_TORQUE_LOOKUP[CP.carFingerprint]
  else:
    return None

  # mirror around zero for signed requests
  return [-x for x in bp[:0:-1]] + bp, [-x for x in v[:0:-1]] + v


class EpsModCarController:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.eps_mod_lookup = get_eps_mod_torque_lookup(CP, CP_SP)

  def get_apply_torque(self, limited_torque: float) -> int:
    bp, v = self.eps_mod_lookup
    return int(np.interp(-limited_torque * bp[-1], bp, v))
