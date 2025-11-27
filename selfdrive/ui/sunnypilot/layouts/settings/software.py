"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os

from openpilot.selfdrive.ui.layouts.settings.software import SoftwareLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeOptionDialog, TreeNode, TreeFolder


class SoftwareLayoutSP(SoftwareLayout):
  def __init__(self):
    super().__init__()
    self.disable_updates_toggle = toggle_item_sp(tr("Disable Updates"), "", param="DisableUpdates", callback=self._on_disable_updates_toggled)
    self._scroller.add_widget(self.disable_updates_toggle)

  def _handle_reboot(self, result):
    if result == DialogResult.CONFIRM:
      ui_state.params.put_bool("DoReboot", True)

  def _on_disable_updates_toggled(self, enabled):
    dialog = ConfirmDialog(tr("System reboot required for changes to take effect. Reboot now?"), tr("Reboot"))
    gui_app.set_modal_overlay(dialog, callback=self._handle_reboot)

  def _on_select_branch(self):
    branches_str = ui_state.params.get("UpdaterAvailableBranches") or ""
    branches = [b for b in branches_str.split(",") if b]
    current_target = ui_state.params.get("UpdaterTargetBranch") or ""
    default_branches = ["release-tizi", "staging", "dev"]

    if HARDWARE.get_device_type() == "tici":
      default_branches = ["release-tici", "staging-tici"]
      branches = [b for b in branches if b.endswith("-tici")]

    top_level_nodes = [TreeNode(b, {'display_name': b}) for b in default_branches if b in branches]
    remaining_branches = [b for b in branches if b not in default_branches]
    prebuilt_nodes = [TreeNode(b, {'display_name': b}) for b in remaining_branches if b.endswith("-prebuilt")]
    non_prebuilt_nodes = [TreeNode(b, {'display_name': b}) for b in remaining_branches if not b.endswith("-prebuilt")]

    folders = [
      TreeFolder("", top_level_nodes),
      TreeFolder("Prebuilt branches", prebuilt_nodes),
      TreeFolder("Non-prebuilt branches", non_prebuilt_nodes),
    ]

    self._branch_dialog = TreeOptionDialog(tr("Select a branch"), folders, current_target, "",
                                           search_prompt=tr("Search for a branch"),
                                           on_exit=self._on_branch_selected)

    gui_app.set_modal_overlay(self._branch_dialog, callback=self._on_branch_selected)

  def _on_branch_selected(self, result):
    if result == DialogResult.CONFIRM and self._branch_dialog is not None:
      selection = self._branch_dialog.selection_ref
      if selection:
        ui_state.params.put("UpdaterTargetBranch", selection)
        self._branch_btn.action_item.set_value(selection)
        os.system("pkill -SIGUSR1 -f system.updated.updated")
    self._branch_dialog = None

  def _update_state(self):
    super()._update_state()
    offroad = ui_state.is_offroad()
    self.disable_updates_toggle.action_item.set_enabled(offroad)

    if offroad:
      self.disable_updates_toggle.set_description(tr("When enabled, automatic software updates will be off.<br><b>This requires a reboot to take effect.</b>"))
    else:
      self.disable_updates_toggle.set_description(tr("Please enable always offroad mode or turn off vehicle to adjust these toggles"))
    self.disable_updates_toggle.show_description(True)
