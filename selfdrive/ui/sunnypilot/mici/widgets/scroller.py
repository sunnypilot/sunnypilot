"""SP NavScroller — exposes _Scroller API not available on upstream Scroller.

Upstream Scroller doesn't expose _Scroller's public API (add_widget, scroll_panel, etc.).
See memory/scroller-snap-bug.md for details.
"""

from openpilot.system.ui.widgets.scroller import NavScroller as _NavScroller


class NavScroller(_NavScroller):
  """NavScroller with _Scroller API forwarding."""

  def add_widget(self, item):
    self._scroller.add_widget(item)

  def add_widgets(self, items):
    self._scroller.add_widgets(items)

  def set_scrolling_enabled(self, enabled):
    self._scroller.set_scrolling_enabled(enabled)

  def set_reset_scroll_at_show(self, scroll):
    self._scroller.set_reset_scroll_at_show(scroll)

  def clear_widgets(self):
    self._scroller._items.clear()

  @property
  def scroll_panel(self):
    return self._scroller.scroll_panel
