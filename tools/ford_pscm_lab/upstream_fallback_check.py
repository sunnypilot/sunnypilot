"""Compare all outgoing Ford packets with pinned upstream and custom senders.

Uses trusted local Git sources, identical synthetic inputs, and the actual CAN
packers. Establishes software equivalence, not physical steering performance.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
from types import ModuleType, SimpleNamespace

import numpy as np
import opendbc
from opendbc.car import structs
from opendbc.car.ford.carcontroller import CarController
from opendbc.car.ford.interface import CarInterface
from opendbc.car.ford.values import CAR, DBC, FordFlags


UPSTREAM = 'f95f996f5917dcbbf2e32fe51b606a24cf836af6'
PREVIOUS_CUSTOM = 'c21a9013700734dd20b09e05aa68329ad8cc20f9'


def reference(directory, revision):
  modules, hashes = {}, {}
  for name in ('fordcan', 'carcontroller'):
    path = f'opendbc/car/ford/{name}.py'
    source = subprocess.check_output(['git', '-C', str(directory), 'show', f'{revision}:{path}'], text=True)
    module = ModuleType(f'ford_reference_{name}')
    exec(compile(source, f'{revision}:{path}', 'exec'), module.__dict__)
    modules[name] = module
    hashes[path] = hashlib.sha256(source.encode()).hexdigest()
  modules['carcontroller'].fordcan = modules['fordcan']
  return modules['carcontroller'].CarController, hashes


def run(cycles, output):
  if cycles < 1:
    raise ValueError('cycles per platform must be positive')
  directory = Path(opendbc.__file__).resolve().parent.parent
  upstream, upstream_hashes = reference(directory, UPSTREAM)
  previous, previous_hashes = reference(directory, PREVIOUS_CUSTOM)
  rng = np.random.default_rng(20260911)
  results = []
  for fingerprint in CAR:
    cp = CarInterface.get_non_essential_params(fingerprint)
    cp_sp = CarInterface.get_non_essential_params_sp(cp, fingerprint)
    for enabled in (False, True) if cp.flags & FordFlags.CANFD else (False,):
      candidate = CarController(DBC[fingerprint], cp, cp_sp)
      baseline = (previous if enabled else upstream)(DBC[fingerprint], cp, cp_sp)
      cc, cc_sp = structs.CarControl(), structs.CarControlSP()
      cc_sp.fordLateralPath.enabled = enabled
      vehicle = SimpleNamespace(out=structs.CarState(), buttons_stock_values=defaultdict(int),
                                acc_tja_status_stock_values=defaultdict(int), lkas_status_stock_values=defaultdict(int))
      packets_checked = 0
      for frame in range(cycles):
        cc.latActive = frame % 97 < 75
        cc.actuators.curvature = float(rng.uniform(-.08, .08))
        speed = (0., .3, 5., 9., 9.001, 10., 35., 55.)[frame % 8] if frame % 3 else float(rng.uniform(0., 55.))
        vehicle.out.vEgo = vehicle.out.vEgoRaw = speed
        vehicle.out.yawRate = float(rng.uniform(-1., 1.))
        # Disabled selection must ignore even valid nonzero custom commands.
        path = cc_sp.fordLateralPath
        path.valid = frame % 31 != 0
        path.pathOffset = float(rng.uniform(-5.11, 5.11))
        path.pathAngle = float(rng.uniform(-.5, .5))
        path.curvature = float(rng.uniform(-.02, .02))
        path.curvatureRate = float(rng.uniform(-.001, .001))
        actual, actual_can = candidate.update(cc.as_reader(), cc_sp, vehicle, frame*10_000_000)
        expected, expected_can = baseline.update(cc.as_reader(), cc_sp, vehicle, frame*10_000_000)
        assert actual_can == expected_can, (fingerprint, enabled, frame, actual_can, expected_can)
        assert actual.to_dict() == expected.to_dict(), (fingerprint, enabled, frame)
        packets_checked += len(actual_can)
      results.append({'fingerprint': str(fingerprint), 'custom_enabled': enabled, 'cycles': cycles,
                      'identical_packets': packets_checked})
  report = {'scope': __doc__, 'seed': 20260911, 'upstream_revision': UPSTREAM,
            'previous_custom_revision': PREVIOUS_CUSTOM, 'upstream_source_sha256': upstream_hashes,
            'previous_custom_source_sha256': previous_hashes, 'results': results,
            'total_cycles': sum(r['cycles'] for r in results),
            'total_identical_packets': sum(r['identical_packets'] for r in results),
            'candidate_source_sha256': {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                        (directory/'opendbc/car/ford/carcontroller.py', directory/'opendbc/car/ford/fordcan.py',
                                         directory/'opendbc/car/structs.py')},
            'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(report, indent=2)+'\n')
  print(json.dumps(report, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--cycles', type=int, default=5000, help='Control cycles per platform and selection')
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  run(args.cycles, args.output)
