"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label
from openpilot.system.version import sunnylink_consent_version, sunnylink_consent_declined


class SunnylinkConsentPage(Widget):
  def __init__(self, done_callback=None):
    super().__init__()
    self._done_callback = done_callback
    self._step = 0

    self._title = Label(tr("sunnylink"), font_size=90, font_weight=FontWeight.BOLD, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._content = [
      {
        "text": tr("sunnylink enables secured remote access to your comma device from anywhere, " +
                   "including settings management, remote monitoring, real-time dashboard, etc."),
        "primary_btn": tr("Enable"),
        "secondary_btn": tr("Disable"),
        "highlight_primary": True
      },
      {
        "text": tr("sunnylink is designed to be enabled as part of sunnypilot's core functionality. " +
                   "If sunnylink is disabled, features such as settings management, remote monitoring, " +
                   "real-time dashboards will be unavailable."),
        "secondary_btn": tr("Back"),
        "danger_btn": tr("Disable"),
        "highlight_primary": True
      }
    ]

    self._primary_btn = Button("", button_style=ButtonStyle.PRIMARY, click_callback=lambda: self._handle_choice("enable"))
    self._secondary_btn = Button("", button_style=ButtonStyle.NORMAL, click_callback=lambda: self._handle_choice("secondary"))
    self._danger_btn = Button("", button_style=ButtonStyle.DANGER, click_callback=lambda: self._handle_choice("disable"))

  def _handle_choice(self, choice):
    if choice == "enable":
      ui_state.params.put_bool("SunnylinkEnabled", True)
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_version)
      if self._done_callback:
        self._done_callback()
    elif choice == "secondary":
      if self._step == 0:
        self._step = 1
      elif self._step == 1:
        self._step = 0
    elif choice == "disable":
      ui_state.params.put_bool("SunnylinkEnabled", False)
      ui_state.params.put("CompletedSunnylinkConsentVersion", sunnylink_consent_declined)
      if self._done_callback:
        self._done_callback()

  def _render(self, _):
    step_data = self._content[self._step]

    welcome_x = self._rect.x + 95
    welcome_y = self._rect.y + 165
    welcome_rect = rl.Rectangle(welcome_x, welcome_y, self._rect.width - welcome_x, 90)
    self._title.render(welcome_rect)

    desc_x = welcome_x
    desc_y = welcome_y + 120
    desc_rect = rl.Rectangle(desc_x, desc_y, self._rect.width - desc_x, self._rect.height - desc_y - 250)

    desc_label = Label(step_data["text"], font_size=90, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    desc_label.render(desc_rect)

    btn_y = self._rect.y + self._rect.height - 160 - 45

    if "danger_btn" in step_data:
      btn_width = (self._rect.width - 45 * 3) / 2

      self._secondary_btn.set_text(step_data["secondary_btn"])
      self._secondary_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))

      self._danger_btn.set_text(step_data["danger_btn"])
      self._danger_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    else:
      btn_width = (self._rect.width - 45 * 3) / 2

      self._secondary_btn.set_text(step_data["secondary_btn"])
      self._secondary_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))

      self._primary_btn.set_text(step_data["primary_btn"])
      self._primary_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    return -1


class SunnylinkOnboarding:
  def __init__(self):
    self.consent_page = SunnylinkConsentPage(done_callback=self._on_done)
    self.consent_done: bool = ui_state.params.get("CompletedSunnylinkConsentVersion") in {sunnylink_consent_version, sunnylink_consent_declined}

  @property
  def completed(self) -> bool:
    return self.consent_done

  def _on_done(self):
    self.consent_done = True

  def render(self, rect):
    if not self.consent_done:
      self.consent_page.render(rect)
