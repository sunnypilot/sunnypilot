"""Parked build of local Chestnut models from driving ONNX files (e.g. a fine-tuned Flip Flop); never selects one.

Staged models (local_model.py: `<model root>/local_onnx/<id>.onnx` + `<id>.json`) are built by the Models screen's
"build local models" button, which runs `python -m openpilot.sunnypilot.models.build_local_model --queued
--status-file <file>`, or by hand with no arguments over SSH.

Uses the reviewed target compiler and environment of the navigation model build. Each ONNX must match its staged
SHA-256 (a truncated copy is refused). On success the artifact and `local_model_<id>_bundle.json` are in
Paths.model_root() and the model appears in the Chestnut model selector under "Local experimental models".
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from openpilot.sunnypilot.models.build_navigation_model import COMPILE_ENV, PreparationCancelled, preflight
from openpilot.sunnypilot.models.local_model import ID_PATTERN, installed_bundles, manifest_name, staged_models
from openpilot.sunnypilot.models.navigation_model import file_sha256


def build(root: Path, basedir: str, check, compiler: Path, onnx: Path, sha256: str, model_id: str, name: str,
          short_name: str, report) -> Path:
  if not ID_PATTERN.match(model_id):
    raise ValueError('The id must be 1-40 lowercase letters, digits or underscores.')
  report('verifying', f'Checking {name}')
  if file_sha256(onnx) != sha256:
    raise RuntimeError(f'{onnx.name} does not match its staged SHA-256; copy it again.')
  check()
  if shutil.disk_usage(root).free < 4 * 1024 ** 3:
    raise RuntimeError('At least 4 GiB of free model storage is required.')
  log_path = root / f'local_model_{model_id}_build.log'
  with tempfile.TemporaryDirectory(prefix=f'.local-model-{model_id}-', dir=root) as directory:
    temporary = Path(directory)
    output = temporary / 'model.pkl'
    report('building', f'Building {name}; keep the device parked')
    command = [sys.executable, str(compiler), str(onnx.resolve()), str(output), '--device-input', '*', '--benchmark-runs', '1']
    with log_path.open('w') as log, subprocess.Popen(command, cwd=basedir, env=os.environ | COMPILE_ENV,
                                                   stdout=log, stderr=subprocess.STDOUT) as process:
      try:
        while process.poll() is None:
          check()
          time.sleep(.2)
        if process.returncode:
          raise RuntimeError(f'Building {name} failed (exit {process.returncode}); see {log_path.name}. Nothing was registered.')
      finally:
        if process.poll() is None:
          process.terminate()
          try:
            process.wait(timeout=2)
          except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    check()
    report('verifying', f'Verifying {name}')
    digest = file_sha256(output)
    artifact = f'local_{model_id}_{digest[:16]}_tinygrad.pkl'
    output.rename(temporary / artifact)
    descriptor = {'version': 1, 'target': 'chestnut', 'id': model_id, 'displayName': name, 'shortName': short_name,
                  'sourceOnnxSha256': sha256, 'artifact': {'fileName': artifact, 'sha256': digest},
                  'compilerEnvironment': COMPILE_ENV, 'compilerSha256': file_sha256(compiler)}
    manifest = temporary / manifest_name(model_id)
    manifest.write_text(json.dumps(descriptor, indent=2) + '\n')
    if not installed_bundles(temporary):
      raise RuntimeError(f'{name} failed its native protocol checks (inputs, outputs, AMD device, output slices). ' +
                         'Nothing was registered.')
    check()
    for old in root.glob(f'local_{model_id}_*_tinygrad.pkl'):  # an earlier build of the same id
      old.unlink()
    (temporary / artifact).replace(root / artifact)
    manifest.replace(root / manifest.name)
  return root / artifact


def build_staged(root: Path, basedir: str, params, hardware, *, queued=False, report=lambda *_args: None) -> int:
  def check():
    if not params.get_bool('IsOffroad'):
      raise PreparationCancelled('Stopped because the device is not offroad. Park before building again.')
    if queued and params.get('ModelManager_DownloadRef') is None:
      raise PreparationCancelled('Local model build canceled.')

  def stage(name, message, progress=0):
    report({'stage': name, 'message': message, 'progress': progress})

  check()
  stage('checking', 'Checking build requirements')
  compiler = preflight(basedir, hardware)
  pending = staged_models(root)
  if not pending:
    stage('ready', 'No staged local models are waiting to be built', 100)
    return 0
  for number, model in enumerate(pending):
    progress = 100 * number / len(pending)
    build(root, basedir, check, compiler, model['onnx'], model['sha256'], model['id'], model['displayName'],
          model['shortName'], lambda name, message, progress=progress: stage(name, message, progress))
  names = ', '.join(model['displayName'] for model in pending)
  stage('ready', f'Ready: select {names} in the Chestnut model selector', 100)
  return len(pending)


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--queued', action='store_true', help='Honor the existing ModelManager cancel request')
  parser.add_argument('--status-file', type=Path)
  args = parser.parse_args()
  from openpilot.common.basedir import BASEDIR
  from openpilot.common.hardware import COMMA_HARDWARE
  from openpilot.common.hardware.hw import Paths
  from openpilot.common.params import Params

  def report(payload):
    if args.status_file:
      temporary = args.status_file.with_suffix('.tmp')
      temporary.write_text(json.dumps(payload))
      temporary.replace(args.status_file)
    else:
      print(payload['message'], flush=True)
  try:
    build_staged(Path(Paths.model_root()), BASEDIR, Params(), COMMA_HARDWARE, queued=args.queued, report=report)
  except Exception as error:
    report({'stage': 'failed', 'message': str(error), 'progress': 0})
    raise SystemExit(1) from error


if __name__ == '__main__':
  main()
