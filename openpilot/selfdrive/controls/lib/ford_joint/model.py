"""Nominal older-PSCM request recurrence for the opt-in joint encoder.

The held fields, filter, slow/fast latch and zero internal I are estimates.
Calibration is packaged numerical data, never loaded from an ECU image.
"""

import bisect
import json
import struct
from pathlib import Path

DT = 0.008


class Calibration:
  def __init__(self):
    self.entries = json.loads(Path(__file__).with_name('calibration.json').read_text())['entries']

  def read(self, address, fmt='f'):
    item = self.entries[hex(address)]
    if item['format'] != fmt:
      raise ValueError(f'Unexpected calibration format: {address:x}')
    return tuple(item['values'])

  def f(self, address):
    return self.read(address)[0]

  def b(self, address):
    return self.read(address, 'B')[0]

  def h(self, address):
    return self.read(address, 'H')[0]


def clip(x, lo, hi):
  return min(max(x, lo), hi)


def slew(x, target, rate):
  return x + clip(target - x, -rate * DT, rate * DT)


def bracket(x, breakpoints):
  i = max(0, bisect.bisect_right(breakpoints, x) - 1)
  if i == len(breakpoints) - 1 or x <= breakpoints[0]:
    return i, 0
  return i, min(255, int((x - breakpoints[i]) * 256 / (breakpoints[i + 1] - breakpoints[i])))


def interp(tab, idx, frac):
  return tab[idx] if not frac else tab[idx] + (tab[idx + 1] - tab[idx]) * frac / 256


