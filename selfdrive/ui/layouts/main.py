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


class MainLayout(Widget):
  def __init__(self):
    super().__init__()

    self._pm = messaging.PubMaster(['bookmarkButton'])

    self._current_mode = MainState.HOME
    self._prev_onroad = False
    # Settings transition animation state
    self._settings_anim_active = False
    self._settings_anim_start = 0.0
    # Use easing/duration similar to mici (slightly bouncy)
    self._settings_anim_duration = 0.32
    self._settings_anim_direction: str | None = None  # 'in' or 'out'
    self._settings_prev_layout: MainState | None = None

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

    # Offroad: existing behavior (reverse entry animation or start exit animation)
    now = rl.get_time()
    if self._settings_anim_active and self._settings_anim_direction == 'in':
      elapsed = now - self._settings_anim_start
      prog = max(0.0, min(1.0, elapsed / self._settings_anim_duration))
      self._settings_anim_direction = 'out'
      self._settings_anim_start = now - (1.0 - prog) * self._settings_anim_duration
      return

    if not self._settings_anim_active and self._current_mode == MainState.SETTINGS:
      self._settings_prev_layout = MainState.HOME if MainState.HOME in self._layouts else None
      self._settings_anim_active = True
      self._settings_anim_direction = 'out'
      self._settings_anim_start = now
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

    # Offroad: start slide-up animation to open settings
    # Record previous layout to render underneath during animation
    self._settings_prev_layout = self._current_mode
    self._settings_anim_active = True
    self._settings_anim_direction = 'in'
    now = rl.get_time()
    self._settings_anim_start = now
    # ensure settings layout can initialize
    self._layouts[MainState.SETTINGS].show_event()

  def _on_settings_clicked(self):
    # Toggle settings: open if not open, close if already open (or reverse animation)
    if self._settings_anim_active:
      # if animating, reverse direction
      if self._settings_anim_direction == 'in':
        self._settings_anim_direction = 'out'
        prog = max(0.0, min(1.0, (rl.get_time() - self._settings_anim_start) / self._settings_anim_duration))
        self._settings_anim_start = rl.get_time() - (self._settings_anim_duration * (1 - prog))
      elif self._settings_anim_direction == 'out':
        self._settings_anim_direction = 'in'
        prog = max(0.0, min(1.0, (rl.get_time() - self._settings_anim_start) / self._settings_anim_duration))
        self._settings_anim_start = rl.get_time() - (self._settings_anim_duration * (1 - prog))
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
      now = rl.get_time()
      elapsed = now - self._settings_anim_start
      t = max(0.0, min(1.0, elapsed / self._settings_anim_duration))
      # easeOutQuad to reduce bounce
      eased = 1 - (1 - t) * (1 - t)

      # During animation, draw a solid backdrop to prevent underlying icons peeking
      rl.draw_rectangle_rec(content_rect, rl.Color(0, 0, 0, 255))

      # Compute animated Y for settings panel (full page)
      full_rect = self._rect
      if self._settings_anim_direction == 'in':
        start_y = full_rect.y + full_rect.height
        end_y = full_rect.y
        cur_y = start_y + (end_y - start_y) * eased
      else:
        # out animation: move down
        start_y = full_rect.y
        end_y = full_rect.y + full_rect.height
        cur_y = start_y + (end_y - start_y) * eased

      animated_rect = rl.Rectangle(full_rect.x, cur_y, full_rect.width, full_rect.height)
      # Render settings layout into animated rect
      self._layouts[MainState.SETTINGS].render(animated_rect)

      # Finish animation
      if t >= 1.0:
        if self._settings_anim_direction == 'in':
          # Entered settings fully
          # Only switch the current mode when not overlaying onroad (to avoid disrupting driving state)
          if self._settings_prev_layout != MainState.ONROAD:
            self._current_mode = MainState.SETTINGS
            # hide the previous layout now that settings is fully visible
            if self._settings_prev_layout is not None:
              try:
                self._layouts[self._settings_prev_layout].hide_event()
              except Exception:
                pass
          else:
            # Keep onroad as the active layout under the overlay
            self._current_mode = MainState.ONROAD
        else:
          # Exited settings, ensure hide_event called
          self._layouts[MainState.SETTINGS].hide_event()
          # Restore previous layout
          if self._settings_prev_layout is not None:
            self._current_mode = self._settings_prev_layout
        self._settings_anim_active = False
        self._settings_anim_direction = None
        self._settings_prev_layout = None
      return

    # No active animation: render the current layout normally
    self._layouts[self._current_mode].render(content_rect)
