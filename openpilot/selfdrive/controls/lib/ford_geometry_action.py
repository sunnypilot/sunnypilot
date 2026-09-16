"""Opt-in action baseline with geometry assistance for stronger turn requests.

The curvature band and release exponent are experimental choices. No PSCM
dynamics or physical tracking are modeled by this reference selector.
"""
import math


class GeometryActionHybrid:
  def __init__(self, start_curvature=.01, full_curvature=.02, release_power=2.):
    if not all(math.isfinite(x) for x in (start_curvature, full_curvature, release_power)) or not 0. < start_curvature < full_curvature or release_power <= 0:
      raise ValueError('Expected positive curvature band and release exponent')
    self.start, self.full, self.release_power = start_curvature, full_curvature, release_power
    self.reset()

  def reset(self):
    self.direction = self.action_peak = self.weight = 0.

  def update(self, action, geometry, *, active=True):
    if not math.isfinite(action):
      self.reset()
      return 0.
    if not active or not math.isfinite(geometry) or abs(geometry) <= self.start:
      self.reset()
      return action
    direction = math.copysign(1., geometry)
    if direction != self.direction:
      self.reset()
      self.direction = direction
    self.weight = 0.
    if action*geometry <= 0:
      return action
    self.action_peak = max(self.action_peak, abs(action))
    if abs(geometry) <= abs(action):
      return action
    progress = min((abs(geometry)-self.start)/(self.full-self.start), 1.)
    turn_weight = progress*progress*(3.-2.*progress)
    # A tiny action rebound after a geometry reset must not authorize full boost.
    release_weight = (abs(action)/max(self.start, self.action_peak))**self.release_power
    self.weight = turn_weight*release_weight
    return action+self.weight*(geometry-action)
