import pyray as rl
from dataclasses import dataclass

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import gui_label
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog

from openpilot.system.ui.sunnypilot.lib.styles import style

@dataclass
class TreeNode:
  folder: str
  display_name: str
  ref: str
  index: int

@dataclass
class TreeFolder:
  folder: str
  nodes: list


class TreeItemWidget(Button):
  def __init__(self, text, ref, is_folder=False, indent_level=0, click_callback=None, favorite_callback=None, is_favorite=False):
    super().__init__(text, click_callback, button_style=ButtonStyle.NORMAL,
                     text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                     text_padding=20 + indent_level * 70, elide_right=True)
    self.text = text
    self.ref = ref
    self.is_folder = is_folder
    self.indent_level = indent_level
    self.is_favorite = is_favorite
    self._favorite_callback = favorite_callback

  def _render(self, rect):
    super()._render(rect)
    if not self.is_folder and self._favorite_callback:
      star_rect = rl.Rectangle(rect.x + rect.width - 50, rect.y + (rect.height - 40) / 2, 40, 40)
      gui_label(star_rect, "*", 70, style.ITEM_TEXT_COLOR if self.is_favorite else style.ITEM_DISABLED_TEXT_COLOR)

  def _handle_mouse_release(self, mouse_pos):
    if not self.is_folder and self._favorite_callback:
      star_rect = rl.Rectangle(self._rect.x + self._rect.width - 50, self._rect.y + (self._rect.height - 40) / 2, 40, 40)
      if rl.check_collision_point_rec(mouse_pos, star_rect):
        self._favorite_callback()
        return True
    return super()._handle_mouse_release(mouse_pos)



class TreeOptionDialog(MultiOptionDialog):
  def __init__(self, title, folders, current_ref="", fav_param="", option_font_weight=FontWeight.MEDIUM):
    super().__init__(title, [], "", option_font_weight)
    self.folders = folders
    self.current_ref = current_ref
    self.selection_ref = current_ref
    self.fav_param = fav_param
    self.expanded = set()
    self.params = Params()
    fav_str = self.params.get(fav_param) or ""
    self.favorites = set(fav_str.split(';')) if fav_str else set()
    self._build_visible_items()

  def _build_visible_items(self):
    self.visible_items = []
    for folder in self.folders:
      is_expanded = folder.folder in self.expanded or folder.folder == ""
      toggle_text = "-" if is_expanded and folder.folder else "+"
      if folder.folder:
        item = TreeItemWidget(f"{toggle_text} {folder.folder}", "", True, 0, lambda f=folder: self._toggle_folder(f))
        self.visible_items.append(item)
      if is_expanded:
        for node in folder.nodes:
          is_fav = node.ref in self.favorites
          indent = 1 if folder.folder else 0
          item = TreeItemWidget(node.display_name, node.ref, False, indent,
                                lambda n=node: self._select_node(n),
                                lambda n=node: self._toggle_favorite(n),
                                is_fav)
          self.visible_items.append(item)

    self.option_buttons = self.visible_items
    self.options = [item.text for item in self.visible_items]
    self.scroller._items = self.visible_items

  def _toggle_folder(self, folder):
    if folder.folder:
      if folder.folder in self.expanded:
        self.expanded.remove(folder.folder)
      else:
        self.expanded.add(folder.folder)
        if folder == self.folders[-1]:
          current_offset = self.scroller.scroll_panel.offset
          self.scroller.scroll_panel.set_offset(current_offset - 200)
      self._build_visible_items()

  def _select_node(self, node):
    self.selection = node.display_name
    self.selection_ref = node.ref

  def _toggle_favorite(self, node):
    if node.ref in self.favorites:
      self.favorites.remove(node.ref)
      fav_folder = next((fav for fav in self.folders if fav.folder == "Favorites"), None)
      if fav_folder:
        fav_folder.nodes = [n for n in fav_folder.nodes if n.ref != node.ref]
        if not fav_folder.nodes:
          self.folders.remove(fav_folder)
    else:
      self.favorites.add(node.ref)
      fav_folder = next((fav for fav in self.folders if fav.folder == "Favorites"), None)
      if not fav_folder:
        fav_folder = TreeFolder("Favorites", [])
        self.folders.insert(1, fav_folder)
      fav_folder.nodes.append(TreeNode("", node.display_name, node.ref, node.index))
      fav_folder.nodes.sort(key=lambda n: n.index, reverse=True)
    if self.fav_param:
      self.params.put(self.fav_param, ';'.join(self.favorites))
    self._build_visible_items()
