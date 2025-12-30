import os
import re
import threading
from enum import IntEnum

import pyray as rl
from openpilot.common.basedir import BASEDIR
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.label import Label
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.version import terms_version, training_version, terms_version_sp

DEBUG = False

STEP_RECTS = [rl.Rectangle(104, 800, 633, 175), rl.Rectangle(1835, 0, 2159, 1080), rl.Rectangle(1835, 0, 2156, 1080),
              rl.Rectangle(1526, 473, 427, 472), rl.Rectangle(1643, 441, 217, 223), rl.Rectangle(1835, 0, 2155, 1080),
              rl.Rectangle(1786, 591, 267, 236), rl.Rectangle(1353, 0, 804, 1080), rl.Rectangle(1458, 485, 633, 211),
              rl.Rectangle(95, 794, 1158, 187), rl.Rectangle(1560, 170, 392, 397), rl.Rectangle(1835, 0, 2159, 1080),
              rl.Rectangle(1351, 0, 807, 1080), rl.Rectangle(1835, 0, 2158, 1080), rl.Rectangle(1531, 82, 441, 920),
              rl.Rectangle(1336, 438, 490, 393), rl.Rectangle(1835, 0, 2159, 1080), rl.Rectangle(1835, 0, 2159, 1080),
              rl.Rectangle(87, 795, 1187, 186)]

DM_RECORD_STEP = 9
DM_RECORD_YES_RECT = rl.Rectangle(695, 794, 558, 187)

RESTART_TRAINING_RECT = rl.Rectangle(87, 795, 472, 186)


class OnboardingState(IntEnum):
  TERMS = 0
  SUNNYLINK = 1
  ONBOARDING = 2
  DECLINE = 3


class TrainingGuide(Widget):
  def __init__(self, completed_callback=None):
    super().__init__()
    self._completed_callback = completed_callback

    self._step = 0
    self._load_image_paths()

    # Load first image now so we show something immediately
    self._textures = [gui_app.texture(self._image_paths[0])]
    self._image_objs = []

    threading.Thread(target=self._preload_thread, daemon=True).start()

  def _load_image_paths(self):
    paths = [fn for fn in os.listdir(os.path.join(BASEDIR, "selfdrive/assets/training")) if re.match(r'^step\d*\.png$', fn)]
    paths = sorted(paths, key=lambda x: int(re.search(r'\d+', x).group()))
    self._image_paths = [os.path.join(BASEDIR, "selfdrive/assets/training", fn) for fn in paths]

  def _preload_thread(self):
    # PNG loading is slow in raylib, so we preload in a thread and upload to GPU in main thread
    # We've already loaded the first image on init
    for path in self._image_paths[1:]:
      self._image_objs.append(gui_app._load_image_from_path(path))

  def _handle_mouse_release(self, mouse_pos):
    if rl.check_collision_point_rec(mouse_pos, STEP_RECTS[self._step]):
      # Record DM camera?
      if self._step == DM_RECORD_STEP:
        yes = rl.check_collision_point_rec(mouse_pos, DM_RECORD_YES_RECT)
        print(f"putting RecordFront to {yes}")
        ui_state.params.put_bool("RecordFront", yes)

      # Restart training?
      elif self._step == len(self._image_paths) - 1:
        if rl.check_collision_point_rec(mouse_pos, RESTART_TRAINING_RECT):
          self._step = -1

      self._step += 1

      # Finished?
      if self._step >= len(self._image_paths):
        self._step = 0
        if self._completed_callback:
          self._completed_callback()

  def _update_state(self):
    if len(self._image_objs):
      self._textures.append(gui_app._load_texture_from_image(self._image_objs.pop(0)))

  def _render(self, _):
    # Safeguard against fast tapping
    step = min(self._step, len(self._textures) - 1)
    rl.draw_texture(self._textures[step], 0, 0, rl.WHITE)

    # progress bar
    if 0 < step < len(STEP_RECTS) - 1:
      h = 20
      w = int((step / (len(STEP_RECTS) - 1)) * self._rect.width)
      rl.draw_rectangle(int(self._rect.x), int(self._rect.y + self._rect.height - h),
                        w, h, rl.Color(70, 91, 234, 255))

    if DEBUG:
      rl.draw_rectangle_lines_ex(STEP_RECTS[step], 3, rl.RED)

    return -1


