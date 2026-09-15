import math

import pytest

from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController


@pytest.mark.parametrize('sign', [-1., 1.])
def test_existing_integral_unwinds_in_current_output(sign):
  core = ModelActionController(.5, .25)
  core.c1, core.correction = sign*.07, sign*.03
  core.update(straight(), sign*.002, current_curvature=sign*.004, speed=20., dt=.01)
  assert core.correction == pytest.approx(sign*.0299)
  assert core.c1 == pytest.approx(sign*.0499)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_unwinding_cannot_charge_opposite_correction_beyond_amplitude_limit(sign):
  core = ModelActionController(.5, .25)
  core.c1, core.correction = sign*.07, sign*.03
  core.update(straight(), 0., current_curvature=sign*.5, speed=20., dt=.01, feedback_dt=.15)
  assert core.correction == 0.
  assert core.c1 == pytest.approx(-sign*.5)


@pytest.mark.parametrize('ki', [0., .25, .5, 1.])
def test_integral_gain_scales_fresh_error_only(ki):
  core = ModelActionController(0., ki)
  core.c1 = .04
  core.update(straight(), .002, current_curvature=.001, speed=20., dt=.01)
  assert core.correction == pytest.approx(ki*.0002)
  before = core.correction
  core.update(straight(), 0., current_curvature=.001, speed=20., dt=.01, feedback_dt=0.)
  assert core.correction == before


def test_zero_error_does_not_erase_holding_correction():
  core = ModelActionController(.5, .25)
  core.c1, core.correction = .14, .1
  for _ in range(50):
    core.update(straight(), .002, current_curvature=.002, speed=20., dt=.01)
    assert core.correction == .1


@pytest.mark.parametrize('ki', [-1., math.inf, math.nan])
def test_invalid_integral_gain_is_rejected(ki):
  with pytest.raises(ValueError):
    ModelActionController(.25, ki)


def test_overflowing_integral_increment_resets():
  core = ModelActionController(.25, 1e308)
  assert not core.update(straight(), 1., current_curvature=0., speed=55., dt=.01).valid
  assert core.c0 == core.c1 == core.correction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_centering_cannot_gate_continuous_heading_correction(sign):
  commands = []
  for offset in (-.1, -.010001, -.01, -.009999, 0., .009999, .01, .010001, .1):
    core = ModelActionController()
    core.c0, core.c1, core.correction = offset, sign*.07, sign*.03
    out = core.update(straight(offset), sign*.002, current_curvature=sign*.004, speed=20., dt=.01)
    commands.append((out.path_angle, core.correction))
  assert len(set(commands)) == 1


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('limited', [False, True])
@pytest.mark.parametrize('gain', [.5, .75])
def test_duplicate_measurements_cannot_retire_integral(sign, limited, gain):
  core = ModelActionController(gain, .25)
  core.c1, core.correction = sign*.07, sign*.03
  core.update(straight(), -sign*.002, current_curvature=sign*.004, speed=20., dt=.01,
              feedback_dt=0., pscm_limited=limited)
  assert core.correction == sign*.03
  assert core.proportional == pytest.approx(-sign*.12*gain)
  assert core.c1 == pytest.approx(-sign*(.01+.12*gain))
