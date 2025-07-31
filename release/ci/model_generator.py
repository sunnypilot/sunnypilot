import os
import sys
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, UTC


def create_short_name(full_name):
  # Remove parentheses and extract alphanumeric words
  clean_name = re.sub(r'\([^)]*\)', '', full_name)
  words = [re.sub(r'[^a-zA-Z0-9]', '', word) for word in clean_name.split() if re.sub(r'[^a-zA-Z0-9]', '', word)]

  if len(words) == 1:
    # If there's only one word, return it as is, lowercased, truncated to 8 characters
    truncated = words[0][:8]
    return truncated.lower() if truncated.isupper() else truncated

  # Handle special case: Name + Version (e.g., "Word A1" -> "WordA1")
  if len(words) == 2 and re.match(r'^[A-Za-z]\d+$', words[1]):
    first_word = words[0].lower() if words[0].isupper() else words[0]
    return (first_word + words[1])[:8]

  # Normal case: first letter and trailing numbers from each word
  result = ''.join(word if word.isdigit() else word[0] + (re.search(r'\d+$', word) or [''])[0] for word in words)
  return result[:8]


def generate_metadata(model_path: Path, output_dir: Path, short_name: str):
  model_path = model_path
  output_path = output_dir
  base = model_path.stem

  # Define output files for tinygrad and metadata
  tinygrad_file = output_path / f"{base}_tinygrad.pkl"
  metadata_file = output_path / f"{base}_metadata.pkl"

  if not tinygrad_file.exists() or not metadata_file.exists():
    print(f"Error: Missing files for model {base} ({tinygrad_file} or {metadata_file})", file=sys.stderr)
    return

  # Calculate the sha256 hashes
  with open(tinygrad_file, 'rb') as f:
    tinygrad_hash = hashlib.sha256(f.read()).hexdigest()

  with open(metadata_file, 'rb') as f:
    metadata_hash = hashlib.sha256(f.read()).hexdigest()

  # Rename the files if a custom file name is provided
  if short_name:
    tinygrad_file = tinygrad_file.rename(output_path / f"{base}_{short_name.lower()}_tinygrad.pkl")
    metadata_file = metadata_file.rename(output_path / f"{base}_{short_name.lower()}_metadata.pkl")

  # Build the metadata structure
  model_metadata = {
    "type": base.split("_")[-1] if "dmonitoring" not in base else "dmonitoring",
    "artifact": {
      "file_name": tinygrad_file.name,
      "download_uri": {
        "url": "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai/-/raw/main/<FILLME>",
        "sha256": tinygrad_hash
      }
    },
    "metadata": {
      "file_name": metadata_file.name,
      "download_uri": {
        "url": "https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai/-/raw/main/<FILLME>",
        "sha256": metadata_hash
      }
    }
  }

  # Return model metadata
  return model_metadata


def create_metadata_json(models: list, output_dir: Path, custom_name=None, short_name=None, is_20hz=False, upstream_branch="unknown"):
  metadata_json = {
    "short_name": short_name,
    "display_name": custom_name or upstream_branch,
    "is_20hz": is_20hz,
    "ref": upstream_branch,
    "environment": "development",
    "runner": "tinygrad",
    "build_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "models": models,
    "overrides": {},
    "index": -1,
    "minimum_selector_version": "-1",
    "generation": "-1",
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
  parser.add_argument("--upstream-branch", default="unknown", help="Upstream branch name")
  args = parser.parse_args()

  # Find all ONNX files in the given directory
  model_paths = glob.glob(os.path.join(args.model_dir, "*.onnx"))
  if not model_paths:
    print(f"No ONNX files found in {args.model_dir}", file=sys.stderr)
    sys.exit(1)

  _output_dir = Path(args.output_dir)
  _output_dir.mkdir(exist_ok=True, parents=True)
  _models = []

  for _model_path in model_paths:
    _model_metadata = generate_metadata(Path(_model_path), _output_dir, create_short_name(args.custom_name))
    if _model_metadata:
      _models.append(_model_metadata)

  if _models:
    create_metadata_json(_models, _output_dir, args.custom_name, create_short_name(args.custom_name), args.is_20hz, args.upstream_branch)
  else:
    print("No models processed.", file=sys.stderr)
