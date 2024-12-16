import numpy as np
import os
from abc import ABC

from cereal import custom
import cereal.messaging as messaging
from pathlib import Path
from openpilot.common.params import Params

from openpilot.selfdrive.modeld.constants import Meta, ModelConstants
from openpilot.selfdrive.modeld.runners import ModelRunner

from openpilot.sunnypilot.modeld.constants import ModelMeta, MetaV1, ModelConstantsV1
from openpilot.sunnypilot.modeld.model_capabilities import ModelCapabilities

from openpilot.system.hardware.hw import Paths

CUSTOM_MODEL_PATH = Paths.model_root()
SIMULATION = "SIMULATION" in os.environ

MODEL_PATHS = {
  ModelRunner.THNEED: Path(__file__).parent / 'models/supercombo.thneed',
  ModelRunner.ONNX: Path(__file__).parent / 'models/supercombo.onnx'}

METADATA_PATH = Path(__file__).parent / 'models/supercombo_metadata.pkl'

ModelGeneration = custom.ModelDataV2SP.ModelGeneration


class ModelStateBase(ABC):
  def __init__(self):

    self.params = Params()
    self.model_generation = self.read_model_generation_param()
    self.model_capabilities = self.get_model_capabilities()
    self.custom_model = self.params.get_bool("CustomDrivingModel") and not SIMULATION and \
                        self.model_capabilities != ModelCapabilities.Default

    self.model_paths = {}
    self.metadata_path = ""
    self.history_buffer_len = 0
    self._inputs = {}
    self._inputs_2 = {}
    self._inputs_fmm = {}
    self._inputs_2_fmm = {}

    # LateralPlannerSolution
    self.driving_style = np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.float32)

    # NavigateOnOpenpilot
    self.timestamp_llk = 0
    self.nav_enabled = False
    self.nav_features = np.zeros(ModelConstantsV1.NAV_FEATURE_LEN, dtype=np.float32)
    self.nav_instructions = np.zeros(ModelConstantsV1.NAV_INSTRUCTION_LEN, dtype=np.float32)

  def get_meta(self):
    meta = Meta

    if self.model_capabilities & ModelCapabilities.Meta_V1:
      meta = MetaV1

    return ModelMeta(meta)

  def read_model_generation_param(self):
    try:
      return int(self.params.get("DrivingModelGeneration"))
    except (ValueError, TypeError):
      return ModelGeneration.default

  def get_model_capabilities(self):
    MC = ModelCapabilities
    capabilities = {
      ModelGeneration.eight: MC.MLSIM,
      ModelGeneration.seven: MC.DesiredCurvatureV2,
      ModelGeneration.six: MC.DesiredCurvatureV2 | MC.Meta_V1,
      ModelGeneration.five: MC.DesiredCurvatureV2 | MC.SIM_POSE | MC.Meta_V1,
      ModelGeneration.four: MC.DesiredCurvatureV2 | MC.SIM_POSE | MC.Meta_V1,
      ModelGeneration.three: MC.DesiredCurvatureV2 | MC.SIM_POSE | MC.NavigateOnOpenpilot | MC.Meta_V1,
      ModelGeneration.two: MC.DesiredCurvatureV1 | MC.SIM_POSE | MC.NavigateOnOpenpilot | MC.Meta_V1,
      ModelGeneration.one: MC.LateralPlannerSolution | MC.SIM_POSE | MC.NavigateOnOpenpilot | MC.Meta_V1,
      ModelGeneration.default: MC.Default,
    }

    # Default model is meant to represent the capabilities of the prebuilt model
    return capabilities.get(self.model_generation, MC.Default)

  def setup_inputs(self):
    if self.model_capabilities & (ModelCapabilities.MLSIM | ModelCapabilities.Default):
      self.history_buffer_len = ModelConstants.HISTORY_BUFFER_LEN
    else:
      self.history_buffer_len = ModelConstantsV1.HISTORY_BUFFER_LEN

    # Default model inputs
    self._inputs = {
      'lateral_control_params': np.zeros(ModelConstants.LATERAL_CONTROL_PARAMS_LEN, dtype=np.float32),
      'prev_desired_curv': np.zeros(ModelConstants.PREV_DESIRED_CURV_LEN * (self.history_buffer_len+1), dtype=np.float32),
    }

    if self.custom_model:
      if self.model_capabilities & ModelCapabilities.LateralPlannerSolution:
        self._inputs = {
          'lat_planner_state': np.zeros(ModelConstants.LAT_PLANNER_STATE_LEN, dtype=np.float32),
        }
      if self.model_capabilities & ModelCapabilities.DesiredCurvatureV1:
        self._inputs = {
          'lateral_control_params': np.zeros(ModelConstants.LATERAL_CONTROL_PARAMS_LEN, dtype=np.float32),
          'prev_desired_curvs': np.zeros(ModelConstantsV1.PREV_DESIRED_CURVS_LEN, dtype=np.float32),
        }
      if self.model_capabilities & ModelCapabilities.NavigateOnOpenpilot:
        self._inputs_2 = {
          'nav_features': np.zeros(ModelConstantsV1.NAV_FEATURE_LEN, dtype=np.float32),
          'nav_instructions': np.zeros(ModelConstantsV1.NAV_INSTRUCTION_LEN, dtype=np.float32),
        }

  def setup_model_path(self):
    if self.custom_model:
      model_name = self.params.get("DrivingModelText", encoding="utf8")
      metadata_name = self.params.get("DrivingModelMetadataText", encoding="utf8")

      self.model_paths = {ModelRunner.THNEED: f"{CUSTOM_MODEL_PATH}/supercombo-{model_name}.thneed"}
      self.metadata_path = f"{CUSTOM_MODEL_PATH}/supercombo_metadata_{metadata_name}.pkl" if model_name else METADATA_PATH
    else:
      self.model_paths = MODEL_PATHS
      self.metadata_path = METADATA_PATH

  def setup_nav(self, sm: messaging.SubMaster):
    self.timestamp_llk = 0
    self.nav_enabled = False
    # Enable/disable nav features
    self.timestamp_llk = sm["navModelDEPRECATED"].locationMonoTime
    nav_valid = sm.valid["navModelDEPRECATED"]  # and (nanos_since_boot() - self.timestamp_llk < 1e9)
    nav_enabled = nav_valid

    if not nav_enabled:
      self.nav_features[:] = 0
      self.nav_instructions[:] = 0

    if nav_enabled and sm.updated["navModelDEPRECATED"]:
      self.nav_features = np.array(sm["navModelDEPRECATED"].features)

    if nav_enabled and sm.updated["navInstruction"]:
      self.nav_instructions[:] = 0
      for maneuver in sm["navInstruction"].allManeuvers:
        distance_idx = 25 + int(maneuver.distance / 20)
        direction_idx = 0
        if maneuver.modifier in ("left", "slight left", "sharp left"):
          direction_idx = 1
        if maneuver.modifier in ("right", "slight right", "sharp right"):
          direction_idx = 2
        if 0 <= distance_idx < 50:
          self.nav_instructions[distance_idx*3 + direction_idx] = 1
