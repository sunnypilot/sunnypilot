# Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#
# This file is part of sunnypilot and is licensed under the MIT License.
# See the LICENSE.md file in the root directory for more details.

import pickle
import numpy as np
from pathlib import Path

METADATA_PATH = Path(__file__).parent / 'models/supercombo_metadata.pkl'


def load_metadata():
  with open(METADATA_PATH, 'rb') as f:
    metadata = pickle.load(f)

  return metadata


def prepare_inputs() -> dict[str, np.ndarray]:
  model_metadata = load_metadata()

  inputs: dict[str, np.ndarray] = {
    key: np.zeros(shape, dtype=np.float32)
    for key, shape in model_metadata['input_shapes'].items()
    if key not in ['input_imgs', 'big_input_imgs']
  }

  return inputs


def parse_runner_inputs(vec_desire, traffic_convention) -> dict[str, np.ndarray]:
  inputs: dict[str, np.ndarray] = {
    'desire': vec_desire,
    'traffic_convention': traffic_convention,
  }

  return inputs
