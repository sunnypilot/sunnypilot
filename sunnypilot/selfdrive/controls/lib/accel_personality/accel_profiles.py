"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

# Profiles
MAX_ACCEL_PROFILES = {
  "eco":                [1.345, 1.3, 1.2, 1.0, 0.77, .572, .455, .365, .32, .10],
  "normal":             [2.00, 2.00, 1.95, 1.65, 1.08, .69,  .60, .49, .37, .15],
  "sport":              [2.00, 2.00, 2.00, 1.90, 1.25, .88,  .70, .60, .45, .20],
}
MAX_ACCEL_BREAKPOINTS = [0.,   1.,   6.,   8.,   11.,  16.,  20., 25., 30., 55.]

MIN_ACCEL_PROFILES = {
  "eco":                [-.05,  -.105,  -0.09, -0.10, -0.65, -0.65],
  "normal":             [-.06,  -.115,  -0.10, -0.11, -0.70, -0.70],
  "sport":              [-.07,  -.125,  -0.11, -0.12, -0.75, -0.75],
  "stock":              [-1.2,  -1.2,  -1.2,  -1.2,  -1.2,  -1.2],
}
MIN_ACCEL_BREAKPOINTS = [0.,     0.6,   5.,    8.,   25.,   40.]


# Precompute slopes for Cubic Bézier curves
def compute_symmetric_slopes(x, y):
  n = len(x)
  if n < 2:
    raise ValueError("At least two points are required to compute slopes.")
  m = np.zeros(n)
  for i in range(n):
    if i == 0:
      m[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
    elif i == n-1:
      m[i] = (y[i] - y[i-1]) / (x[i] - x[i-1])
    else:
      m[i] = ((y[i+1] - y[i]) / (x[i+1] - x[i]) + (y[i] - y[i-1]) / (x[i] - x[i-1])) / 2
  return m


MAX_ACCEL_SLOPES = {
  mode: compute_symmetric_slopes(MAX_ACCEL_BREAKPOINTS, values)
  for mode, values in MAX_ACCEL_PROFILES.items()
}

MIN_ACCEL_SLOPES = {
  mode: compute_symmetric_slopes(MIN_ACCEL_BREAKPOINTS, values)
  for mode, values in MIN_ACCEL_PROFILES.items()
}

# Hermite interpolation function
def hermite_interpolate(x, xp, yp, slopes, mode):
  # Clip x inside the domain
  x = np.clip(x, xp[0], xp[-1])

  # Find segment
  idx = np.searchsorted(xp, x) - 1
  idx = np.clip(idx, 0, len(slopes[mode]) - 1)

  x0, x1 = xp[idx], xp[idx+1]
  y0, y1 = yp[idx], yp[idx+1]
  m0, m1 = slopes[mode][idx], slopes[mode][idx+1]

  t = (x - x0) / (x1 - x0)
  h00 = 2*t**3 - 3*t**2 + 1
  h10 = t**3 - 2*t**2 + t
  h01 = -2*t**3 + 3*t**2
  h11 = t**3 - t**2

  interpolated = (h00 * y0) + (h10 * (x1 - x0) * m0) + (h01 * y1) + (h11 * (x1 - x0) * m1)
  return interpolated

# Final functions to call
def get_max_accel_hermite(v_ego: float, mode: str = "normal") -> float:
  return float(hermite_interpolate(v_ego, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[mode], MAX_ACCEL_SLOPES, mode))

def get_min_accel_hermite(v_ego: float, mode: str = "normal") -> float:
  return float(hermite_interpolate(v_ego, MIN_ACCEL_BREAKPOINTS, MIN_ACCEL_PROFILES[mode], MIN_ACCEL_SLOPES, mode))
