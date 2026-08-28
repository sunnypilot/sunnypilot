#!/usr/bin/env python3
"""Generate the temporary milestone celebration chime."""

import math
import wave
from array import array
from pathlib import Path


SAMPLE_RATE = 48_000
DURATION_SECONDS = 0.82
NOTES = (
  (0.00, 523.25),
  (0.11, 659.25),
  (0.22, 783.99),
)


def note_sample(age: float, frequency: float) -> float:
  if not 0 <= age <= 0.58:
    return 0.0
  attack = min(age / 0.008, 1.0)
  release = min((0.58 - age) / 0.15, 1.0)
  envelope = attack * release * math.exp(-3.8 * age)
  tone = math.sin(math.tau * frequency * age) + 0.16 * math.sin(math.tau * frequency * 2 * age)
  return envelope * tone


def main() -> None:
  output = Path(__file__).parents[4] / "openpilot/selfdrive/assets/sounds/milestone.wav"
  samples = array('h')
  for frame in range(round(SAMPLE_RATE * DURATION_SECONDS)):
    t = frame / SAMPLE_RATE
    value = 0.38 * sum(note_sample(t - start, frequency) for start, frequency in NOTES)
    samples.append(round(max(-1.0, min(1.0, value)) * 32767))

  with wave.open(str(output), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(samples.tobytes())


if __name__ == "__main__":
  main()
