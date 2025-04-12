import os
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime

def generate_metadata(model_path: str, output_dir: Path, file_name: str = None):
  model_path = Path(model_path)
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
  if file_name:
    tinygrad_file = tinygrad_file.rename(output_path / f"{base}_{file_name}_tinygrad.pkl")
    metadata_file = metadata_file.rename(output_path / f"{base}_{file_name}_metadata.pkl")

  # Build the metadata structure
  model_metadata = {
    "name": file_name or base,
    "drive_model": {
      "file_name": tinygrad_file.name,
      "sha256": tinygrad_hash
    },
    "metadata": {
      "file_name": metadata_file.name,
      "sha256": metadata_hash
    }
  }

  # Return model metadata
  return model_metadata


def create_metadata_json(models, output_dir, custom_name=None, file_name=None, is_20hz=False, upstream_branch="unknown"):
  metadata_json = {
    "display_name": custom_name or upstream_branch,
    "full_name": file_name or "default",
    "is_20hz": is_20hz,
    "ref": upstream_branch,
    "build_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "models": models
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
  parser.add_argument("--file-name", help="File name prefix for the model")
  parser.add_argument("--is-20hz", action="store_true", help="Whether this is a 20Hz model")
  parser.add_argument("--upstream-branch", default="unknown", help="Upstream branch name")
  args = parser.parse_args()

  # Find all ONNX files in the given directory
  model_paths = glob.glob(os.path.join(args.model_dir, "*.onnx"))
  if not model_paths:
    print(f"No ONNX files found in {args.model_dir}", file=sys.stderr)
    sys.exit(1)

  output_dir = Path(args.output_dir)
  output_dir.mkdir(exist_ok=True, parents=True)
  models = []

  for model_path in model_paths:
    model_metadata = generate_metadata(model_path, output_dir, args.file_name)
    if model_metadata:
      models.append(model_metadata)

  if models:
    create_metadata_json(models, output_dir, args.custom_name, args.file_name, args.is_20hz, args.upstream_branch)
  else:
    print("No models processed.", file=sys.stderr)
