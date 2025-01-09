# Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#
# This file is part of sunnypilot and is licensed under the MIT License.
# See the LICENSE.md file in the root directory for more details.

import hashlib
import os
from openpilot.common.params import Params
from cereal import custom, messaging


async def verify_file(file_path: str, expected_hash: str) -> bool:
  """Verifies file hash against expected hash"""
  if not os.path.exists(file_path):
    return False

  sha256_hash = hashlib.sha256()
  with open(file_path, "rb") as file:
    for chunk in iter(lambda: file.read(4096), b""):
      sha256_hash.update(chunk)

  return sha256_hash.hexdigest().lower() == expected_hash.lower()


def get_active_bundle(params: Params) -> custom.ModelManagerSP.ModelBundle:
  """Gets the active model bundle from cache"""
  if params is None:
    params = Params()

  if active_bundle := params.get("ModelManager_ActiveBundle"):
    return messaging.log_from_bytes(active_bundle, custom.ModelManagerSP.ModelBundle)

  return None


def get_model_runner_by_filename(filename: str) -> custom.ModelManagerSP.Runner:
  if filename.endswith(".thneed"):
    return custom.ModelManagerSP.Runner.snpe

  if filename.endswith("_tinygrad.pkl"):
    return custom.ModelManagerSP.Runner.tinygrad


def get_active_model_runner(params: Params, force_check=False) -> custom.ModelManagerSP.Runner:
  """
  Get the active model runner based on the given parameters and optional force check.

  This function is responsible for retrieving the active model runner, either by using
  an existing cached model runner type or by determining it dynamically through the
  model bundle and its associated models. If no active bundle or specific model type
  is found, it defaults to stock runner (tinygrad).

  :param params: A `Params` instance containing configuration details required to determine
                 the active model runner. If `None`, a new `Params` instance is created.
  :type params: Params
  :param force_check: A boolean flag to forcefully skip the model runner type cache and resolve
                      the active runner explicitly. Defaults to False.
  :type force_check: bool
  :return: The resolved active model runner, either from cache, bundle models, or a default runner.
  :rtype: custom.ModelManagerSP.Runner
  """
  if params is None:
    params = Params()

  if not force_check and (cached_runner := params.get("ModelRunnerTypeCache")):
    return cached_runner

  runner = custom.ModelManagerSP.Runner.tinygrad

  if active_bundle := get_active_bundle(params):
    drive_model = next(model for model in active_bundle.models if model.type == custom.ModelManagerSP.Type.drive)
    runner = get_model_runner_by_filename(drive_model.fileName)

  params.put("ModelRunnerTypeCache", runner)
  return runner
