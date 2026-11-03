"""Explicitly installed RL Navigation model, appended to the normal catalog.

No artifact is bundled or selected automatically. The installer verifies the
official ONNX bytes before target compilation; this reader rechecks the resulting
plain artifact hash, device and native protocol before exposing a selectable row.
"""
import base64
import builtins
import hashlib
import io
import json
from pathlib import Path
import pickle
import struct

import numpy as np

SOURCE_COMMIT = 'afbf2e547e9319e2eb9f515e1e4330af63705cec'
SOURCE_ONNX_SHA256 = '1d18c42ea4cd95c8bffab4635844b78b8e2d4e25b9de44a9c5ac2e0961371a2e'
SOURCE_ONNX_BYTES = 814591106
# Alternate transport; accepted only when the bytes match the official upstream LFS pointer above.
SOURCE_ONNX_URL = ('https://github.com/happymaj11r/openpilot-models/releases/download/' +
                   'big-nav-model-integration-1d18c42e/big_driving_supercombo.onnx')
BUILD_REF = 'local-prepare-rl-navigation-80eedcdd'
MODEL_NAME = 'RL Navigation 80eedcdd (experimental)'
MANIFEST_NAME = 'rl_nav_80eedcdd_bundle.json'
SELECTOR_VERSION = 21
_validated = {}


class _SliceMetadata(pickle.Unpickler):
  def find_class(self, module, name):
    if module == 'builtins' and name == 'slice':
      return builtins.slice
    raise pickle.UnpicklingError('Unsupported output-slice metadata class')


def file_sha256(path):
  with Path(path).open('rb') as stream:
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def compatible_metadata(extras):
  try:
    specs, outputs = extras['input_specs'], extras['metadata']['output_shapes']
    expected = {
      'new_img': ((2, 6, 128, 256), np.uint8), 'desire': ((8,), np.float32),
      'traffic_convention': ((1, 2), np.float32), 'action_t': ((1, 2), np.float32),
      'nav_map': ((1, 1, 256, 256), np.float32), 'navigation': ((1, 47), np.float32),
      'state_img_q': ((2, 5, 6, 128, 256), np.uint8), 'state_desire_q': ((132, 1, 8), np.float32),
      'state_feat_q': ((128, 1, 16384), np.float32), 'state_map_features_q': ((128, 1, 64), np.float32),
      'state_navigation_features_q': ((128, 1, 64), np.float32),
    }
    if set(specs) != set(expected):
      return False
    for name, (shape, dtype) in expected.items():
      if tuple(specs[name][0]) != shape or np.dtype(specs[name][1]) != dtype or 'AMD' not in specs[name][2]:
        return False
      if name.startswith('state_') and tuple(outputs.get('next_' + name, ())) != shape:
        return False
    expected_outputs = {'outputs': ((1, 18580), np.float32)} | {
      'next_' + name: value for name, value in expected.items() if name.startswith('state_')}
    if set(outputs) != set(expected_outputs) or set(extras['output_specs']) != set(expected_outputs):
      return False
    for name, (shape, dtype) in expected_outputs.items():
      actual = extras['output_specs'][name]
      if tuple(outputs[name]) != shape or tuple(actual[0]) != shape or np.dtype(actual[1]) != dtype or 'AMD' not in actual[2]:
        return False
    encoded = extras['metadata']['metadata']['output_slices']
    # Upstream ONNX metadata uses wrapped Base64. Permit only ASCII whitespace
    # around its encoded bytes; keep strict decoding and restricted unpickling.
    encoded = encoded.translate(str.maketrans('', '', ' \t\r\n\v\f'))
    slices = _SliceMetadata(io.BytesIO(base64.b64decode(encoded, validate=True))).load()
    required = {'plan': slice(917, 1907), 'action': slice(2062, 2066),
                'desire_state': slice(2054, 2062), 'desire_pred': slice(855, 887)}
    if any(slices.get(name) != value for name, value in required.items()):
      return False
  except (ValueError, KeyError, TypeError, IndexError, AttributeError, EOFError, pickle.UnpicklingError):
    return False
  return True


def installed_bundle(model_root):
  """Return a normal selector bundle only for a present verified target build."""
  root = Path(model_root)
  try:
    manifest_path = root / MANIFEST_NAME
    if manifest_path.stat().st_size > 16384:
      return None
    manifest = json.loads(manifest_path.read_text())
    artifact = manifest['artifact']
    name, expected = artifact['fileName'], artifact['sha256']
    if (manifest.get('version') != 1 or manifest.get('target') != 'chestnut' or
        manifest.get('sourceOnnxSha256') != SOURCE_ONNX_SHA256 or
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
      _validated.clear()
      _validated[key] = True
    return {
      'index': 2147483000, 'short_name': 'RLNAV80', 'display_name': MODEL_NAME,
      'ref': 'local-rl-nav-80eedcdd-' + expected[:16], 'is_big': True,
      'environment': 'development', 'runner': 'tinygrad', 'generation': 12,
      'is_20hz': True, 'minimum_selector_version': SELECTOR_VERSION,
      'overrides': {'folder': 'Local experimental models', 'lat': '.0', 'long': '.3'},
      'models': [{'type': 'chunked', 'artifact': {'file_name': name,
                  'download_uri': {'url': path.resolve().as_uri(), 'sha256': expected}}}],
    }
  except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, EOFError, pickle.UnpicklingError, struct.error):
    return None