class TermsPage(Widget):
  def __init__(self, on_accept=None, on_decline=None):
    super().__init__()
    self._on_accept = on_accept
    self._on_decline = on_decline

    self._title = Label(tr("Welcome to sunnypilot"), font_size=90, font_weight=FontWeight.BOLD, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._desc = Label(tr("You must accept the Terms of Service to use sunnypilot. Read the latest terms at https://sunnypilot.ai/terms before continuing."),
                       font_size=90, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._decline_btn = Button(tr("Decline"), click_callback=on_decline)
    self._accept_btn = Button(tr("Agree"), button_style=ButtonStyle.PRIMARY, click_callback=on_accept)

  def _render(self, _):
    welcome_x = self._rect.x + 95
    welcome_y = self._rect.y + 165
    welcome_rect = rl.Rectangle(welcome_x, welcome_y, self._rect.width - welcome_x, 90)
    self._title.render(welcome_rect)

    desc_x = welcome_x
    # TODO: Label doesn't top align when wrapping
    desc_y = welcome_y - 100
    desc_rect = rl.Rectangle(desc_x, desc_y, self._rect.width - desc_x, self._rect.height - desc_y - 250)
    self._desc.render(desc_rect)

    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._decline_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._accept_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    if DEBUG:
      rl.draw_rectangle_lines_ex(welcome_rect, 3, rl.RED)
      rl.draw_rectangle_lines_ex(desc_rect, 3, rl.RED)

    return -1


class SunnylinkPage(Widget):
  def __init__(self, done_callback=None):
    super().__init__()
    self._done_callback = done_callback
    self._step = 0

    self._title = Label(tr("sunnylink"), font_size=90, font_weight=FontWeight.BOLD, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._content = [
      {
        "text": tr("sunnylink enables secured remote access to your comma device from anywhere, "
                   "including settings management, remote monitoring, real-time dashboard, etc."),
        "primary_btn": tr("Enable"),
        "secondary_btn": tr("Disable"),
        "highlight_primary": True
      },
      {
        "text": tr("sunnylink is designed to be enabled as part of sunnypilot's core functionality. "
                   "If sunnylink is disabled, features such as settings management, remote monitoring, "
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
      if self._done_callback:
        self._done_callback()
    elif choice == "secondary":
      if self._step == 0:
        self._step = 1
      elif self._step == 1:
        self._step = 0
    elif choice == "disable":
      ui_state.params.put_bool("SunnylinkEnabled", False)
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


class DeclinePage(Widget):
  def __init__(self, back_callback=None):
    super().__init__()
    self._text = Label(tr("You must accept the Terms of Service in order to use sunnypilot."),
                       font_size=90, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._back_btn = Button(tr("Back"), click_callback=back_callback)
    self._uninstall_btn = Button(tr("Decline, uninstall sunnypilot"), button_style=ButtonStyle.DANGER,
                                 click_callback=self._on_uninstall_clicked)

  def _on_uninstall_clicked(self):
    ui_state.params.put_bool("DoUninstall", True)
    gui_app.request_close()

  def _render(self, _):
    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._back_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._uninstall_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    # text rect in middle of top and button
    text_height = btn_y - (200 + 45)
    text_rect = rl.Rectangle(self._rect.x + 165, self._rect.y + (btn_y - text_height) / 2 + 10, self._rect.width - (165 * 2), text_height)
    if DEBUG:
      rl.draw_rectangle_lines_ex(text_rect, 3, rl.RED)
    self._text.render(text_rect)


class OnboardingWindow(Widget):
  def __init__(self):
    super().__init__()
    self._accepted_terms: bool = ui_state.params.get("HasAcceptedTerms") == terms_version and \
                                 ui_state.params.get("HasAcceptedTermsSP") == terms_version_sp
    self._sunnylink_consented: bool = ui_state.params.get("CompletedSunnylinkConsent") == "1.0"
    self._training_done: bool = ui_state.params.get("CompletedTrainingVersion") == training_version

    self._state = OnboardingState.TERMS
    if self._accepted_terms:
      self._state = OnboardingState.SUNNYLINK
      if self._sunnylink_consented:
        self._state = OnboardingState.ONBOARDING

    # Windows
    self._terms = TermsPage(on_accept=self._on_terms_accepted, on_decline=self._on_terms_declined)
    self._sunnylink = SunnylinkPage(done_callback=self._on_sunnylink_done)
    self._training_guide: TrainingGuide | None = None
    self._decline_page = DeclinePage(back_callback=self._on_decline_back)

  @property
  def completed(self) -> bool:
    return self._accepted_terms and self._sunnylink_consented and self._training_done

  def _on_terms_declined(self):
    self._state = OnboardingState.DECLINE

  def _on_decline_back(self):
    self._state = OnboardingState.TERMS

  def _on_terms_accepted(self):
    ui_state.params.put("HasAcceptedTerms", terms_version)
    ui_state.params.put("HasAcceptedTermsSP", terms_version_sp)
    self._state = OnboardingState.SUNNYLINK
    if self._sunnylink_consented:
      self._state = OnboardingState.ONBOARDING

    if self._sunnylink_consented and self._training_done:
      gui_app.set_modal_overlay(None)

  def _on_sunnylink_done(self):
    ui_state.params.put("CompletedSunnylinkConsent", "1.0")
    self._sunnylink_consented = True
    self._state = OnboardingState.ONBOARDING
    if self._training_done:
      gui_app.set_modal_overlay(None)

  def _on_completed_training(self):
    ui_state.params.put("CompletedTrainingVersion", training_version)
    gui_app.set_modal_overlay(None)

  def _render(self, _):
    if self._training_guide is None:
      self._training_guide = TrainingGuide(completed_callback=self._on_completed_training)

    if self._state == OnboardingState.TERMS:
      self._terms.render(self._rect)
    elif self._state == OnboardingState.SUNNYLINK:
      self._sunnylink.render(self._rect)
    elif self._state == OnboardingState.ONBOARDING:
      self._training_guide.render(self._rect)
    elif self._state == OnboardingState.DECLINE:
      self._decline_page.render(self._rect)
    return -1
