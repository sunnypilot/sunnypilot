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


class RecentPaths:
  def __init__(self, t_idxs, window: float = WINDOW):
    self.t = np.asarray(t_idxs, dtype=np.float64)
    self.window = float(window)
    self.held: list[list] = []  # per path: age, metres come since, action's curvature, metres it was for, rates, speeds, metres along

  def reset(self) -> None:
    self.held = []

  def _curvature(self, rates, speeds, at: float) -> float:
    return float(np.interp(at, self.t, rates)) / max(float(np.interp(at, self.t, speeds)), MIN_SPEED)

  def update(self, yaw_rates, speeds, action_curvature: float, v_ego: float, action_t: float, dt: float) -> tuple[float, float]:
    """(own, anchored) curvature asks for this frame. yaw_rates, speeds: this frame's path at the model's time steps
    (rad/s, m/s); action_curvature: what the action alone asks (1/m); v_ego: the car's speed; action_t: s until the
    steering asked now arrives; dt: s since the frame before."""
    v = max(float(v_ego), 0.0)
    for path in self.held:
      path[0] += dt
      path[1] += v * dt
    self.held = [path for path in self.held if path[0] <= self.window + 1e-9]
    speeds = np.maximum(np.asarray(speeds, dtype=np.float64), 0.0)
    along = np.concatenate([[0.0], np.cumsum(0.5 * (speeds[1:] + speeds[:-1]) * np.diff(self.t))])
    self.held.append([0.0, 0.0, float(action_curvature), v * action_t, np.array(yaw_rates, dtype=np.float64), speeds,
                      along + 1e-6 * np.arange(len(along))])
    own, anchored = [], []
    for _, come, level, was, rates, path_speeds, path_along in self.held:
      there = self._curvature(rates, path_speeds, float(np.interp(come + v * action_t, path_along, self.t)))
      meant = self._curvature(rates, path_speeds, float(np.interp(was, path_along, self.t)))
      own.append(there)
      anchored.append(level + there - meant)
    return float(np.mean(own)), float(np.mean(anchored))


class SignalSteer:
  """The steering ask of a frame from its action and the recent paths, by whether a turn is signalled."""

  def __init__(self, t_idxs, window: float | None = None, fade: float = FADE, anchor_turns: bool | None = None):
    self.anchor_turns = os.path.exists(ANCHOR_SWITCH) if anchor_turns is None else anchor_turns
    self.paths = RecentPaths(t_idxs, (ANCHOR_WINDOW if self.anchor_turns else WINDOW) if window is None else window)
    self.fade = float(fade)
    self.signalled = 0.0  # how far the steering has moved over from the anchored ask to the paths' own

  def reset(self) -> None:
    self.paths.reset()
    self.signalled = 0.0

  def update(self, yaw_rates, speeds, action_curvature: float, cued: bool, v_ego: float, action_t: float, dt: float) -> float:
    own, anchored = self.paths.update(yaw_rates, speeds, action_curvature, v_ego, action_t, dt)
    most = dt / self.fade
    self.signalled += float(np.clip((1.0 if cued and not self.anchor_turns else 0.0) - self.signalled, -most, most))
    ask = self.signalled * own + (1.0 - self.signalled) * anchored
    fast = float(np.clip((v_ego - TOWN[0]) / (TOWN[1] - TOWN[0]), 0.0, 1.0))
    return (1.0 - fast) * ask + fast * float(action_curvature)
