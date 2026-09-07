from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.helpers import check_camera_jit


class TestCheckCameraJit(OpenpilotTestCase):
  def test_missing_camera_is_named(self):
    mici_only = {'metadata': {}, 'run_policy': None, (1344, 760): None}
    with self.assertRaisesRegex(RuntimeError, r"1928x1208 driver camera.*has only \[1344x760\]"):
      check_camera_jit(mici_only, 1928, 1208, "driving_tinygrad.pkl")

  def test_compiled_camera_passes(self):
    both = {'metadata': {}, (1344, 760): None, (1928, 1208): None}
    for cam_w, cam_h in ((1344, 760), (1928, 1208)):
      check_camera_jit(both, cam_w, cam_h, "driving_tinygrad.pkl")
