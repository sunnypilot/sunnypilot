
from cereal import log
import numpy as np

class DynamicPersonalityController:
  """
  Controller for managing dynamic personality-based following distances
  that adapt based on vehicle speed and selected driving personality.
  """

  def __init__(self):
    pass

  def compute_symmetric_slopes(self, x, y):
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

  def hermite_interpolate(self, x, xp, yp, slopes):
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

  def get_dynamic_follow_distance(self, v_ego, personality=log.LongitudinalPersonality.standard):
    """
    Calculate the dynamic follow distance based on current speed and personality.

    Args:
        v_ego: Current vehicle speed
        personality: Selected longitudinal personality mode

    Returns:
        float: The calculated follow distance factor
    """
    if personality == log.LongitudinalPersonality.relaxed:
      x_vel =  [0.,   8.3, 14.5, 19.7, 22.2, 40.]
      y_dist = [1.20, 1.20, 1.80, 1.80, 1.90, 1.90]
    elif personality == log.LongitudinalPersonality.standard:
      x_vel =  [0.,   2.,   6.,   14.,  14.5, 19.7, 22.2, 40.]
      y_dist = [1.20, 1.20, 1.31, 1.31, 1.37, 1.37, 1.60, 1.60]
    elif personality == log.LongitudinalPersonality.aggressive:
      x_vel =  [0.,   1.,    5.,   14.,  14.5, 19.7, 22.2, 40.]
      y_dist = [1.10, 1.10,  1.30, 1.30, 1.35, 1.35, 1.45, 1.45]
    else:
      raise NotImplementedError("Dynamic personality not supported")

    slopes = self.compute_symmetric_slopes(x_vel, y_dist)
    result = float(self.hermite_interpolate(v_ego, x_vel, y_dist, slopes))

    return result