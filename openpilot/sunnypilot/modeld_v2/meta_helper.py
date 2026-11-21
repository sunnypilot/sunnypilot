from openpilot.sunnypilot.modeld_v2.constants import Meta
from openpilot.sunnypilot.modeld_v2.meta_20hz import Meta20hz
from openpilot.sunnypilot.models.helpers import get_active_bundle


def load_meta_constants():
  if (bundle := get_active_bundle()) and bundle.is20hz:
    return Meta20hz
  return Meta
