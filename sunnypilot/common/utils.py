import numpy as np

def compute_symmetric_slopes(x, y):
  """
  Compute symmetric slopes for use in Hermite interpolation.

  Args:
      x: Array of x coordinates
      y: Array of y coordinates

  Returns:
      Array of computed slopes at each point
  """
  n = len(x)
  m = np.zeros(n)
  for i in range(n):
    if i == 0:
      m[i] = (y[i+1] - y[i]) / (x[i+1] - x[i])
    elif i == n-1:
      m[i] = (y[i] - y[i-1]) / (x[i] - x[i-1])
    else:
      m[i] = ((y[i+1] - y[i]) / (x[i+1] - x[i]) + (y[i] - y[i-1]) / (x[i] - x[i-1])) / 2
  return m

def hermite_interpolate(x, xp, yp, slopes):
  """
  Perform Hermite interpolation at point x given data points and slopes.

  Args:
      x: Point at which to interpolate
      xp: Array of x coordinates of data points
      yp: Array of y coordinates of data points
      slopes: Array of slopes at data points

  Returns:
      Interpolated value at x
  """
  x = np.clip(x, xp[0], xp[-1])
  idx = np.searchsorted(xp, x) - 1
  idx = np.clip(idx, 0, len(slopes) - 2)

  x0, x1 = xp[idx], xp[idx+1]
  y0, y1 = yp[idx], yp[idx+1]
  m0, m1 = slopes[idx], slopes[idx+1]

  t = (x - x0) / (x1 - x0)
  h00 = 2*t**3 - 3*t**2 + 1
  h10 = t**3 - 2*t**2 + t
  h01 = -2*t**3 + 3*t**2
  h11 = t**3 - t**2

  return (h00 * y0) + (h10 * (x1 - x0) * m0) + (h01 * y1) + (h11 * (x1 - x0) * m1)