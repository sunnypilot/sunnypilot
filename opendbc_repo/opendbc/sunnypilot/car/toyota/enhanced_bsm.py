"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from opendbc.car import structs
from opendbc.car.can_definitions import CanData
from opendbc.car.toyota import toyotacan
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP

LEFT_BLINDSPOT = b"\x41"
RIGHT_BLINDSPOT = b"\x42"
LEFT_SIDE = LEFT_BLINDSPOT[0]
RIGHT_SIDE = RIGHT_BLINDSPOT[0]

# BLINDSPOTD1/D2 aren't real distances despite the DBC name: verified against 3 real routes, values
# fall into 3 clean bands - idle (0), a small transitional-noise band (seen 1-31, rare: single-digit
# occurrence counts, present during side/state transitions), and two real zone codes (~46-47 and
# ~50-53, consistent across routes and cars - likely mirroring stock BSM's own ADJACENT/APPROACHING
# split). A plain nonzero check lets the noise band through as false "occupied" hits; gate on the
# real-zone floor instead - comfortably above every noise value seen, comfortably below neither zone code.
BLINDSPOT_NOISE_FLOOR = 35

# DEBUG also carries a 1-bit BLINDSPOT flag (byte 4) that isn't read here. Checked against the same
# route: stayed 0 across all frames, including every confirmed real detection - not a usable signal.


class EnhancedBsm:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.CP = CP
    self.CP_SP = CP_SP

  @property
  def enabled(self):
    return bool(self.CP_SP.flags & ToyotaFlagsSP.SP_ENHANCED_BSM)


class _BsmSideState:
  def __init__(self):
    self.blindspot = False
    self.counter = 0

  def update(self, distance_1, distance_2):
    # every fresh matching-side reading directly reflects the current occupancy check - this is not
    # a latch. A drop to an idle/noise reading on this exact side clears it immediately, same as the
    # original. The counter is purely a silence timeout for when this side stops responding entirely,
    # not a "hold the last detection for a while" mechanism.
    self.blindspot = distance_1 > BLINDSPOT_NOISE_FLOOR or distance_2 > BLINDSPOT_NOISE_FLOOR
    self.counter = 100

  def decay(self):
    self.counter = max(0, self.counter - 1)
    if self.counter == 0:
      self.blindspot = False


# Enhanced BSM (@arne182, @rav4kumar)
class EnhancedBsmCarState(EnhancedBsm):
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    super().__init__(CP, CP_SP)

    self._sides = {LEFT_SIDE: _BsmSideState(), RIGHT_SIDE: _BsmSideState()}

  def update(self, cp, frame: int) -> tuple[bool, bool]:
    # Let's keep all the commented out code for easy debug purposes in the future.
    distance_1 = cp.vl["DEBUG"].get('BLINDSPOTD1')
    distance_2 = cp.vl["DEBUG"].get('BLINDSPOTD2')
    side = cp.vl["DEBUG"].get('BLINDSPOTSIDE')

    if all(val is not None for val in [distance_1, distance_2, side]) and side in self._sides:
      self._sides[side].update(distance_1, distance_2)

    for side_state in self._sides.values():
      side_state.decay()

    return self._sides[LEFT_SIDE].blindspot, self._sides[RIGHT_SIDE].blindspot


class _BsmSideController:
  def __init__(self, addr_byte: bytes):
    self.addr_byte = addr_byte
    self.debug_enabled = False
    self.last_poll_frame = 0

  def update(self, frame: int, poll_phase: int, e_bsm_rate: int, always_on: bool, vego_ok: bool) -> list[CanData]:
    can_sends = []

    if not self.debug_enabled:
      if always_on or vego_ok:  # eagle eye camera will stop working if bsm is switched on under 6m/s
        can_sends.append(toyotacan.create_set_bsm_debug_mode(self.addr_byte, True))
        self.debug_enabled = True
        self.last_poll_frame = frame  # give the poll loop a fresh baseline so the stale-poll disable check below can't fire before the first real poll
    else:
      # no periodic re-assert: re-sending DiagnosticSessionControl(extendedSession) while already in that
      # session appears to make the ECU intermittently drop its own detection state (confirmed against a
      # real route - two reasserts landed inside an 8s window where the ECU went silent on that side).
      # send it once and leave it alone, matching the original, proven-stable behavior.
      if not always_on and frame - self.last_poll_frame > 50:
        can_sends.append(toyotacan.create_set_bsm_debug_mode(self.addr_byte, False))
        self.debug_enabled = False

      if frame % e_bsm_rate == poll_phase:
        can_sends.append(toyotacan.create_bsm_polling_status(self.addr_byte))
        self.last_poll_frame = frame

    return can_sends


# Enhanced BSM (@arne182, @rav4kumar)
class EnhancedBsmCarController(EnhancedBsm):
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    super().__init__(CP, CP_SP)

    self._left = _BsmSideController(LEFT_BLINDSPOT)
    self._right = _BsmSideController(RIGHT_BLINDSPOT)

  def update(self, CS: structs.CarState, frame: int, e_bsm_rate: int = 20, always_on: bool = True) -> list[CanData]:
    if frame <= 200:
      return []

    vego_ok = CS.out.vEgo > 6
    can_sends = self._left.update(frame, 0, e_bsm_rate, always_on, vego_ok)
    can_sends += self._right.update(frame, e_bsm_rate // 2, e_bsm_rate, always_on, vego_ok)
    return can_sends
