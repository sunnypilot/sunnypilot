"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections import deque
from dataclasses import dataclass, field
import math

import numpy as np

DEFAULT_SAMPLE_RATE = 16000
FRAME_RATE = 20.0          # micd publishes 800 samples @ 16kHz = 50ms (20 Hz)
FFT_SIZE = 1024            # ~64ms analysis window
NUM_BANDS = 12
HISTORY_FRAMES = 50        # 2.5 seconds of flux/energy history @ 20 Hz

# Tempo autocorrelation lag bounds @ 20 Hz: 7..17 frames -> 70..171 BPM
MIN_TEMPO_LAG = 7
MAX_TEMPO_LAG = 17

# Hysteresis thresholds for stable music detection (rejects road noise & talking)
ENTER_MUSIC_CONF = 0.58
EXIT_MUSIC_CONF = 0.36
MIN_ACTIVE_RMS = 0.012


@dataclass
class MusicState:
  is_music: bool = False
  confidence: float = 0.0
  beat_pulse: float = 0.0       # 0..1 sharp onset with smooth decay
  groove_phase: float = 0.0     # radians advancing at estimated tempo
  bpm: float = 116.0
  energy: float = 0.0           # 0..1 normalized musical loudness
  bands: tuple[float, ...] = field(default_factory=lambda: (0.0,) * NUM_BANDS)


