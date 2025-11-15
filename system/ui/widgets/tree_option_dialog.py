#  /**
#   * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
#   *
#   * This file is part of sunnypilot and is licensed under the MIT License.
#   * See the LICENSE.md file in the root directory for more details.
#   */

import pyray as rl
from dataclasses import dataclass
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.common.params import Params

# Constants
MARGIN = 50
TITLE_FONT_SIZE = 70
ITEM_HEIGHT = 135
BUTTON_SPACING = 50
BUTTON_HEIGHT = 160
ITEM_SPACING = 5
STAR_ICON_SIZE = 100
FOLDER_ICON_SIZE = 40
INDENT_SIZE = 50


@dataclass
class TreeNode:
  """Represents a single item in the tree"""
  display_name: str
  ref: str  # Unique identifier for the item
  index: int = 0


@dataclass
class TreeFolder:
  """Represents a folder containing tree nodes"""
  folder: str  # Folder name, empty string for top-level items
  items: list[TreeNode]


class TreeItemWidget(Widget):
  """Widget representing a single tree item (folder or node)"""

  def __init__(self, text: str, ref: str = "", is_folder: bool = False,
               indent_level: int = 0, click_callback=None, favorite_callback=None,
               is_favorite: bool = False, star_icon=None, folder_icon=None):
    super().__init__()
    self.text = text
    self.ref = ref
    self.is_folder = is_folder
    self.indent_level = indent_level
    self.is_expanded = False
    self.is_selected = False
    self.is_favorite = is_favorite
    self._click_callback = click_callback
    self._favorite_callback = favorite_callback
    self.star_icon = star_icon
    self.folder_icon = folder_icon
    self.children: list[TreeItemWidget] = []

    # Fixed height for tree items
    self._rect = rl.Rectangle(0, 0, 0, ITEM_HEIGHT)

  def add_child(self, child):
    self.children.append(child)

  def toggle_expand(self):
    if self.is_folder:
      self.is_expanded = not self.is_expanded

  def _render(self, _):
    # Background color based on selection state
    bg_color = rl.Color(70, 91, 234, 255) if self.is_selected else rl.Color(79, 79, 79, 255)

    # Draw background with rounded corners
    rl.draw_rectangle_rounded(self._rect, 0.07, 10, bg_color)

    # Calculate text position with indent
    text_x = self._rect.x + self.indent_level * INDENT_SIZE + 20
    text_y = self._rect.y + (self._rect.height - TITLE_FONT_SIZE) / 2
    text_width = self._rect.width - self.indent_level * INDENT_SIZE - 40

    # Draw folder icon if folder
    if self.is_folder and self.folder_icon:
      icon_x = text_x
      icon_y = self._rect.y + (self._rect.height - FOLDER_ICON_SIZE) / 2
      rl.draw_texture_ex(self.folder_icon, rl.Vector2(icon_x, icon_y), 0,
                         FOLDER_ICON_SIZE / self.folder_icon.width, rl.WHITE)
      text_x += FOLDER_ICON_SIZE + 10
      text_width -= FOLDER_ICON_SIZE + 10

    # Draw text
    text_rect = rl.Rectangle(text_x, text_y, text_width - STAR_ICON_SIZE - 20, TITLE_FONT_SIZE)
    gui_label(text_rect, self.text, 55, font_weight=FontWeight.LIGHT,
              color=rl.WHITE)

    # Draw star icon for non-folder items (on the right)
    if not self.is_folder and self.star_icon:
      star_x = self._rect.x + self._rect.width - STAR_ICON_SIZE - 20
      star_y = self._rect.y + (self._rect.height - STAR_ICON_SIZE) / 2
      star_rect = rl.Rectangle(star_x, star_y, STAR_ICON_SIZE, STAR_ICON_SIZE)

      # Check if star icon is clicked
      for mouse_event in gui_app.mouse_events:
        if mouse_event.left_released and rl.check_collision_point_rec(mouse_event.pos, star_rect):
          if self._favorite_callback:
            self._favorite_callback(self)
          return

      # Draw star icon (filled if favorite, empty otherwise)
      icon_scale = STAR_ICON_SIZE / self.star_icon.width
      rl.draw_texture_ex(self.star_icon, rl.Vector2(star_x, star_y), 0, icon_scale,
                        rl.WHITE if self.is_favorite else rl.Color(255, 255, 255, 100))

  def _handle_mouse_release(self, mouse_pos):
    """Handle click on the item"""
    if self._click_callback:
      self._click_callback(self)
    return True


