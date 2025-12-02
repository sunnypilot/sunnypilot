import time
import pyray as rl
from enum import IntEnum
import cereal.messaging as messaging
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.layouts.home import HomeLayout
from openpilot.selfdrive.ui.layouts.settings.settings import SettingsLayout, PanelType
from openpilot.selfdrive.ui.onroad.augmented_road_view import AugmentedRoadView
from openpilot.selfdrive.ui.ui_state import device, ui_state
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.layouts.onboarding import OnboardingWindow

if gui_app.sunnypilot_ui():
  from openpilot.selfdrive.ui.sunnypilot.layouts.settings.settings import SettingsLayoutSP as SettingsLayout


class MainState(IntEnum):
  HOME = 0
  SETTINGS = 1
  ONROAD = 2

SETTINGS_ANIMATION_OFFSET = 160


class MainLayout(Widget):
  def __init__(self):
    super().__init__()

    self._pm = messaging.PubMaster(['bookmarkButton'])

    self._current_mode = MainState.HOME
    self._prev_onroad = False
    # Settings transition animation state (matches keyboard animation behavior)
    self._settings_anim_active = False
    self._settings_anim_duration = 0.25
    self._settings_anim_direction: str | None = None  # 'in' or 'out'
    self._settings_prev_layout: MainState | None = None
    self._settings_anim_progress = 0.0
    self._settings_anim_last_time: float | None = None

    # Initialize layouts
    self._layouts = {MainState.HOME: HomeLayout(), MainState.SETTINGS: SettingsLayout(), MainState.ONROAD: AugmentedRoadView()}

    self._content_rect = rl.Rectangle(0, 0, 0, 0)

    # Set callbacks
    self._setup_callbacks()

    # Start onboarding if terms or training not completed
    self._onboarding_window = OnboardingWindow()
    if not self._onboarding_window.completed:
      gui_app.set_modal_overlay(self._onboarding_window)

  def _render(self, _):
    self._handle_onroad_transition()
    self._render_main_content()

  def _setup_callbacks(self):
    # Home layout settings tap opens toggles by default
    self._layouts[MainState.HOME].set_settings_callback(lambda: self.open_settings(PanelType.TOGGLES))
    self._layouts[MainState.HOME].set_panel_callback(lambda panel: self.open_settings(panel))
    # Intercept settings close to run slide-down animation
    self._layouts[MainState.SETTINGS].set_callbacks(on_close=self._close_settings_requested)
    self._layouts[MainState.ONROAD].set_click_callback(self._on_onroad_clicked)
    try:
      self._layouts[MainState.ONROAD].set_settings_callback(lambda: self.open_settings(PanelType.DEVICE))
    except Exception:
      pass

  def _close_settings_requested(self):
    """Close settings: instantly in onroad (clear modal), animated offroad."""
    # If we're onroad and settings was shown as a modal overlay, close instantly
    if ui_state.started:
      try:
        self._layouts[MainState.SETTINGS].hide_event()
      except Exception:
        pass
      # Clear the modal overlay so input returns to onroad
      gui_app.set_modal_overlay(None)
      # Restore active layout to ONROAD (or previous layout if recorded)
      if self._settings_prev_layout is not None:
        self._current_mode = self._settings_prev_layout
      else:
        self._current_mode = MainState.ONROAD
      # Ensure settings state cleared
      self._settings_anim_active = False
      self._settings_anim_direction = None
      self._settings_prev_layout = None
      return

    # Offroad: mirror keyboard animation behavior
    if self._settings_anim_active:
      if self._settings_anim_direction == 'in':
        self._settings_anim_direction = 'out'
        self._settings_anim_last_time = None
      return

    if self._current_mode == MainState.SETTINGS:
      self._settings_prev_layout = MainState.HOME if MainState.HOME in self._layouts else None
      self._start_settings_animation('out')
    device.add_interactive_timeout_callback(self._set_mode_for_state)

  def _update_layout_rects(self):
    self._content_rect = rl.Rectangle(self._rect.x, self._rect.y, self._rect.width, self._rect.height)

  def _handle_onroad_transition(self):
    if ui_state.started != self._prev_onroad:
      self._prev_onroad = ui_state.started

      self._set_mode_for_state()

  def _set_mode_for_state(self):
    if ui_state.started:
      self._set_current_layout(MainState.ONROAD)
    else:
      self._set_current_layout(MainState.HOME)

  def _set_current_layout(self, layout: MainState):
    if layout != self._current_mode:
      self._layouts[self._current_mode].hide_event()
      self._current_mode = layout
      self._layouts[self._current_mode].show_event()

  def _render_settings_modal(self):
    """Modal callable that renders the settings layout full-screen.

    Returning -1 keeps the modal active; the settings close path will
    call `gui_app.set_modal_overlay(None)` when it needs to dismiss it.
    """
    try:
      self._layouts[MainState.SETTINGS].render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    except Exception:
      pass
    return -1

  def _start_settings_animation(self, direction: str):
    self._settings_anim_active = True
    self._settings_anim_direction = direction
    self._settings_anim_last_time = None
    self._settings_anim_progress = 0.0 if direction == 'in' else 1.0

  def _update_settings_animation(self):
    if not self._settings_anim_active or self._settings_anim_direction is None:
      return

    now = time.monotonic()
    if self._settings_anim_last_time is None:
      self._settings_anim_last_time = now
      return

    direction_factor = 1.0 if self._settings_anim_direction == 'in' else -1.0
    delta = direction_factor * (now - self._settings_anim_last_time) / self._settings_anim_duration
    self._settings_anim_progress = max(0.0, min(1.0, self._settings_anim_progress + delta))
    self._settings_anim_last_time = now

    if self._settings_anim_direction == 'in' and self._settings_anim_progress >= 1.0:
      self._finish_settings_animation_in()
    elif self._settings_anim_direction == 'out' and self._settings_anim_progress <= 0.0:
      self._finish_settings_animation_out()

  def _finish_settings_animation_in(self):
    self._settings_anim_active = False
    self._settings_anim_direction = None
    self._settings_anim_last_time = None
    if self._settings_prev_layout not in (None, MainState.ONROAD):
      try:
        self._layouts[self._settings_prev_layout].hide_event()
      except Exception:
        pass
    if self._settings_prev_layout != MainState.ONROAD:
      self._current_mode = MainState.SETTINGS
    else:
      self._current_mode = MainState.ONROAD
    self._settings_prev_layout = None
    self._settings_anim_progress = 1.0

  def _finish_settings_animation_out(self):
    self._settings_anim_active = False
    self._settings_anim_direction = None
    self._settings_anim_last_time = None
    try:
      self._layouts[MainState.SETTINGS].hide_event()
    except Exception:
      pass
    if self._settings_prev_layout is not None:
      self._current_mode = self._settings_prev_layout
    else:
      self._current_mode = MainState.HOME
    self._settings_prev_layout = None
    self._settings_anim_progress = 0.0

  @staticmethod
  def _ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 3)

  def open_settings(self, panel_type: PanelType):
    # Prepare settings layout
    self._layouts[MainState.SETTINGS].set_current_panel(panel_type)

    # If onroad, open settings instantly (no animation) as a modal overlay
    if ui_state.started:
      # Keep ONROAD active underneath the settings overlay
      self._settings_prev_layout = MainState.ONROAD
      self._settings_anim_active = False
      self._settings_anim_direction = None
      # ensure settings layout can initialize
      self._layouts[MainState.SETTINGS].show_event()
      # Render settings as a modal so it's drawn while onroad stays active
      gui_app.set_modal_overlay(self._render_settings_modal)
      return

    # Offroad: start slide animation (or reverse if exiting)
    if self._settings_anim_active and self._settings_anim_direction == 'out':
      self._settings_anim_direction = 'in'
      self._settings_anim_last_time = None
      return

    self._settings_prev_layout = self._current_mode
    self._layouts[MainState.SETTINGS].show_event()
    self._start_settings_animation('in')

  def _on_settings_clicked(self):
    # Toggle settings: open if not open, close if already open (or reverse animation)
    if self._settings_anim_active:
      if self._settings_anim_direction == 'in':
        self._settings_anim_direction = 'out'
      else:
        self._settings_prev_layout = self._current_mode
        self._settings_anim_direction = 'in'
      self._settings_anim_last_time = None
      return

    if self._current_mode == MainState.SETTINGS:
      # start closing animation
      self._close_settings_requested()
    else:
      self.open_settings(PanelType.DEVICE)

  def _on_bookmark_clicked(self):
    user_bookmark = messaging.new_message('bookmarkButton')
    user_bookmark.valid = True
    self._pm.send('bookmarkButton', user_bookmark)

  def _on_onroad_clicked(self):
    # Sidebar removed; no-op toggle to avoid unexpected view switches
    return

  def _render_main_content(self):
    content_rect = self._rect
    # If a settings animation is active, render previous layout underneath and animate settings sliding
    if self._settings_anim_active and self._settings_anim_direction is not None:
      self._update_settings_animation()
      if not self._settings_anim_active:
        self._layouts[self._current_mode].render(content_rect)
        return

      eased = self._ease_out_cubic(self._settings_anim_progress)
      slide_offset = (1.0 - eased) * SETTINGS_ANIMATION_OFFSET

      base_layout = self._settings_prev_layout if self._settings_prev_layout is not None else self._current_mode
      if base_layout is not None and base_layout in self._layouts:
        try:
          self._layouts[base_layout].render(content_rect)
        except Exception:
          pass

      animated_rect = rl.Rectangle(content_rect.x, content_rect.y + slide_offset,
                                    content_rect.width, content_rect.height)
      self._layouts[MainState.SETTINGS].render(animated_rect)
      return

    # No active animation: render the current layout normally
    self._layouts[self._current_mode].render(content_rect)
