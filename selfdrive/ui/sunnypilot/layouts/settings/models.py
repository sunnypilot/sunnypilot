from openpilot.system.ui.sunnypilot.lib.list_view import button_item_sp, toggle_item_sp
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.tree_option_dialog import TreeOptionDialog, TreeNode, TreeFolder
from openpilot.system.ui.lib.application import gui_app
from openpilot.common.params import Params


class ModelsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._init_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _init_items(self):
    items = [
      button_item_sp("Current Model", "SELECT", callback=self._on_model_select),
      toggle_item_sp("Live Learning Steer Delay"),
    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)

  def _on_model_select(self):
    # Demo data for TreeOptionDialog
    tree_items = [
      # Top-level items (no folder)
      TreeFolder(
        folder="",
        items=[
          TreeNode("Default Model", "default_model", 0),
          TreeNode("Experimental Model", "experimental_model", 1),
        ]
      ),
      # Models folder
      TreeFolder(
        folder="Available Models",
        items=[
          TreeNode("Model A - Comfort", "model_a_comfort", 2),
          TreeNode("Model B - Aggressive", "model_b_aggressive", 3),
          TreeNode("Model C - Balanced", "model_c_balanced", 4),
          TreeNode("Model D - Highway", "model_d_highway", 5),
          TreeNode("Model E - City", "model_e_city", 6),
        ]
      ),
      # Development Models folder
      TreeFolder(
        folder="Development Models",
        items=[
          TreeNode("Dev Model Alpha", "dev_alpha", 7),
          TreeNode("Dev Model Beta", "dev_beta", 8),
          TreeNode("Dev Model Gamma", "dev_gamma", 9),
        ]
      ),
      # Custom Models folder
      TreeFolder(
        folder="Custom Models",
        items=[
          TreeNode("Custom Model 1", "custom_1", 10),
          TreeNode("Custom Model 2", "custom_2", 11),
          TreeNode("Custom Model 3", "custom_3", 12),
        ]
      ),
    ]

    # Get current model selection
    current_model = "default_model"

    # Create and show the tree dialog
    dialog = TreeOptionDialog(
      title="Select Model",
      items=tree_items,
      current=current_model,
      fav_param="ModelManager_Favs"
    )

    # Set as modal overlay
    gui_app.set_modal_overlay(dialog)

    # Save selection when dialog closes
    def save_selection():
      if dialog.selection != current_model:
        self._params.put("ModelSelection", dialog.selection)
        # Update button text or other UI elements here if needed

    # Note: In a real implementation, you'd need to hook into the dialog's close event
    # to call save_selection(). For now, this demonstrates the usage.
