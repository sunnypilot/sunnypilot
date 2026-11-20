"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import hashlib
import os
import pickle
from pathlib import Path
import numpy as np

from cereal import custom
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.models.constants import Meta, MetaSimPose, MetaTombRaider
from openpilot.system.hardware.hw import Paths

# SET ME TO THE EXACT JSON VERSION WE SET IN SUNNYPILOT_MODELS REPO
REQUIRED_JSON_VERSION = 15

CUSTOM_MODEL_PATH = Paths.model_root()
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'
ModelManager = custom.ModelManagerSP
_LAST_VALIDATED_RAW = None


def _compute_hash(file_path: str) -> str | None:
  from openpilot.common.file_chunker import read_file_chunked
  try:
    return hashlib.sha256(read_file_chunked(file_path)).hexdigest().lower()
  except FileNotFoundError:
    return None


async def verify_file(file_path: str, expected_hash: str) -> bool:
  file_hash = _compute_hash(file_path)
  return file_hash == expected_hash.lower() if file_hash else False


def _verify_file(file_path: str, expected_hash: str) -> bool:
  file_hash = _compute_hash(file_path)
  return file_hash == expected_hash.lower() if file_hash else False


def is_bundle_version_compatible(bundle: dict) -> bool:
  """
  The bundle parsed from the json specifies a `minimum_selector_version`, which defines the minimum selector version
  required to load the model. This function ensures that:
    the bundle MUST match the `REQUIRED_JSON_VERSION` set here in helpers.
  """
  return bundle.get("minimumSelectorVersion", 0) == REQUIRED_JSON_VERSION


def _bundle_artifacts(bundle: custom.ModelManagerSP.ModelBundle) -> list[tuple[str, str]]:
  artifacts = []
  for model in getattr(bundle, 'models', []) or []:
    for artifact in (getattr(model, 'artifact', None), getattr(model, 'metadata', None)):
      if artifact and getattr(artifact, 'fileName', None) and getattr(artifact, 'downloadUri', None):
        sha256 = getattr(artifact.downloadUri, 'sha256', None)
        if sha256:
          artifacts.append((artifact.fileName, sha256))
  return artifacts


def _bundle_is_valid_locally(bundle: custom.ModelManagerSP.ModelBundle) -> bool:
  model_root = Paths.model_root()
  return all(_verify_file(os.path.join(model_root, file_name), expected_hash)
             for file_name, expected_hash in _bundle_artifacts(bundle))


def _bundle_needs_reset(active_bundle: custom.ModelManagerSP.ModelBundle, available_bundles: list[custom.ModelManagerSP.ModelBundle] | None) -> bool:
  if active_bundle is None:
    return False

  if available_bundles is not None:
    matching_bundle = None
    for bundle in available_bundles:
      if getattr(active_bundle, 'ref', None) and getattr(bundle, 'ref', None):
        if active_bundle.ref == bundle.ref:
          matching_bundle = bundle
          break
      elif getattr(active_bundle, 'internalName', None) == getattr(bundle, 'internalName', None):
        matching_bundle = bundle
        break

    if matching_bundle is None:
      return True
    if active_bundle.minimumSelectorVersion != matching_bundle.minimumSelectorVersion:
      return True

    active_runner = getattr(active_bundle, 'runner', None)
    matching_runner = getattr(matching_bundle, 'runner', None)
    if active_runner is not None and matching_runner is not None:
      if getattr(active_runner, 'raw', active_runner) != getattr(matching_runner, 'raw', matching_runner):
        return True
    if set(_bundle_artifacts(active_bundle)) != set(_bundle_artifacts(matching_bundle)):
      return True

  return not _bundle_is_valid_locally(active_bundle)


