"""Offroad target build/registration; never selects or starts the model.

The complete Nav graph has not yet been compiled on a supported target in this
work. This uses the repository's existing Chestnut compile recipe, rather than
pretending the Mac ORT smoke provides a device artifact or numerical parity.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from openpilot.sunnypilot.models.navigation_model import MANIFEST_NAME, SOURCE_COMMIT, SOURCE_ONNX_SHA256, file_sha256, installed_bundle

COMPILE_ENV = {'DEBUG': '1', 'DEV': 'USB+AMD:LLVM', 'FRAME_DEV': 'CPU', 'FLOAT16': '1',
               'GMMU': '0', 'TC_OPT': '2', 'TC_MIN_GLOBALS': '32'}


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--onnx', required=True, type=Path, help='Already downloaded exact official-SHA ONNX')
  args = parser.parse_args()
  from openpilot.common.basedir import BASEDIR
  from openpilot.common.hardware import COMMA_HARDWARE
  from openpilot.common.hardware.hw import Paths
  from openpilot.common.params import Params

  params = Params()
  if not COMMA_HARDWARE or params.get_bool('IsOnroad'):
    parser.error('This build requires an offroad comma device with a supported Chestnut GPU; Mac outputs are not device artifacts.')
  if file_sha256(args.onnx) != SOURCE_ONNX_SHA256:
    parser.error('The ONNX bytes do not match the official RL Navigation artifact.')
  root = Path(Paths.model_root())
  root.mkdir(parents=True, exist_ok=True)
  compiler = Path(BASEDIR) / 'openpilot/sunnypilot/modeld_v2/compile_modeld_v2.py'
  with tempfile.TemporaryDirectory(prefix='.rl-nav-build-', dir=root) as directory:
    output = Path(directory) / 'rl_nav_80eedcdd_tinygrad.pkl'
    command = [sys.executable, str(compiler), str(args.onnx.resolve()), str(output), '--device-input', '*', '--benchmark-runs', '1']
    with subprocess.Popen(command, cwd=BASEDIR, env=os.environ | COMPILE_ENV) as process:
      while process.poll() is None:
        if params.get_bool('IsOnroad'):
          process.terminate()
          try:
            process.wait(timeout=5)
          except subprocess.TimeoutExpired:
            process.kill()
          raise RuntimeError('Build stopped because the device entered onroad; no model was registered.')
        time.sleep(.2)
      if process.returncode:
        raise RuntimeError(f'Existing target compiler failed (exit {process.returncode}); no model was registered.')
    if params.get_bool('IsOnroad'):
      raise RuntimeError('Device entered onroad; no model was registered.')
    digest = file_sha256(output)
    name = 'rl_nav_80eedcdd_' + digest[:16] + '_tinygrad.pkl'
    descriptor = {'version': 1, 'target': 'chestnut', 'sourceOnnxSha256': SOURCE_ONNX_SHA256,
                  'sourceRef': 'commaai/openpilot:' + SOURCE_COMMIT, 'sourceCheckpoint': '80eedcdd/12864 (not the separate N16 PKL)',
                  'artifact': {'fileName': name, 'sha256': digest}, 'compilerEnvironment': COMPILE_ENV,
                  'compilerSha256': file_sha256(compiler)}
    # Validate in the temporary directory before publishing either artifact.
    output.rename(Path(directory) / name)
    (Path(directory) / MANIFEST_NAME).write_text(json.dumps(descriptor, indent=2) + '\n')
    if installed_bundle(directory) is None:
      raise RuntimeError('Target artifact failed its plain-format/navigation protocol checks; not registered.')
    (Path(directory) / name).replace(root / name)
    (Path(directory) / MANIFEST_NAME).replace(root / MANIFEST_NAME)
  print('Verified RL Navigation build registered. Select it explicitly in the Chestnut model selector while offroad.')
  print('This build check is not a route-following, curb-clearance or source-vs-device numerical parity verdict.')


if __name__ == '__main__':
  main()
