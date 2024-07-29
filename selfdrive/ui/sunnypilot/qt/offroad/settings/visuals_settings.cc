/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/visuals_settings.h"

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
    "",
    dev_ui_settings_texts,
    380);
  dev_ui_settings->showDescription();

  // Visuals: Display Metrics above Chevron
  std::vector<QString> chevron_info_settings_texts{tr("Off"), tr("Distance"), tr("Speed"), tr("Time"), tr("All")};
  chevron_info_settings = new ButtonParamControlSP(
    "ChevronInfo", tr("Display Metrics Below Chevron"), tr("Display useful metrics below the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control)."),
    "",
    chevron_info_settings_texts,
    300);
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
    "",
    sidebar_temp_texts,
    255);
  sidebar_temp_setting->showDescription();
  addItem(sidebar_temp_setting);

  // trigger offroadTransition when going onroad/offroad
  connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
  });

  QObject::connect(toggles["MapboxFullScreen"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    toggles["MapboxFullScreen"]->showDescription();
  });
}
