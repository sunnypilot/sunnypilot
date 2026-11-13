"""
Steering from the model's recent paths.

A big model with an action output steers from that output: a lateral acceleration, divided by the speed squared. At
town speeds a small error in it is a large one at the wheel (0.1 m/s2 is 22 degrees at 7 mph), and the wheel twitches.
The model's path does not have that problem, and every path it made in the last second also says how hard the road
turns where the car will be when the steering asked now arrives. Paths that agree about the road give that with no
delay, unlike an average of past steering; one frame's own error counts for one in twenty.

Each path is read by distance - where the car has really got to since the path was made, along the path's own
length - so a driver who goes slower or faster than the model expected does not shift the turn.

Two asks come out of the recent paths:
  own       the mean of what the paths say. Used while a turn is signalled: the car commits to the turn its paths show.
  anchored  each frame's action, moved on by the change its own path expects since, averaged: the action's level, the
            paths' shape. Used with no signal: the action decides and the paths only smooth it, because a path alone,
            at a junction nobody signalled for, can talk itself into a turn.
On faster roads the action steers alone, as it always has.

A model trained on the driver's own lines (the closed-loop fine-tunes) places its turns with its action, and the paths'
own ask under-steers them; for such a model the anchored ask is used in signalled turns too, over a shorter window.
That is switched by the file ANCHOR_SWITCH, read when a drive starts.

Two more switches, both off unless their toggles are on:
  pursuit    (PathSteeringPursuit) the paths' own ask above knows the road's shape but not where the car is now: each
             path was planned from where the car was when it was made, so drift since is never pulled back. With
             pursuit, every recent path is placed in the car's frame of now (by dead reckoning the car's own
             curvature since the path was made) and steered at like a driver looking ahead: the curvature of the arc
             from the car to a point on the path a short way ahead (pure pursuit). Averaged over the recent paths as
             before, so still smooth, but a car that has drifted wide or tight is steered back. Used in place of the
             paths' own ask in signalled turns.
  geometric  (PathSteeringGeometry) read each path's curvature from its shape, the change in heading per metre over a
             few metres, and measure distance along it from its points, instead of yaw rate over planned speed. A plan
             that expects to creep through a corner has a small planned speed and so a noisy, too large yaw-rate
             curvature; its shape does not.
"""

import os

import numpy as np

MIN_SPEED = 1.0       # m/s, as openpilot's steer-from-plan formula
WINDOW = 1.0          # s of recent paths that count
TOWN = (9.0, 13.0)    # m/s: below, the recent paths take part; above, the action steers alone; a mix in between
FADE = 0.6            # s to move over between the anchored ask and the paths' own when the signal changes
CUE_S = 6.6           # s a turn pulse stays in the model's own cue history: that long, a turn counts as signalled
ANCHOR_SWITCH = '/data/recent_paths_anchor'  # exists: the anchored ask in signalled turns too (a trained model)
ANCHOR_WINDOW = 0.6   # s of recent paths that count with the anchored ask in turns
PURSUIT_MIN = 4.0     # m: the nearest the pursuit point is ever looked at
PURSUIT_LEAD = 0.5    # s of driving, past the steering delay, to the pursuit point
PURSUIT_TAU = 0.3     # s: the pursuit ask weighs each recent path by exp(-age / this), as its dead reckoning ages
GEOM_SPAN = 2.0       # m either side over which the geometric curvature measures the change in heading
GEOM_MIN_LEN = 3.0    # m: a path shorter than this (the car about to stop) is read by yaw rate, as without the switch


def _geometric_curvature(along, yaws):
  """Curvature (1/m) at each of a path's points, from the change in heading over GEOM_SPAN either side of it."""
  lo = np.maximum(along - GEOM_SPAN, along[0])
  hi = np.minimum(along + GEOM_SPAN, along[-1])
  return (np.interp(hi, along, yaws) - np.interp(lo, along, yaws)) / np.maximum(hi - lo, 1e-3)


