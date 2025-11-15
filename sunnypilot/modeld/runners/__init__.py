import os
from typing import cast, Protocol
from openpilot.system.hardware import TICI

USE_THNEED = int(os.getenv('USE_THNEED', str(int(TICI))))
USE_SNPE = int(os.getenv('USE_SNPE', str(int(TICI))))
THNEED = 'THNEED'
SNPE = 'SNPE'
ONNX = 'ONNX'


class Runtime:
  CPiU = 0
  GPU = 1
  DSP = 2


class ModelRunnerInterface(Protocol):
  def addInput(self, name: str, buffer) -> None: ...
  def setInputBuffer(self, name: str, buffer) -> None: ...
  def getCLBuffer(self, name: str): ...
  def execute(self) -> None: ...


def ModelRunner(paths, *args, **kwargs) -> ModelRunnerInterface:
  if THNEED in paths and USE_THNEED:
    from openpilot.sunnypilot.modeld.runners.thneedmodel_pyx import ThneedModel as Runner
    runner_type = THNEED
  elif SNPE in paths and USE_SNPE:
    from openpilot.sunnypilot.modeld.runners.snpemodel_pyx import SNPEModel as Runner
    runner_type = SNPE
  elif ONNX in paths:
    from openpilot.sunnypilot.modeld.runners.onnxmodel import ONNXModel as Runner
    runner_type = ONNX
  else:
    raise Exception("Couldn't select a model runner, make sure to pass at least one valid model path")

  runner = Runner(str(paths[runner_type]), *args, **kwargs)
  return cast(ModelRunnerInterface, runner)  # Cast if mypy complains about the Protocol match
