#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_visuals_settings.h"

#include <tuple>
#include <vector>

VisualsPanel::VisualsPanel(QWidget *parent) : ListWidgetSP(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "BrakeLights",
      tr("Display Braking Status"),
      tr("Enable this will turn the current speed value to red while the brake is used."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "StandStillTimer",
      tr("Display Stand Still Timer"),
      tr("Enable this will display time spent at a stop (i.e., at a stop lights, stop signs, traffic congestions)."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ReverseDmCam",
      tr("Display DM Camera in Reverse Gear"),
      tr("Show Driver Monitoring camera while the car is in reverse gear."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ShowDebugUI",
      tr("OSM: Show debug UI elements"),
      tr("OSM: Show UI elements that aid debugging."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "FeatureStatus",
      tr("Display Feature Status"),
      tr("Display the statuses of certain features on the driving screen."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "OnroadSettings",
      tr("Enable Onroad Settings"),
      tr("Display the Onroad Settings button on the driving screen to adjust feature options on the driving screen, without navigating into the settings menu."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TrueVEgoUi",
      tr("Speedometer: Display True Speed"),
      tr("Display the true vehicle current speed from wheel speed sensors."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "HideVEgoUi",
      tr("Speedometer: Hide from Onroad Screen"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "EndToEndLongAlertUI",
      tr("Display End-to-end Longitudinal Status (Beta)"),
      tr("Enable this will display an icon that appears when the End-to-end model decides to start or stop."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "MapboxFullScreen",
      tr("Navigation: Display in Full Screen"),
      tr("Enable this will display the built-in navigation in full screen.<br>To switch back to driving view, <font color='yellow'>tap on the border edge</font>."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "Map3DBuildings",
      tr("Map: Display 3D Buildings"),
      tr("Parse and display 3D buildings on map. Thanks to jakethesnake420 for this implementation."),
      "../assets/offroad/icon_blank.png",
    },
  };

  // Visuals: Developer UI Info (Dev UI)
  std::vector<QString> dev_ui_settings_texts{tr("Off"), tr("5 Metrics"), tr("10 Metrics")};
  dev_ui_settings = new ButtonParamControlSP(
    "DevUIInfo", tr("Developer UI"), tr("Display real-time parameters and metrics from various sources."),
    "../assets/offroad/icon_blank.png",
    dev_ui_settings_texts,
    380);
  dev_ui_settings->showDescription();

  // Visuals: Display Metrics above Chevron
  std::vector<QString> chevron_info_settings_texts{tr("Off"), tr("Distance"), tr("Speed"), tr("Distance\nSpeed")};
  chevron_info_settings = new ButtonParamControlSP(
    "ChevronInfo", tr("Display Metrics Below Chevron"), tr("Display useful metrics below the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control)."),
    "../assets/offroad/icon_blank.png",
    chevron_info_settings_texts,
    340);
  chevron_info_settings->showDescription();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "StandStillTimer") {
      addItem(dev_ui_settings);
    }

    if (param == "HideVEgoUi") {
      addItem(chevron_info_settings);
    }
  }

  std::vector<QString> sidebar_temp_texts{tr("Off"), tr("RAM"), tr("CPU"), tr("GPU"), tr("Max")};
  sidebar_temp_setting = new ButtonParamControlSP(
    "SidebarTemperatureOptions", tr("Display Temperature on Sidebar"), "",
    "../assets/offroad/icon_blank.png",
    sidebar_temp_texts,
    255);
  sidebar_temp_setting->showDescription();
  addItem(sidebar_temp_setting);

  // trigger offroadTransition when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
  });

  QObject::connect(toggles["MapboxFullScreen"], &ToggleControl::toggleFlipped, [=](bool state) {
    toggles["MapboxFullScreen"]->showDescription();
  });
}
