"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
# import subprocess
# import threading
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.list_view import button_item
# from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
# from openpilot.system.ui.lib.application import gui_app
# from openpilot.selfdrive.ui.ui_state import ui_state
# from openpilot.system.ui.widgets import DialogResult

class ExternalStorageControl:
  def __init__(self):
    self.item = button_item(tr("External Storage"), "", tr(tr("Extend your comma device's storage by inserting a USB drive into the aux port.")),
                            #callback=primary_callback_function_goes_here()
    )
  """Add the external storage stuff here in this file! The imports are included based on what I saw in the cpp implementation. they may or
     may not be relevant..."""
