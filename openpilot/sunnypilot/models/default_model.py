import argparse
import os
import hashlib
import requests
import re

from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot import get_file_hash
from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL, DEFAULT_BIG_MODEL
from openpilot.sunnypilot.models.fetcher import ModelFetcher


def get_default_model() -> str:
  show_big_model = (ui_state.chestnut_present
                    and (ui_state.chestnut_active or ui_state.chestnut_loading or ui_state.is_offroad()))

  return DEFAULT_BIG_MODEL if show_big_model else DEFAULT_MODEL


DEFAULT_MODEL_NAME_PATH = os.path.join(BASEDIR, "openpilot", "sunnypilot", "models", "model_name.py")
MODEL_HASH_PATH = os.path.join(BASEDIR, "openpilot", "sunnypilot", "models", "tests", "model_hash")
SUPERCOMBO_ONNX_PATH = os.path.join(BASEDIR, "openpilot", "selfdrive", "modeld", "models", "driving_supercombo.onnx")


def update_model_hash():
  supercombo_hash = get_file_hash(SUPERCOMBO_ONNX_PATH)
  combined_hash = hashlib.sha256(supercombo_hash.encode()).hexdigest()

  with open(MODEL_HASH_PATH, "w") as f:
    f.write(combined_hash)

  print(f"Generated and updated new combined model hash to {MODEL_HASH_PATH}")


def get_ref_for_name(url: str, name: str) -> str:
  response = requests.get(url, timeout=10)
  if response.status_code == 200:
    bundles = response.json()["bundles"]
    matching = [b for b in bundles if re.search(name, f"{b['short_name']} {b['display_name']}", re.IGNORECASE)]
    if matching:
      return max(matching, key=lambda b: int(b["index"]))["ref"]
  return ""


def update_default_model_names(default_model_name: str, default_big_model_name: str):
  print("[CHANGE DEFAULT MODEL NAMES]")
  small_ref = get_ref_for_name(ModelFetcher.MODEL_URL, default_model_name)
  big_ref = get_ref_for_name(ModelFetcher.MODEL_URL_CHESTNUT, default_big_model_name)

  with open(DEFAULT_MODEL_NAME_PATH, "w") as f:
    f.write(f'DEFAULT_MODEL = "{default_model_name}"\n')
    f.write(f'DEFAULT_MODEL_REF = "{small_ref}"\n')
    f.write(f'DEFAULT_BIG_MODEL = "{default_big_model_name}"\n')
    f.write(f'DEFAULT_BIG_MODEL_REF = "{big_ref}"\n')

  print(f'New default small model name: "{default_model_name}" (ref: {small_ref})')
  print(f'New default big model name: "{default_big_model_name}" (ref: {big_ref})')
  print("[DONE]")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Update default model names and hash")
  parser.add_argument("--new_small_model_name", type=str, help="New default small model name")
  parser.add_argument("--new_big_model_name", type=str, help="New default big model name")
  args = parser.parse_args()

  if args.new_small_model_name is None and args.new_big_model_name is None:
    new_name = input(f'Enter new default small model name (current: "{DEFAULT_MODEL}", leave empty to keep): ').strip()
    new_big_model_name = input(f'Enter new default big model name (current: "{DEFAULT_BIG_MODEL}", leave empty to keep): ').strip()
  else:
    new_name, new_big_model_name = args.new_small_model_name, args.new_big_model_name

  update_default_model_names(new_name or DEFAULT_MODEL, new_big_model_name or DEFAULT_BIG_MODEL)
  update_model_hash()
