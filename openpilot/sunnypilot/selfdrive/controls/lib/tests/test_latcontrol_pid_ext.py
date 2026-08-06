import math

import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_pid_ext import DecayingIntegratorPIDController

RATE = 100
DT = 1.0 / RATE


def build_pid(decay_tau=2.0):
  return DecayingIntegratorPIDController(0.05, 0.05, pos_limit=1.0, neg_limit=-1.0, rate=RATE, decay_tau=decay_tau)


class TestDecayingIntegratorPIDController:
  def test_accumulates_normally_when_not_frozen(self):
    """Unfrozen behavior must be identical to stock PIDController - only freeze behavior changes."""
    pid = build_pid()
    for _ in range(50):
      pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=False)
    assert pid.i > 0

  def test_decays_toward_zero_while_frozen(self):
    pid = build_pid(decay_tau=2.0)
    for _ in range(200):  # 2s build-up, well below saturation so anti-windup doesn't clip i
      pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=False)
    i_before = pid.i
    assert i_before > 0

    i_trace = []
    for _ in range(600):  # 6s frozen = 3 time constants
      pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=True)
      i_trace.append(pid.i)

    # monotonic decay toward zero, never grows, never flips sign
    assert all(0 <= i_trace[k + 1] <= i_trace[k] for k in range(len(i_trace) - 1))
    assert i_trace[-1] < 0.05 * i_before, "should be mostly decayed after 3 time constants"

  def test_matches_exponential_decay_time_constant(self):
    """Sanity-checks the decay is a real exp(-t/tau), not just 'decreasing'."""
    pid = build_pid(decay_tau=2.0)
    pid.i = 1.0

    for _ in range(200):  # exactly one time constant (2s @ 100Hz)
      pid.update(error=0.0, speed=1.0, feedforward=0.0, freeze_integrator=True)

    assert pid.i == pytest.approx(math.exp(-1.0), rel=1e-3)

  def test_no_discontinuity_at_freeze_transition(self):
    """The whole point: control output must not jump the instant freeze conditions engage."""
    pid = build_pid(decay_tau=2.0)
    for _ in range(200):
      pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=False)
    control_before = pid.control

    control_after = pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=True)

    assert abs(control_after - control_before) < 0.01, "output jumped at the freeze transition"

  def test_stale_integral_does_not_kick_back_in_on_unfreeze(self):
    """The bug this exists to fix: after a long freeze, unfreezing must not suddenly reapply a
    large stale integral untouched for however long the freeze lasted."""
    pid = build_pid(decay_tau=2.0)
    for _ in range(200):
      pid.update(error=1.0, speed=1.0, feedforward=0.0, freeze_integrator=False)
    i_peak = pid.i

    for _ in range(1000):  # 10s frozen, ~5 time constants
      pid.update(error=0.0, speed=1.0, feedforward=0.0, freeze_integrator=True)

    # unfreeze: the resumed integral must be near zero, not the stale peak
    pid.update(error=0.0, speed=1.0, feedforward=0.0, freeze_integrator=False)
    assert abs(pid.i) < 0.01 * i_peak
