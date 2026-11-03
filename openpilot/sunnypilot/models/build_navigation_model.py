"""Parked preparation of the exact RL Navigation model; never selects it."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import requests

from openpilot.sunnypilot.models.navigation_model import (MANIFEST_NAME, SOURCE_COMMIT, SOURCE_ONNX_BYTES, SOURCE_ONNX_SHA256,
                                                        SOURCE_ONNX_URL, file_sha256, installed_bundle)

COMPILE_ENV = {'DEBUG': '1', 'DEV': 'USB+AMD:LLVM', 'FRAME_DEV': 'CPU', 'FLOAT16': '1',
               'GMMU': '0', 'TC_OPT': '2', 'TC_MIN_GLOBALS': '32'}
COMPILER_SHA256 = '0ff7415619aa267914f858c24b3f3c32583f75aceebd89ec4f56e70e9daf32ac'


class PreparationCancelled(RuntimeError):
  pass


def check_allowed(params, queued):
  if params.get_bool('IsOnroad'):
    raise PreparationCancelled('Stopped because the device entered onroad. Park before preparing again.')
  if queued and params.get('ModelManager_DownloadRef') is None:
    raise PreparationCancelled('Navigation model preparation canceled.')


def preflight(basedir, hardware):
  if not hardware:
    raise RuntimeError('Preparation requires a comma device with a supported Chestnut GPU.')
  compiler = Path(basedir) / 'openpilot/sunnypilot/modeld_v2/compile_modeld_v2.py'
  if not compiler.is_file() or file_sha256(compiler) != COMPILER_SHA256:
    raise RuntimeError('Target compiler is missing or differs from the reviewed source. Update this branch first.')
  # Use the same search order and optional paths as the target runtime.
  from tinygrad.runtime.support.c import DLL
  usb = DLL.findlib('libusb', ['usb-1.0'])
  if not usb:
    raise RuntimeError('Required libusb is missing. No model was built; update the device system software.')
  ctypes.CDLL(usb)
  library = DLL.findlib('llvm', [f'LLVM-{version}' for version in range(21, 13, -1)] + ['LLVM'])
  if library:
    llvm = ctypes.CDLL(library)
    if hasattr(llvm, 'LLVMGetVersion') and hasattr(llvm, 'LLVMInitializeAMDGPUTarget'):
      major, minor, patch = ctypes.c_uint(), ctypes.c_uint(), ctypes.c_uint()
      llvm.LLVMGetVersion(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
      if major.value >= 18:
        return compiler
  raise RuntimeError('LLVM 18 or newer with AMDGPU support is missing. No model was built; update the device system software.')


def download_source(path, check, report):
  """Bounded stream, exact length and authoritative hash; partial bytes never become a source."""
  if path.is_file() and path.stat().st_size == SOURCE_ONNX_BYTES:
    report('verifying', 'Verifying cached navigation model', 0)
    if file_sha256(path) == SOURCE_ONNX_SHA256:
      check()
      return
  partial = path.with_suffix('.partial')
  try:
    check()
    report('downloading', 'Downloading navigation model', 0)
    digest, total, started = hashlib.sha256(), 0, time.monotonic()
    with requests.get(SOURCE_ONNX_URL, stream=True, timeout=(15, 5), headers={'Accept-Encoding': 'identity'}) as response:
      response.raise_for_status()
      length = response.headers.get('Content-Length')
      if length is not None and int(length) != SOURCE_ONNX_BYTES:
        raise RuntimeError('Navigation model download has an unexpected length.')
      with partial.open('wb') as stream:
        for block in response.iter_content(chunk_size=256 * 1024):
          check()
          if not block:
            continue
          total += len(block)
          if total > SOURCE_ONNX_BYTES:
            raise RuntimeError('Navigation model download exceeded its pinned size.')
          stream.write(block)
          digest.update(block)
          elapsed = max(.001, time.monotonic() - started)
          report('downloading', 'Downloading navigation model', min(99, total / SOURCE_ONNX_BYTES * 100), total / elapsed)
    if total != SOURCE_ONNX_BYTES or digest.hexdigest() != SOURCE_ONNX_SHA256:
      raise RuntimeError('Navigation model download failed its official size/SHA-256 verification.')
    check()
    partial.replace(path)
  finally:
    partial.unlink(missing_ok=True)


def prepare(root, basedir, params, hardware, *, queued=False, onnx=None, report=lambda *_args: None):
  def check():
    check_allowed(params, queued)
  check()
  report('verifying', 'Checking target build requirements', 0)
  compiler = preflight(basedir, hardware)
  root.mkdir(parents=True, exist_ok=True)
  # Source + compiled output + compiler scratch; fail before the large transfer.
  if shutil.disk_usage(root).free < 4 * 1024 ** 3:
    raise RuntimeError('At least 4 GiB of free model storage is required for preparation.')
  if installed_bundle(root) is not None:
    report('ready', 'Navigation model ready — select it in the Chestnut model selector', 100)
    return
  source = Path(onnx) if onnx else root / 'rl_nav_80eedcdd_source.onnx'
  if onnx:
    if source.stat().st_size != SOURCE_ONNX_BYTES or file_sha256(source) != SOURCE_ONNX_SHA256:
      raise RuntimeError('The ONNX bytes do not match the official RL Navigation artifact.')
  else:
    download_source(source, check, report)
  check()
  with tempfile.TemporaryDirectory(prefix='.rl-nav-build-', dir=root) as directory:
    temporary = Path(directory)
    output = temporary / 'navigation.pkl'
    report('building', 'Building navigation model — keep the device parked', 0)
    command = [sys.executable, str(compiler), str(source.resolve()), str(output), '--device-input', '*', '--benchmark-runs', '1']
    log_path = root / 'rl_nav_80eedcdd_build.log'
    with log_path.open('w') as log, subprocess.Popen(command, cwd=basedir, env=os.environ | COMPILE_ENV,
                                                   stdout=log, stderr=subprocess.STDOUT) as process:
      try:
        while process.poll() is None:
          check()
          time.sleep(.2)
        if process.returncode:
          raise RuntimeError(f'Target compilation failed (exit {process.returncode}); see {log_path.name}. No model was registered.')
      finally:
        if process.poll() is None:
          process.terminate()
          try:
            process.wait(timeout=2)
          except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    check()
    report('verifying', 'Verifying compiled navigation model', 99)
    digest = file_sha256(output)
    name = 'rl_nav_80eedcdd_' + digest[:16] + '_tinygrad.pkl'
    descriptor = {'version': 1, 'target': 'chestnut', 'sourceOnnxSha256': SOURCE_ONNX_SHA256,
                  'sourceRef': 'commaai/openpilot:' + SOURCE_COMMIT, 'sourceCheckpoint': '80eedcdd/12864 (not the separate N16 PKL)',
                  'artifact': {'fileName': name, 'sha256': digest}, 'compilerEnvironment': COMPILE_ENV,
                  'compilerSha256': file_sha256(compiler)}
    output.rename(temporary / name)
    (temporary / MANIFEST_NAME).write_text(json.dumps(descriptor, indent=2) + '\n')
    if installed_bundle(temporary) is None:
      raise RuntimeError('Compiled model failed its plain-format/navigation protocol checks. No model was registered.')
    check()
    (temporary / name).replace(root / name)
    check()
    (temporary / MANIFEST_NAME).replace(root / MANIFEST_NAME)
  report('ready', 'Navigation model ready — select it in the Chestnut model selector', 100)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--onnx', type=Path, help='Optional already downloaded official-SHA ONNX')
  parser.add_argument('--queued', action='store_true', help='Honor the existing ModelManager cancel request')
  parser.add_argument('--status-file', type=Path)
  args = parser.parse_args()
  from openpilot.common.basedir import BASEDIR
  from openpilot.common.hardware import COMMA_HARDWARE
  from openpilot.common.hardware.hw import Paths
  from openpilot.common.params import Params

  def report(stage, message, progress, speed=0):
    payload = {'stage': stage, 'message': message, 'progress': progress, 'speed': speed}
    if args.status_file:
      temporary = args.status_file.with_suffix('.tmp')
      temporary.write_text(json.dumps(payload))
      temporary.replace(args.status_file)
    else:
      print(message, flush=True)
  try:
    prepare(Path(Paths.model_root()), BASEDIR, Params(), COMMA_HARDWARE, queued=args.queued, onnx=args.onnx, report=report)
  except Exception as error:
    report('failed', str(error), 0)
    raise SystemExit(1) from error


if __name__ == '__main__':
  main()
