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
  ".idea/",
  ".run/",
  ".run/",
  "release/ci/scons_cache/",
  ".gitlab-ci.yml",
  ".clang-tidy",
  ".dockerignore",
  ".editorconfig",
  ".gitmodules",
  ".pre-commit-config.yaml",
  ".python-version",
  ".dockerignore",
  "tinygrad/",
  "__pycache__/",
  ".pytest_cache/",
  ".sconsign.dblite",
  ".DS_Store",
  ".env",
  ".*/.gitignore",
  "Jenkinsfile",
  "poetry.lock",
  "panda/SConstruct",
  "panda/setup.cfg",
  "panda/setup.py",
  "panda/tests/__init__.py",
  "panda/tests/benchmark.py",
  "panda/tests/black_white_loopback_test.py",
  "panda/tests/black_white_relay_endurance.py",
  "panda/tests/black_white_relay_test.py",
  "panda/tests/bulk_write_test.py",
  "panda/tests/can_printer.py",
  "panda/tests/canfd/test_canfd.py",
  "panda/tests/check_fw_size.py",
  "panda/tests/ci_shell.sh",
  "panda/tests/debug_console.py",
  "panda/tests/development/register_hashmap_spread.py",
  "panda/tests/echo.py",
  "panda/tests/elm_car_simulator.py",
  "panda/tests/elm_throughput.py",
  "panda/tests/fan/fan_test.py",
  "panda/tests/fan/fan_tuning.py",
  "panda/tests/get_version.py",
  "panda/tests/health_test.py",
  "panda/tests/hitl/__init__.py",
  "panda/tests/hitl/1_program.py",
  "panda/tests/hitl/2_health.py",
  "panda/tests/hitl/3_usb_to_can.py",
  "panda/tests/hitl/4_can_loopback.py",
  "panda/tests/hitl/5_spi.py",
  "panda/tests/hitl/6_safety.py",
  "panda/tests/hitl/7_internal.py",
  "panda/tests/hitl/8_misc.py",
  "panda/tests/hitl/9_harness.py",
  "panda/tests/hitl/conftest.py",
  "panda/tests/hitl/helpers.py",
  "panda/tests/hitl/known_bootstub/bootstub_f4_first_dos_production.panda.bin",
  "panda/tests/hitl/known_bootstub/bootstub_f4_only_bcd.panda.bin",
  "panda/tests/hitl/known_bootstub/bootstub.panda_h7.bin",
  "panda/tests/hitl/reset_jungles.py",
  "panda/tests/hitl/run_parallel_tests.sh",
  "panda/tests/hitl/run_serial_tests.sh",
  "panda/tests/ir_test.py",
  "panda/tests/libpanda/libpanda_py.py",
  "panda/tests/libpanda/libpanda.so",
  "panda/tests/libpanda/panda.c",
  "panda/tests/libpanda/panda.os",
  "panda/tests/libpanda/safety_helpers.h",
  "panda/tests/libpanda/safety_helpers.py",
  "panda/tests/libpanda/SConscript",
  "panda/tests/libs/resetter.py",
  "panda/tests/loopback_test.py",
  "panda/tests/message_drop_test.py",
  "panda/tests/misra/coverage_table",
  "panda/tests/misra/install.sh",
  "panda/tests/misra/suppressions.txt",
  "panda/tests/misra/test_misra.sh",
  "panda/tests/misra/test_mutation.py",
  "panda/tests/read_flash_spi.py",
  "panda/tests/read_st_flash.sh",
  "panda/tests/read_winusb_descriptors.py",
  "panda/tests/reflash_internal_panda.py",
  "panda/tests/relay_test.py",
  "panda/tests/restore_flash_spi.py",
  "panda/tests/safety_replay/__init__.py",
  "panda/tests/safety_replay/helpers.py",
  "panda/tests/safety_replay/replay_drive.py",
  "panda/tests/safety/__init__.py",
  "panda/tests/safety/common.py",
  "panda/tests/safety/hyundai_common.py",
  "panda/tests/safety/test_body.py",
  "panda/tests/safety/test_chrysler.py",
  "panda/tests/safety/test_defaults.py",
  "panda/tests/safety/test_elm327.py",
  "panda/tests/safety/test_ford.py",
  "panda/tests/safety/test_gm.py",
  "panda/tests/safety/test_honda.py",
  "panda/tests/safety/test_hyundai_canfd.py",
  "panda/tests/safety/test_hyundai.py",
  "panda/tests/safety/test_mazda.py",
  "panda/tests/safety/test_nissan.py",
  "panda/tests/safety/test_subaru_preglobal.py",
  "panda/tests/safety/test_subaru.py",
  "panda/tests/safety/test_tesla.py",
  "panda/tests/safety/test_toyota.py",
  "panda/tests/safety/test_volkswagen_mqb.py",
  "panda/tests/safety/test_volkswagen_pq.py",
  "panda/tests/safety/test.sh",
  "panda/tests/setup_device_ci.sh",
  "panda/tests/som_debug.sh",
  "panda/tests/som/on-device.py",
  "panda/tests/som/test_bootkick.py",
  "panda/tests/spam_can.py",
  "panda/tests/standalone_test.py",
  "panda/tests/test_rsa.c",
  "panda/tests/usbprotocol/test_comms.py",
  "panda/tests/usbprotocol/test_pandalib.py",
  "panda/tests/usbprotocol/test.sh",

  "selfdrive/boardd/tests/",
]

# Merge the blacklists
blacklist += sunnypilot_blacklist

# gets you through the blacklist
whitelist = [
  "^tools/lib/(?!.*__pycache__).*$",
  "tools/bodyteleop/",

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
  "tinygrad_repo/tinygrad/.*.py",
]

# Sunnypilot whitelist
sunnypilot_blacklist = [
  "selfdrive/boardd/tests/test_boardd_loopback.py",
]

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
