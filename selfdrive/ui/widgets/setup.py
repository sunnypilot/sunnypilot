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

    # Center-aligned title label
    self._side_label = Label(
      lambda: tr("Hey there..."),
      font_weight=FontWeight.MEDIUM,
      font_size=64,
      halign="center"
    )

  def set_open_settings_callback(self, callback):
    self._open_settings_callback = callback

  # -----------------------------
  #   Main render switch
  # -----------------------------
  def _render(self, rect: rl.Rectangle):
    if not ui_state.prime_state.is_paired():
      self._render_registration(rect)
    else:
      self._render_side_prompt(rect)

  # -----------------------------
  #   Setup screen (pairing)
  # -----------------------------
  def _render_registration(self, rect: rl.Rectangle):

    rl.draw_rectangle_rounded(
      rl.Rectangle(rect.x, rect.y, rect.width, rect.height),
      0.03, 20,
      rl.Color(51, 51, 51, 255)
    )

    x = rect.x + 64
    y = rect.y + 48
    w = rect.width - 128

    # Title
    font = gui_app.font(FontWeight.BOLD)
    rl.draw_text_ex(font, tr("Finish Setup"), rl.Vector2(x, y), 75, 0, rl.WHITE)
    y += 113

    # Description
    desc = tr("Pair your device with Konik Stable (stable.konik.ai)")
    light_font = gui_app.font(FontWeight.NORMAL)
    wrapped = wrap_text(light_font, desc, 50, int(w))

    for line in wrapped:
      rl.draw_text_ex(light_font, line, rl.Vector2(x, y), 50, 0, rl.WHITE)
      y += 50 * FONT_SCALE

    button_rect = rl.Rectangle(x, y + 30, w, 200)
    self._pair_device_btn.render(button_rect)

  # -----------------------------
  #   Centered side widget
  # -----------------------------
  def _render_side_prompt(self, rect: rl.Rectangle):

    # Style and consistent spacing
    horizontal_padding = 56
    vertical_padding = 40
    spacing = 42

    # Box width similar to OP tiles
    box_width = min(rect.width * 0.8, 900)
    box_x = rect.x + (rect.width - box_width) / 2

    # Text width inside the box
    w = box_width - (horizontal_padding * 2)

    # Description text
    desc_font = gui_app.font(FontWeight.NORMAL)
    desc_text = tr("Hope you're having a great day!")
    wrapped_desc = wrap_text(desc_font, desc_text, 40, int(w))

    # Dynamic box height
    title_h = 64
    desc_h = len(wrapped_desc) * (40 * FONT_SCALE)

    box_height = (
      vertical_padding +
      title_h +
      spacing +
      desc_h +
      vertical_padding
    )

    # Draw the centered background box
    rl.draw_rectangle_rounded(
      rl.Rectangle(box_x, rect.y, box_width, box_height),
      0.04, 20,
      rl.Color(51, 51, 51, 255)
    )

    # -----------------------------
    #   Render content inside box
    # -----------------------------
    y = rect.y + vertical_padding

    # Centered title inside the box
    self._side_label.render(
      rl.Rectangle(box_x + horizontal_padding, y, w, title_h)
    )

    y += title_h + spacing

    # Center the description text manually
    for line in wrapped_desc:
      # Measure text width so we can center it
      tw = rl.measure_text_ex(desc_font, line, 40, 0).x
      text_x = box_x + (box_width - tw) / 2
      rl.draw_text_ex(desc_font, line, rl.Vector2(text_x, y), 40, 0, rl.WHITE)
      y += 40 * FONT_SCALE

  # -----------------------------
  #   Pairing Dialog
  # -----------------------------
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