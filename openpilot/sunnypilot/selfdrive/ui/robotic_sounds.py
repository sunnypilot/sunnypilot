"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
import wave

import numpy as np

from openpilot.cereal import custom, log
from openpilot.common.basedir import BASEDIR
from openpilot.common.swaglog import cloudlog

AudibleAlert = log.SelfdriveState.AudibleAlert
AudibleAlertSP = custom.SelfdriveStateSP.AudibleAlert

ROBOTIC_SOUNDS_DIR = os.path.join(BASEDIR, "openpilot/sunnypilot/selfdrive/assets/sounds/robotic")

ROBOTIC_SOUND_FILES: dict[int, str] = {
  AudibleAlert.engage: "engage.wav",
  AudibleAlert.disengage: "disengage.wav",
  AudibleAlert.refuse: "refuse.wav",
  AudibleAlert.prompt: "warning.wav",
  AudibleAlert.promptRepeat: "warning_repeat.wav",
  AudibleAlert.promptDistracted: "dm_warning.wav",
  AudibleAlert.preAlert: "pre_alert.wav",
  AudibleAlert.warningSoft: "critical.wav",
  AudibleAlert.warningImmediate: "dm_critical.wav",
  AudibleAlertSP.promptSingleLow: "prompt_single_low.wav",
  AudibleAlertSP.promptSingleHigh: "prompt_single_high.wav",
}


class RoboticSoundPack:
  """Manages pre-loaded robotic voice/chirp WAV buffers for Soundd when MiciRoboticUI is active."""

  def __init__(self, params, sample_rate: int = 48000):
    self._params = params
    self._sample_rate = sample_rate
    self.enabled: bool = self._params.get_bool("MiciRoboticUI")
    self.sounds: dict[int, np.ndarray] = {}

  def load(self) -> None:
    self.sounds = {}
    for alert_id, filename in ROBOTIC_SOUND_FILES.items():
      path = os.path.join(ROBOTIC_SOUNDS_DIR, filename)
      if not os.path.exists(path):
        cloudlog.warning(f"Robotic sound file missing: {path}")
        continue
      with wave.open(path, "r") as wavefile:
        assert wavefile.getnchannels() == 1
        assert wavefile.getsampwidth() == 2
        assert wavefile.getframerate() == self._sample_rate
        length = wavefile.getnframes()
        self.sounds[alert_id] = np.frombuffer(wavefile.readframes(length), dtype=np.int16).astype(np.float32) / (2**16 / 2)

  def refresh_param(self) -> bool:
    """Refresh MiciRoboticUI param; returns True if the enabled state changed."""
    new_val = self._params.get_bool("MiciRoboticUI")
    changed = new_val != self.enabled
    self.enabled = new_val
    return changed

  def get_buffer(self, alert_id: int, default_sounds: dict[int, np.ndarray]) -> np.ndarray:
    if self.enabled and alert_id in self.sounds:
      return self.sounds[alert_id]
    return default_sounds[alert_id]
