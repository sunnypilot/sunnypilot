"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass, field

import pyray as rl
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import gui_label, Label
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
    super().__init__(text, click_callback, button_style=ButtonStyle.NORMAL, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                     text_padding=20 + indent_level * 30, elide_right=True)
    self.text = text
    self.ref = ref
    self.is_folder = is_folder
    self.indent_level = indent_level
    self.is_favorite = is_favorite
    self.selected = False
    self._favorite_callback = favorite_callback
    self.text_padding = 20 + indent_level * 30
    self.border_radius = 10

  def _render(self, rect):
    indent = 60 * self.indent_level if self.indent_level > 0 else 10
    self._rect = rl.Rectangle(rect.x + indent, rect.y, rect.width - indent, rect.height)
    color = style.BUTTON_PRIMARY_COLOR if self.selected and not (self.ref == "search_bar" or self.is_folder) else style.BUTTON_DISABLED_BG_COLOR
    roundness = self.border_radius / (min(self._rect.width, self._rect.height) / 2)
    rl.draw_rectangle_rounded(self._rect, roundness, 10, color)
    text_rect = rl.Rectangle(self._rect.x + self.text_padding + 20, self._rect.y, self._rect.width - self.text_padding - 20 - 90, self._rect.height)
    self._label.render(text_rect)

    if not self.is_folder and self._favorite_callback:
      draw_star(self._rect.x + self._rect.width - 90, self._rect.y + self._rect.height / 2, 40, self.is_favorite,
                style.ON_BG_COLOR if self.is_favorite else rl.GRAY)

  def _handle_mouse_release(self, mouse_pos):
    star_rect = rl.Rectangle(self._rect.x + self._rect.width - 90 - 40, self._rect.y + self._rect.height / 2 - 40, 80, 80)
    if not self.is_folder and self._favorite_callback and rl.check_collision_point_rec(mouse_pos, star_rect):
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
    self.search_prompt = search_prompt or tr("Search")
    self.get_folders_fn = get_folders_fn
    self.on_exit = on_exit
    self.display_func = display_func or (lambda node: node.data.get('display_name', node.ref))
    self.search_funcs = search_funcs or [lambda node: node.data.get('display_name', ''), lambda node: node.data.get('short_name', '')]
    self._build_visible_items()
    self.cancel_rect = None
    self.select_rect = None

  def _on_search_confirm(self, result, text):
    if result == DialogResult.CONFIRM:
      self.query = text
      self._build_visible_items()
    gui_app.set_modal_overlay(self, callback=self.on_exit)

  def _on_search_clicked(self):
    InputDialogSP(tr("Enter search query"), current_text=self.query, callback=self._on_search_confirm).show()

  def _toggle_folder(self, folder):
    if folder.folder:
      if folder.folder in self.expanded:
        self.expanded.remove(folder.folder)
      else:
        self.expanded.add(folder.folder)
      if folder == self.folders[-1] and folder.folder in self.expanded:
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

  def _build_visible_items(self, reset_scroll=True):
    self.visible_items = [TreeItemWidget(self.query or self.search_prompt, "search_bar", False, 0, self._on_search_clicked)]
    for folder in self.folders:
      nodes = [node for node in folder.nodes if not self.query or search_from_list(self.query, [search_func(node) for search_func in self.search_funcs])]
      if not nodes and self.query:
        continue
      expanded = folder.folder in self.expanded or not folder.folder or bool(self.query)
      if folder.folder:
        self.visible_items.append(TreeItemWidget(f"{'-' if expanded else '+'} {folder.folder}", "", True, 0,
                                                 lambda folder_ref=folder: self._toggle_folder(folder_ref)))
      if expanded:
        for node in nodes:
          favorite_cb = (lambda node_ref=node: self._toggle_favorite(node_ref)) if self.fav_param and node.ref != "Default" else None
          self.visible_items.append(TreeItemWidget(self.display_func(node), node.ref, False, 1 if folder.folder else 0,
                                                   lambda node_ref=node: self._select_node(node_ref), favorite_cb, node.ref in self.favorites))
    self.option_buttons = self.visible_items
    self.options = [item.text for item in self.visible_items]
    self.scroller._items = self.visible_items
    if reset_scroll:
      self.scroller.scroll_panel.set_offset(0)

  def _draw_button(self, button_rect, button_text, is_primary=False, is_enabled=True):
    if is_primary and is_enabled:
      button_color = style.BUTTON_PRIMARY_COLOR
    elif not is_enabled:
      button_color = style.BUTTON_NEUTRAL_GRAY
    else:
      button_color = style.BUTTON_DISABLED_BG_COLOR
    roundness = 10 / (min(button_rect.width, button_rect.height) / 2)
    rl.draw_rectangle_rounded(button_rect, roundness, 10, button_color)
    label = Label(button_text, 60, FontWeight.NORMAL, rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                  text_color=rl.WHITE if is_enabled else rl.GRAY)
    label.render(button_rect)

  def _render(self, rect):
    dialog_content_rect = rl.Rectangle(rect.x + 50, rect.y + 50, rect.width - 100, rect.height - 100)
    rl.draw_rectangle_rounded(dialog_content_rect, 0.02, 20, rl.BLACK)
    gui_label(rl.Rectangle(dialog_content_rect.x + 50, dialog_content_rect.y + 50, dialog_content_rect.width - 100, 70),
              self.title, 70, font_weight=FontWeight.BOLD)

    options_area_rect = rl.Rectangle(dialog_content_rect.x + 50, dialog_content_rect.y + 170, dialog_content_rect.width - 100, dialog_content_rect.height - 330)
    for index, option_text in enumerate(self.options):
      self.option_buttons[index].selected = (option_text == self.selection)
      self.option_buttons[index].set_button_style(ButtonStyle.PRIMARY if option_text == self.selection else ButtonStyle.NORMAL)
      self.option_buttons[index].set_rect(rl.Rectangle(0, 0, options_area_rect.width, 135))
    self.scroller.render(options_area_rect)

    button_width = (dialog_content_rect.width - 150) / 2
    button_y_position = dialog_content_rect.y + dialog_content_rect.height - 160
    self.cancel_rect = rl.Rectangle(dialog_content_rect.x + 50, button_y_position, button_width, 160)
    self.select_rect = rl.Rectangle(dialog_content_rect.x + 100 + button_width, button_y_position, button_width, 160)

    self._draw_button(self.cancel_rect, tr("Cancel"))
    self._draw_button(self.select_rect, tr("Select"), True, self.selection != self.current)
    return self._result

  def _handle_mouse_release(self, mouse_pos):
    if self.cancel_rect and rl.check_collision_point_rec(mouse_pos, self.cancel_rect):
      self._set_result(DialogResult.CANCEL)
      return True
    if self.select_rect and rl.check_collision_point_rec(mouse_pos, self.select_rect) and self.selection != self.current:
      self._set_result(DialogResult.CONFIRM)
      return True
    return super()._handle_mouse_release(mouse_pos)
