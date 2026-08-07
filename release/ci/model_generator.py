"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import sys
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, UTC


def create_short_name(full_name: str) -> str:
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


def generate_chunked_model(driving_pkl: Path) -> dict:
  tinygrad_hash = hashlib.sha256(_read_pkl_bytes(driving_pkl)).hexdigest()

  chunks_config = []
  manifest_file = Path(f"{driving_pkl}.chunkmanifest")
  if manifest_file.exists():
    num_chunks = int(manifest_file.read_text().strip())
    for i in range(num_chunks):
      chunk_path = Path(f"{driving_pkl}.chunk{i + 1:02d}of{num_chunks:02d}")
      if chunk_path.exists():
        chunk_hash = hashlib.sha256(chunk_path.read_bytes()).hexdigest()
        chunks_config.append({
          "file_name": chunk_path.name,
          "sha256": chunk_hash
        })

  artifact_data = {
    "file_name": driving_pkl.name,
    "download_uri": {
      "url": "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai/-/raw/main/",
      "sha256": tinygrad_hash
    }
  }

  if chunks_config:
    artifact_data["chunks"] = chunks_config

  return {
    "type": "chunked",
    "artifact": artifact_data,
  }


def create_metadata_json(models: list, output_dir: Path, custom_name=None, short_name=None, is_20hz=False, upstream_branch="unknown") -> None:
  bundle_json = {
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
  metadata_json = {
    "bundles": [bundle_json]
  }

  with open(output_dir / "metadata.json", "w") as f:
    json.dump(metadata_json, f, indent=2)
  print("Generated metadata.json")


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="Generate metadata JSON for the compiled JIT model")
  parser.add_argument("--model-dir", default="./models", help="Directory containing the model files")
  parser.add_argument("--output-dir", default="./output", help="Output directory for metadata")
  parser.add_argument("--custom-name", help="Custom display name for the model")
  parser.add_argument("--is-20hz", action="store_true", help="Whether this is a 20Hz model")
  parser.add_argument("--upstream-branch", default="unknown", help="Upstream branch name")
  args = parser.parse_args()

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

  _model_metadata = generate_chunked_model(_driving_pkl)
  create_metadata_json([_model_metadata], _output_dir, args.custom_name, _short_name, args.is_20hz, args.upstream_branch)