def validate_active_bundle(params: Params, available_bundles: list[custom.ModelManagerSP.ModelBundle] | None = None) -> None:
  global _LAST_VALIDATED_RAW

  raw_bundle = params.get("ModelManager_ActiveBundle")
  if not raw_bundle:
    return

  if raw_bundle == _LAST_VALIDATED_RAW:
    return

  active_bundle = get_active_bundle(params, raw_bundle_dict=raw_bundle)
  if active_bundle is None or _bundle_needs_reset(active_bundle, available_bundles):
    cloudlog.warning("Active model bundle invalid; resetting to default")
    params.remove("ModelManager_ActiveBundle")
    params.put("ModelRunnerTypeCache", int(custom.ModelManagerSP.Runner.stock), block=True)
    _LAST_VALIDATED_RAW = None
  else:
    _LAST_VALIDATED_RAW = raw_bundle


def get_active_bundle(params: Params | None = None, raw_bundle_dict: dict | bytes | None = None) -> "custom.ModelManagerSP.ModelBundle | None":
  params = params or Params()
  try:
    active_bundle_dict = raw_bundle_dict if raw_bundle_dict is not None else (params.get("ModelManager_ActiveBundle") or {})
    if active_bundle_dict and is_bundle_version_compatible(active_bundle_dict):
      return custom.ModelManagerSP.ModelBundle(**active_bundle_dict)
  except Exception:
    pass
  return None


def get_active_model_runner(params: Params | None = None, force_check: bool = False) -> int:
  params = params or Params()
  cached_runner_type = params.get("ModelRunnerTypeCache")
  if cached_runner_type is not None and not force_check:
    return cached_runner_type
  runner_type = custom.ModelManagerSP.Runner.stock
  if active_bundle := get_active_bundle(params):
    runner_type = active_bundle.runner.raw

  if cached_runner_type != runner_type:
    params.put("ModelRunnerTypeCache", int(runner_type), block=True)

  return runner_type


def _get_model():
  if bundle := get_active_bundle():
    drive_model = next(model for model in bundle.models if model.type == ModelManager.Model.Type.supercombo)
    return drive_model
  return None


def load_metadata():
  model = _get_model()
  metadata_path = f"{CUSTOM_MODEL_PATH}/{model.metadata.fileName}" if model else METADATA_PATH

  with open(metadata_path, 'rb') as f:
    return pickle.load(f)


def prepare_inputs(model_metadata: dict) -> dict[str, np.ndarray]:
  return {
    key: np.zeros(shape, dtype=np.float32).flatten()
    for key, shape in model_metadata['input_shapes'].items()
    if 'img' not in key
  }


def load_meta_constants(model_metadata: dict):
  """ Loads the appropriate meta model class based on key shapes"""
  if 'sim_pose' in model_metadata['input_shapes']:
    return MetaSimPose

  meta_slice = model_metadata['output_slices']['meta']
  if (meta_slice.start, meta_slice.stop, meta_slice.step) == (5868, 5921, None):
    return MetaTombRaider

  return Meta


# The following method(s) are modeld helper methods
def plan_x_idxs_helper(constants, plan, model_output) -> list[float]:
  # times at X_IDXS according to plan.
  LINE_T_IDXS = [np.nan] * constants.IDX_N
  LINE_T_IDXS[0] = 0.0
  plan_x = model_output['plan'][0, :, plan.POSITION][:, 0].tolist()
  for xidx in range(1, constants.IDX_N):
    tidx = 0
    # increment tidx until we find an element that's further away than the current xidx
    while tidx < constants.IDX_N - 1 and plan_x[tidx + 1] < constants.X_IDXS[xidx]:
      tidx += 1
    if tidx == constants.IDX_N - 1:
      # if the plan doesn't extend far enough, set plan_t to the max value (10s), then break
      LINE_T_IDXS[xidx] = constants.T_IDXS[constants.IDX_N - 1]
      break
    # interpolate to find `t` for the current xidx
    current_x_val = plan_x[tidx]
    next_x_val = plan_x[tidx + 1]
    p = (constants.X_IDXS[xidx] - current_x_val) / (next_x_val - current_x_val) if abs(
      next_x_val - current_x_val) > 1e-9 else float('nan')
    LINE_T_IDXS[xidx] = p * constants.T_IDXS[tidx + 1] + (1 - p) * constants.T_IDXS[tidx]
  return LINE_T_IDXS