def interp_int(tab, idx, frac):
  if not frac:
    return tab[idx]
  d = tab[idx + 1] - tab[idx]
  return tab[idx] + (1 if d >= 0 else -1) * (abs(d) * frac // 256)


def f32(x):
  return struct.unpack('<f', struct.pack('<f', x))[0]


def interp_f32(tab, idx, frac):
  return tab[idx] if not frac else f32(tab[idx] + f32(f32(tab[idx + 1] - tab[idx]) * frac) / 256)


def bracket_f32(x, breakpoints):
  i = max(0, bisect.bisect_right(breakpoints, x) - 1)
  if i == len(breakpoints) - 1 or x <= breakpoints[0]:
    return i, 0
  fraction = f32(f32(f32(x - breakpoints[i]) / f32(breakpoints[i + 1] - breakpoints[i])) * 256)
  return i, min(255, int(fraction))


class MainRequest:
  def __init__(self, cal=None, *, native_lookup=False):
    self.cal = cal or Calibration()
    c = self.cal
    self.speed_bp = c.read(0xFEF25E40, '8H')
    self.distance_bp = c.read(0xFEF25D98, '10f')
    self.tables = {
      a: c.read(a, fmt)
      for a, fmt in [
        (0xFEF258FC, '8B'),
        (0xFEF25B78, '8f'),
        (0xFEF25B98, '8f'),
        (0xFEF25BB8, '8f'),
        (0xFEF25BE8, '8f'),
        (0xFEF25C60, '8H'),
        (0xFEF25D70, '10f'),
        (0xFEF25DC0, '10f'),
        (0xFEF25DE8, '10f'),
        (0xFEF25E20, '8H'),
        (0xFEF25E30, '8H'),
      ]
    }
    self.c0 = self.c1 = self.c2 = self.c3 = self.c0_i = self.filtered = 0.0
    self.preview_t = c.f(0xFEF25A58)
    self.fast = False
    # Opt-in preserves the reproducibility of archived exploratory replays.
    # New inverse-allocation experiments use this corrected native lookup path.
    self.native_lookup = native_lookup

  def step(self, speed_kmh, c0, c1, c2=0.0, c3=0.0, active=True, interaction=1.0, freeze_i=False, release_i=False, special_release=False, indicator=False):
    c = self.cal
    # 180f4e: input state, speed lookup, history-dependent slew selection.
    lookup_speed = f32(speed_kmh) if self.native_lookup else speed_kmh
    si, sf = bracket(int(lookup_speed * 256) & 0xFFFF, self.speed_bp)
    self.c3 = slew(self.c3, c3, c.f(0xFEF259E8 if active else 0xFEF259EC))
    c2_target = c2 + interp(self.tables[0xFEF25BE8], si, sf) * c3
    self.c2 = slew(self.c2, c2_target, c.f(0xFEF259E4 if active else 0xFEF259F0))
    if interaction < c.f(0xFEF259F4):
      self.fast = True
    elif abs(c0) <= c.f(0xFEF25A00) and abs(c1) <= c.f(0xFEF25A10):
      self.fast = False
    c1rate = c.f(0xFEF25A14 if not active else (0xFEF25A0C if self.fast else 0xFEF25A08))
    c0rate = c.f(0xFEF25A04 if not active else (0xFEF259FC if self.fast else 0xFEF259F8))
    self.c1 = slew(self.c1, c1, c1rate)
    self.c0 = slew(self.c0, c0, c0rate)
    # 181270: EDL C0/time derivative and mode shortening gains are zero.
    target_t = clip(c.f(0xFEF25A58) - c.f(0xFEF2596C) * abs(self.c2) - (c.f(0xFEF259A0) if indicator else 0), c.f(0xFEF2599C), c.f(0xFEF25A58))
    self.preview_t += clip(target_t - self.preview_t, c.f(0xFEF259A4) * DT, c.f(0xFEF259A8) * DT)
    lookup_interp = interp_f32 if self.native_lookup else interp
    distance = clip(
      f32(f32(lookup_speed * f32(0.28)) * f32(self.preview_t)) if self.native_lookup else speed_kmh * 0.28 * self.preview_t,
      lookup_interp(self.tables[0xFEF25BB8], si, sf),
      lookup_interp(self.tables[0xFEF25B98], si, sf),
    )
    di, df = (bracket_f32 if self.native_lookup else bracket)(distance, self.distance_bp)
    g0 = lookup_interp(self.tables[0xFEF25DE8], di, df)
    g1 = lookup_interp(self.tables[0xFEF25DC0], di, df)
    g3 = lookup_interp(self.tables[0xFEF25D70], di, df)
    opposite = abs(self.c0) > c.h(0xFEF25A70) / 8192 and abs(self.c0_i) > c.h(0xFEF25A72) / 8192 and self.c0 * self.c0_i < 0
    forced_release = special_release or opposite
    if active and not release_i and not forced_release:
      delta = 0 if freeze_i else clip(self.c0, c.f(0xFEF25968), c.f(0xFEF25960)) * interp(self.tables[0xFEF25B78], si, sf)
      self.c0_i = clip(self.c0_i + delta * DT, c.f(0xFEF25964), c.f(0xFEF2595C))
    else:
      rate = (c.h(0xFEF25A74) if special_release else interp_int(self.tables[0xFEF25C60], si, sf)) if forced_release else c.h(0xFEF25A60)
      self.c0_i = slew(self.c0_i, 0, rate / 512)
    req = g3 * self.c3 + g1 * self.c1 + g0 * (self.c0 + self.c0_i) + self.c2

    def contribution(lo, hi, x):
      return clip(abs(x) - lo, 0, max(1e-6, hi - lo)) / max(1e-6, hi - lo)

    v = speed_kmh * 0.28
    heading_weight = contribution(c.b(0xFEF25AA5) / 128, c.b(0xFEF25AA6) / 128, self.c1 * v)
    curvature_weight = contribution(c.b(0xFEF25AA1) / 64, c.b(0xFEF25AA2) / 64, self.c2 * v * v)
    rate_weight = contribution(c.b(0xFEF25A9E) / 32, c.b(0xFEF25A9F) / 32, self.c3 * v * v * v)
    alpha = min(
      c.b(0xFEF25AA4) / 256,
      (interp_int(self.tables[0xFEF258FC], si, sf) + c.b(0xFEF25AA7) * heading_weight + c.b(0xFEF25AA3) * curvature_weight + c.b(0xFEF25AA0) * rate_weight)
      / 256,
    )
    self.filtered += alpha * (req - self.filtered)
    return {
      'held_c0': self.c0,
      'held_c1': self.c1,
      'held_c2': self.c2,
      'held_c3': self.c3,
      'integral_c0': self.c0_i,
      'request_curvature': req,
      'filtered_curvature': self.filtered,
      'preview_distance': distance,
      'preview_time': self.preview_t,
      'fast_flag': int(self.fast),
      'speed_index': si,
      'speed_fraction': sf,
      'alpha': alpha,
      'g0': g0,
      'g1': g1,
      'accel_request': self.filtered * (speed_kmh / 3.6) ** 2,
      'accel_bound': interp_int(self.tables[0xFEF25E20], si, sf) / 8192,
      'c0_contribution': g0 * self.c0,
      'c1_contribution': g1 * self.c1,
      'c0_i_contribution': g0 * self.c0_i,
    }
