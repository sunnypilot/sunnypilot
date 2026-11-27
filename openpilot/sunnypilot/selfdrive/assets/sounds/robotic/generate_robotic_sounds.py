#!/usr/bin/env python3
"""Generate EMO-inspired robotic chirps and vocoded voice alert WAVs (48 kHz, mono, 16-bit PCM).

Run this script whenever tweaking the robotic sound pack:
  python3 openpilot/sunnypilot/selfdrive/assets/sounds/robotic/generate_robotic_sounds.py
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import wave

import numpy as np

SAMPLE_RATE = 48000
MAX_INT16 = 32767
OUT_DIR = Path(__file__).resolve().parent


def write_wav(path: Path, samples: np.ndarray) -> None:
  clipped = np.clip(samples, -1.0, 1.0)
  pcm = (clipped * MAX_INT16).astype(np.int16)
  with wave.open(str(path), "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(pcm.tobytes())


def adsr(n: int, attack: float = 0.015, release: float = 0.04) -> np.ndarray:
  env = np.ones(n, dtype=np.float32)
  a_n = min(n // 2, int(attack * SAMPLE_RATE))
  r_n = min(n // 2, int(release * SAMPLE_RATE))
  if a_n > 0:
    env[:a_n] = np.linspace(0.0, 1.0, a_n, dtype=np.float32)
  if r_n > 0:
    env[-r_n:] = np.linspace(1.0, 0.0, r_n, dtype=np.float32)
  return env


def emo_chirp(f_start: float, f_end: float, duration: float, vibrato_hz: float = 0.0, vibrato_depth: float = 0.0, gain: float = 0.65) -> np.ndarray:
  """Synthesize an expressive EMO-like harmonic chirp with smooth pitch glide."""
  n = int(SAMPLE_RATE * duration)
  t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
  # Smooth cubic-ish frequency glide
  progress = t / max(duration, 1e-6)
  s_curve = progress * progress * (3.0 - 2.0 * progress)
  freq = f_start + (f_end - f_start) * s_curve
  if vibrato_hz > 0.0:
    freq = freq + vibrato_depth * np.sin(2.0 * np.pi * vibrato_hz * t)
  phase = 2.0 * np.pi * np.cumsum(freq) / SAMPLE_RATE

  # Warm robotic timbre: fundamental + soft 2nd & 3rd harmonics
  sig = (
    0.72 * np.sin(phase)
    + 0.22 * np.sin(2.0 * phase + 0.3)
    + 0.08 * np.sin(3.0 * phase)
  )
  env = adsr(n, attack=min(0.015, duration * 0.2), release=min(0.055, duration * 0.35))
  return (sig * env * gain).astype(np.float32)


def silence(duration: float) -> np.ndarray:
  return np.zeros(int(SAMPLE_RATE * duration), dtype=np.float32)


def robotize_voice(samples: np.ndarray, carrier_hz: float = 165.0) -> np.ndarray:
  """Apply a clean EMO-style robotic vocoder / comb-resonance effect while keeping speech crisp."""
  n = len(samples)
  if n == 0:
    return samples
  t = np.arange(n, dtype=np.float32) / SAMPLE_RATE

  # Normalize speech input
  peak = float(np.max(np.abs(samples)))
  if peak > 1e-5:
    samples = samples / peak

  # Short metallic comb resonance (~5.5 ms delay) for unmistakable robot character
  delay = int(0.0055 * SAMPLE_RATE)
  comb = samples.copy()
  if delay < n:
    comb[delay:] += 0.42 * samples[:-delay]

  # Gentle ring modulation blended with intelligible dry+comb voice
  carrier = 0.65 * np.sin(2.0 * np.pi * carrier_hz * t) + 0.35 * np.sin(2.0 * np.pi * carrier_hz * 2.0 * t)
  ring = comb * carrier
  blended = 0.62 * comb + 0.38 * ring

  # Soft saturation & normalization
  blended = np.tanh(blended * 1.45)
  peak = float(np.max(np.abs(blended)))
  if peak > 1e-5:
    blended = blended / peak * 0.94
  return blended.astype(np.float32)


def synthesize_robotic_phrase(text: str, rate: int = 205, carrier_hz: float = 175.0) -> np.ndarray | None:
  """Render a short spoken phrase via macOS `say` + `ffmpeg`/`afconvert`, then robotize it."""
  say_bin = shutil.which("say")
  ffmpeg_bin = shutil.which("ffmpeg")
  if not say_bin or not ffmpeg_bin:
    return None

  with tempfile.TemporaryDirectory() as tmpdir:
    aiff_path = Path(tmpdir) / "speech.aiff"
    wav_path = Path(tmpdir) / "speech.wav"
    # Use a crisp clear voice ("Samantha" or system default) pitched up slightly via ffmpeg asetrate
    cmd_say = [say_bin, "-r", str(rate), "-o", str(aiff_path), text]
    subprocess.run(cmd_say, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Convert to 48kHz mono 16-bit WAV, slight pitch-up (+12%) for cute EMO-like robot timbre, trim silence
    cmd_ff = [
      ffmpeg_bin, "-y", "-i", str(aiff_path),
      "-af", "silenceremove=start_periods=1:start_threshold=-40dB:stop_periods=1:stop_threshold=-40dB,asetrate=22050*1.12,aresample=48000",
      "-ac", "1", "-ar", str(SAMPLE_RATE), "-sample_fmt", "s16",
      str(wav_path),
    ]
    subprocess.run(cmd_ff, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with wave.open(str(wav_path), "rb") as wf:
      raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return robotize_voice(raw, carrier_hz=carrier_hz)


def build_all_sounds() -> None:
  # 1. EMO-style expressive chirps & vocalizations (punchy & bubbly loudness matching stock WAVs)
  engage = np.concatenate([
    emo_chirp(660, 1020, 0.11, gain=0.88),
    silence(0.025),
    emo_chirp(1020, 1580, 0.19, vibrato_hz=24, vibrato_depth=28, gain=0.94),
  ])
  write_wav(OUT_DIR / "engage.wav", engage)

  disengage = np.concatenate([
    emo_chirp(1080, 740, 0.13, gain=0.86),
    silence(0.025),
    emo_chirp(700, 440, 0.19, gain=0.84),
  ])
  write_wav(OUT_DIR / "disengage.wav", disengage)

  refuse = np.concatenate([
    emo_chirp(480, 340, 0.12, vibrato_hz=32, vibrato_depth=28, gain=0.88),
    silence(0.04),
    emo_chirp(390, 270, 0.16, vibrato_hz=32, vibrato_depth=28, gain=0.88),
  ])
  write_wav(OUT_DIR / "refuse.wav", refuse)

  pre_alert = emo_chirp(860, 1480, 0.22, vibrato_hz=26, vibrato_depth=22, gain=0.88)
  write_wav(OUT_DIR / "pre_alert.wav", pre_alert)

  prompt_low = emo_chirp(620, 500, 0.19, gain=0.84)
  write_wav(OUT_DIR / "prompt_single_low.wav", prompt_low)

  prompt_high = emo_chirp(1080, 1420, 0.17, gain=0.88)
  write_wav(OUT_DIR / "prompt_single_high.wav", prompt_high)

  # 2. Hybrid chirp + vocoded robotic spoken phrases for warnings & critical alerts
  def hybrid(intro: np.ndarray, phrase: str, fallback: np.ndarray, tail_pause: float = 0.0, carrier_hz: float = 175.0) -> np.ndarray:
    voice = synthesize_robotic_phrase(phrase, carrier_hz=carrier_hz)
    body = voice if voice is not None else fallback
    parts = [intro, silence(0.04), body]
    if tail_pause > 0.0:
      parts.append(silence(tail_pause))
    return np.concatenate(parts)

  warning = hybrid(
    emo_chirp(820, 1120, 0.12, gain=0.65),
    "Heads up",
    emo_chirp(1120, 880, 0.22, gain=0.65),
    carrier_hz=185.0,
  )
  write_wav(OUT_DIR / "warning.wav", warning)

  warning_repeat = hybrid(
    emo_chirp(860, 1180, 0.12, gain=0.68),
    "Attention",
    emo_chirp(1180, 900, 0.22, gain=0.68),
    tail_pause=0.35,
    carrier_hz=185.0,
  )
  write_wav(OUT_DIR / "warning_repeat.wav", warning_repeat)

  dm_warning = hybrid(
    np.concatenate([emo_chirp(740, 1080, 0.10, gain=0.68), silence(0.03), emo_chirp(880, 1240, 0.10, gain=0.68)]),
    "Eyes on road",
    emo_chirp(1050, 780, 0.25, gain=0.68),
    tail_pause=0.35,
    carrier_hz=190.0,
  )
  write_wav(OUT_DIR / "dm_warning.wav", dm_warning)

  critical = hybrid(
    np.concatenate([emo_chirp(1320, 1520, 0.11, gain=0.80), silence(0.03), emo_chirp(1520, 1320, 0.11, gain=0.80)]),
    "Take control",
    emo_chirp(1480, 1100, 0.26, gain=0.80),
    tail_pause=0.28,
    carrier_hz=160.0,
  )
  write_wav(OUT_DIR / "critical.wav", critical)

  dm_critical = hybrid(
    np.concatenate([
      emo_chirp(1450, 1720, 0.09, gain=0.85),
      silence(0.025),
      emo_chirp(1450, 1720, 0.09, gain=0.85),
    ]),
    "Take control now",
    emo_chirp(1680, 1200, 0.28, gain=0.85),
    tail_pause=0.22,
    carrier_hz=150.0,
  )
  write_wav(OUT_DIR / "dm_critical.wav", dm_critical)

  print(f"Generated 11 robotic WAV files in {OUT_DIR}")


if __name__ == "__main__":
  build_all_sounds()
