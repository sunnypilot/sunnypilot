"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log, custom
import numpy as np
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

LongPersonality = log.LongitudinalPersonality
AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality

# Acceleration Profiles mapped to AccelPersonality (eco/normal/sport)
MAX_ACCEL_PROFILES = {
    AccelPersonality.eco:       [2.0,  1.99,  1.88, 1.10, .500, .292, .15, .10],   # eco
    AccelPersonality.normal:    [2.0,  2.00,  1.94, 1.22, .635, .33, .22, .16],   # normal
    AccelPersonality.sport:     [2.0,  2.00,  2.00, 1.85, .800, .54, .32, .22],    # sport
}
MAX_ACCEL_BREAKPOINTS =         [0.,   4.,   6.,   9.,   16.,  25.,  30., 55.]

# Braking profiles mapped to LongPersonality (relaxed/standard/aggressive)
MIN_ACCEL_PROFILES = {
    LongPersonality.relaxed:    [-.0006, -.0006, -.010,  -.30,  -1.20],  # gentler braking
    LongPersonality.standard:   [-.0007, -.0007, -.012,  -.35,  -1.20],  # normal braking
    LongPersonality.aggressive: [-.0020, -.0008, -.014,  -.40,  -1.20],  # more aggressive braking
}
MIN_ACCEL_BREAKPOINTS =         [0.,   3.0,    11.,    14,  50.]

# Follow distance profiles mapped to LongPersonality (relaxed/standard/aggressive)
FOLLOW_PROFILES = {
    LongPersonality.relaxed:    [1.55, 1.65, 1.65, 1.80],  # more spread out
    LongPersonality.standard:   [1.45, 1.45, 1.45, 1.55],  # balanced
    LongPersonality.aggressive: [1.20, 1.25, 1.28, 1.35],  # tighter
}
FOLLOW_BREAKPOINTS =            [0.,   6.,   18.,  36.]


class VibePersonalityController:
    """Controller for acceleration and distance personalities"""

    def __init__(self):
        self.params = Params()
        self.frame = 0
        self.accel_personality = AccelPersonality.normal
        self.long_personality = LongPersonality.standard
        self.param_keys = {
            'accel_personality': 'AccelPersonality',
            'long_personality': 'LongitudinalPersonality',
            'enabled': 'VibePersonalityEnabled',
            'accel_enabled': 'VibeAccelPersonalityEnabled',
            'follow_enabled': 'VibeFollowPersonalityEnabled'
        }

    def _update_from_params(self):
        """Update personalities from params"""
        if self.frame % int(1. / DT_MDL) != 0:
            return

        accel_personality_int = int(self.params.get(self.param_keys['accel_personality']))
        self.accel_personality = accel_personality_int

        long_personality_int = int(self.params.get(self.param_keys['long_personality']))
        self.long_personality = long_personality_int

    def _get_toggle_state(self, key: str) -> bool:
        return self.params.get_bool(self.param_keys[key])

    def _set_toggle_state(self, key: str, value: bool):
        self.params.put_bool(self.param_keys[key], value)

    def set_accel_personality(self, personality: int) -> bool:
        self.accel_personality = personality
        self.params.put(self.param_keys['accel_personality'], str(personality))
        return True

    def cycle_accel_personality(self) -> int:
        personalities = [AccelPersonality.eco, AccelPersonality.normal, AccelPersonality.sport]
        current_idx = personalities.index(self.accel_personality)
        next_personality = personalities[(current_idx + 1) % len(personalities)]
        self.set_accel_personality(next_personality)
        return int(next_personality)

    def get_accel_personality(self) -> int:
        self._update_from_params()
        return int(self.accel_personality)

    def set_long_personality(self, personality: int) -> bool:
        self.long_personality = personality
        self.params.put(self.param_keys['long_personality'], str(personality))
        return True

    def cycle_long_personality(self) -> int:
        personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
        current_idx = personalities.index(self.long_personality)
        next_personality = personalities[(current_idx + 1) % len(personalities)]
        self.set_long_personality(next_personality)
        return int(next_personality)

    def get_long_personality(self) -> int:
        self._update_from_params()
        return int(self.long_personality)

    def toggle_personality(self): return self._toggle_flag('enabled')
    def toggle_accel_personality(self): return self._toggle_flag('accel_enabled')
    def toggle_follow_distance_personality(self): return self._toggle_flag('follow_enabled')

    def _toggle_flag(self, key):
        current = self._get_toggle_state(key)
        self._set_toggle_state(key, not current)
        return not current

    def set_personality_enabled(self, enabled: bool): self._set_toggle_state('enabled', enabled)
    def is_accel_enabled(self) -> bool: return self._get_toggle_state('enabled') and self._get_toggle_state('accel_enabled')
    def is_follow_enabled(self) -> bool: return self._get_toggle_state('enabled') and self._get_toggle_state('follow_enabled')
    def is_enabled(self) -> bool: return self._get_toggle_state('enabled') and (self._get_toggle_state('accel_enabled') or self._get_toggle_state('follow_enabled'))

    def get_accel_limits(self, v_ego: float) -> tuple[float, float]:
        """Get acceleration limits based on current personalities."""
        self._update_from_params()
        max_a = np.interp(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self.accel_personality])
        min_a = np.interp(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[self.long_personality])
        return float(min_a), float(max_a)

    def get_follow_distance_multiplier(self, v_ego: float) -> float:
        """Get dynamic following distance based on speed and personality"""
        self._update_from_params()
        return float(np.interp(v_ego, FOLLOW_BREAKPOINTS, FOLLOW_PROFILES[self.long_personality]))

    def get_min_accel(self, v_ego: float) -> float:
        return self.get_accel_limits(v_ego)[0]

    def get_max_accel(self, v_ego: float) -> float:
        return self.get_accel_limits(v_ego)[1]

    def reset(self):
        self.accel_personality = AccelPersonality.normal
        self.long_personality = LongPersonality.standard
        self.frame = 0

    def update(self):
        self.frame += 1
