"""
Sidebar adapter - uses BluePilot's modular sidebar implementation
Supports SidebarSP inheritance for sunnypilot compatibility
"""
from bluepilot.ui.widgets.sidebar import SidebarBP
from bluepilot.ui.lib.constants import BPConstants
from openpilot.system.ui.lib.application import gui_app

# Import SidebarSP if sunnypilot UI is enabled
if gui_app.sunnypilot_ui():
  from openpilot.selfdrive.ui.sunnypilot.layouts.sidebar import SidebarSP
  
  class Sidebar(SidebarBP, SidebarSP):
    """Sidebar with SidebarSP inheritance for sunnylink support"""
    def __init__(self):
      SidebarSP.__init__(self)
      SidebarBP.__init__(self)
      
    def _update_state(self):
      """Update state including sunnylink"""
      SidebarBP._update_state(self)
      SidebarSP._update_sunnylink_status(self)
else:
  # Export SidebarBP as Sidebar for compatibility
  Sidebar = SidebarBP

# Export width constant
SIDEBAR_WIDTH = BPConstants.SIDEBAR_WIDTH