class RecentPaths:
  def __init__(self, t_idxs, window: float = WINDOW):
    self.t = np.asarray(t_idxs, dtype=np.float64)
    self.window = float(window)
    self.held: list[dict] = []
    self.pursuit = 0.0  # the pursuit ask of the last update, averaged over the recent paths (1/m)

  def reset(self) -> None:
    self.held = []
    self.pursuit = 0.0

  def _curvature(self, rates, speeds, at: float) -> float:
    return float(np.interp(at, self.t, rates)) / max(float(np.interp(at, self.t, speeds)), MIN_SPEED)

  def _curvature_at(self, path: dict, distance: float) -> float:
    if path['geo'] is not None:
      return float(np.interp(distance, path['along'], path['geo']))
    return self._curvature(path['rates'], path['speeds'], float(np.interp(distance, path['along'], self.t)))

  def update(self, yaw_rates, speeds, action_curvature: float, v_ego: float, action_t: float, dt: float,
             positions=None, yaws=None, car_curvature: float = 0.0, geometric: bool = False) -> tuple[float, float]:
    """(own, anchored) curvature asks for this frame, and self.pursuit. yaw_rates, speeds: this frame's path at the
    model's time steps (rad/s, m/s); action_curvature: what the action alone asks (1/m); v_ego: the car's speed;
    action_t: s until the steering asked now arrives; dt: s since the frame before. positions (x, y per time step, m,
    the car's frame at this frame), yaws (rad) and car_curvature (what the car is really steering, 1/m) are needed for
    the pursuit ask and the geometric curvature; without positions pursuit is the own ask."""
    v = max(float(v_ego), 0.0)
    for path in self.held:
      path['age'] += dt
      path['come'] += v * dt
      turn = v * float(car_curvature) * dt
      mid = path['pose'][2] + 0.5 * turn
      path['pose'][0] += v * dt * np.cos(mid)
      path['pose'][1] += v * dt * np.sin(mid)
      path['pose'][2] += turn
    self.held = [path for path in self.held if path['age'] <= self.window + 1e-9]

    speeds = np.maximum(np.asarray(speeds, dtype=np.float64), 0.0)
    xy = None if positions is None else np.asarray(positions, dtype=np.float64)[:, :2]
    geo, along = None, None
    if xy is not None:
      geo_along = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]) + 1e-6 * np.arange(len(xy))
      if geometric and yaws is not None and geo_along[-1] >= GEOM_MIN_LEN:
        along = geo_along
        geo = _geometric_curvature(along, np.unwrap(np.asarray(yaws, dtype=np.float64)))
    if along is None:
      along = np.concatenate([[0.0], np.cumsum(0.5 * (speeds[1:] + speeds[:-1]) * np.diff(self.t))])
      along = along + 1e-6 * np.arange(len(along))
    path = {'age': 0.0, 'come': 0.0, 'level': float(action_curvature), 'was': v * action_t,
            'rates': np.array(yaw_rates, dtype=np.float64), 'speeds': speeds, 'along': along, 'geo': geo,
            'xy': xy, 'xy_along': None if xy is None else geo_along, 'pose': [0.0, 0.0, 0.0]}
    self.held.append(path)

    own, anchored, pursuit = [], [], []
    look = max(PURSUIT_MIN, v * (action_t + PURSUIT_LEAD))
    for path in self.held:
      there = self._curvature_at(path, path['come'] + v * action_t)
      meant = self._curvature_at(path, path['was'])
      own.append(there)
      anchored.append(path['level'] + there - meant)
      if path['xy'] is not None:
        px, py, pyaw = path['pose']
        s = path['come'] + look
        dx = float(np.interp(s, path['xy_along'], path['xy'][:, 0])) - px
        dy = float(np.interp(s, path['xy_along'], path['xy'][:, 1])) - py
        ahead = np.cos(pyaw) * dx + np.sin(pyaw) * dy
        side = -np.sin(pyaw) * dx + np.cos(pyaw) * dy
        pursuit.append(2.0 * side / max(ahead * ahead + side * side, 1.0))
      else:
        pursuit.append(there)
    weights = np.exp(-np.array([path['age'] for path in self.held]) / PURSUIT_TAU)
    self.pursuit = float(np.dot(weights, pursuit) / weights.sum())
    return float(np.mean(own)), float(np.mean(anchored))


class SignalSteer:
  """The steering ask of a frame from its action and the recent paths, by whether a turn is signalled."""

  def __init__(self, t_idxs, window: float | None = None, fade: float = FADE, anchor_turns: bool | None = None):
    self.anchor_turns = os.path.exists(ANCHOR_SWITCH) if anchor_turns is None else anchor_turns
    self.paths = RecentPaths(t_idxs, (ANCHOR_WINDOW if self.anchor_turns else WINDOW) if window is None else window)
    self.fade = float(fade)
    self.signalled = 0.0  # how far the steering has moved over from the anchored ask to the paths' own
    self.pursuit = False    # the PathSteeringPursuit toggle
    self.geometric = False  # the PathSteeringGeometry toggle

  def reset(self) -> None:
    self.paths.reset()
    self.signalled = 0.0

  def update(self, yaw_rates, speeds, action_curvature: float, cued: bool, v_ego: float, action_t: float, dt: float,
             positions=None, yaws=None, car_curvature: float = 0.0) -> float:
    own, anchored = self.paths.update(yaw_rates, speeds, action_curvature, v_ego, action_t, dt,
                                      positions, yaws, car_curvature, self.geometric)
    if self.pursuit and positions is not None:
      own = self.paths.pursuit
    most = dt / self.fade
    self.signalled += float(np.clip((1.0 if cued and not self.anchor_turns else 0.0) - self.signalled, -most, most))
    ask = self.signalled * own + (1.0 - self.signalled) * anchored
    fast = float(np.clip((v_ego - TOWN[0]) / (TOWN[1] - TOWN[0]), 0.0, 1.0))
    return (1.0 - fast) * ask + fast * float(action_curvature)
