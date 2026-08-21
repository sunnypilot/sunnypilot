from openpilot.selfdrive.modeld.helpers import usbgpu_present

DEFAULT_MODEL = "CD210"
DEFAULT_BIG_MODEL = "Lebowski"


def get_default_model() -> str:
  return DEFAULT_BIG_MODEL if usbgpu_present() else DEFAULT_MODEL
