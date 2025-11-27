import pyray as rl
from enum import IntEnum
import cereal.messaging as messaging
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.layouts.sidebar import Sidebar, SIDEBAR_WIDTH
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

    self._sidebar = Sidebar()
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

    self._sidebar_rect = rl.Rectangle(0, 0, 0, 0)
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
    self._sidebar.set_callbacks(on_settings=self._on_settings_clicked,
                                on_flag=self._on_bookmark_clicked,
                                open_settings=lambda: self.open_settings(PanelType.TOGGLES))
    self._layouts[MainState.HOME]._setup_widget.set_open_settings_callback(lambda: self.open_settings(PanelType.FIREHOSE))
    self._layouts[MainState.HOME].set_settings_callback(lambda: self.open_settings(PanelType.TOGGLES))
    # Intercept settings close to run slide-down animation
    self._layouts[MainState.SETTINGS].set_callbacks(on_close=self._close_settings_requested)
    self._layouts[MainState.ONROAD].set_click_callback(self._on_onroad_clicked)

  def _close_settings_requested(self):
    """Start slide-down animation to close settings instead of switching immediately."""
    # If an entry animation is in progress, reverse it
    now = rl.get_time()
    if self._settings_anim_active and self._settings_anim_direction == 'in':
      # compute current progress
      elapsed = now - self._settings_anim_start
      prog = max(0.0, min(1.0, elapsed / self._settings_anim_duration))
      # start exit such that visual position remains continuous
      self._settings_anim_direction = 'out'
      # set start so that eased progress for 'out' begins at current eased position
      # approximate by setting start so elapsed produces same prog when reversed
      self._settings_anim_start = now - (1.0 - prog) * self._settings_anim_duration
      return

    # If not animating, start an exit animation from fully visible settings
    if not self._settings_anim_active and self._current_mode == MainState.SETTINGS:
      self._settings_prev_layout = MainState.HOME if MainState.HOME in self._layouts else None
      self._settings_anim_active = True
      self._settings_anim_direction = 'out'
      self._settings_anim_start = now
    device.add_interactive_timeout_callback(self._set_mode_for_state)

  def _update_layout_rects(self):
    self._sidebar_rect = rl.Rectangle(self._rect.x, self._rect.y, SIDEBAR_WIDTH, self._rect.height)

    x_offset = SIDEBAR_WIDTH if self._sidebar.is_visible else 0
    self._content_rect = rl.Rectangle(self._rect.y + x_offset, self._rect.y, self._rect.width - x_offset, self._rect.height)

  def _handle_onroad_transition(self):
    if ui_state.started != self._prev_onroad:
      self._prev_onroad = ui_state.started

      self._set_mode_for_state()

  def _set_mode_for_state(self):
    if ui_state.started:
      # Don't hide sidebar from interactive timeout
      if self._current_mode != MainState.ONROAD:
        self._sidebar.set_visible(False)
      self._set_current_layout(MainState.ONROAD)
    else:
      self._set_current_layout(MainState.HOME)
      self._sidebar.set_visible(True)

  def _set_current_layout(self, layout: MainState):
    if layout != self._current_mode:
      self._layouts[self._current_mode].hide_event()
      self._current_mode = layout
      self._layouts[self._current_mode].show_event()

  def open_settings(self, panel_type: PanelType):
    # Prepare settings layout and start slide-up animation from bottom
    self._layouts[MainState.SETTINGS].set_current_panel(panel_type)
    # Record previous layout to render underneath during animation
    self._settings_prev_layout = self._current_mode
    # Start entering animation
    self._settings_anim_active = True
    self._settings_anim_direction = 'in'
    now = rl.get_time()
    self._settings_anim_start = now
    # ensure settings layout can initialize
    self._layouts[MainState.SETTINGS].show_event()
    # Hide sidebar so settings becomes full page
    self._sidebar.set_visible(False)

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
    self._sidebar.set_visible(not self._sidebar.is_visible)

  def _render_main_content(self):
    # Render sidebar
    if self._sidebar.is_visible:
      self._sidebar.render(self._sidebar_rect)

    content_rect = self._content_rect if self._sidebar.is_visible else self._rect
    # If a settings animation is active, render previous layout underneath and animate settings sliding
    if self._settings_anim_active and self._settings_anim_direction is not None:
      now = rl.get_time()
      elapsed = now - self._settings_anim_start
      t = max(0.0, min(1.0, elapsed / self._settings_anim_duration))
      # easeOutBack (tiny overshoot / bounce) to match mici feel
      # https://easings.net/#easeOutBack
      c1 = 1.70158
      c3 = c1 + 1
      eased = 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

      # Determine base (under) layout
      base_layout = self._layouts[self._settings_prev_layout] if self._settings_prev_layout is not None else self._layouts[self._current_mode]
      base_layout.render(content_rect)

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
