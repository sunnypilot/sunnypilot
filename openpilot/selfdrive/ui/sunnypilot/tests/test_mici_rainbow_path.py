"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from unittest import mock

import numpy as np
import raylib_nb as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH, model_renderer
from openpilot.selfdrive.ui.onroad.model_renderer import ModelPoints
from openpilot.selfdrive.ui.sunnypilot.onroad.rainbow_path import RainbowPath
from openpilot.selfdrive.ui.ui_state import ui_state

PATH = np.array([[100, 200], [110, 100], [150, 100], [160, 200]], dtype=np.float32)


class TestMiciRainbowPath(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    renderer = object.__new__(model_renderer.ModelRenderer)
    renderer._rect = rl.Rectangle(SIDE_PANEL_WIDTH, 0, 464, 240)
    renderer._path = ModelPoints(projected_points=PATH)
    renderer._available_filter = FirstOrderFilter(0.0, 0.1, 0.05)
    renderer.rainbow_path = RainbowPath()
    renderer._longitudinal_control = False
    self.renderer = renderer
    self.calls = []
    patchers = (
      mock.patch.object(model_renderer, 'draw_polygon', lambda rect, points, color=None, gradient=None:
                        self.calls.append((np.array(points), gradient))),
      mock.patch.object(ui_state, 'rainbow_path', True),
    )
    for patcher in patchers:
      patcher.start()
      self.addCleanup(patcher.stop)

  def _draw(self, rainbow: bool, visible: float = 1.0):
    ui_state.rainbow_path = rainbow
    self.renderer._visible = visible
    self.calls.clear()
    self.renderer._draw_path()
    assert len(self.calls) == 1
    return self.calls[0]

  def test_rainbow_path_draws_where_the_path_does(self):
    points, _ = self._draw(rainbow=True)
    np.testing.assert_array_equal(points, self._draw(rainbow=False)[0])
    np.testing.assert_array_equal(points, PATH + (SIDE_PANEL_WIDTH, 0))

  def test_rainbow_path_fades_with_the_path(self):
    _, gradient = self._draw(rainbow=True, visible=0.5)
    _, full = self._draw(rainbow=True)
    assert [c.a for c in gradient.colors] == [round(c.a * 0.5) for c in full.colors]
