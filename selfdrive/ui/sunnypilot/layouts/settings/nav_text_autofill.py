import json
import threading
from functools import partial
import pyray as rl

from openpilot.system.ui.widgets.keyboard import Keyboard, CONTENT_MARGIN
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.sunnypilot.navd.navigation_helpers.mapbox_integration import MapboxIntegration
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult

class AutofillKeyboard(Keyboard):
  def __init__(self, max_text_size=255, min_text_size=0):
    super().__init__(max_text_size, min_text_size)
    self.mapbox = MapboxIntegration()
    self.params = Params()
    self.lock = threading.Lock()
    self.suggestions = []
    self.suggestion_buttons = []
    self._last_search_text = ""
    self._updated = False

  def handle_key_press(self, key):
    super().handle_key_press(key)
    if len(self.text) >= 3 and self.text != self._last_search_text:
      self._last_search_text = self.text
      threading.Thread(target=self._fetch_suggestions, args=(self.text,)).start()
    elif len(self.text) < 3:
      with self.lock:
        self.suggestions, self._updated = [], True

  def _fetch_suggestions(self, text):
    try:
      pos = json.loads(self.params.get("LastGPSPosition") or "{}")
    except Exception:
      pos = {}
    result = self.mapbox.get_autocomplete_suggestions(text, pos.get('longitude'), pos.get('latitude'))
    with self.lock:
      self.suggestions = result
      self._updated = True

  def _suggestion_clicked(self, s):
    self.set_text(s.get('place_name', ''))
    with self.lock:
      self.suggestions = []
      self._updated = True

  def _render(self, rect: rl.Rectangle):
    with self.lock:
      if self._updated:
        self.suggestion_buttons = [Button(s.get('place_name', ''), partial(self._suggestion_clicked, s),
                                          button_style=ButtonStyle.NORMAL, font_size=35,
                                          text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT,
                                          text_padding=10, elide_right=True) for s in self.suggestions[:3]]
        self._updated = False
      btns = self.suggestion_buttons[:]

    ret = super()._render(rect)
    if btns:
      overlay = rl.Rectangle(rect.x + CONTENT_MARGIN, rect.y + CONTENT_MARGIN, rect.width - 2 * CONTENT_MARGIN, 155)
      rl.draw_rectangle_rec(overlay, rl.Color(0, 0, 0, 200))
      for i, b in enumerate(btns):
        b.render(rl.Rectangle(overlay.x, overlay.y + i * 50, overlay.width, 45))
    return ret

class AutofillInputDialogSP:
  def __init__(self, title, sub_title=None, current_text="", param=None, callback=None, min_text_size=0):
    self.kb = AutofillKeyboard(255, min_text_size)
    self.kb.set_title(tr(title), *(tr(sub_title),) if sub_title else ())
    self.kb.set_text(current_text)
    self.param = param
    self.callback = callback

  def show(self):
    def on_done(res):
      txt = self.kb.text if res == DialogResult.CONFIRM else ""
      if res == DialogResult.CONFIRM and self.param:
        self.kb.params.put(self.param, txt)
      if self.callback:
        self.callback(res, txt)
    gui_app.set_modal_overlay(self.kb, on_done)
