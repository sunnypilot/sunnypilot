#!/usr/bin/env python3

from openpilot.selfdrive.car import make_can_msg
from openpilot.selfdrive.car.toyota.values import TSS2_CAR

LEFT_BLIND_SPOT = b'\x41'
RIGHT_BLIND_SPOT = b'\x42'

class SPontroller:
    def __init__(self, CP):
        #self._enabled = ENABLED
        self.left_blindspot_debug_enabled = False
        self.right_blindspot_debug_enabled = False
        self.last_blindspot_frame = 0


    def _create_debug_msg(self, lr, enable):
        if enable:
            m = lr + b'\x02\x10\x60\x00\x00\x00\x00'
        else:
            m = lr + b'\x02\x10\x01\x00\x00\x00\x00'
        return make_can_msg(0x750, m, 0)

    def _create_poll_status_msg(self, lr):
        m = lr + b'\x02\x21\x69\x00\x00\x00\x00'
        return make_can_msg(0x750, m, 0)

    def get_can_sends(self, frame, v_ego, can_sends):
        if not self._enabled or frame <= 200:
            return can_sends

        def handle_blindspot(side, enabled, frame_diff, rate_divisor):
            if not enabled:
                if self._blind_spot_always_on or v_ego > 6: # eagle eye camera will stop working if right bsm is switched on under 6m/s
                    can_sends.append(self._create_debug_msg(side, True))
                    return True
            else:
                if not self._blind_spot_always_on and frame - frame_diff > 50:
                    can_sends.append(self._create_debug_msg(side, False))
                    return False
                if frame % self._blind_spot_rate == rate_divisor:
                    can_sends.append(self._create_poll_status_msg(side))
                    self._blind_spot_frame = frame
            return enabled

        # left bsm
        self._blind_spot_debug_enabled_left = handle_blindspot(
            LEFT_BLIND_SPOT,
            self._blind_spot_debug_enabled_left,
            self._blind_spot_frame,
            0
        )

        # right bsm
        self._blind_spot_debug_enabled_right = handle_blindspot(
            RIGHT_BLIND_SPOT,
            self._blind_spot_debug_enabled_right,
            self._blind_spot_frame,
            self._blind_spot_rate / 2
        )

        return can_sends