import pyray as rl
from openpilot.common.time_helpers import system_time_valid
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.widgets.pairing_dialog import PairingDialog
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label


class SetupWidget(Widget):
  def __init__(self):
    super().__init__()
    self._open_settings_callback = None
    self._pairing_dialog: PairingDialog | None = None

    self._pair_device_btn = Button(
      lambda: tr("Pair device"),
      self._show_pairing,
      button_style=ButtonStyle.PRIMARY
    )

    # NOTE: halign REMOVED because it crashes the UI
    self._side_label = Label(
      lambda: tr("Hey there..."),
      font_weight=FontWeight.MEDIUM,
      font_size=64
    )

  def set_open_settings_callback(self, callback):
    self._open_settings_callback = callback

  def _render(self, rect: rl.Rectangle):
    if not ui_state.prime_state.is_paired():
      self._render_registration(rect)
    else:
      self._render_side_prompt(rect)

  def _render_registration(self, rect: rl.Rectangle):

    rl.draw_rectangle_rounded(
      rl.Rectangle(rect.x, rect.y, rect.width, rect.height),
      0.03, 20,
      rl.Color(51, 51, 51, 255)
    )

    x = rect.x + 64
    y = rect.y + 48
    w = rect.width - 128

    font = gui_app.font(FontWeight.BOLD)
    rl.draw_text_ex(font, tr("Finish Setup"), rl.Vector2(x, y), 75, 0, rl.WHITE)
    y += 113

    desc = tr("Pair your device with Konik Stable (stable.konik.ai)")
    light_font = gui_app.font(FontWeight.NORMAL)
    wrapped = wrap_text(light_font, desc, 50, int(w))

    for line in wrapped:
      rl.draw_text_ex(light_font, line, rl.Vector2(x, y), 50, 0, rl.WHITE)
      y += 50 * FONT_SCALE

    button_rect = rl.Rectangle(x, y + 30, w, 200)
    self._pair_device_btn.render(button_rect)

  def _render_side_prompt(self, rect: rl.Rectangle):
    """
    Box aligned EXACTLY under Chill Mode button.
    Uses the same column width & x-position.
    """

    # This rect is too tall.
    # We need the same vertical offset as HomeLayout uses for the driving mode tile.

    TILE_HEIGHT = 125 + 40   # driving mode height (125) + bottom spacing (40)

    # X alignment identical to Chill mode tile
    x = rect.x + 56
    w = rect.width - 112

    # Y position directly under the Chill Mode button
    y = rect.y + TILE_HEIGHT + 40

    BOX_HEIGHT = 200

    # Draw background box
    rl.draw_rectangle_rounded(
        rl.Rectangle(x, y, w, BOX_HEIGHT),
        0.04, 20,
        rl.Color(51, 51, 51, 255)
    )

    # ---- Title ----
    title_y = y + 35
    self._side_label.render(
        rl.Rectangle(x + 30, title_y, w - 60, 64)
    )

    # ---- Description ----
    desc = tr("Hope you're having a great day!")
    desc_font = gui_app.font(FontWeight.NORMAL)

    desc_y = title_y + 80

    rl.draw_text_ex(
        desc_font,
        desc,
        rl.Vector2(x + 30, desc_y),
        40,
        0,
        rl.WHITE
    )

  def _show_pairing(self):
    if not system_time_valid():
      dlg = alert_dialog(tr("Please connect to Wi-Fi to complete initial pairing"))
      gui_app.set_modal_overlay(dlg)
      return

    if not self._pairing_dialog:
      self._pairing_dialog = PairingDialog()

    gui_app.set_modal_overlay(
      self._pairing_dialog,
      lambda result: setattr(self, '_pairing_dialog', None)
    )

  def __del__(self):
    if self._pairing_dialog:
      del self._pairing_dialog