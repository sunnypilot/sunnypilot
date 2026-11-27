"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
import time
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
  AudibleAlert.warningImmediateSystem: "critical.wav",
  AudibleAlert.warningImmediateUser: "dm_critical.wav",
  AudibleAlertSP.promptSingleLow: "prompt_single_low.wav",
  AudibleAlertSP.promptSingleHigh: "prompt_single_high.wav",
}

# Custom reactive robotic chirp IDs (non-overlapping with AudibleAlert / AudibleAlertSP enums)
CHIRP_SPEED_UP = 1001
CHIRP_SPEED_DOWN = 1002
CHIRP_STARTLED = 1003
CHIRP_BOOST = 1004
CHIRP_BOOKMARK = 1005
CHIRP_BLINKER = 1006

REACTIVE_CHIRP_IDS = {
  CHIRP_SPEED_UP,
  CHIRP_SPEED_DOWN,
  CHIRP_STARTLED,
  CHIRP_BOOST,
  CHIRP_BOOKMARK,
  CHIRP_BLINKER,
}

SET_SPEED_NA = 255
CHIRP_COOLDOWN = 0.6  # minimum seconds between reactive chirps


def _adsr(n: int, sr: int, attack: float = 0.012, release: float = 0.035) -> np.ndarray:
  env = np.ones(n, dtype=np.float32)
  a_n = min(n // 2, int(attack * sr))
  r_n = min(n // 2, int(release * sr))
  if a_n > 0:
    env[:a_n] = np.linspace(0.0, 1.0, a_n, dtype=np.float32)
  if r_n > 0:
    env[-r_n:] = np.linspace(1.0, 0.0, r_n, dtype=np.float32)
  return env


def synth_emo_chirp(
  f_start: float,
  f_end: float,
  duration: float,
  sr: int = 48000,
  vibrato_hz: float = 0.0,
  vibrato_depth: float = 0.0,
  gain: float = 0.85,
) -> np.ndarray:
  """Synthesize a bright, bubbly EMO-style harmonic chirp in pure NumPy."""
  n = max(1, int(sr * duration))
  t = np.arange(n, dtype=np.float32) / sr
  p = t / max(duration, 1e-6)
  s_curve = p * p * (3.0 - 2.0 * p)
  freq = f_start + (f_end - f_start) * s_curve
  if vibrato_hz > 0.0:
    freq = freq + vibrato_depth * np.sin(2.0 * np.pi * vibrato_hz * t)
  phase = 2.0 * np.pi * np.cumsum(freq) / sr
  sig = (
    0.66 * np.sin(phase)
    + 0.24 * np.sin(2.0 * phase + 0.35)
    + 0.10 * np.sin(3.0 * phase)
  )
  env = _adsr(n, sr, attack=min(0.012, duration * 0.2), release=min(0.045, duration * 0.35))
  return np.clip(sig * env * gain, -0.98, 0.98).astype(np.float32)


def _sil(duration: float, sr: int = 48000) -> np.ndarray:
  return np.zeros(int(sr * duration), dtype=np.float32)


def build_procedural_sounds(sr: int = 48000) -> dict[int, np.ndarray]:
  """Build bubbly EMO chirps in pure NumPy (used for reactive chirps and guaranteed WAV fallback)."""
  return {
    # Core alert fallbacks (in case WAV LFS files are unavailable on device)
    AudibleAlert.engage: np.concatenate([
      synth_emo_chirp(660, 1020, 0.10, sr, gain=0.86),
      _sil(0.025, sr),
      synth_emo_chirp(1020, 1580, 0.18, sr, vibrato_hz=24, vibrato_depth=28, gain=0.90),
    ]),
    AudibleAlert.disengage: np.concatenate([
      synth_emo_chirp(1080, 740, 0.12, sr, gain=0.82),
      _sil(0.025, sr),
      synth_emo_chirp(700, 440, 0.18, sr, gain=0.80),
    ]),
    AudibleAlert.refuse: np.concatenate([
      synth_emo_chirp(480, 340, 0.11, sr, vibrato_hz=32, vibrato_depth=28, gain=0.85),
      _sil(0.04, sr),
      synth_emo_chirp(390, 270, 0.15, sr, vibrato_hz=32, vibrato_depth=28, gain=0.85),
    ]),
    AudibleAlert.preAlert: synth_emo_chirp(860, 1480, 0.20, sr, vibrato_hz=26, vibrato_depth=22, gain=0.84),
    AudibleAlertSP.promptSingleLow: synth_emo_chirp(620, 500, 0.18, sr, gain=0.80),
    AudibleAlertSP.promptSingleHigh: synth_emo_chirp(1080, 1420, 0.16, sr, gain=0.84),
    AudibleAlert.prompt: np.concatenate([
      synth_emo_chirp(920, 1340, 0.11, sr, gain=0.88),
      _sil(0.03, sr),
      synth_emo_chirp(1340, 1040, 0.16, sr, gain=0.86),
    ]),
    AudibleAlert.promptRepeat: np.concatenate([
      synth_emo_chirp(960, 1380, 0.11, sr, gain=0.88),
      _sil(0.03, sr),
      synth_emo_chirp(1380, 1060, 0.15, sr, gain=0.86),
      _sil(0.28, sr),
    ]),
    AudibleAlert.promptDistracted: np.concatenate([
      synth_emo_chirp(840, 1280, 0.09, sr, gain=0.90),
      _sil(0.025, sr),
      synth_emo_chirp(980, 1480, 0.12, sr, vibrato_hz=22, vibrato_depth=20, gain=0.90),
      _sil(0.30, sr),
    ]),
    AudibleAlert.warningSoft: np.concatenate([
      synth_emo_chirp(1380, 1680, 0.10, sr, gain=0.94),
      _sil(0.025, sr),
      synth_emo_chirp(1680, 1260, 0.14, sr, gain=0.94),
      _sil(0.22, sr),
    ]),
    AudibleAlert.warningImmediateSystem: np.concatenate([
      synth_emo_chirp(1520, 1880, 0.09, sr, gain=0.96),
      _sil(0.02, sr),
      synth_emo_chirp(1520, 1880, 0.09, sr, gain=0.96),
      _sil(0.02, sr),
      synth_emo_chirp(1880, 1400, 0.12, sr, gain=0.96),
      _sil(0.18, sr),
    ]),
    AudibleAlert.warningImmediateUser: np.concatenate([
      synth_emo_chirp(1520, 1880, 0.09, sr, gain=0.96),
      _sil(0.02, sr),
      synth_emo_chirp(1520, 1880, 0.09, sr, gain=0.96),
      _sil(0.02, sr),
      synth_emo_chirp(1880, 1400, 0.12, sr, gain=0.96),
      _sil(0.18, sr),
    ]),
    # Reactive chirps for driving & user interactions
    CHIRP_SPEED_UP: np.concatenate([
      synth_emo_chirp(880, 1180, 0.075, sr, gain=0.72),
      _sil(0.015, sr),
      synth_emo_chirp(1180, 1520, 0.09, sr, gain=0.75),
    ]),
    CHIRP_SPEED_DOWN: np.concatenate([
      synth_emo_chirp(1220, 940, 0.075, sr, gain=0.70),
      _sil(0.015, sr),
      synth_emo_chirp(940, 680, 0.09, sr, gain=0.70),
    ]),
    CHIRP_STARTLED: np.concatenate([
      synth_emo_chirp(720, 1680, 0.11, sr, vibrato_hz=38, vibrato_depth=45, gain=0.82),
      _sil(0.02, sr),
      synth_emo_chirp(1480, 980, 0.10, sr, gain=0.78),
    ]),
    CHIRP_BOOST: np.concatenate([
      synth_emo_chirp(640, 1040, 0.07, sr, gain=0.76),
      _sil(0.015, sr),
      synth_emo_chirp(1040, 1640, 0.13, sr, vibrato_hz=28, vibrato_depth=35, gain=0.80),
    ]),
    CHIRP_BOOKMARK: np.concatenate([
      synth_emo_chirp(980, 1380, 0.07, sr, gain=0.78),
      _sil(0.02, sr),
      synth_emo_chirp(1240, 1720, 0.10, sr, vibrato_hz=24, vibrato_depth=25, gain=0.82),
    ]),
    CHIRP_BLINKER: synth_emo_chirp(920, 1180, 0.065, sr, gain=0.55),
  }


class RoboticSoundPack:
  """Manages pre-loaded robotic voice/chirp buffers and reactive driving chirps for Soundd."""

  def __init__(self, params, sample_rate: int = 48000):
    self._params = params
    self._sample_rate = sample_rate
    self.enabled: bool = self._params.get_bool("MiciRoboticUI")
    self.sounds: dict[int, np.ndarray] = {}

    # Edge-detection state for reactive chirps
    self._prev_set_speed: float = SET_SPEED_NA
    self._prev_blinker: bool = False
    self._last_chirp_time: float = 0.0

  def load(self) -> None:
    # Start with guaranteed pure-NumPy procedural chirps so soundd never fails if LFS WAVs are missing
    self.sounds = build_procedural_sounds(self._sample_rate)

    for alert_id, filename in ROBOTIC_SOUND_FILES.items():
      path = os.path.join(ROBOTIC_SOUNDS_DIR, filename)
      if not os.path.exists(path):
        cloudlog.warning(f"Robotic sound file missing, using procedural fallback: {path}")
        continue
      try:
        with wave.open(path, "r") as wavefile:
          if (
            wavefile.getnchannels() != 1
            or wavefile.getsampwidth() != 2
            or wavefile.getframerate() != self._sample_rate
          ):
            cloudlog.warning(f"Robotic sound format mismatch, using procedural fallback: {path}")
            continue
          length = wavefile.getnframes()
          if length > 0:
            self.sounds[alert_id] = np.frombuffer(wavefile.readframes(length), dtype=np.int16).astype(np.float32) / (2**16 / 2)
      except Exception as e:
        cloudlog.warning(f"Failed to load robotic WAV (possible Git LFS pointer), using procedural fallback: {path} ({e})")

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

  def detect_reactive_chirp(self, sm, now: float | None = None) -> int | None:
    """Detect driving/user events that should emit a cute one-shot robotic chirp."""
    if not self.enabled:
      return None

    t = time.monotonic() if now is None else now
    if t - self._last_chirp_time < CHIRP_COOLDOWN:
      return None

    chirp: int | None = None

    if sm.updated.get("userBookmark") or sm.updated.get("bookmarkButton"):
      chirp = CHIRP_BOOKMARK
    elif sm.updated.get("carState"):
      cs = sm["carState"]
      v_cruise = cs.vCruiseCluster
      if v_cruise == 0.0 and sm.valid.get("controlsState"):
        v_cruise = sm["controlsState"].deprecated.vCruise

      cruise_set = 0 < v_cruise < SET_SPEED_NA
      if cruise_set and self._prev_set_speed != SET_SPEED_NA and v_cruise != self._prev_set_speed:
        chirp = CHIRP_SPEED_UP if v_cruise > self._prev_set_speed else CHIRP_SPEED_DOWN
      self._prev_set_speed = v_cruise

      blinker = bool(cs.leftBlinker or cs.rightBlinker)
      if chirp is None and blinker and not self._prev_blinker:
        chirp = CHIRP_BLINKER
      self._prev_blinker = blinker

      if chirp is None and not cs.standstill:
        if cs.aEgo < -3.0:
          chirp = CHIRP_STARTLED
        elif cs.aEgo > 2.2:
          chirp = CHIRP_BOOST

    if chirp is not None:
      self._last_chirp_time = t
    return chirp
