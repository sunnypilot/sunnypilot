# Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#
# This file is part of sunnypilot and is licensed under the MIT License.
# See the LICENSE.md file in the root directory for more details.

import os
import pickle
import numpy as np
from pathlib import Path
from cereal import custom
from openpilot.sunnypilot.modeld.runners import ModelRunner
from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.system.hardware import PC
from openpilot.system.hardware.hw import Paths

USE_ONNX = os.getenv('USE_ONNX', PC)

CUSTOM_MODEL_PATH = Paths.model_root()
METADATA_PATH = Path(__file__).parent / '../models/supercombo_metadata.pkl'

ModelManager = custom.ModelManagerSP


def load_model():
  if USE_ONNX:
    model_paths = {ModelRunner.ONNX: Path(__file__).parent / '../models/supercombo.onnx'}
  elif bundle := get_active_bundle():
    drive_model = next(model for model in bundle.models if model.type == ModelManager.Type.drive)
    model_paths = {ModelRunner.THNEED: f"{CUSTOM_MODEL_PATH}/{drive_model.fileName}"}
  else:
    model_paths = {ModelRunner.THNEED: Path(__file__).parent / '../models/supercombo.thneed'}

  return model_paths


def load_metadata():
  if bundle := get_active_bundle():
    metadata_model = next(model for model in bundle.models if model.type == ModelManager.Type.metadata)
    metadata_path = f"{CUSTOM_MODEL_PATH}/{metadata_model.fileName}"
  else:
    metadata_path = METADATA_PATH

  with open(metadata_path, 'rb') as f:
    metadata = pickle.load(f)

  return metadata


def prepare_inputs(metadata) -> dict[str, np.ndarray]:
  # img buffers are managed in openCL transform code
  inputs: dict[str, np.ndarray] = {
    key: np.zeros(shape, dtype=np.float32)
    for key, shape in metadata['input_shapes'].items()
    if key not in ['input_imgs', 'big_input_imgs']
  }

  return inputs


def get_model_generation() -> int:
  if bundle := get_active_bundle():
    drive_model = next(model for model in bundle.models if model.type == ModelManager.Type.drive)
    return drive_model.generation

  return 0  # default generation
