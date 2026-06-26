"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os
import pickle
import sys
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_OUTPUT_KEYS = frozenset({
  "plan",
  "lane_lines",
  "road_edges",
  "lead",
  "desire_state",
  "desire_pred",
  "meta",
  "lead_prob",
  "lane_lines_prob",
  "pose",
  "wide_from_device_euler",
  "road_transform",
  "hidden_state",
})
OPTIONAL_OUTPUT_KEYS = frozenset({
  "planplus",
  "sim_pose",
  "desired_curvature",
})


def validate_model_outputs(metadata_paths: list[Path]) -> None:
  combined_keys: set[str] = set()
  for path in metadata_paths:
    if path.stat().st_size == 0:
      print(f"skipping empty metadata: {path}")
      continue
    with open(path, "rb") as f:
      metadata = pickle.load(f)
    combined_keys.update(metadata.get("output_slices", {}).keys())
  missing = REQUIRED_OUTPUT_KEYS - combined_keys
  if missing:
    raise ValueError(f"Combined model metadata is missing required output keys: {sorted(missing)}")
  detected_optional = sorted(OPTIONAL_OUTPUT_KEYS & combined_keys)
  if detected_optional:
    print(f"Optional output keys detected: {detected_optional}")


def create_short_name(full_name):
  # Remove parentheses and extract alphanumeric words
  clean_name = re.sub(r'\([^)]*\)', '', full_name)
  words = [re.sub(r'[^a-zA-Z0-9]', '', word) for word in clean_name.split() if re.sub(r'[^a-zA-Z0-9]', '', word)]

  if len(words) == 1:
    return words[0][:8].upper()

  # Handle special case: Name + Version (e.g., "Word A1" -> "WordA1")
  if len(words) == 2 and re.match(r'^[A-Za-z]\d+$', words[1]):
    return (words[0] + words[1])[:8].upper()

  result = ""
  for word in words:
    # Version or number patterns
    if (re.match(r'^\d+[a-zA-Z]+$', word) or
        re.match(r'^\d+[vVbB]\d+$', word) or
        re.match(r'^[vVbB]\d+$', word) or
        re.match(r'^\d{4}$', word)):
      result += word.upper()
    # All uppercase abbreviations (2-3 letters)
    elif re.match(r'^[A-Z]{2,3}$', word):
      result += word
    # Letters+digits (for example tr15 rev2)
    elif re.match(r'^[a-zA-Z]+[0-9]+$', word):
      result += word[0].upper() + ''.join(re.findall(r'\d+', word))
    elif word.isalpha():
      result += word[0].upper()
    elif word.isdigit():
      result += word
    else:
      result += word[0].upper()
  return result[:8]


def _read_pkl_bytes(pkl_path: Path) -> bytes:
  manifest = Path(f"{pkl_path}.chunkmanifest")
  if manifest.exists():
    num_chunks = int(manifest.read_text().strip())
    parts = []
    for i in range(num_chunks):
      chunk = Path(f"{pkl_path}.chunk{i + 1:02d}of{num_chunks:02d}")
      parts.append(chunk.read_bytes())
    return b''.join(parts)
  return pkl_path.read_bytes()


def _find_driving_pkl(output_path: Path) -> Path | None:
  for pattern in ('driving_tinygrad.pkl', 'driving_*_tinygrad.pkl'):
    matches = sorted(output_path.glob(pattern))
    if matches:
      return matches[0]
  for pattern in ('driving_tinygrad.pkl.chunkmanifest', 'driving_*_tinygrad.pkl.chunkmanifest'):
    matches = sorted(output_path.glob(pattern))
    if matches:
      return Path(str(matches[0]).removesuffix('.chunkmanifest'))
  return None


def _rename_pkl_with_chunks(old_pkl: Path, new_pkl: Path) -> Path:
  manifest = Path(f"{old_pkl}.chunkmanifest")
  if manifest.exists():
    for f in sorted(old_pkl.parent.glob(f"{old_pkl.name}.chunk*")):
      f.rename(old_pkl.parent / f.name.replace(old_pkl.name, new_pkl.name, 1))
    return new_pkl
  return old_pkl.rename(new_pkl)


