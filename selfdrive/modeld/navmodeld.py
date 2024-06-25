#!/usr/bin/env python3
import gc
import math
import time
import ctypes
import numpy as np
from pathlib import Path

from cereal import messaging
from cereal.messaging import PubMaster, SubMaster
from msgq.visionipc import VisionIpcClient, VisionStreamType
from openpilot.common.swaglog import cloudlog
from openpilot.common.params import Params
from openpilot.common.realtime import set_realtime_priority
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.modeld.runners import ModelRunner, Runtime
from openpilot.selfdrive.sunnypilot import get_model_generation
from openpilot.system.hardware.hw import Paths

NAV_INPUT_SIZE = 256*256
NAV_FEATURE_LEN = 256
NAV_DESIRE_LEN = 32
NAV_OUTPUT_SIZE = 2*2*ModelConstants.IDX_N + NAV_DESIRE_LEN + NAV_FEATURE_LEN
MODEL_PATHS = {}

CUSTOM_MODEL_PATH = Paths.model_root()

class NavModelOutputXY(ctypes.Structure):
  _fields_ = [
    ("x", ctypes.c_float),
    ("y", ctypes.c_float)]

class NavModelOutputPlan(ctypes.Structure):
  _fields_ = [
    ("mean", NavModelOutputXY*ModelConstants.IDX_N),
    ("std", NavModelOutputXY*ModelConstants.IDX_N)]

class NavModelResult(ctypes.Structure):
  _fields_ = [
    ("plan", NavModelOutputPlan),
    ("desire_pred", ctypes.c_float*NAV_DESIRE_LEN),
    ("features", ctypes.c_float*NAV_FEATURE_LEN)]

class ModelState:
  inputs: dict[str, np.ndarray]
  output: np.ndarray
  model: ModelRunner

  def __init__(self):
    assert ctypes.sizeof(NavModelResult) == NAV_OUTPUT_SIZE * ctypes.sizeof(ctypes.c_float)
    self.output = np.zeros(NAV_OUTPUT_SIZE, dtype=np.float32)
    self.param_s = Params()
    self.custom_model, self.model_gen = get_model_generation(self.param_s)
    if self.custom_model and self.model_gen not in (0, 4):
      _model_name = self.param_s.get("NavModelText", encoding="utf8")
      _model_paths = {
        ModelRunner.SNPE: f"{CUSTOM_MODEL_PATH}/navmodel_q_{_model_name}.dlc"}
    else:
      _model_paths = MODEL_PATHS
    self.inputs = {'input_img': np.zeros(NAV_INPUT_SIZE, dtype=np.uint8)}
    self.model = ModelRunner(_model_paths, self.output, Runtime.DSP, True, None)
    self.model.addInput("input_img", None)

  def run(self, buf:np.ndarray) -> tuple[np.ndarray, float]:
    self.inputs['input_img'][:] = buf

    t1 = time.perf_counter()
    self.model.setInputBuffer("input_img", self.inputs['input_img'].view(np.float32))
    self.model.execute()
    t2 = time.perf_counter()
    return self.output, t2 - t1

def get_navmodel_packet(model_output: np.ndarray, valid: bool, frame_id: int, location_ts: int, execution_time: float, dsp_execution_time: float):
  model_result = ctypes.cast(model_output.ctypes.data, ctypes.POINTER(NavModelResult)).contents
  msg = messaging.new_message('navModelDEPRECATED')
  msg.valid = valid
  navModel = msg.navModelDEPRECATED
  navModel.frameId = frame_id
  navModel.locationMonoTime = location_ts
  navModel.modelExecutionTime = execution_time
  navModel.dspExecutionTime = dsp_execution_time
  navModel.features = model_result.features[:]
  navModel.desirePrediction = model_result.desire_pred[:]
  navModel.position.x = [p.x for p in model_result.plan.mean]
  navModel.position.y = [p.y for p in model_result.plan.mean]
  navModel.position.xStd = [math.exp(p.x) for p in model_result.plan.std]
  navModel.position.yStd = [math.exp(p.y) for p in model_result.plan.std]
  return msg


def main():
  gc.disable()
  set_realtime_priority(1)

  # there exists a race condition when two processes try to create a
  # SNPE model runner at the same time, wait for dmonitoringmodeld to finish
  cloudlog.warning("waiting for dmonitoringmodeld to initialize")
  if not Params().get_bool("DmModelInitialized", True):
    return

  model = ModelState()
  cloudlog.warning("models loaded, navmodeld starting")

  vipc_client = VisionIpcClient("navd", VisionStreamType.VISION_STREAM_MAP, True)
  while not vipc_client.connect(False):
    time.sleep(0.1)
  assert vipc_client.is_connected()
  cloudlog.warning(f"connected with buffer size: {vipc_client.buffer_len}")

  sm = SubMaster(["navInstruction"])
  pm = PubMaster(["navModelDEPRECATED"])

  while True:
    buf = vipc_client.recv()
    if buf is None:
      continue

    sm.update(0)
    t1 = time.perf_counter()
    model_output, dsp_execution_time = model.run(buf.data[:buf.uv_offset])
    t2 = time.perf_counter()

    valid = vipc_client.valid and sm.valid["navInstruction"]
    pm.send("navModelDEPRECATED", get_navmodel_packet(model_output, valid, vipc_client.frame_id, vipc_client.timestamp_sof, t2 - t1, dsp_execution_time))


if __name__ == "__main__":
  main()
