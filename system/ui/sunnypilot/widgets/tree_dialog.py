import pyray as rl
from dataclasses import dataclass, field

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog

from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.helpers.fuzzy_search import search_from_list
from openpilot.system.ui.sunnypilot.widgets.helpers.star_icon import draw_star
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP

@dataclass
class TreeNode:
  ref: str
  data: dict = field(default_factory=dict)

@dataclass
class TreeFolder:
  folder: str
  nodes: list


class TreeItemWidget(Button):
  def __init__(self, text, ref, is_folder=False, indent_level=0, click_callback=None, favorite_callback=None, is_favorite=False):
    super().__init__(text, click_callback, button_style=ButtonStyle.NORMAL,
                     text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                     text_padding=20 + indent_level * 90, elide_right=True)
    self.text = text
    self.ref = ref
    self.is_folder = is_folder
    self.indent_level = indent_level
    self.is_favorite = is_favorite
    self._favorite_callback = favorite_callback

  @property
  def _star_rect(self):
    return rl.Rectangle(self._rect.x + self._rect.width - 65, self._rect.y + (self._rect.height - 40) / 2, 40, 40)

  def _render(self, rect):
    super()._render(rect)
    if not self.is_folder and self._favorite_callback:
      draw_star(self._star_rect.x + self._star_rect.width / 2, self._star_rect.y + self._star_rect.height / 2,
                25, self.is_favorite, style.ON_BG_COLOR if self.is_favorite else rl.GRAY)

  def _handle_mouse_release(self, mouse_pos):
    if not self.is_folder and self._favorite_callback and rl.check_collision_point_rec(mouse_pos, self._star_rect):
      self._favorite_callback()
      return True
    return super()._handle_mouse_release(mouse_pos)


class TreeOptionDialog(MultiOptionDialog):
  def __init__(self, title, folders, current_ref="", fav_param="", option_font_weight=FontWeight.MEDIUM, search_prompt=None,
               get_folders_fn=None, on_exit=None, display_func=None, search_funcs=None):
    super().__init__(title, [], "", option_font_weight)
    self.folders = folders
    self.selection_ref = current_ref
    self.fav_param = fav_param
    self.expanded = set()
    self.params = Params()
    val = self.params.get(fav_param) if fav_param else None
    self.favorites = set(val.split(';')) if val else set()

    self.query = ""
    self.search_prompt = search_prompt if search_prompt else tr("Search")
    self.get_folders_fn = get_folders_fn
    self.on_exit = on_exit
    self.display_func = display_func or (lambda node: node.data.get('display_name', node.ref))
    self.search_funcs = search_funcs or [lambda node: node.data.get('display_name', ''), lambda node: node.data.get('short_name', '')]

    self._build_visible_items()

  def _on_search_clicked(self):
    def _on_search_confirm(result, text):
      if result == DialogResult.CONFIRM:
        self.query = text
        self._build_visible_items()
      gui_app.set_modal_overlay(self, callback=self.on_exit)

    InputDialogSP(tr("Enter search query"), current_text=self.query, callback=_on_search_confirm).show()

  def _build_visible_items(self, reset_scroll=True):
    self.visible_items = [TreeItemWidget(self.query or self.search_prompt, "search_bar", False, 0, self._on_search_clicked)]

    for folder in self.folders:
      nodes = [node for node in folder.nodes if not self.query or search_from_list(self.query, [f(node) for f in self.search_funcs])]
      if not nodes and self.query:
        continue

      expanded = folder.folder in self.expanded or not folder.folder or bool(self.query)
      if folder.folder:
        self.visible_items.append(TreeItemWidget(f"{'-' if expanded else '+'} {folder.folder}", "", True, 0, lambda f=folder: self._toggle_folder(f)))

      if expanded:
        for node in nodes:
          cb = None if node.ref == "Default" else lambda n=node: self._toggle_favorite(n)
          self.visible_items.append(TreeItemWidget(self.display_func(node), node.ref, False, 1 if folder.folder else 0,
                                                   lambda n=node: self._select_node(n), cb, node.ref in self.favorites))

    self.option_buttons = self.visible_items
    self.options = [item.text for item in self.visible_items]
    self.scroller._items = self.visible_items
    if reset_scroll:
      self.scroller.scroll_panel.set_offset(0)

  def _toggle_folder(self, folder):
    if folder.folder:
      if folder.folder in self.expanded:
        self.expanded.remove(folder.folder)
      else:
        self.expanded.add(folder.folder)
        if folder == self.folders[-1]:
          self.scroller.scroll_panel.set_offset(self.scroller.scroll_panel.offset - 200)
      self._build_visible_items(reset_scroll=False)

  def _select_node(self, node):
    self.selection = self.display_func(node)
    self.selection_ref = node.ref

  def _toggle_favorite(self, node):
    self.favorites.remove(node.ref) if node.ref in self.favorites else self.favorites.add(node.ref)
    if self.fav_param:
      self.params.put(self.fav_param, ';'.join(self.favorites))

    if self.get_folders_fn:
      self.folders = self.get_folders_fn(self.favorites)

    self._build_visible_items(reset_scroll=False)
