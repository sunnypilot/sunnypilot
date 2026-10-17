#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os
os.environ['GMMU'] = '0'
import multiprocessing
import time
from openpilot.common.hardware.hw import Paths
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.modeld.helpers import chestnut_present
from openpilot.sunnypilot.modeld_v2.helpers import cache_is_fresh, load_model
from openpilot.sunnypilot.models.helpers import get_selected_bundle


def main():
  """
  The main entry point for offroad cache creation.
  Runs every 10 seconds and checks for stale model caches.
  Chestnut cache needs the gpu to build, so that slot waits until it is plugged in, or simply runs during modeld startup.
  """
  params, failed, spawn = Params(), set(), multiprocessing.get_context("spawn")
  while True:
    for bundle in [get_selected_bundle(params, source) for source in (("qcom", "chestnut") if chestnut_present() else ("qcom",))]:
      path = os.path.join(Paths.model_root(), bundle.models[0].artifact.fileName) if bundle and bundle.models else ""
      if not os.path.isfile(path) or cache_is_fresh(path) or (attempt := (path, os.stat(path).st_mtime_ns)) in failed:
        continue
      (worker := spawn.Process(target=load_model, args=(path,), daemon=True)).start()
      worker.join()
      if not cache_is_fresh(path):
        cloudlog.error(f"model cache warmup failed for {path} with exit code {worker.exitcode}")
        failed.add(attempt)
    time.sleep(10)


if __name__ == "__main__":
  main()
