# Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#
# This file is part of sunnypilot and is licensed under the MIT License.
# See the LICENSE.md file in the root directory for more details.

import os
import pickle
import numpy as np
from pathlib import Path
from cereal import custom
from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.system.hardware.hw import Paths

CUSTOM_MODEL_PATH = Paths.model_root()
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'

ModelManager = custom.ModelManagerSP


def get_custom_model_paths():
  bundle = get_active_bundle(None)
  if bundle:
    drive_model = next((model for model in bundle.models if model.type == ModelManager.Type.drive), None)
    metadata_model = next(model for model in bundle.models if model.type == ModelManager.Type.metadata)
    if drive_model and metadata_model:
      return {"model": f"{CUSTOM_MODEL_PATH}/{drive_model.fileName}", "metadata": f"{CUSTOM_MODEL_PATH}/{metadata_model.fileName}"}

  return None


def load_custom_metadata():
  if not (bundle := get_active_bundle(None)):
    return None

  metadata_model = next(model for model in bundle.models if model.type == ModelManager.Type.metadata)
  metadata_path = f"{CUSTOM_MODEL_PATH}/{metadata_model.fileName}"
  with open(metadata_path, 'rb') as f:
    return pickle.load(f)


def prepare_inputs(model_metadata) -> dict[str, np.ndarray]:
  # img buffers are managed in openCL transform code so we don't pass them as inputs
  inputs: dict[str, np.ndarray] = {
    key: np.zeros(shape, dtype=np.float32).flatten()  # Inputs were defined flattened back then
    for key, shape in model_metadata['input_shapes'].items()
    if key not in ['input_imgs', 'big_input_imgs']
  }

  return inputs
