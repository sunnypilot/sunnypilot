import numpy as np

from opendbc.car import rate_limit, DT_CTRL
from opendbc.sunnypilot.car.toyota.brake_onset import BrakeOnsetShaper, ONSET_J_DOWN, HARD_BRAKE_ACCEL

DT = DT_CTRL * 3
STOCK_J = 4.0
UP_STEP = 4.0 * DT


def run(requests, a0=0.0, fcw=False):
  shaper = BrakeOnsetShaper(DT, STOCK_J)
  a = a0
  out = []
  for req in requests:
    step = shaper.down_step(req, a, bypass=shaper.is_urgent(req, fcw))
    a = rate_limit(req, a, step, UP_STEP)
    out.append(a)
  return np.array(out)


def at(out, t):
  return out[int(round(t / DT)) - 1]


class TestBrakeOnset:
  def test_step_brake_eases_in_over_the_first_second(self):
    out = run([-1.5] * 60)
    assert at(out, 0.09) > -0.06  # first 0.15 s: barely anything
    assert at(out, 0.21) > -0.12  # 0.2 s: still very light
    assert -0.45 < at(out, 0.36) < -0.10  # ~0.35 s: building slowly
    assert -0.60 < at(out, 0.60) < -0.15  # 0.6 s: still gentle, about a fifth of the way
    assert -1.10 < at(out, 1.00) < -0.55  # 1.0 s: about half way, the ramp is now running up
    assert np.isclose(at(out, 1.5), -1.5, atol=1e-6)  # settled once the ramp reaches the stock limit

  def test_jerk_follows_the_schedule_and_never_exceeds_stock(self):
    out = run([-1.9] * 60, a0=1.0)  # large step, still above the hard-brake bypass
    jerks = np.diff(np.concatenate([[1.0], out])) / DT
    assert jerks.min() >= -STOCK_J - 1e-6
    assert jerks[0] >= -ONSET_J_DOWN[0] - 1e-6
    assert jerks[int(0.09 / DT)] >= -ONSET_J_DOWN[1] - 1e-6
    # the blend is one straight ramp: jerk keeps growing monotonically until the stock limit
    ramp = -jerks[int(0.1 / DT):int(0.6 / DT)]
    assert np.all(np.diff(ramp) >= -1e-6)

  def test_lead_switch_during_a_settled_brake_gets_the_same_soft_onset(self):
    reqs = [-0.6] * 70 + [-1.8] * 60  # long enough for the schedule to wind fully back before the switch
    out = run(reqs)
    t_switch = 70 * DT
    assert np.isclose(at(out, t_switch), -0.6, atol=1e-6)
    assert at(out, t_switch + 0.09) > -0.6 - 0.05
    assert at(out, t_switch + 0.21) > -0.6 - 0.25
    assert np.isclose(out[-1], -1.8, atol=1e-6)

  def test_hard_brake_request_bypasses_the_schedule(self):
    out = run([HARD_BRAKE_ACCEL - 0.5] * 20)
    assert np.isclose(out[0], -STOCK_J * DT, atol=1e-6)
    assert at(out, 0.3) <= -1.1

  def test_fcw_bypasses_the_schedule(self):
    out = run([-1.5] * 20, fcw=True)
    assert np.isclose(out[0], -STOCK_J * DT, atol=1e-6)

  def test_release_is_untouched(self):
    out = run([1.0] * 20, a0=-1.5)
    assert np.isclose(out[0], -1.5 + UP_STEP, atol=1e-6)

  def test_gentle_request_passes_straight_through(self):
    reqs = list(np.linspace(0.0, -0.2, 40))  # ~0.17 m/s^3, below the gentlest onset limit (0.25)
    out = run(reqs)
    assert np.allclose(out, reqs, atol=1e-9)

  def test_short_pause_does_not_fully_rearm(self):
    shaper = BrakeOnsetShaper(DT, STOCK_J)
    a = 0.0
    for _ in range(int(0.3 / DT)):
      a = rate_limit(-1.5, a, shaper.down_step(-1.5, a), UP_STEP)
    t_after_ramp = shaper.t_onset
    for _ in range(2):  # hold for two frames, request steady
      shaper.down_step(a, a)
    assert 0.0 < shaper.t_onset < t_after_ramp
    for _ in range(int(1.0 / DT)):  # a full second of settled brake winds it back completely
      shaper.down_step(a, a)
    assert shaper.t_onset == 0.0
