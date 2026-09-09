"""Deterministic numerical stress and exhaustive field-boundary CAN checks.

Analytic straight/rotated paths supply an independent y(7) oracle. The
reference slew uses scalar arithmetic. Packing is checked against direct
Float32/CAN packing of the continuous state, independently of host _packed.
No synthetic plant is fitted or used to claim vehicle tracking performance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from opendbc.car.ford.fordcan import create_lat_ctl2_msg
from tools.ford_pscm_lab.model_action_replay import PINNED_OPENDBC, WireCheck, verify_dependency, revision


def line(offset, heading=0.):
  s = np.linspace(0., 30., 33)
  return SimpleNamespace(position=SimpleNamespace(x=s*math.cos(heading), y=offset+s*math.sin(heading)),
                         orientation=SimpleNamespace(z=np.full_like(s, heading)))


def check_raw_packing(wire, controller, path):
  # Set a raw Float32 publication independently of the host quantization helper.
  msg = custom.CarControlSP.new_message()
  msg.fordLateralPath.pathOffset = controller.c0
  msg.fordLateralPath.pathAngle = controller.c1
  raw = create_lat_ctl2_msg(wire.packer, wire.bus, 2 if path.valid else 0, -msg.fordLateralPath.pathOffset,
                            -msg.fordLateralPath.pathAngle, 0., 0., wire.count % 16)
  wire.check(path)
  wire.parser.update([wire.count*10_000_000, [raw]])
  decoded = wire.parser.vl['LateralMotionControl2']
  assert abs(decoded['LatCtlPathOffst_L_Actl']+path.path_offset) < 1e-9
  assert abs(decoded['LatCtlPath_An_Actl']+path.path_angle) < 1e-9


def run(cycles, seed, output, opendbc_revision=PINNED_OPENDBC):
  dependency = verify_dependency(opendbc_revision)
  if cycles < 1:
    raise ValueError('cycles must be positive')
  rng = np.random.default_rng(seed)
  controller, mirrored, wire = ModelActionController(), ModelActionController(), WireCheck()
  c0 = c1 = 0.
  resets = 0
  rates = (4., .5)
  dt_values = (.002, .003, .01, .013, .05, .1)
  max_continuous_step = np.zeros(2)
  for i in range(cycles):
    offset, heading = float(rng.uniform(-8., 8.)), float(rng.uniform(-1.2, 1.2))
    speed = float(rng.uniform(.3, 55.))
    desired = float(rng.uniform(-.15, .15))
    dt = dt_values[i % len(dt_values)]
    active = i % 137 != 0
    valid = i % 211 != 0
    if i % 307 == 0:
      dt = .101
    model, mirror = line(offset, heading), line(-offset, -heading)
    if i % 401 == 0:
      model.position.y[4] = mirror.position.y[4] = math.nan
    out = controller.update(model, desired, speed=speed, dt=dt, active=active, valid=valid)
    other = mirrored.update(mirror, -desired, speed=speed, dt=dt, active=active, valid=valid)
    expected_valid = active and valid and dt <= .1 and i % 401 != 0
    assert out.valid == other.valid == expected_valid
    previous = np.array([c0, c1])
    if expected_valid:
      target = (max(-5.11, min(5.11, offset+7.*math.sin(heading))), max(-.5, min(.5, max(7., speed)*desired)))
      c0 += max(-4.*dt, min(4.*dt, target[0]-c0))
      c1 += max(-.5*dt, min(.5*dt, target[1]-c1))
      step = abs(np.array([controller.c0, controller.c1])-previous)
      assert (step <= np.array(rates)*dt+1e-10).all()
      max_continuous_step = np.maximum(max_continuous_step, step)
    else:
      c0 = c1 = 0.
      resets += 1
      assert out.path_offset == out.path_angle == 0.
    assert abs(controller.c0-c0) < 1e-10 and abs(controller.c1-c1) < 1e-10
    assert abs(controller.c0+mirrored.c0) < 1e-10 and abs(controller.c1+mirrored.c1) < 1e-10
    assert abs(out.path_offset+other.path_offset) <= .0100001
    assert abs(out.path_angle+other.path_angle) <= .0005001
    assert out.curvature == out.curvature_rate == other.curvature == other.curvature_rate == 0.
    check_raw_packing(wire, controller, out)

  # Every representable host C0/C1 value, plus the float32 immediately below,
  # at, and above each half-quantum transition. Seed the slew positions only
  # here to isolate packing from slew; the sequence above checks actual slew.
  boundary_cases = 0
  for field, resolution, low, high in ((0, .01, -5.11, 5.11), (1, .0005, -.5, .5)):
    grid = np.arange(round(low/resolution), round(high/resolution)+1)*resolution
    for value in np.r_[grid, (grid[:-1]+grid[1:])/2.]:
      raw = np.float32(value)
      for scalar in (np.nextafter(raw, np.float32(-np.inf)), raw, np.nextafter(raw, np.float32(np.inf))):
        selected = float(np.clip(scalar, low, high))
        offset, heading = (selected, 0.) if field == 0 else (0., selected)
        controller.c0, controller.c1 = offset, heading
        out = controller.update(line(offset), heading/20., speed=20., dt=.01)
        check_raw_packing(wire, controller, out)
        boundary_cases += 1
  report = {'seed': seed, 'random_cycles': cycles, 'mirrored_core_updates': cycles,
            'invalid_or_inactive_resets': resets, 'field_boundary_cases': boundary_cases,
            'float32_can_round_trips': wire.count, 'analytic_targets_scalar_slew_and_mirror_checks_pass': True,
            'direct_raw_float32_packing_matches_host_output': True, 'max_continuous_step_c0_c1': max_continuous_step.tolist(),
            'calibration_approved': False, 'scope': 'Numerical construction only; no PSCM response or closed-loop performance claims.',
            'opendbc_import_head': revision(dependency),
            'source_sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (Path(__file__), Path(ford_model_action.__file__), Path(__file__).with_name('model_action_replay.py'))}}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: v for k, v in report.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--cycles', type=int, default=200_000)
  parser.add_argument('--seed', type=int, default=20260907)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--opendbc-revision', default=PINNED_OPENDBC,
                      help='Exact required dependency commit; defaults to the historical replay pin.')
  args = parser.parse_args()
  run(args.cycles, args.seed, args.output, args.opendbc_revision)
