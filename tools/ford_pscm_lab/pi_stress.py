"""Check PI arithmetic and CAN invariants without a model of vehicle response."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from tools.ford_pscm_lab.feedback_replay import OPENDBC, original_controller
from tools.ford_pscm_lab.model_action_replay import WireCheck, verify_dependency
from tools.ford_pscm_lab.pi_replay import BASELINE, CANDIDATE


def stress(cycles, gain, output):
  verify_dependency(OPENDBC)
  rng = np.random.default_rng(20260913)
  candidate, candidate_hash = original_controller(CANDIDATE)
  controller = type(candidate.core)(proportional_gain=gain)
  mirror = type(candidate.core)(proportional_gain=gain)
  zero = type(candidate.core)()
  original, original_hash = original_controller(BASELINE)
  wire = WireCheck()
  release_count = 0
  for i in range(cycles):
    desired, measured = rng.uniform(-.1, .1, 2)
    speed, dt, offset = rng.uniform(.3, 55.), rng.uniform(.002, .1), rng.uniform(-8., 8.)
    active, enabled, limited = i % 211 != 0, i % 97 != 0, i % 7 == 0
    feedback_dt = 0. if i % 5 == 0 else rng.uniform(.002, .15)
    previous = controller.c0, controller.c1, controller.correction
    count = controller.carryover_release_count
    args = {'speed': speed, 'dt': dt, 'feedback_dt': feedback_dt, 'active': active,
            'feedback_enabled': enabled, 'pscm_limited': limited}
    def model(y):
      return SimpleNamespace(position=SimpleNamespace(x=[0., 20.], y=[y, y]), orientation=SimpleNamespace(z=[0., 0.]))
    out = controller.update(model(offset), desired, current_curvature=measured, **args)
    other = mirror.update(model(-offset), -desired, current_curvature=-measured, **args)
    z = zero.update(model(offset), desired, current_curvature=measured, **args)
    old = original.core.update(model(offset), desired, current_curvature=measured, **args)
    assert z == old and zero.correction == original.core.correction
    state = np.array([controller.c0, controller.c1, controller.correction, controller.proportional])
    np.testing.assert_allclose(state, -np.array([mirror.c0, mirror.c1, mirror.correction, mirror.proportional]), atol=1e-10, rtol=0.)
    assert controller.carryover_release_count == mirror.carryover_release_count
    assert abs(controller.request_release+mirror.request_release) <= 1e-10
    assert controller.unwind_release == -mirror.unwind_release
    assert abs(controller.c0) <= 5.11+1e-10 and abs(controller.c1) <= .5+1e-10 and abs(controller.correction) <= 1.+1e-10
    if active:
      distance = max(7., speed)
      base = min(.5, max(-.5, distance*desired))
      p = gain*distance*(desired-measured) if enabled else 0.
      assert controller.proportional == p
      assert abs(controller.c0-previous[0]) <= 4.*dt+1e-10
      assert abs(controller.c1-previous[1]) <= .5*dt+1e-10
      if enabled:
        released = controller.carryover_release_count > count
        release_count += released or bool(controller.unwind_release)
        remaining = 0. if released else previous[2]-controller.unwind_release+controller.request_release
        increment = (desired-measured)*speed*feedback_dt
        direction = measured if measured else previous[1]
        if limited and increment*direction > 0.:
          increment = min(max(increment, min(-remaining, 0.)), max(-remaining, 0.))
        lower, upper = max(-.5, previous[1]-.5*dt), min(.5, previous[1]+.5*dt)
        target = base+p+remaining
        increment = min(max(increment, min(lower-target, 0.)), max(upper-target, 0.))
        assert abs(controller.correction-(remaining+increment)) <= 1e-10
      else:
        assert controller.correction == 0.
      target = min(.5, max(-.5, base+p+controller.correction))
      expected = previous[1]+min(.5*dt, max(-.5*dt, target-previous[1]))
      assert abs(controller.c1-expected) <= 1e-10
    else:
      assert np.all(state == 0.)
    assert out.curvature == out.curvature_rate == other.curvature == other.curvature_rate == 0.
    wire.check(out)
  report = {'cycles': cycles, 'gain': gain, 'seed': 20260913, 'mirrored_updates': cycles,
            'zero_gain_exact_v5_comparisons': cycles, 'can_round_trips': wire.count,
            'candidate_revision': CANDIDATE, 'candidate_source_sha256': candidate_hash,
            'baseline_revision': BASELINE, 'baseline_source_sha256': original_hash,
            'release_cycles': release_count, 'calibration_approved': False,
            'checks':
            'Independent scalar PI arithmetic, combined anti-windup, mirror symmetry, slew/amplitude, driver/PSCM gates, resets, zero-P v5 parity and CAN.',
            'scope': __doc__, 'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                               (Path(__file__).resolve(),)}}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(report, indent=2)+'\n')
  print(json.dumps(report, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--cycles', type=int, default=200_000)
  parser.add_argument('--gain', type=float, default=.25)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  stress(args.cycles, args.gain, args.output)
