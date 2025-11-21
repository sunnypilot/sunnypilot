from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params

onroad_brightness_timer_values = {
  0: 15,
  1: 30,
  2: 60,
  3: 120,
  4: 180,
  5: 240,
  6: 300,
  7: 360,
  8: 420,
  9: 480,
  10: 540,
  11: 600
}

class DisplayLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._onroad_brightness_toggle = toggle_item_sp(
      param="OnroadScreenOffControl",
      title=lambda: tr("Onroad Screen: Reduced Brightness"),
      description=lambda: tr("Turn off device screen or reduce brightness after driving starts. " +
         "It automatically brightens again when screen is touched or a visible alert is displayed."),
    )
    self._onroad_brightness_timer = option_item_sp(
      param="OnroadScreenOffTimer",
      title=lambda: tr("Onroad Brightness Delay"),
      description="",
      min_value=0,
      max_value=11,
      value_change_step=1,
      value_map=onroad_brightness_timer_values,
      label_callback=lambda value: f"{value} s" if value < 60 else f"{int(value/60)} m",
    )
    self._onroad_brightness = option_item_sp(
      param="OnroadScreenOffBrightness",
      title=lambda: tr("Onroad Brightness"),
      description="",
      min_value=0,
      max_value=90,
      value_change_step=5,
      label_callback=lambda value: f"{value} %" if value > 0 else tr("Screen Off"),
    )
    self._global_brightness = option_item_sp(
      param="Brightness",
      title=tr("Global Brightness"),
      description=lambda: tr("Overrides the brightness of the device. This applies to both onroad and offroad screens."),
      min_value=-5,
      max_value=100,
      value_change_step=5,
      label_callback=lambda value: f"{value}" if value > 0 else tr("Auto") if value == 0 else tr("Auto(Dark)")
    )
    self._interactivity_timeout = option_item_sp(
      param="InteractivityTimeout",
      title=lambda: tr("Interactivity Timeout"),
      description=lambda: tr("Apply a custom timeout for settings UI." +
                             "<br>This is the time after which settings UI closes automatically " +
                             "if user is not interacting with the screen."),
      min_value=0,
      max_value=120,
      value_change_step=10,
      label_callback=lambda value: (tr("Default") if not value or value == 0 else
                                    f"{value} s" if value < 60 else f"{int(value/60)} m")
    )
    items = [
      self._onroad_brightness_toggle,
      self._onroad_brightness_timer,
      self._onroad_brightness,
      self._global_brightness,
      self._interactivity_timeout,
    ]
    return items

  def _update_state(self):
    super()._update_state()
    self._onroad_brightness_timer.set_visible(self._onroad_brightness_toggle.action_item.get_state())
    self._onroad_brightness.set_visible(self._onroad_brightness_toggle.action_item.get_state())

    self.hide_for_now()

  def hide_for_now(self):
    self._onroad_brightness_toggle.set_visible(False)
    self._onroad_brightness_timer.set_visible(False)
    self._onroad_brightness.set_visible(False)
    self._global_brightness.set_visible(False)
    self._interactivity_timeout.set_visible(False)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
