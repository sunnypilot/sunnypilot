#!/usr/bin/env python3
import sys
import shutil
import pickle
import codecs
import onnx
from pathlib import Path

from openpilot.system.hardware.hw import Paths


def get_name_and_shape(value_info):
  shape = tuple([int(dim.dim_value) for dim in value_info.type.tensor_type.shape.dim])
  return value_info.name, shape


def get_metadata_value_by_name(model, name):
  for prop in model.metadata_props:
    if prop.key == name:
      return prop.value
  return None


def generate_metadata_pkl(model_path, output_path):
  try:
    model = onnx.load(str(model_path))
    output_slices = get_metadata_value_by_name(model, 'output_slices')

    if output_slices:
      metadata = {
        'model_checkpoint': get_metadata_value_by_name(model, 'model_checkpoint'),
        'output_slices': pickle.loads(codecs.decode(output_slices.encode(), "base64")),
        'input_shapes': dict([get_name_and_shape(x) for x in model.graph.input]),
        'output_shapes': dict([get_name_and_shape(x) for x in model.graph.output])
      }
      with open(output_path, 'wb') as f:
        pickle.dump(metadata, f)
      return True
    else:
      return False
  except Exception:
    return False


def install_models(model_dir):
  model_dir = Path(model_dir)
  models = ["driving_off_policy", "driving_policy", "driving_vision"]
  found_models = []

  for model in models:
    if (model_dir / f"{model}.onnx").exists():
      found_models.append(model)

  if not found_models:
    return

  try:
    custom_name = input(f"Found models ({', '.join(found_models)}). Enter model short name (e.g. wmiv4): ").strip()
  except EOFError:
    return

  if not custom_name:
    print("No name provided, skipping installation.")
    return

  dest_dir = Path(Paths.model_root())
  dest_dir.mkdir(parents=True, exist_ok=True)

  for model in found_models:
    onnx_path = model_dir / f"{model}.onnx"
    tinygrad_pkl = model_dir / f"{model}_tinygrad.pkl"
    metadata_pkl = model_dir / f"{model}_metadata.pkl"

    if not metadata_pkl.exists():
      generate_metadata_pkl(onnx_path, metadata_pkl)

    dest_tinygrad = dest_dir / f"{model}_{custom_name}_tinygrad.pkl"
    dest_metadata = dest_dir / f"{model}_{custom_name}_metadata.pkl"

    if tinygrad_pkl.exists():
      shutil.move(str(tinygrad_pkl), str(dest_tinygrad))
    if metadata_pkl.exists():
      shutil.move(str(metadata_pkl), str(dest_metadata))

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: install_models_pc.py <model_dir>")
    sys.exit(1)
  install_models(sys.argv[1])
