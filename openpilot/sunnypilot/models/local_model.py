"""Locally built Chestnut models: a fine-tuned driving ONNX compiled on the device, appended to the normal catalog.

A model to build is staged as `<model root>/local_onnx/<id>.onnx` plus `<id>.json` ({"displayName", "shortName",
"sha256"}). "Build local models" in the Models screen (LOCAL_BUILD_REF) or build_local_model.py compiles each staged
ONNX that has no build yet and writes `local_model_<id>_bundle.json` next to the artifact in Paths.model_root(). This
reader rechecks each descriptor's artifact hash, AMD device and native protocol (the generation-12 big model without
navigation inputs, as Flip Flop and Light Speed 2) before exposing a selectable row. Nothing is selected automatically.
"""
import base64
import io
import json
from pathlib import Path
import pickle
import re
import struct

import numpy as np

from openpilot.sunnypilot.models.navigation_model import _SliceMetadata, file_sha256

MANIFEST_PREFIX, MANIFEST_SUFFIX = 'local_model_', '_bundle.json'
STAGING_DIR = 'local_onnx'
LOCAL_BUILD_REF = 'local-build-staged-models'
ID_PATTERN = re.compile(r'^[a-z0-9_]{1,40}$')
SELECTOR_VERSION = 21
BASE_INDEX = 2147483100
FOLDER = 'Local experimental models'
STATE_INPUTS = {
  'state_img_q': ((2, 5, 6, 128, 256), np.uint8), 'state_desire_q': ((132, 1, 8), np.float32),
  'state_feat_q': ((128, 1, 16384), np.float32),
}
INPUTS = {
  'new_img': ((2, 6, 128, 256), np.uint8), 'desire': ((8,), np.float32),
  'traffic_convention': ((1, 2), np.float32), 'action_t': ((1, 2), np.float32),
} | STATE_INPUTS
OUTPUTS = {'outputs': ((1, 18452), np.float32)} | {'next_' + name: value for name, value in STATE_INPUTS.items()}
REQUIRED_SLICES = {'plan': slice(917, 1907), 'action': slice(2062, 2066),
                   'desire_state': slice(2054, 2062), 'desire_pred': slice(855, 887)}
_validated: dict = {}


def manifest_name(model_id: str) -> str:
  return MANIFEST_PREFIX + model_id + MANIFEST_SUFFIX


def compatible_metadata(extras) -> bool:
  try:
    specs, outputs = extras['input_specs'], extras['metadata']['output_shapes']
    if set(specs) != set(INPUTS) or set(outputs) != set(OUTPUTS) or set(extras['output_specs']) != set(OUTPUTS):
      return False
    for name, (shape, dtype) in INPUTS.items():
      if tuple(specs[name][0]) != shape or np.dtype(specs[name][1]) != dtype or 'AMD' not in specs[name][2]:
        return False
    for name, (shape, dtype) in OUTPUTS.items():
      actual = extras['output_specs'][name]
      if tuple(outputs[name]) != shape or tuple(actual[0]) != shape or np.dtype(actual[1]) != dtype or 'AMD' not in actual[2]:
        return False
    encoded = extras['metadata']['metadata']['output_slices'].translate(str.maketrans('', '', ' \t\r\n\v\f'))
    slices = _SliceMetadata(io.BytesIO(base64.b64decode(encoded, validate=True))).load()
    return all(slices.get(name) == value for name, value in REQUIRED_SLICES.items())
  except (ValueError, KeyError, TypeError, IndexError, AttributeError, EOFError, pickle.UnpicklingError):
    return False


