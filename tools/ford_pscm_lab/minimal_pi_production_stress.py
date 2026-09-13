"""Independent arithmetic and C0-independence stress for production PI."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from tools.ford_pscm_lab.model_action_replay import WireCheck
from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController


def stress(cycles, output):
  wire = WireCheck()
  kp, ki = .5, .25
  rng = np.random.default_rng(20260913)
  core, mirror, other = (ModelActionController() for _ in range(3))
  for i in range(cycles):
    desired, measured = rng.uniform(-.1, .1, 2)
    speed, dt, offset, alternate = rng.uniform(.3, 55.), rng.uniform(.002, .1), *rng.uniform(-8., 8., 2)
    active, enabled, limited = i % 211 != 0, i % 97 != 0, i % 7 == 0
    feedback_dt = 0. if i % 5 == 0 else rng.uniform(.002, .15)
    before = core.c0, core.c1, core.correction
    args = {'speed': speed, 'dt': dt, 'feedback_dt': feedback_dt, 'active': active,
            'feedback_enabled': enabled, 'pscm_limited': limited}

    def model(y):
      return SimpleNamespace(position=SimpleNamespace(x=[0., 20.], y=[y, y]), orientation=SimpleNamespace(z=[0., 0.]))

    outputs = [core.update(model(offset), desired, current_curvature=measured, **args),
               mirror.update(model(-offset), -desired, current_curvature=-measured, **args),
               other.update(model(alternate), desired, current_curvature=measured, **args)]
    state = np.array([core.c0, core.c1, core.correction, core.proportional])
    np.testing.assert_allclose(state, -np.array([mirror.c0, mirror.c1, mirror.correction, mirror.proportional]), atol=1e-10, rtol=0.)
    assert (core.c1, core.correction, core.proportional) == (other.c1, other.correction, other.proportional)
    if active:
      distance = max(7., speed)
      base = min(.5, max(-.5, distance*desired))
      target_c0 = min(5.11, max(-5.11, offset+7.*(distance*desired-base)))
      assert abs(core.c0-(before[0]+min(4.*dt, max(-4.*dt, target_c0-before[0])))) <= 1e-10
      p = kp*distance*(desired-measured) if enabled else 0.
      integral = 0.
      if enabled:
        increment = ki*(desired-measured)*speed*feedback_dt
        direction = measured if measured else before[1]
        if limited and increment*direction > 0.:
          increment = min(max(increment, min(-before[2], 0.)), max(-before[2], 0.))
        integral = before[2]
        if increment*integral < 0.:
          cancel = math.copysign(min(abs(increment), abs(integral)), increment)
          integral += cancel
          increment -= cancel
        lower, upper = max(-.5, before[1]-.5*dt), min(.5, before[1]+.5*dt)
        request = base+p+integral
        integral += min(max(increment, min(lower-request, 0.)), max(upper-request, 0.))
      assert core.proportional == p and abs(core.correction-integral) <= 1e-10
      request = min(.5, max(-.5, base+p+integral))
      assert abs(core.c1-(before[1]+min(.5*dt, max(-.5*dt, request-before[1])))) <= 1e-10
      assert abs(core.c0) <= 5.11+1e-10 and abs(core.c1) <= .5+1e-10 and abs(core.correction) <= 1.+1e-10
    else:
      assert np.all(state == 0.)
    for command in outputs:
      assert command.curvature == command.curvature_rate == 0.
      wire.check(command)
  result = {'cycles': cycles, 'kp': kp, 'ki': ki, 'controller_updates': 3*cycles,
            'can_round_trips': wire.count, 'seed': 20260913, 'independent_c0_comparisons': cycles,
            'checks': 'Independent scalar PI/unwind-first/anti-windup arithmetic, mirror symmetry, exact C0 independence, limits, slew, resets, CAN.',
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (Path(__file__).resolve(), Path(ford_model_action.__file__).resolve())}}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(result, indent=2)+'\n')
  print(json.dumps(result))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--cycles', type=int, default=20_000)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  stress(args.cycles, args.output)
