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


def get_active_bundle(params: Params | None) -> custom.ModelManagerSP.ModelBundle:
  """
  Retrieves and deserializes the active model bundle from the provided parameters.

  This function attempts to extract and deserialize a model bundle from the given
  `params`. If the parameter `ModelManager_ActiveBundle` is present, it is
  deserialized into a `ModelBundle` object. If not, the function returns `None`.

  Note: We intentionally don't set a default value for `params` to encourage
  the caller to provide it explicitly. If not provided, the function will
  instantiate a new `Params` object internally.

  :param params: Optional. Can provide None and will instantiate it itself.
  :type params: Params | None
  :return: A deserialized `ModelBundle` instance if the active bundle
      is found in the provided parameters, otherwise `None`.
  :rtype: custom.ModelManagerSP.ModelBundle | None
  """
  if params is None:
    params = Params()

  if active_bundle := params.get("ModelManager_ActiveBundle"):
    return messaging.log_from_bytes(active_bundle, custom.ModelManagerSP.ModelBundle)

  return None

def is_active_model_20hz(params: Params | None) -> [bool | None]:
  """
  Determine if the active model is operating at 20Hz.

  This function evaluates the provided parameters to determine the active
  bundle and checks its frequency status. If there is no active bundle,
  the function will return None. If a bundle is active, the function will
  return a boolean value indicating whether the model is operating at
  20Hz.

  :param params: System or configuration parameters used to fetch the 
      active bundle. The parameter can be None.
  :type params: Params | None
  :return: A boolean indicating if the active model is operating at 20Hz,
      or None if no active bundle is found.
  :rtype: bool | None
  """
  if active_bundle := get_active_bundle(params):
    return active_bundle.is20hz

  return None