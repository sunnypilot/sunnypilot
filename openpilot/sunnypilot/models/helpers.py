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

from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.models.constants import Meta, MetaSimPose, MetaTombRaider
from openpilot.common.hardware.hw import Paths
from openpilot.selfdrive.modeld.helpers import usbgpu_present

# SET ME TO THE EXACT JSON VERSION WE SET IN SUNNYPILOT_MODELS REPO
REQUIRED_JSON_VERSION = 18

CUSTOM_MODEL_PATH = Paths.model_root()
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'
ModelManager = custom.ModelManagerSP

ACTIVE_BUNDLE_KEYS = {
  "qcom": "ModelManager_ActiveBundle",
  "usbgpu": "ModelManager_ActiveBundleUSBGPU",
}
_LAST_VALIDATED_RAW: dict[str, dict | None] = {}


def _compute_hash(file_path: str) -> str | None:
  from openpilot.common.file_chunker import open_file_chunked
  try:
    with open_file_chunked(file_path) as file:
      return hashlib.file_digest(file, "sha256").hexdigest().lower()
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
  from openpilot.common.file_chunker import get_chunk_name
  for model in getattr(bundle, 'models', []) or []:
    for artifact in (getattr(model, 'artifact', None),):
      if artifact and getattr(artifact, 'fileName', None):
        if len(artifact.chunks) > 0:
          for i, chunk in enumerate(artifact.chunks):
            chunk_name = get_chunk_name(artifact.fileName, i, len(artifact.chunks))
            if getattr(chunk, 'sha256', None):
              artifacts.append((chunk_name, chunk.sha256))
        else:
          if getattr(artifact, 'downloadUri', None):
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
      if active_bundle.ref and bundle.ref:
        if active_bundle.ref == bundle.ref:
          matching_bundle = bundle
          break
      elif active_bundle.internalName == bundle.internalName:
        matching_bundle = bundle
        break

    if matching_bundle is None:
      return True
    if active_bundle.minimumSelectorVersion != matching_bundle.minimumSelectorVersion:
      return True
    if active_bundle.runner != matching_bundle.runner:
      return True
    if set(_bundle_artifacts(active_bundle)) != set(_bundle_artifacts(matching_bundle)):
      return True

  return not _bundle_is_valid_locally(active_bundle)


def _parse_active_bundle(raw_bundle) -> "custom.ModelManagerSP.ModelBundle | None":
  try:
    if isinstance(raw_bundle, dict) and raw_bundle and is_bundle_version_compatible(raw_bundle):
      return custom.ModelManagerSP.ModelBundle(**raw_bundle)
  except Exception:
    pass
  return None


def get_selected_bundle(params: Params | None = None, source: str = "qcom") -> "custom.ModelManagerSP.ModelBundle | None":
  params = params or Params()
  return _parse_active_bundle(params.get(ACTIVE_BUNDLE_KEYS[source]))


def get_active_source(usbgpu: bool | None = None, usbgpu_active: bool | None = None,
                      usbgpu_loading: bool | None = None, offroad: bool | None = None) -> str:
  if usbgpu is None:
    usbgpu = usbgpu_present()
  state_valid = usbgpu_active is not None or usbgpu_loading is not None or offroad is not None
  big_active = usbgpu and (not state_valid or usbgpu_active or usbgpu_loading or offroad)
  return "usbgpu" if big_active else "qcom"


def get_active_bundle(params: Params | None = None, *, usbgpu: bool | None = None) -> "custom.ModelManagerSP.ModelBundle | None":
  # no cross-slot fallback: an empty active slot means the hardware default, which
  # only stock modeld can run - modeld_v2 requires a real bundle
  params = params or Params()
  return get_selected_bundle(params, get_active_source(usbgpu=usbgpu))


def resolve_bundle_by_ref(
  ref: str, source_bundles: dict[str, list[custom.ModelManagerSP.ModelBundle]],
) -> "tuple[custom.ModelManagerSP.ModelBundle, str] | None":
  for source, bundles in source_bundles.items():
    for bundle in bundles:
      if bundle.ref == ref:
        return bundle, source
  return None


def _validate_active_bundle(params: Params, source: str, available_bundles: list[custom.ModelManagerSP.ModelBundle] | None = None) -> None:
  global _LAST_VALIDATED_RAW

  key = ACTIVE_BUNDLE_KEYS[source]
  raw_bundle = params.get(key)
  if not raw_bundle:
    return

  if _LAST_VALIDATED_RAW.get(key) == raw_bundle:
    return

  active_bundle = _parse_active_bundle(raw_bundle)
  if active_bundle is None or _bundle_needs_reset(active_bundle, available_bundles):
    cloudlog.warning(f"Active model bundle invalid for {source}; resetting to default")
    params.remove(key)
    _LAST_VALIDATED_RAW[key] = None
  else:
    _LAST_VALIDATED_RAW[key] = raw_bundle


def validate_active_bundles(params: Params, source_bundles: dict[str, list[custom.ModelManagerSP.ModelBundle]]) -> None:
  # an empty list means the fetch failed, not that the catalog dropped the bundle
  for source, bundles in source_bundles.items():
    _validate_active_bundle(params, source, bundles or None)
  get_active_model_runner(params, force_check=True)


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
  metadata_path = METADATA_PATH

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
