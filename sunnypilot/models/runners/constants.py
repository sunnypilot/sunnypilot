import os
import numpy as np
from openpilot.system.hardware.hw import Paths
from cereal import custom

# Type definitions for clarity
NumpyDict = dict[str, np.ndarray]
ShapeDict = dict[str, tuple[int, ...]]
SliceDict = dict[str, slice]

ModelType = custom.ModelManagerSP.Model.Type
Model = custom.ModelManagerSP.Model

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')
CUSTOM_MODEL_PATH = Paths.model_root()
