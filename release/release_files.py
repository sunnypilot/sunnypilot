#!/usr/bin/env python3
import os
import re
from pathlib import Path

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = HERE + "/.."

# blacklisting is for two purposes:
# - minimizing release download size
# - keeping the diff readable
blacklist = [
  "^scripts/",
  "body/STL/",
  "tools/cabana/",
  "panda/examples/",
  "opendbc/generator/",

  "^tools/",
  "^tinygrad_repo/",

  "matlab.*.md",

  ".git$",  # for submodules
  ".git/",
  ".github/",
  ".devcontainer/",
  "Darwin/",
  ".vscode/",

  # no LFS
  ".lfsconfig",
  ".gitattributes",
]

# Sunnypilot blacklist
sunnypilot_blacklist = [
  "system/loggerd/sunnylink_uploader.py",  # Temporarily, until we are ready to roll it out widely
  "system/manager/gitlab_runner.sh",
  ".idea/",
  ".run/",
  ".run/",
  ".*__pycache__/.*",
  ".*\.pyc",
  "tinygrad/*",
  "teleoprtc/*"
  "^body/.*"
  "third_party/snpe/x86_64/*",
  "body/board/canloader.py",
  "body/board/flash_base.sh",
  "body/board/flash_knee.sh",
  "body/board/recover.sh",
  ".*/test/",
  ".*/tests/",
  ".*tinygrad_repo/tinygrad/renderer/",
  "README.md",
  ".*internal/",
  "docs/.*",
  ".sconsign.dblite",
  "release/ci/scons_cache/",
  ".gitlab-ci.yml",
  ".clang-tidy",
  ".dockerignore",
  ".editorconfig",
  ".gitmodules",
  ".pre-commit-config.yaml",
  ".python-version",
  "Dockerfile",
  "dockerfile",
  "SECURITY.md",
  "codecov.yml",
  "conftest.py",
  "poetry.lock",
]

# Merge the blacklists
blacklist += sunnypilot_blacklist

# gets you through the blacklist
whitelist = [
  "^tools/lib/(?!.*__pycache__).*$",
  "tools/bodyteleop/(?!.*__pycache__).*$",

  "tinygrad_repo/openpilot/compile2.py",
  "tinygrad_repo/extra/onnx.py",
  "tinygrad_repo/extra/onnx_ops.py",
  "tinygrad_repo/extra/thneed.py",
  "tinygrad_repo/extra/utils.py",
  "tinygrad_repo/tinygrad/codegen/kernel.py",
  "tinygrad_repo/tinygrad/codegen/linearizer.py",
  "tinygrad_repo/tinygrad/features/image.py",
  "tinygrad_repo/tinygrad/features/search.py",
  "tinygrad_repo/tinygrad/nn/*",
  "tinygrad_repo/tinygrad/renderer/cstyle.py",
  "tinygrad_repo/tinygrad/renderer/opencl.py",
  "tinygrad_repo/tinygrad/runtime/lib.py",
  "tinygrad_repo/tinygrad/runtime/ops_cpu.py",
  "tinygrad_repo/tinygrad/runtime/ops_disk.py",
  "tinygrad_repo/tinygrad/runtime/ops_gpu.py",
  "tinygrad_repo/tinygrad/shape/*",
  "tinygrad_repo/tinygrad/.*.py$",
]

# Sunnypilot whitelist
sunnypilot_whitelist = [
  ".*selfdrive/test/fuzzy_generation.py",
  ".*selfdrive/test/helpers.py",
  ".*selfdrive/test/__init__.py",
  ".*selfdrive/test/setup_device_ci.sh",
  ".*selfdrive/test/test_time_to_onroad.py",
  ".*selfdrive/test/test_onroad.py",
  ".*system/manager/test/test_manager.py",
  ".*system/manager/test/__init__.py",
  ".*system/qcomgpsd/tests/test_qcomgpsd.py",
  ".*system/updated/casync/tests/test_casync.py",
  ".*system/updated/tests/test_git.py",
  ".*system/updated/tests/test_base.py",
  ".*tools/lib/tests/test_route_library.py",
  ".*tools/lib/tests/test_caching.py",
  ".*tools/lib/tests/test_logreader.py",
  ".*tools/lib/tests/test_readers.py",
  ".*tools/lib/tests/__init__.py",
  ".*tools/lib/tests/test_comma_car_segments.py",
  ".*selfdrive/ui/tests/test_translations.py",
  ".*selfdrive/car/tests/__init__.py",
  ".*selfdrive/car/tests/test_car_interfaces.py",
  ".*selfdrive/navd/tests/test_navd.py",
  ".*selfdrive/navd/tests/test_map_renderer.py",
  ".*selfdrive/boardd/tests/test_boardd_loopback.py",
  ".*tinygrad_repo/tinygrad/renderer/opencl.py",
  ".*tinygrad_repo/tinygrad/renderer/cstyle.py",
  ".*INTEGRATION.md",
  ".*HOW-TOS.md",
  ".*CARS.md",
  ".*LIMITATIONS.md",
  ".*CONTRIBUTING.md",
  ".*sunnyhaibin0850_qrcode_paypal.me.png",
]

# Merge the whitelists
whitelist += sunnypilot_whitelist

if __name__ == "__main__":
  for f in Path(ROOT).rglob("**/*"):
    if not (f.is_file() or f.is_symlink()):
      continue

    rf = str(f.relative_to(ROOT))
    blacklisted = any(re.search(p, rf) for p in blacklist)
    whitelisted = any(re.search(p, rf) for p in whitelist)
    if blacklisted and not whitelisted:
      continue

    print(rf)