class MusicAnalyzer:
  """Low-CPU pure-NumPy cabin music detector, beat tracker, and 12-band equalizer analyzer.

  Distinguishes ambient music from car road/wind noise and human speech by combining:
    1. Adaptive cabin noise-floor gating
    2. Spectral tonality (1 - spectral flatness) to reject broadband road/wind noise
    3. Musical bandwidth balance (bass + treble presence) to reject narrowband talking
    4. Rhythmic tempo periodicity (spectral flux autocorrelation at 70-171 BPM)
    5. Temporal energy continuity (speech has frequent inter-word silences)
  """

  def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
    self._sample_rate = sample_rate
    self._window = np.hanning(FFT_SIZE).astype(np.float32)
    self._ring = np.zeros(FFT_SIZE, dtype=np.float32)
    self._prev_mag: np.ndarray | None = None

    self._noise_floor: float = 0.008
    self._confidence: float = 0.0
    self._is_music: bool = False
    self._beat_pulse: float = 0.0
    self._groove_phase: float = 0.0
    self._bpm: float = 116.0
    self._energy: float = 0.0
    self._bands = np.zeros(NUM_BANDS, dtype=np.float32)

    self._flux_hist: deque[float] = deque(maxlen=HISTORY_FRAMES)
    self._active_hist: deque[float] = deque(maxlen=HISTORY_FRAMES)
    self._bass_flux_hist: deque[float] = deque(maxlen=20)

    self._build_frequency_masks(sample_rate)

  def _build_frequency_masks(self, sr: int) -> None:
    self._sample_rate = sr
    freqs = np.fft.rfftfreq(FFT_SIZE, d=1.0 / sr)
    self._freqs = freqs
    self._bass_mask = (freqs >= 55.0) & (freqs < 230.0)
    self._speech_mask = (freqs >= 300.0) & (freqs < 2400.0)
    self._treble_mask = (freqs >= 2800.0) & (freqs < min(7600.0, sr * 0.48))
    self._tonal_mask = (freqs >= 100.0) & (freqs < 4000.0)

    # 12 log-spaced equalizer bands (60 Hz .. 7200 Hz)
    edges = np.geomspace(60.0, min(7200.0, sr * 0.47), NUM_BANDS + 1)
    self._band_slices: list[tuple[int, int]] = []
    for i in range(NUM_BANDS):
      lo = int(np.searchsorted(freqs, edges[i]))
      hi = max(lo + 1, int(np.searchsorted(freqs, edges[i + 1])))
      self._band_slices.append((lo, min(hi, len(freqs))))

  @property
  def state(self) -> MusicState:
    return MusicState(
      is_music=self._is_music,
      confidence=self._confidence,
      beat_pulse=self._beat_pulse,
      groove_phase=self._groove_phase,
      bpm=self._bpm,
      energy=self._energy,
      bands=tuple(float(b) for b in self._bands),
    )

  def step_visual_decay(self, dt: float) -> MusicState:
    """Advance smooth 60 FPS groove phase and beat decay between 20 Hz audio chunks."""
    if self._is_music:
      rad_per_sec = (self._bpm / 60.0) * math.pi  # half-note sway cycle
      self._groove_phase = (self._groove_phase + rad_per_sec * dt) % (math.tau * 4.0)
    decay = math.exp(-dt * 7.5)
    self._beat_pulse *= decay
    if not self._is_music:
      self._bands *= math.exp(-dt * 6.0)
    return self.state

  def process_audio_bytes(self, data: bytes, sample_rate: int = DEFAULT_SAMPLE_RATE) -> MusicState:
    """Process a rawAudioData int16 PCM byte buffer from micd."""
    if not data:
      return self.state
    if sample_rate > 0 and sample_rate != self._sample_rate:
      self._build_frequency_masks(sample_rate)
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return self.process_samples(samples)

  def process_samples(self, samples: np.ndarray) -> MusicState:
    """Analyze a normalized float32 [-1, 1] mono audio chunk (~50 ms)."""
    n = len(samples)
    if n == 0:
      return self.state

    # Update rolling FFT window
    if n >= FFT_SIZE:
      self._ring[:] = samples[-FFT_SIZE:]
    else:
      self._ring[:-n] = self._ring[n:]
      self._ring[-n:] = samples

    rms = float(np.sqrt(np.mean(self._ring * self._ring)))

    # Slow adaptive cabin noise floor (tracks down quickly, tracks up very slowly)
    if rms < self._noise_floor:
      self._noise_floor = 0.85 * self._noise_floor + 0.15 * rms
    else:
      self._noise_floor = 0.996 * self._noise_floor + 0.004 * rms
    self._noise_floor = max(0.003, min(0.08, self._noise_floor))

    # Gate very quiet / pure-floor frames
    above_floor = rms > max(MIN_ACTIVE_RMS, self._noise_floor * 1.45)
    self._active_hist.append(1.0 if above_floor else 0.0)

    # FFT magnitude spectrum
    spec = np.abs(np.fft.rfft(self._ring * self._window)) / (FFT_SIZE * 0.5)
    power = spec * spec + 1e-12

    # 1. Spectral tonality (1 - flatness): music is tonal/harmonic; road noise is flat
    tonal_p = power[self._tonal_mask]
    geo_mean = float(np.exp(np.mean(np.log(tonal_p))))
    arith_mean = float(np.mean(tonal_p))
    flatness = geo_mean / max(arith_mean, 1e-12)
    tonality_score = float(np.clip((0.52 - flatness) / 0.36, 0.0, 1.0))

    # 2. Musical bandwidth balance: speech is concentrated in 300-2400Hz with weak bass+treble
    total_p = float(np.sum(power[1:])) + 1e-12
    bass_ratio = float(np.sum(power[self._bass_mask])) / total_p
    speech_ratio = float(np.sum(power[self._speech_mask])) / total_p
    treble_ratio = float(np.sum(power[self._treble_mask])) / total_p
    non_speech_ratio = bass_ratio + treble_ratio
    # Penalize narrowband vocal-only energy (speech_ratio > 0.78 and low bass+treble)
    bandwidth_score = float(np.clip(non_speech_ratio / 0.34, 0.0, 1.0))
    if speech_ratio > 0.80 and bass_ratio < 0.12:
      bandwidth_score *= 0.25

    # 3. Spectral flux & bass onset flux
    if self._prev_mag is None:
      flux = 0.0
      bass_flux = 0.0
    else:
      diff = np.maximum(0.0, spec - self._prev_mag)
      flux = float(np.sum(diff))
      bass_flux = float(np.sum(diff[self._bass_mask]))
    self._prev_mag = spec

    self._flux_hist.append(flux)
    self._bass_flux_hist.append(bass_flux)

    # 4. Tempo periodicity via normalized autocorrelation of spectral flux (70-171 BPM)
    rhythm_score = 0.0
    if len(self._flux_hist) >= MAX_TEMPO_LAG + 12:
      arr = np.array(self._flux_hist, dtype=np.float32)
      arr_centered = arr - np.mean(arr)
      denom = float(np.dot(arr_centered, arr_centered))
      if denom > 1e-9:
        best_corr = 0.0
        best_lag = 10
        for lag in range(MIN_TEMPO_LAG, MAX_TEMPO_LAG + 1):
          c = float(np.dot(arr_centered[:-lag], arr_centered[lag:])) / denom
          if c > best_corr:
            best_corr = c
            best_lag = lag
        rhythm_score = float(np.clip((best_corr - 0.14) / 0.32, 0.0, 1.0))
        if best_corr > 0.22:
          est_bpm = (60.0 * FRAME_RATE) / best_lag
          # Smooth BPM estimate
          self._bpm = 0.90 * self._bpm + 0.10 * float(np.clip(est_bpm, 75.0, 170.0))

    # 5. Temporal continuity (music fills frames steadily; talking has frequent pauses)
    continuity = float(np.mean(self._active_hist)) if self._active_hist else 0.0
    continuity_score = float(np.clip((continuity - 0.45) / 0.45, 0.0, 1.0))

    # Combined music frame score
    if not above_floor:
      frame_score = 0.0
    else:
      frame_score = (
        0.30 * tonality_score
        + 0.25 * bandwidth_score
        + 0.30 * rhythm_score
        + 0.15 * continuity_score
      )
      # Require both harmonic tonality AND either rhythmic lock or rich musical bandwidth
      if tonality_score < 0.22 or (rhythm_score < 0.15 and bandwidth_score < 0.45):
        frame_score *= 0.35

    # Smooth confidence with hysteresis (~1.4s attack, ~2.0s release @ 20 Hz)
    alpha = 0.055 if frame_score > self._confidence else 0.035
    self._confidence = (1.0 - alpha) * self._confidence + alpha * frame_score

    if not self._is_music and self._confidence >= ENTER_MUSIC_CONF:
      self._is_music = True
    elif self._is_music and self._confidence <= EXIT_MUSIC_CONF:
      self._is_music = False

    # Beat onset pulse (bass + overall flux spike above rolling mean)
    if self._is_music and len(self._bass_flux_hist) >= 6:
      bf_mean = float(np.mean(self._bass_flux_hist))
      bf_std = float(np.std(self._bass_flux_hist)) + 1e-6
      if bass_flux > bf_mean + 0.95 * bf_std and bass_flux > 0.015:
        strength = float(np.clip((bass_flux - bf_mean) / (2.2 * bf_std), 0.45, 1.0))
        self._beat_pulse = max(self._beat_pulse, strength)

    # Normalized energy & 12-band equalizer bars (log-compressed for lush visuals)
    self._energy = float(np.clip((rms - self._noise_floor) / max(0.10, self._noise_floor * 4.5), 0.0, 1.0))
    for i, (lo, hi) in enumerate(self._band_slices):
      band_mag = float(np.sqrt(np.mean(power[lo:hi])))
      # Log scale into 0..1 with slight treble tilt for lively equalizer shape
      tilt = 1.0 + 0.16 * i
      norm = float(np.clip(math.log1p(band_mag * 150.0 * tilt) / 2.0, 0.0, 1.0))
      if norm > self._bands[i]:
        self._bands[i] = 0.45 * self._bands[i] + 0.55 * norm
      else:
        self._bands[i] = 0.78 * self._bands[i] + 0.22 * norm

    return self.state
