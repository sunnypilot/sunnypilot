import pyray as rl
from collections.abc import Callable
from openpilot.system.ui.widgets import Widget

# Sidebar removed; keep a stub to satisfy imports elsewhere.
SIDEBAR_WIDTH = 0


class Sidebar(Widget):
  def __init__(self):
    super().__init__()
    self._visible = False

  @property
  def is_visible(self) -> bool:
    return self._visible

  def set_visible(self, visible: bool | Callable[[], bool] = True) -> None:
    self._visible = visible() if callable(visible) else bool(visible)

  def set_callbacks(self, **_kwargs) -> None:
    # Compatibility no-op
    return

  def _render(self, rect: rl.Rectangle) -> None:
    # Sidebar is intentionally not drawn.
    return
