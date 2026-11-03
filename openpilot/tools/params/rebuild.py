#!/usr/bin/env python3
"""Rebuild only the release's ARM64 Linux Params C API, in an isolated container."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
import urllib.request
import zipfile

SOURCE_FILES = [
  'openpilot/common/params.h', 'openpilot/common/params.cc', 'openpilot/common/params_c.cc',
  'openpilot/common/params_keys.h', 'openpilot/common/queue.h', 'openpilot/common/timing.h',
  'openpilot/common/util.cc', 'openpilot/common/util.h', 'openpilot/common/swaglog.cc', 'openpilot/common/swaglog.h',
  'openpilot/common/hardware/hw.h', 'openpilot/common/hardware/base.h',
  'openpilot/common/hardware/comma/hardware.h', 'openpilot/common/hardware/pc/hardware.h',
  'openpilot/common/version.h', 'openpilot/sunnypilot/common/version.h',
  'openpilot/cereal/gen/cpp/log.capnp.h', 'openpilot/cereal/gen/cpp/car.capnp.h',
  'openpilot/cereal/gen/cpp/custom.capnp.h', 'openpilot/cereal/gen/cpp/deprecated.capnp.h',
  'openpilot/common/params.py',
]
PACKAGES = {'comma-deps-capnproto', 'comma-deps-json11', 'comma-deps-zeromq'}
IMAGE = 'sunnypilot-params-arm64:bookworm-gcc12'


def digest(path):
  return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_bytes(repo, name):
  path = repo / name
  return path.read_bytes() if path.exists() else subprocess.check_output(['git', 'show', f'HEAD:{name}'], cwd=repo)


def prepare(repo, staging):
  hashes = {}
  for name in SOURCE_FILES + ['openpilot/common/tests/test_params.py', 'openpilot/common/tests/test_params_flag_buffers.py']:
    path = staging / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tracked_bytes(repo, name))
    hashes[name] = digest(path)
  dependencies = []
  lock = tomllib.loads(tracked_bytes(repo, 'uv.lock').decode())
  for package in lock['package']:
    if package['name'] not in PACKAGES:
      continue
    wheel = next(item for item in package['wheels'] if 'aarch64' in item['url'])
    path = staging / 'wheels' / wheel['url'].split('/')[-1]
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
      with urllib.request.urlopen(wheel['url'], timeout=120) as response:
        path.write_bytes(response.read())
    if digest(path) != wheel['hash'].removeprefix('sha256:'):
      raise ValueError(f"Dependency hash mismatch: {package['name']}")
    with zipfile.ZipFile(path) as archive:
      archive.extractall(staging / 'deps')
    dependencies.append({'name': package['name'], 'version': package['version'], 'url': wheel['url'], 'sha256': digest(path)})
  for name in ('rebuild.py', 'verify.py'):
    shutil.copyfile(Path(__file__).with_name(name), staging / name)
  provenance = {'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip(),
                'files': hashes, 'dependencies': dependencies}
  (staging / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


def compile_library():
  root = Path('/build')
  deps = root / 'deps'
  capnp = next(deps.glob('comma_deps_capnproto-*.data/purelib/capnproto/install'))
  json11 = next(deps.glob('comma_deps_json11-*.data/purelib/json11/install'))
  zmq = next(deps.glob('comma_deps_zeromq-*.data/purelib/zeromq/install'))
  (root / 'out').mkdir(exist_ok=True)
  command = ['g++', '-std=c++17', '-D__COMMA_HARDWARE__', '-mcpu=cortex-a57', '-O2', '-g', '-fPIC', '-shared', '-pthread',
             '-I' + str(root / 'openpilot'), '-I' + str(root), '-I' + str(root / 'openpilot/cereal/gen/cpp'),
             '-I' + str(capnp / 'include'), '-I' + str(json11 / 'include'), '-I' + str(zmq / 'include')]
  command += [str(root / 'openpilot/common' / name) for name in ('params_c.cc', 'params.cc', 'util.cc', 'swaglog.cc')]
  command += [str(json11 / 'lib/libjson11.a'), str(zmq / 'lib/libzmq.a'), str(capnp / 'lib/libcapnp.a'), str(capnp / 'lib/libkj.a'),
              '-ldl', '-lrt', '-Wl,-z,defs', '-o', str(root / 'out/libparams_c.so')]
  subprocess.run(command, check=True)
  result = {'command': command, 'compiler': subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
            'machine': subprocess.check_output(['uname', '-m'], text=True).strip(),
            'sha256': digest(root / 'out/libparams_c.so'), 'bytes': (root / 'out/libparams_c.so').stat().st_size}
  (root / 'out/build.json').write_text(json.dumps(result, indent=2) + '\n')
  print(json.dumps(result))


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--work-dir', type=Path)
  parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
  parser.add_argument('--skip-image-build', action='store_true', help='Use an already built, audited builder image')
  parser.add_argument('--image', default=IMAGE)
  args = parser.parse_args()
  if args.inside:
    compile_library()
    return
  if args.work_dir is None:
    parser.error('--work-dir is required (outside the checkout)')
  repo = Path(__file__).resolve().parents[3]
  staging = args.work_dir.resolve()
  if staging == repo or repo in staging.parents:
    parser.error('--work-dir must be outside the checkout')
  staging.mkdir(parents=True, exist_ok=True)
  prepare(repo, staging)
  if not args.skip_image_build:
    subprocess.run(['docker', 'build', '--platform', 'linux/arm64', '-t', args.image, str(Path(__file__).parent)], check=True)
  for command in (['python3', '/build/rebuild.py', '--inside'], ['python3', '/build/verify.py']):
    subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--cap-drop', 'ALL', '--platform', 'linux/arm64',
                    '-v', f'{staging}:/build', '-w', '/build', args.image, *command], check=True)
  print(f"Verified library: {staging / 'out/libparams_c.so'} (not installed automatically)")


if __name__ == '__main__':
  main()
