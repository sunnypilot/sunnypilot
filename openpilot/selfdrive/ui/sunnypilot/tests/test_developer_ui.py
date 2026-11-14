"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace

import pytest
import raylib_nb as rl

from openpilot.selfdrive.ui.sunnypilot.onroad import developer_ui


@pytest.mark.parametrize(("x", "y", "drawn"), [
  (100, 100, True),
  (95, 100, False),     # left of the scissor
  (2110, 100, False),   # past the screen's right edge, inside the scissor
  (100, 1060, False),   # past the bottom
])
def test_unit_label_is_only_rasterized_whole(monkeypatch, x, y, drawn):
  """The unit label is copied off the screen once and cached: a clipped first draw would cache it blank."""
  class Rasterized(Exception):
    pass

  def screen():
    raise Rasterized

  monkeypatch.setattr(developer_ui, "measure_text_cached", lambda *a: rl.Vector2(60, 30))
  monkeypatch.setattr(developer_ui, "gui_app", SimpleNamespace(width=2160, height=1080))
  monkeypatch.setattr(developer_ui.rl, "cpu", SimpleNamespace(screen=screen))
  clip = rl.Rectangle(100, 20, 2200, 1060)
  if drawn:
    with pytest.raises(Rasterized):
      developer_ui.load_text_texture(None, "km/h", 28, x, y, clip)
  else:
    assert developer_ui.load_text_texture(None, "km/h", 28, x, y, clip) is None
