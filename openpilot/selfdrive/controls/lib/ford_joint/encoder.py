"""Joint C0/C1 allocation with optional short causal target-trend preview.

No future tape, retained trajectory or maneuver modes. Preview duration is a
tuning parameter; the next-update accuracy constraint retains the current target.
"""

import copy
import ctypes
import math
import sys
from pathlib import Path
import numpy as np

from openpilot.selfdrive.controls.lib.ford_joint.model import DT, interp, interp_int
from openpilot.selfdrive.controls.lib.ford_joint.inverse import static_pair, quantize

class DoubleArray(np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS')):
  @classmethod
  def from_param(cls, value):
    validated = super().from_param(value)
    # NumPy's default _as_parameter_ uses ctypes.cast, creating reference cycles.
    # card disables cyclic GC. Keep the array alive for this synchronous call
    # with an acyclic owner reference instead, retaining ndpointer validation.
    pointer = ctypes.c_void_p(validated.data)
    pointer._owner = value
    return pointer


def state(m):
  return np.array([m.c0, m.c1, m.c0_i, m.filtered, float(m.fast)], dtype=np.float64)


def parameters(m, speed, freeze_i=True, interaction=1.0):
  if m.c2 != 0 or m.c3 != 0:
    raise ValueError('C2/C3 must be zero')
  if abs(m.preview_t - m.cal.f(0xFEF25A58)) > 1e-9:
    raise ValueError('Fixed preview time required')
  c = m.cal
  probe = copy.copy(m).step(speed, m.c0, m.c1, freeze_i=freeze_i, interaction=interaction)
  si, sf = probe['speed_index'], probe['speed_fraction']
  return np.array(
    [
      probe['g0'],
      probe['g1'],
      interp_int(m.tables[0xFEF258FC], si, sf) / 256,
      c.b(0xFEF25AA5) / 128,
      c.b(0xFEF25AA6) / 128,
      c.b(0xFEF25AA7) / 256,
      c.b(0xFEF25AA4) / 256,
      speed * 0.28,
      c.f(0xFEF259F4),
      interaction,
      c.f(0xFEF259F8),
      c.f(0xFEF259FC),
      c.f(0xFEF25A08),
      c.f(0xFEF25A0C),
      c.f(0xFEF25A00),
      c.f(0xFEF25A10),
      c.h(0xFEF25A70) / 8192,
      c.h(0xFEF25A72) / 8192,
      0.0 if freeze_i else interp(m.tables[0xFEF25B78], si, sf) * DT,
      c.f(0xFEF25968),
      c.f(0xFEF25960),
      c.f(0xFEF25964),
      c.f(0xFEF2595C),
      interp_int(m.tables[0xFEF25C60], si, sf) / 512 * DT,
    ],
    dtype=np.float64,
  )


LIB = ctypes.CDLL(str(Path(__file__).with_name('libencoder' + ('.dylib' if sys.platform == 'darwin' else '.so'))))
LIB.paired_cost.argtypes = [DoubleArray, DoubleArray, ctypes.c_double, DoubleArray, ctypes.c_int, ctypes.c_double, ctypes.c_double, DoubleArray]
LIB.paired_cost.restype = ctypes.c_double
LIB.paired_select.argtypes = [DoubleArray, DoubleArray, ctypes.c_double, DoubleArray, ctypes.c_int, DoubleArray, ctypes.c_int,
                            DoubleArray, ctypes.c_int, ctypes.c_int, DoubleArray]
LIB.paired_select.restype = None
LIB.paired_immediate_bound.argtypes = [DoubleArray, DoubleArray, ctypes.c_double, DoubleArray, ctypes.c_int, DoubleArray, ctypes.c_int]
LIB.paired_immediate_bound.restype = ctypes.c_double
LIB.paired_preview_select.argtypes = [DoubleArray, DoubleArray, DoubleArray, DoubleArray, ctypes.c_int, ctypes.c_int, ctypes.c_double,
                                     DoubleArray, ctypes.c_int, DoubleArray, ctypes.c_int, DoubleArray]
LIB.paired_preview_select.restype = None


def levels(held, pref, rate, count, lsb, bound, clear):
  reach = rate * 0.008 * count + lsb / 2
  lo = max(round(-bound / lsb), math.floor((held - reach) / lsb))
  hi = min(round(bound / lsb), math.ceil((held + reach) / lsb))
  # Include both sides of the fast-latch clearing thresholds even when outside
  # the reachable range: equal slew endpoints can otherwise have different flags.
  candidates = [i * lsb for i in range(lo, hi + 1)]
  candidates.extend((math.floor(sign * clear / lsb) + offset) * lsb for sign in (-1, 1) for offset in (-1, 0, 1))
  candidates.extend((pref, round(held / lsb) * lsb, -bound, bound))
  return np.array(sorted({min(max(x, -bound), bound) for x in candidates}), dtype=np.float64)


class PairedRelease:
  def __init__(self, request, freeze_i=True, interaction=1.0, preserve_now=True):
    self.request = request
    self.freeze_i = freeze_i
    self.interaction = interaction
    self.preserve_now = preserve_now

  def choose(self, speed_kmh, curvature, phase=0, *, curvature_rate=0.0, preview=0.0, curvature_bound=math.inf):
    m = self.request
    if not self.freeze_i or m.c0_i != 0:
      raise ValueError('Joint encoder requires its nominal zero-I estimate')
    s = state(m)
    if phase not in range(10) or speed_kmh <= 0 or not all(math.isfinite(x) for x in (speed_kmh, curvature, *s)):
      raise ValueError('Finite moving-vehicle inputs and scheduler phase required')
    if not math.isfinite(curvature_rate) or not 0.0 <= preview <= 0.15:
      raise ValueError('Finite target trend and bounded preview required')
    if preview and (not math.isfinite(curvature_bound) or curvature_bound <= 0 or abs(curvature) > curvature_bound + 1e-12):
      raise ValueError('Finite positive curvature bound must contain the current target')
    p = parameters(m, speed_kmh, True, self.interaction)
    # parameters() already probed this same state/speed for the channel gains.
    pref = np.array(quantize(static_pair(m, curvature, speed_kmh, gains=(float(p[0]), float(p[1])))))
    target = float(p[0] * pref[0] + p[1] * pref[1])
    count = next(k for k in range(1, 3) if (phase + 8 * k) // 10 > 0)
    c0s = levels(m.c0, pref[0], max(p[10:12]), count, 0.01, 5.11, p[14])
    c1s = levels(m.c1, pref[1], max(p[12:14]), count, 0.0005, 0.5, p[15])
    result = np.full(9, np.nan)
    preview_limited = False
    if preview and curvature_rate:
      immediate_bound = LIB.paired_immediate_bound(s, p, target, pref, count, c0s, len(c0s)) if self.preserve_now else 1e300
      if not math.isfinite(immediate_bound):
        raise ValueError('No finite immediate accuracy bound')
      n = math.ceil(preview / 0.008)
      times = np.minimum(np.arange(n + 1) * 0.008, preview)
      forecast = curvature + curvature_rate * times
      bounded = np.clip(forecast, -curvature_bound, curvature_bound)
      preview_limited = bool(np.any(forecast != bounded))
      pairs = np.array([quantize(static_pair(m, float(k), speed_kmh, gains=(float(p[0]), float(p[1])))) for k in bounded])
      targets = np.ascontiguousarray(pairs[:, 0] * p[0] + pairs[:, 1] * p[1])
      # Include forecast return pairs while retaining every original candidate.
      # The unused ordinary selection was already in these original grids.
      c0s = np.unique(np.r_[pairs[:, 0], c0s])
      c1s = np.unique(np.r_[pairs[:, 1], c1s])
      LIB.paired_preview_select(s, p, targets, pairs.ravel(), n, count, immediate_bound, c0s, len(c0s), c1s, len(c1s), result)
      if not np.isfinite(result).all() or abs(result[0]) > 5.11 or abs(result[1]) > 0.5 or abs(result[6] - target) > immediate_bound + 1.1e-12:
        raise ValueError('No bounded preview command preserving immediate accuracy')
    else:
      LIB.paired_select(s, p, target, pref, count, c0s, len(c0s), c1s, len(c1s), int(self.preserve_now), result)
      if not np.isfinite(result).all() or abs(result[0]) > 5.11 or abs(result[1]) > 0.5:
        raise ValueError('No finite bounded joint command')
    return tuple(result[:2]), {
      'cost': float(result[2]),
      'first_state': result[3:8].copy(),
      'count': count,
      'pref': pref,
      'planned_target': target,
      'evaluations': len(c0s) * len(c1s),
      'immediate_error_bound': result[8],
      'preview_limited': preview_limited,
    }
