"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.slider import SmallSlider
from openpilot.system.ui.mici_setup import TermsHeader, TermsPage as SetupTermsPage


class SunnylinkConsentPage(SetupTermsPage):
  def __init__(self, on_accept=None, on_decline=None, left_text: str = "disable", right_text: str = "enable"):
    super().__init__(on_accept, on_decline, left_text, continue_text=right_text)

    self._title_header = TermsHeader("sunnylink",
                                     gui_app.texture("../../sunnypilot/selfdrive/assets/logo.png", 66, 60))

    self._terms_label = UnifiedLabel("sunnylink enables secured remote access to your comma device from anywhere, "
                                     "including settings management, remote monitoring, real-time dashboard, etc.",
                                     36, FontWeight.ROMAN)

  @property
  def _content_height(self):
    return self._terms_label.rect.y + self._terms_label.rect.height - self._scroll_panel.get_offset()

  def _render(self, _):
    super()._render(_)
    return -1

  def _render_content(self, scroll_offset):
    self._title_header.set_position(self._rect.x + 16, self._rect.y + 12 + scroll_offset)
    self._title_header.render()

    self._terms_label.render(rl.Rectangle(
      self._rect.x + 16,
      self._title_header.rect.y + self._title_header.rect.height + self.ITEM_SPACING,
      self._rect.width - 100,
      self._terms_label.get_content_height(int(self._rect.width - 100)),
    ))


class SunnylinkConsentDisableConfirmPage(SunnylinkConsentPage):
  def __init__(self, on_accept=None, on_decline=None):
    super().__init__(on_accept=on_decline, on_decline=on_accept, left_text="enable", right_text="disable")

    # we flip the continue & disable buttons to use slider for disable
    self._continue_slider = True
    self._continue_button = SmallSlider("disable", confirm_callback=on_decline)
    self._scroll_panel.set_enabled(lambda: not self._continue_button.is_pressed)

    self._title_header = TermsHeader("disable sunnylink?",
                                     gui_app.texture("icons_mici/setup/red_warning.png", 66, 60))

    self._terms_label = UnifiedLabel("sunnylink is designed to be enabled as part of sunnypilot's core functionality. "
                                     "If sunnylink is disabled, features such as settings management, "
                                     "remote monitoring, real-time dashboards will be unavailable.",
                                     36, FontWeight.ROMAN)
