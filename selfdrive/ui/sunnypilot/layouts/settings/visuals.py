from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget

CHEVRON_INFO_DESCRIPTION = {
  "enabled": tr_noop("Display useful metrics below the chevron that tracks the lead car " +
                     "only applicable to cars with sunnypilot longitudinal control."),
  "disabled": tr_noop("This feature requires sunnypilot longitudinal control to be available.")
}



class VisualsLayout(Widget):
  def __init__(self):
    super().__init__()

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._blind_spot_toggle = toggle_item_sp(
      title=lambda: tr("Show Blind Spot Warnings"),
      description=tr("Enabling this will display warnings when a vehicle is detected in your " +
                     "blind spot as long as your car has BSM supported."),
      param="BlindSpot",
    )
    self._rainbow_toggle = toggle_item_sp(
      title=lambda: tr("Enable Tesla Rainbow Mode"),
      description=lambda: tr("A beautiful rainbow effect on the path the model wants to take. " +
                             "It does not affect driving in any way."),
      param="RainbowMode",
    )
    self._standstill_timer_toggle = toggle_item_sp(
      title=lambda: tr("Enable Standstill Timer"),
      description=lambda: tr("Show a timer on the HUD when the car is at a standstill."),
      param="StandstillTimer",
    )
    self._roadname_toggle = toggle_item_sp(
      param="RoadNameToggle",
      title=lambda: tr("Display Road Name"),
      description=lambda: tr("Displays the name of the road the car is traveling on." +
                             "<br>The OpenStreetMap database of the location must be downloaded from " +
                             "the OSM panel to fetch the road name."),
    )
    self._green_light_toggle = toggle_item_sp(
      param="GreenLightAlert",
      title=lambda: tr("Green Traffic Light Alert (Beta)"),
      description=lambda: tr("A chime and on-screen alert will play when the traffic light you are waiting for " +
                             "turns green and you have no vehicle in front of you." +
                             "<br>Note: This chime is only designed as a notification. " +
                             "It is the driver's responsibility to observe their environment and make decisions accordingly."),
    )
    self._lead_depart_toggle = toggle_item_sp(
      param="LeadDepartAlert",
      title=lambda: tr("Lead Departure Alert (Beta)"),
     description=lambda: tr("A chime and on-screen alert will play when you are stopped, and the vehicle in front of you start moving." +
                            "<br>Note: This chime is only designed as a notification. " +
                            "It is the driver's responsibility to observe their environment and make decisions accordingly."),
    )
    self._true_vego_ui_toggle = toggle_item_sp(
      param="TrueVEgoUI",
      title=lambda: tr("Speedometer: Always Display True Speed"),
      description=lambda: tr("Always display the true vehicle current speed from wheel speed sensors."),
    )
    self._hide_vego_ui_toggle = toggle_item_sp(
      param="HideVEgoUI",
      title=lambda: tr("Speedometer: Hide from Onroad Screen"),
      description=lambda: tr("When enabled, the speedometer on the onroad screen is not displayed."),
    )
    self._turn_signals_toggle = toggle_item_sp(
      param="ShowTurnSignals",
      title=lambda: tr("Display Turn Signals"),
      description=lambda: tr("When enabled, visual turn indicators are drawn on the HUD."),
    )
    self._chevron_info = multiple_button_item_sp(
      title=lambda: tr("Display Metrics Below Chevron"),
      description="",
      buttons=[lambda: tr("Off"), lambda: tr("Distance"), lambda: tr("Speed"), lambda: tr("Time"), lambda: tr("All")],
      param="ChevronInfo",
      inline=False
    )
    self._dev_ui_info = multiple_button_item_sp(
      title=lambda: tr("Developer UI"),
      description=lambda: tr("Display real-time parameters and metrics from various sources."),
      buttons=[lambda: tr("Off"), lambda: tr("Right"), lambda: tr("Right & Bottom")],
      param="DevUIInfo",
      button_width=350,
      inline=False
    )

    items = [
      self._blind_spot_toggle,
      self._rainbow_toggle,
      self._standstill_timer_toggle,
      self._roadname_toggle,
      self._green_light_toggle,
      self._lead_depart_toggle,
      self._true_vego_ui_toggle,
      self._hide_vego_ui_toggle,
      self._turn_signals_toggle,
      self._chevron_info,
      self._dev_ui_info,
    ]
    return items

  def _update_state(self):
    super()._update_state()
    if ui_state_sp.has_longitudinal_control:
      self._chevron_info.set_description(tr(CHEVRON_INFO_DESCRIPTION["enabled"]))
      self._chevron_info.action_item.set_enabled(True)
    else:
      self._chevron_info.set_description(tr(CHEVRON_INFO_DESCRIPTION["disabled"]))
      self._chevron_info.action_item.set_enabled(False)
      ui_state_sp.params.put("ChevronInfo", 0)

    self.hide_for_now()

  def hide_for_now(self):
    self._blind_spot_toggle.set_visible(False)
    self._rainbow_toggle.set_visible(False)
    self._standstill_timer_toggle.set_visible(False)
    self._roadname_toggle.set_visible(False)
    self._green_light_toggle.set_visible(False)
    self._lead_depart_toggle.set_visible(False)
    self._true_vego_ui_toggle.set_visible(False)
    self._hide_vego_ui_toggle.set_visible(False)
    self._turn_signals_toggle.set_visible(False)
    self._chevron_info.set_visible(False)
    self._dev_ui_info.set_visible(False)

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
    self._chevron_info.show_description(not ui_state_sp.has_longitudinal_control)
