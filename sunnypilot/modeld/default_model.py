import argparse
import os
import hashlib

from openpilot.common.basedir import BASEDIR

DEFAULT_MODEL_NAME_PATH = os.path.join(BASEDIR, "common", "model.h")
MODEL_HASH_PATH = os.path.join(BASEDIR, "sunnypilot", "modeld", "tests", "model_hash")
ONNX_PATH = os.path.join(BASEDIR, "selfdrive", "modeld", "models", "supercombo.onnx")


def get_hash(path: str) -> str:
  sha256_hash = hashlib.sha256()
  with open(path, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
      sha256_hash.update(byte_block)
  return sha256_hash.hexdigest()


def update_model_hash():
  new_hash = get_hash(ONNX_PATH)
  with open(MODEL_HASH_PATH, "w") as f:
    f.write(new_hash)
  print(f"Generated and updated new hash to {MODEL_HASH_PATH}")


def update_default_model_name(name: str):
  with open(DEFAULT_MODEL_NAME_PATH) as f:
    current_name = f.read().split('"')[1]
  print(f'Old default model name: "{current_name}"')
  with open(DEFAULT_MODEL_NAME_PATH, "w") as f:
    f.write(f'#define DEFAULT_MODEL "{name}"\n')
  print(f'New default model name: "{name}"')


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Update default model name and hash")
  parser.add_argument("--new_name", type=str, help="New default model name")
  args = parser.parse_args()

  if args.new_name:
    update_default_model_name(args.new_name)
    update_model_hash()
  else:
    print("Warning: No new default model name provided. Use --new_name to specify. Skipping...")
