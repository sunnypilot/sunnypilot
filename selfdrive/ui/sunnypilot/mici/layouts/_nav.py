"""Shared navigation helpers for mici layout sub-views."""
from openpilot.system.ui.widgets.scroller import NavScroller


def make_sub_view(items):
  """Create a NavScroller sub-view; NavWidget auto-pops on swipe-dismiss."""
  view = NavScroller()
  view.add_widgets(items)
  return view
