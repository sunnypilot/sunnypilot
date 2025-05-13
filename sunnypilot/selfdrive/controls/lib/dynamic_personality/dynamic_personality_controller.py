from cereal import log
from openpilot.sunnypilot.common.utils import compute_symmetric_slopes, hermite_interpolate

class DynamicPersonalityController:
  """
  Controller for managing dynamic personality-based following distances
  that adapt based on vehicle speed and selected driving personality.
  """

  def __init__(self):
    pass

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
      x_vel =  [0., 2.5,  5.,   19.7,   22.2, 40.]
      y_dist = [1.25, 1.25, 1.3, 1.3, 1.75, 1.75]
    elif personality == log.LongitudinalPersonality.standard:
      x_vel =  [0., 2.5,  5.,   19.7,   22.2, 40.]
      y_dist = [1.20, 1.20, 1.275, 1.275, 1.50, 1.50]
    elif personality == log.LongitudinalPersonality.aggressive:
      x_vel =  [0., 2.5,  6.,   19.7,   22.2, 40.]
      y_dist = [0.92, 0.9, 1.25, 1.25, 1.30, 1.30]
    else:
      raise NotImplementedError("Dynamic personality not supported")

    slopes = compute_symmetric_slopes(x_vel, y_dist)
    result = float(hermite_interpolate(v_ego, x_vel, y_dist, slopes))

    return result
