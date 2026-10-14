import io
import pickle
import struct
import sys
from pathlib import Path

from openpilot.common.file_chunker import get_manifest_path
from openpilot.common.hardware import AGNOS
from openpilot.common.hardware.usb import CHESTNUT_USB_PRODUCT, USB_DEVICES_PATH, is_chestnut_usb_id

MODELS_DIR = Path(__file__).resolve().parent / 'models'


def modeld_pkl_path(chestnut: bool):
  prefix = 'big_' if chestnut else ''
  return MODELS_DIR / f'{prefix}driving_tinygrad.pkl'

def load_oob(f, chestnut=False):
  import numpy as np
  from tinygrad import Context, Tensor
  device = 'USB+AMD:LLVM' if chestnut else 'QCOM' if AGNOS else 'METAL' if sys.platform == 'darwin' else 'CPU:LLVM'
  with Context(DEV=device):
    opcodes = f.read(struct.unpack('<q', f.read(8))[0])
    buffers = Tensor(np.frombuffer(f.read(), np.uint8)).realize().uop.buffer
    return type("_Unpickler", (pickle.Unpickler,), {"persistent_load": lambda self, pid: buffers.view(*pid)})(io.BytesIO(opcodes)).load()

def chestnut_present() -> bool:
  for d in USB_DEVICES_PATH.glob("*"):
    try:
      usb_id = (int((d / "idVendor").read_text(), 16), int((d / "idProduct").read_text(), 16))
      product = (d / "product").read_text().strip()
      if is_chestnut_usb_id(*usb_id) and product == CHESTNUT_USB_PRODUCT:
        return True
    except Exception:
      pass
  return False

def chestnut_compiled() -> bool:
  path = modeld_pkl_path(chestnut=True)
  return (path.is_file() or Path(get_manifest_path(path)).is_file()) and all(
    (MODELS_DIR / f'big_driving_warp_{size}_tinygrad.pkl').is_file() for size in ('1344x760', '1928x1208'))
