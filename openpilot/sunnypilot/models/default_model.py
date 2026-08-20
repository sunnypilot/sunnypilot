import argparse
import os
import hashlib

from openpilot.common.basedir import BASEDIR
from openpilot.sunnypilot import get_file_hash
from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL, DEFAULT_BIG_MODEL
from openpilot.selfdrive.modeld.helpers import usbgpu_present

DEFAULT_MODEL_NAME_PATH = os.path.join(BASEDIR, "openpilot", "sunnypilot", "models", "model_name.py")
MODEL_HASH_PATH = os.path.join(BASEDIR, "openpilot", "sunnypilot", "models", "tests", "model_hash")
BIG_MODEL_HASH_PATH = os.path.join(BASEDIR, "openpilot", "sunnypilot", "models", "tests", "model_hash_big")
SUPERCOMBO_ONNX_PATH = os.path.join(BASEDIR, "openpilot", "selfdrive", "modeld", "models", "driving_supercombo.onnx")
BIG_SUPERCOMBO_ONNX_PATH = os.path.join(BASEDIR, "openpilot", "selfdrive", "modeld", "models", "big_driving_supercombo.onnx")


def _model_hash(path: str) -> str:
  return hashlib.sha256(get_file_hash(path).encode()).hexdigest()


def update_model_hash():
  with open(MODEL_HASH_PATH, "w") as f:
    f.write(_model_hash(SUPERCOMBO_ONNX_PATH))
  with open(BIG_MODEL_HASH_PATH, "w") as f:
    f.write(_model_hash(BIG_SUPERCOMBO_ONNX_PATH))

  print(f"Generated and updated new model hashes to {MODEL_HASH_PATH} and {BIG_MODEL_HASH_PATH}")


def get_default_model() -> str:
  return DEFAULT_BIG_MODEL if usbgpu_present() else DEFAULT_MODEL


def update_default_model_names(default_model_name: str, default_big_model_name: str):
  print("[CHANGE DEFAULT MODEL NAMES]")
  with open(DEFAULT_MODEL_NAME_PATH, "w") as f:
    f.write(f'DEFAULT_MODEL = "{default_model_name}"\n')
    f.write(f'DEFAULT_BIG_MODEL = "{default_big_model_name}"\n')

  print(f'New default small model name: "{default_model_name}"')
  print(f'New default big model name: "{default_big_model_name}"')
  print("[DONE]")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Update default model names and hash")
  parser.add_argument("--new_small_model_name", type=str, help="New default model name")
  parser.add_argument("--new_big_model_name", type=str, help="New default big model name")
  args = parser.parse_args()

  current_name = DEFAULT_MODEL
  current_big_model_name = DEFAULT_BIG_MODEL

  new_name = args.new_small_model_name if args.new_small_model_name is not None else input(
    f'Enter new default small model name (current: "{current_name}", leave empty to keep): ').strip()
  new_big_model_name = args.new_big_model_name if args.new_big_model_name is not None else input(
    f'Enter new default big model name (current: "{current_big_model_name}", leave empty to keep): ').strip()

  if not new_name and not new_big_model_name:
    print("No new default model names provided. Default model names and hash will not be updated! (aborted)")
    exit(0)

  final_name = current_name
  final_big_model_name = current_big_model_name

  if new_name:
    if current_name == new_name:
      print(f'Proposed default model name: "{new_name}" is the same as the current default model name.')
      confirm = input("Confirm? (y/n): ").upper().strip()
      if confirm != "Y":
        print(f'Default model name will not be updated: "{new_name}"')
      else:
        final_name = new_name
    else:
      final_name = new_name

  if new_big_model_name:
    if current_big_model_name == new_big_model_name:
      print(f'Proposed default big model name: "{new_big_model_name}" is the same as the current default big model name.')
      confirm = input("Confirm? (y/n): ").upper().strip()
      if confirm != "Y":
        print(f'Default big model name will not be updated: "{new_big_model_name}"')
      else:
        final_big_model_name = new_big_model_name
    else:
      final_big_model_name = new_big_model_name

  if final_name == current_name and final_big_model_name == current_big_model_name:
    print("No changes made. Default model names and hash will not be updated! (aborted)")
    exit(0)

  update_default_model_names(final_name, final_big_model_name)
  update_model_hash()
