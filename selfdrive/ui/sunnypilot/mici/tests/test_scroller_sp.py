import pyray as rl

from openpilot.system.ui.lib.application import MouseEvent, MousePos, gui_app
from openpilot.system.ui.lib.scroll_panel2 import ScrollState
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets import scroller as scroller_mod
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.scroll_panel_sp import GuiScrollPanel2SP


class DummyScrollIndicator:
  def update(self, *_) -> None:
    pass

  def render(self) -> None:
    pass


class DummyWidget(Widget):
  def __init__(self, rect: rl.Rectangle):
    super().__init__()
    self.set_rect(rect)

  def _render(self, _) -> None:
    pass


def _mouse_event(x: float, y: float, *, pressed: bool = False, released: bool = False,
                 down: bool = True, t: float = 0.0) -> MouseEvent:
  return MouseEvent(MousePos(x, y), 0, pressed, released, down, t)


def test_vertical_snap_items_are_supported(monkeypatch):
  monkeypatch.setattr(scroller_mod, "ScrollIndicator", DummyScrollIndicator)

  scroller = scroller_mod._Scroller([], horizontal=False, snap_items=True, scroll_indicator=False)
  scroller.set_rect(rl.Rectangle(0, 0, 100, 100))
  scroller.scroll_panel.set_offset(-60)

  captured_snap_target = None

  def update(_, __, snap_target=None):
    nonlocal captured_snap_target
    captured_snap_target = snap_target
    return scroller.scroll_panel.get_offset()

  monkeypatch.setattr(scroller.scroll_panel, "update", update)

  visible_items = [
    DummyWidget(rl.Rectangle(0, -60, 100, 100)),
    DummyWidget(rl.Rectangle(0, 40, 100, 100)),
  ]
  scroller._get_scroll(visible_items, 200)

  assert captured_snap_target == -100


def test_scroll_panel_sp_rejects_orthogonal_drags(monkeypatch):
  panel = GuiScrollPanel2SP(horizontal=True)
  bounds = rl.Rectangle(0, 0, 100, 100)

  monkeypatch.setattr(gui_app, "_mouse_events", [_mouse_event(10, 10, pressed=True, t=1.0)])
  panel.update(bounds, 200)
  assert panel.state == ScrollState.PRESSED

  monkeypatch.setattr(gui_app, "_mouse_events", [_mouse_event(23, 60, t=1.1)])
  panel.update(bounds, 200)

  assert panel.state == ScrollState.STEADY
  assert panel.get_offset() == 0


def test_scroll_panel_sp_can_disable_out_of_bounds_handling(monkeypatch):
  panel = GuiScrollPanel2SP(horizontal=False, handle_out_of_bounds=False)
  bounds = rl.Rectangle(0, 0, 100, 100)
  monkeypatch.setattr(gui_app, "_mouse_events", [])

  panel.set_offset(20)
  panel.update(bounds, 200)
  assert panel.get_offset() == 0

  panel.set_offset(-150)
  panel.update(bounds, 200)
  assert panel.get_offset() == -100
