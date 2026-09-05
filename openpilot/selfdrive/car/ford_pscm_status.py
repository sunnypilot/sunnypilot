"""Publish the Ford PSCM's actual CAN status without changing opendbc structs."""
import math

from opendbc.car import Bus
from opendbc.car.ford.values import FordFlags


MESSAGE = 'Lane_Assist_Data3_FD1'
SIGNALS = ('LatCtlSte_D_Stat', 'LatCtlLim_D_Stat', 'LatCtlCpblty_D_Stat', 'LaActDeny_B_Actl')


def populate_ford_pscm_status(CP, can_parsers, CS_SP, can_valid):
  if CP.brand != 'ford' or not CP.flags & FordFlags.CANFD:
    return
  status = CS_SP.init('fordPscmStatus')
  parser = can_parsers.get(Bus.pt)
  if parser is None:
    return
  values = parser.vl.get(MESSAGE, {})
  timestamps = parser.ts_nanos.get(MESSAGE, {})
  if any(signal not in values or signal not in timestamps for signal in SIGNALS):
    return
  received = timestamps[SIGNALS[0]]
  if received <= 0 or any(timestamps[signal] != received for signal in SIGNALS):
    return
  decoded = [values[signal] for signal in SIGNALS]
  if any(not math.isfinite(value) or int(value) != value or not 0 <= value <= maximum
         for value, maximum in zip(decoded, (7, 3, 3, 1), strict=True)):
    return
  status.canMonoTime = received
  status.lateralState, status.limit, status.capability = map(int, decoded[:3])
  status.denied = bool(decoded[3])
  # CI.update already checked all parser validity. Reading can_valid again here
  # would advance the parser's invalid-message counter a second time per tick.
  # Age is evaluated by the feedback consumer using this original CAN timestamp.
  status.valid = bool(can_valid)
