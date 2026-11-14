"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace
from unittest import mock

import raylib_nb as rl

from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot.onroad import developer_ui


class Rasterized(Exception):
  pass


def screen():
  raise Rasterized


class TestDeveloperUi(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    for target, name, value in ((developer_ui, "measure_text_cached", lambda *a: rl.Vector2(60, 30)),
                                (developer_ui, "gui_app", SimpleNamespace(width=2160, height=1080)),
                                (developer_ui.rl, "cpu", SimpleNamespace(screen=screen))):
      patcher = mock.patch.object(target, name, value)
      patcher.start()
      self.addCleanup(patcher.stop)

  # a clipped first draw would cache the unit label blank
  @parameterized.expand([
    (100, 100, True),
    (95, 100, False),     # left of the scissor
    (2110, 100, False),   # past the screen's right edge
    (100, 1060, False),   # past the bottom
  ])
  def test_unit_label_is_only_rasterized_whole(self, x, y, drawn):
    clip = rl.Rectangle(100, 20, 2200, 1060)
    if drawn:
      with self.assertRaises(Rasterized):
        developer_ui.load_text_texture(None, "km/h", 28, x, y, clip)
    else:
      assert developer_ui.load_text_texture(None, "km/h", 28, x, y, clip) is None
