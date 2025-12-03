from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.sunnypilot.models.runners.model_runner import ModelRunner
from openpilot.sunnypilot.models.runners.tinygrad.tinygrad_runner import TinygradRunner, TinygradSplitRunner
from openpilot.sunnypilot.models.runners.constants import ModelType
from openpilot.system.hardware import TICI

if not TICI:
  from openpilot.sunnypilot.models.runners.onnx.onnx_runner import ONNXRunner

def get_model_runner() -> ModelRunner:
  """
  Factory function to create and return the appropriate ModelRunner instance.

  Selects between ONNXRunner (for non-TICI platforms) and TinygradRunner
  (for TICI platforms), choosing TinygradSplitRunner if separate vision/policy
  models are detected in the active bundle.

  :return: An instance of a ModelRunner subclass (ONNXRunner, TinygradRunner, or TinygradSplitRunner).
  """
  if not TICI:
    return ONNXRunner()

  # On TICI platforms, use Tinygrad runners
  bundle = get_active_bundle()
  if bundle and bundle.models:
    model_types = {m.type.raw for m in bundle.models}
    # Check if the bundle uses separate vision and policy models
    if ModelType.vision in model_types or ModelType.policy in model_types:
      return TinygradSplitRunner()
    # Otherwise, assume a single model (likely supercombo)
    if bundle.models:
      return TinygradRunner(bundle.models[0].type.raw)

  # Default fallback to TinygradRunner with the supercombo type if bundle info is missing/incomplete
  return TinygradRunner(ModelType.supercombo)
