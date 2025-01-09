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


def get_model_path():
  if USE_ONNX:
    return {ModelRunner.ONNX: Path(__file__).parent / '../models/supercombo.onnx'}

  if bundle := get_active_bundle():
    drive_model = next(model for model in bundle.models if model.type == ModelManager.Type.drive)
    return {ModelRunner.THNEED: f"{CUSTOM_MODEL_PATH}/{drive_model.fileName}"}

  return {ModelRunner.THNEED: Path(__file__).parent / '../models/supercombo.thneed'}


def load_metadata():
  metadata_path = METADATA_PATH

  if bundle := get_active_bundle():
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