def generate_metadata(model_path: Path, output_dir: Path, short_name: str, driving_pkl: Path):
  base = model_path.stem
  metadata_file = output_dir / f"{base}_metadata.pkl"

  if short_name:
    renamed_meta = output_dir / f"{base}_{short_name.lower()}_metadata.pkl"
    if metadata_file.exists() and not renamed_meta.exists():
      metadata_file = metadata_file.rename(renamed_meta)
    elif renamed_meta.exists():
      metadata_file = renamed_meta

  if not metadata_file.exists():
    print(f"Warning: Missing metadata for {base} ({metadata_file}), skipping", file=sys.stderr)
    return

  tinygrad_hash = hashlib.sha256(_read_pkl_bytes(driving_pkl)).hexdigest()

  with open(metadata_file, 'rb') as f:
    metadata_hash = hashlib.sha256(f.read()).hexdigest()

  model_type = "offPolicy" if "off_policy" in base else "onPolicy" if "on_policy" in base else base.split("_")[-1]

  return {
    "type": model_type,
    "artifact": {
      "file_name": driving_pkl.name,
      "download_uri": {
        "url": "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai/-/raw/main/",
        "sha256": tinygrad_hash
      }
    },
    "metadata": {
      "file_name": metadata_file.name,
      "download_uri": {
        "url": "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai/-/raw/main/",
        "sha256": metadata_hash
      }
    }
  }


def create_metadata_json(models: list, output_dir: Path, custom_name=None, short_name=None, is_20hz=False, upstream_branch="unknown"):
  metadata_json = {
    "short_name": short_name,
    "display_name": custom_name or upstream_branch,
    "is_20hz": is_20hz,
    "ref": upstream_branch,
    "environment": "development",
    "runner": "tinygrad",
    "index": -1,
    "minimum_selector_version": "-1",
    "generation": "-1",
    "build_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "overrides": {},
    "models": models,
  }

  # Write metadata to output_dir
  with open(output_dir / "metadata.json", "w") as f:
    json.dump(metadata_json, f, indent=2)

  print(f"Generated metadata.json with {len(models)} models.")


if __name__ == "__main__":
  import argparse
  import glob

  parser = argparse.ArgumentParser(description="Generate metadata for model files")
  parser.add_argument("--model-dir", default="./models", help="Directory containing ONNX model files")
  parser.add_argument("--output-dir", default="./output", help="Output directory for metadata")
  parser.add_argument("--custom-name", help="Custom display name for the model")
  parser.add_argument("--is-20hz", action="store_true", help="Whether this is a 20Hz model")
  parser.add_argument("--validate-only", action="store_true")
  parser.add_argument("--upstream-branch", default="unknown", help="Upstream branch name")
  args = parser.parse_args()

  if args.validate_only:
    metadata_paths = glob.glob(os.path.join(args.model_dir, "*_metadata.pkl"))
    if not metadata_paths:
      print(f"No metadata files found in {args.model_dir}", file=sys.stderr)
      sys.exit(1)
    validate_model_outputs([Path(p) for p in metadata_paths])
    print(f"Validated {len(metadata_paths)} metadata files successfully.")
    sys.exit(0)

  # Find all ONNX files in the given directory
  model_paths = glob.glob(os.path.join(args.model_dir, "*.onnx"))
  if not model_paths:
    print(f"No ONNX files found in {args.model_dir}", file=sys.stderr)
    sys.exit(1)

  _output_dir = Path(args.output_dir)
  _output_dir.mkdir(exist_ok=True, parents=True)
  _short_name = create_short_name(args.custom_name) if args.custom_name else None

  _driving_pkl = _find_driving_pkl(_output_dir)
  if not _driving_pkl:
    print(f"No driving_tinygrad.pkl found in {_output_dir}", file=sys.stderr)
    sys.exit(1)

  if _short_name:
    new_pkl = _output_dir / f"driving_{_short_name.lower()}_tinygrad.pkl"
    if not new_pkl.exists():
      _driving_pkl = _rename_pkl_with_chunks(_driving_pkl, new_pkl)
    else:
      _driving_pkl = new_pkl

  _models = []

  for _model_path in model_paths:
    _model_metadata = generate_metadata(Path(_model_path), _output_dir, _short_name, _driving_pkl)
    if _model_metadata:
      _models.append(_model_metadata)

  if _models:
    create_metadata_json(_models, _output_dir, args.custom_name, _short_name, args.is_20hz, args.upstream_branch)
  else:
    print("No models processed.", file=sys.stderr)