def _bundle(root: Path, manifest_path: Path, order: int) -> dict | None:
  try:
    if manifest_path.stat().st_size > 16384:
      return None
    manifest = json.loads(manifest_path.read_text())
    model_id, artifact = manifest['id'], manifest['artifact']
    name, expected = artifact['fileName'], artifact['sha256']
    if (manifest.get('version') != 1 or manifest.get('target') != 'chestnut' or
        not isinstance(model_id, str) or not ID_PATTERN.match(model_id) or manifest_path.name != manifest_name(model_id) or
        not isinstance(manifest.get('displayName'), str) or not 0 < len(manifest['displayName']) <= 80 or
        not isinstance(manifest.get('shortName'), str) or not 0 < len(manifest['shortName']) <= 12 or
        not isinstance(name, str) or Path(name).name != name or not name.endswith('.pkl') or
        not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected)):
      return None
    path = root / name
    if path.resolve().parent != root.resolve():
      return None
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns, expected)
    if key not in _validated:
      if file_sha256(path) != expected:
        return None
      from openpilot.sunnypilot.modeld_v2.helpers import read_parts
      parts, extras = read_parts(str(path))
      if 'run' not in parts or not compatible_metadata(extras):
        return None
      _validated[key] = True
    return {
      'index': BASE_INDEX + order, 'short_name': manifest['shortName'], 'display_name': manifest['displayName'],
      'ref': f'local-{model_id}-{expected[:16]}', 'is_big': True,
      'environment': 'development', 'runner': 'tinygrad', 'generation': 12,
      'is_20hz': True, 'minimum_selector_version': SELECTOR_VERSION,
      'overrides': {'folder': FOLDER, 'lat': '.0', 'long': '.3'},
      'models': [{'type': 'chunked', 'artifact': {'file_name': name,
                  'download_uri': {'url': path.resolve().as_uri(), 'sha256': expected}}}],
    }
  except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, EOFError, pickle.UnpicklingError, struct.error):
    return None


def installed_bundles(model_root) -> list[dict]:
  """Normal selector bundles for every present, verified local build, in manifest-name order."""
  root = Path(model_root)
  bundles = (_bundle(root, path, order) for order, path in enumerate(_manifests(root)))
  return [bundle for bundle in bundles if bundle is not None]


def manifest_for_artifact(model_root, file_name: str) -> str | None:
  """The descriptor that belongs to an installed local artifact, so cache cleanup keeps it with its artifact."""
  for bundle in installed_bundles(model_root):
    if bundle['models'][0]['artifact']['file_name'] == file_name:
      return manifest_name(bundle['ref'].split('-')[1])  # ref is local-<id>-<hash>; ids have no '-'
  return None


def _manifests(root: Path) -> list[Path]:
  try:
    return sorted(p for p in root.iterdir() if p.name.startswith(MANIFEST_PREFIX) and p.name.endswith(MANIFEST_SUFFIX))
  except OSError:
    return []


def staged_models(model_root) -> list[dict]:
  """Staged ONNX models whose build is not installed: [{id, onnx, displayName, shortName, sha256}], by id. Cheap (reads
  only the small JSON files, never hashes), so the UI can call it; the build checks the ONNX hash itself."""
  root = Path(model_root)
  built = set()
  for path in _manifests(root):
    try:
      manifest = json.loads(path.read_text()) if path.stat().st_size <= 16384 else {}
      if (root / Path(manifest['artifact']['fileName']).name).is_file():
        built.add((manifest['id'], manifest['sourceOnnxSha256']))
    except (OSError, ValueError, KeyError, TypeError):
      continue
  staged = []
  try:
    sidecars = sorted((root / STAGING_DIR).glob('*.json'))
  except OSError:
    return []
  for sidecar in sidecars:
    try:
      model_id, onnx = sidecar.stem, sidecar.with_suffix('.onnx')
      info = json.loads(sidecar.read_text()) if sidecar.stat().st_size <= 16384 else {}
      sha256, name, short_name = info['sha256'], info['displayName'], info['shortName']
      if (not ID_PATTERN.match(model_id) or not onnx.is_file() or not isinstance(sha256, str) or len(sha256) != 64 or
          any(c not in '0123456789abcdef' for c in sha256) or not isinstance(name, str) or not 0 < len(name) <= 80 or
          not isinstance(short_name, str) or not 0 < len(short_name) <= 12 or (model_id, sha256) in built):
        continue
      staged.append({'id': model_id, 'onnx': onnx, 'displayName': name, 'shortName': short_name, 'sha256': sha256})
    except (OSError, ValueError, KeyError, TypeError):
      continue
  return staged
