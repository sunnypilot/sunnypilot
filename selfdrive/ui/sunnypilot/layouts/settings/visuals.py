from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params


class VisualsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._blind_spot_toggle = toggle_item_sp(
      title=tr("Show Blind Spot Warnings"),
      description=(
        "Enabling this will display warnings when a vehicle is detected in your blind spot as long as your car has BSM supported."),
      param="BlindSpot",
    )
    self._rainbow_toggle = toggle_item_sp(
      title=tr("Enable Tesla Rainbow Mode"),
      description=tr("A beautiful rainbow effect on the path the model wants to take.") +
                  tr("It does not affect driving in any way."),
      param="RainbowMode",
    )
    self._standstill_timer_toggle = toggle_item_sp(
      title=tr("Enable Standstill Timer"),
      description=tr("Show a timer on the HUD when the car is at a standstill."),
      param="StandstillTimer",
    )
    self._roadname_toggle = toggle_item_sp(
      param="RoadNameToggle",
      title=tr("Display Road Name"),
      description=tr("Displays the name of the road the car is traveling on. ") +
                  tr("The OpenStreetMap database of the location must be downloaded from the OSM panel to fetch the road name."),
    )
    self._green_light_toggle = toggle_item_sp(
      param="GreenLightAlert",
      title=tr("Green Traffic Light Alert (Beta)"),
      description=tr("A chime and on-screen alert will play when the traffic light you are waiting for turns green and you have no vehicle in front of you. ") +
                  tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly."),
    )
    self._lead_depart_toggle = toggle_item_sp(
      param="LeadDepartAlert",
      title=tr("Lead Departure Alert (Beta)"),
     description=tr("A chime and on-screen alert will play when you are stopped, and the vehicle in front of you start moving. ") +
                 tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly."),
    )
    self._true_vego_ui_toggle = toggle_item_sp(
      param="TrueVEgoUI",
      title=tr("Speedometer: Always Display True Speed"),
      description=tr("Always display the true vehicle current speed from wheel speed sensors."),
    )
    self._hide_vego_ui_toggle = toggle_item_sp(
      param="HideVEgoUI",
      title=tr("Speedometer: Hide from Onroad Screen"),
      description=tr("When enabled, the speedometer on the onroad screen is not displayed."),
    )
    self._turn_signals_toggle = toggle_item_sp(
      param="ShowTurnSignals",
      title=tr("Display Turn Signals"),
      description=tr("When enabled, visual turn indicators are drawn on the HUD."),
    )
    self._chevron_info = multiple_button_item_sp(
      title=tr("Display Metrics Below Chevron"),
      description=tr("Display useful metrics below the chevron that tracks the lead car (only applicable to cars with sunnypilot longitudinal control)."),
      buttons=[tr("Off"), tr("Distance"), tr("Speed"), tr("Time"), tr("All")],
      param="ChevronInfo",
    )
    self._dev_ui_info = multiple_button_item_sp(
      title=tr("Developer UI"),
      description=tr("Display real-time parameters and metrics from various sources."),
      buttons=[tr("Off"), tr("Right"), tr("Right & Bottom")],
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