class TreeOptionDialog(Widget):
  """Dialog for selecting an item from a hierarchical tree structure with favorites support"""

  def __init__(self, title: str, items: list[TreeFolder], current: str = "", fav_param: str = ""):
    super().__init__()
    self.title = title
    self.items = items
    self.current = current
    self.selection = current
    self.fav_param = fav_param
    self.params = Params()

    # Load favorites from params
    self.favorites: set[str] = set()
    if fav_param:
      fav_str = self.params.get(fav_param)
      if fav_str:
        self.favorites = set(fav for fav in fav_str.split(';') if fav)

    # Load icons
    self.star_filled_icon = None
    self.star_empty_icon = None
    self.folder_icon = None

    try:
      self.star_filled_icon = rl.load_texture("../../sunnypilot/selfdrive/assets/icons/star-filled.png")
      self.star_empty_icon = rl.load_texture("../../sunnypilot/selfdrive/assets/icons/star-empty.png")
      self.folder_icon = rl.load_texture("../assets/icons/menu.png")
    except:
      # Icons are optional
      pass

    # Build tree structure
    self.tree_items: list[TreeItemWidget] = []
    self.ref_to_item: dict[str, TreeItemWidget] = {}  # Map ref to item for quick lookup
    self._build_tree()

    # Create scroller with all visible items
    self.scroller = Scroller(self._get_visible_items(), spacing=ITEM_SPACING, pad_end=True)

    # Buttons
    self.cancel_button = Button("Cancel", click_callback=lambda: gui_app.set_modal_overlay(None))
    self.select_button = Button("Select", click_callback=self._on_select, button_style=ButtonStyle.PRIMARY)

  def _build_tree(self):
    """Build the tree structure from the input items"""
    folders: dict[str, TreeItemWidget] = {}

    # Create favorites folder
    favorites_folder = TreeItemWidget(
      "Favorites", "", is_folder=True, indent_level=0,
      click_callback=self._on_item_clicked,
      folder_icon=self.folder_icon
    )
    folders["__favorites__"] = favorites_folder
    self.tree_items.append(favorites_folder)

    # First pass: create all folders and items
    for tree_folder in self.items:
      folder_name = tree_folder.folder

      if not folder_name:
        # Top-level items (no folder)
        for node in tree_folder.items:
          item = self._create_item_widget(node, indent_level=0)
          self.tree_items.append(item)
          self.ref_to_item[node.ref] = item
      else:
        # Items in a folder
        if folder_name not in folders:
          folder_widget = TreeItemWidget(
            folder_name, "", is_folder=True, indent_level=0,
            click_callback=self._on_item_clicked,
            folder_icon=self.folder_icon
          )
          folders[folder_name] = folder_widget
          # Insert after favorites folder
          self.tree_items.insert(1, folder_widget)

        folder_widget = folders[folder_name]
        for node in tree_folder.items:
          item = self._create_item_widget(node, indent_level=1)
          folder_widget.add_child(item)
          self.ref_to_item[node.ref] = item

          # Auto-expand folder if it contains the current selection
          if node.ref == self.current:
            folder_widget.is_expanded = True

    # Second pass: populate favorites folder
    for fav_ref in self.favorites:
      if fav_ref in self.ref_to_item:
        original_item = self.ref_to_item[fav_ref]
        # Create a duplicate item for the favorites folder
        fav_item = self._create_item_widget(
          TreeNode(original_item.text, fav_ref, 0),
          indent_level=1
        )
        favorites_folder.add_child(fav_item)

        # Auto-expand favorites if it contains the current selection
        if fav_ref == self.current:
          favorites_folder.is_expanded = True

  def _create_item_widget(self, node: TreeNode, indent_level: int) -> TreeItemWidget:
    """Create a tree item widget from a TreeNode"""
    is_fav = node.ref in self.favorites
    star_icon = self.star_filled_icon if is_fav else self.star_empty_icon

    item = TreeItemWidget(
      node.display_name, node.ref, is_folder=False, indent_level=indent_level,
      click_callback=self._on_item_clicked,
      favorite_callback=self._on_favorite_toggled,
      is_favorite=is_fav,
      star_icon=star_icon
    )

    if node.ref == self.current:
      item.is_selected = True

    return item

  def _get_visible_items(self) -> list[TreeItemWidget]:
    """Get all currently visible items in the tree (respecting expand/collapse state)"""
    visible = []
    for item in self.tree_items:
      visible.append(item)
      if item.is_folder and item.is_expanded:
        visible.extend(item.children)
    return visible

  def _on_item_clicked(self, item: TreeItemWidget):
    """Handle click on a tree item"""
    if item.is_folder:
      # Toggle folder expansion
      item.toggle_expand()
      # Rebuild scroller with new visible items
      visible_items = self._get_visible_items()
      self.scroller._items = visible_items
      for widget in visible_items:
        widget.set_touch_valid_callback(self.scroller.scroll_panel.is_touch_valid)
    else:
      # Select the item
      # Deselect all items first
      for ref_item in self.ref_to_item.values():
        ref_item.is_selected = False
      # Also deselect favorite duplicates
      for tree_item in self.tree_items:
        if tree_item.is_folder:
          for child in tree_item.children:
            child.is_selected = False

      # Select the clicked item
      item.is_selected = True
      self.selection = item.ref

  def _on_favorite_toggled(self, item: TreeItemWidget):
    """Handle toggling favorite status of an item"""
    if item.ref in self.favorites:
      # Remove from favorites
      self.favorites.discard(item.ref)

      # Update all instances of this item (original + duplicate in favorites)
      if item.ref in self.ref_to_item:
        self.ref_to_item[item.ref].is_favorite = False
        self.ref_to_item[item.ref].star_icon = self.star_empty_icon

      # Remove from favorites folder
      favorites_folder = self.tree_items[0]
      favorites_folder.children = [c for c in favorites_folder.children if c.ref != item.ref]
    else:
      # Add to favorites
      self.favorites.add(item.ref)

      # Update all instances of this item
      if item.ref in self.ref_to_item:
        self.ref_to_item[item.ref].is_favorite = True
        self.ref_to_item[item.ref].star_icon = self.star_filled_icon

      # Add to favorites folder
      favorites_folder = self.tree_items[0]
      fav_item = self._create_item_widget(
        TreeNode(item.text, item.ref, 0),
        indent_level=1
      )
      # Insert at the beginning of favorites
      favorites_folder.children.insert(0, fav_item)

    # Save favorites to params
    if self.fav_param:
      self.params.put(self.fav_param, ';'.join(self.favorites))

    # Rebuild scroller with new visible items
    visible_items = self._get_visible_items()
    self.scroller._items = visible_items
    for widget in visible_items:
      widget.set_touch_valid_callback(self.scroller.scroll_panel.is_touch_valid)

  def _on_select(self):
    """Handle select button click"""
    gui_app.set_modal_overlay(None)

  def _render(self, rect):
    dialog_rect = rl.Rectangle(rect.x + MARGIN, rect.y + MARGIN,
                               rect.width - 2 * MARGIN, rect.height - 2 * MARGIN)
    rl.draw_rectangle_rounded(dialog_rect, 0.02, 20, rl.Color(27, 27, 27, 255))

    content_rect = rl.Rectangle(dialog_rect.x + MARGIN, dialog_rect.y + MARGIN,
                                dialog_rect.width - 2 * MARGIN, dialog_rect.height - 2 * MARGIN)

    # Title
    gui_label(rl.Rectangle(content_rect.x, content_rect.y, content_rect.width, TITLE_FONT_SIZE),
             self.title, 70, font_weight=FontWeight.MEDIUM)

    # Tree area
    tree_y = content_rect.y + TITLE_FONT_SIZE + 25
    tree_h = content_rect.height - TITLE_FONT_SIZE - BUTTON_HEIGHT - 60
    tree_rect = rl.Rectangle(content_rect.x, tree_y, content_rect.width, tree_h)

    # Update all visible items with correct width
    for item in self._get_visible_items():
      item.set_rect(rl.Rectangle(0, 0, tree_rect.width, ITEM_HEIGHT))

    self.scroller.render(tree_rect)

    # Buttons
    button_y = content_rect.y + content_rect.height - BUTTON_HEIGHT
    button_w = (content_rect.width - BUTTON_SPACING) / 2

    cancel_rect = rl.Rectangle(content_rect.x, button_y, button_w, BUTTON_HEIGHT)
    self.cancel_button.render(cancel_rect)

    select_rect = rl.Rectangle(content_rect.x + button_w + BUTTON_SPACING, button_y, button_w, BUTTON_HEIGHT)
    self.select_button.set_enabled(self.selection != self.current)
    self.select_button.render(select_rect)

    return -1

  def show_event(self):
    """Reset scroll position when dialog is shown"""
    self.scroller.show_event()

  def hide_event(self):
    """Clean up when dialog is hidden"""
    self.scroller.hide_event()
