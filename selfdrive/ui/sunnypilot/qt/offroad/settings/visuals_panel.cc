/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/visuals_panel.h"

VisualsPanel::VisualsPanel(QWidget *parent) : QWidget(parent) {
  param_watcher = new ParamWatcher(this);
  connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    paramsRefresh();
  });

  main_layout = new QStackedLayout(this);
  ListWidgetSP *list = new ListWidgetSP(this, false);

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  std::vector<std::tuple<QString, QString, QString, QString, bool> > toggle_defs{
    {
      "BlindSpot",
      tr("Show Blind Spot Warnings"),
      tr("Enabling this will display warnings when a vehicle is detected in your blind spot as long as your car has BSM supported."),
      "",
      false,
    },
    {
      "RainbowMode",
      tr("Enable Tesla Rainbow Mode"),
      RainbowizeWords(tr("A beautiful rainbow effect on the path the model wants to take.")) + "<br/><i>" + tr("It")+ " <b>" + tr("does not") + "</b> " + tr("affect driving in any way.") + "</i>",
      "",
      false,
    },
    {
      "StandstillTimer",
      tr("Enable Standstill Timer"),
      tr("Show a timer on the HUD when the car is at a standstill."),
      "",
      false,
    },
    {
      "RoadNameToggle",
      tr("Display Road Name"),
      tr("Displays the name of the road the car is traveling on. The OpenStreetMap database of the location must be downloaded from the OSM panel to fetch the road name."),
      "",
      false,
    },
    {
      "SteeringIconRotate",
      tr("Show Steering Wheel Rotation"),
      tr("Rotate the on-screen steering wheel icon to reflect the current steering wheel angle of the car"),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
    {
      "VisualWideCam",
      tr("Force Wide Cam"),
      tr("Forces the wide cam view regardless of experimental mode status."),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
    {
      "VisualFPS",
      tr("Show FPS Overlay"),
      tr("Display current and average FPS on screen for performance monitoring."),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
    {
      "VisualRadarTracks",
      tr("Show Radar Tracks"),
      tr("Shows what the cars radar sees."),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
    {
      "VisualStyleBlend",
      tr("Blend to Visual Style"),
      tr("Blend to view when using Minimal/Vision visual style."),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
    {
      "VisualStyleOverheadBlend",
      tr("Blend to Overhead Visual Style"),
      tr("Blend to Overhead view when using Minimal/Vision visual style."),
      "../assets/offroad/icon_monitoring.png",
      false,
    },
  };

  // Add regular toggles first
  for (auto &[param, title, desc, icon, needs_restart] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);

    if (needs_restart && !locked) {
      toggle->setDescription(toggle->getDescription() + tr(" Changing this setting will restart openpilot if the car is powered on."));

      QObject::connect(uiState(), &UIState::engagedChanged, [toggle](bool engaged) {
        toggle->setEnabled(!engaged);
      });

      QObject::connect(toggle, &ParamControlSP::toggleFlipped, [=](bool state) {
        params.putBool("OnroadCycleRequested", true);
      });
    }

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
    param_watcher->addParam(param);
  }

  // Visuals: Visual Style
  std::vector<QString> visual_style_settings_texts{tr("Default"), tr("Minimal"), tr("Vision"), tr("Overhead")};
  visual_style_settings = new ButtonParamControlSP(
    "VisualStyle", tr("Visual Style"), tr("Controls how the road and driving environment are displayed in the onroad UI."),
    "",
    visual_style_settings_texts,
    250);
  list->addItem(visual_style_settings);

  // Visuals: VisualStyleBlend Threshold
  visual_style_threshold_settings = new OptionControlSP("VisualStyleBlendThreshold", tr("Adjust Overhead Blend Threshold"),
                                      tr("Adjust the threshold when overhead blend activates."),
                                      "", {10, 80}, 5, false, nullptr, false);

  connect(visual_style_threshold_settings, &OptionControlSP::updateLabels, [=]() {
    int value = QString::fromStdString(params.get("VisualStyleBlendThreshold")).toInt();
    visual_style_threshold_settings->setLabel(QString::number(value) + " mph");
  });

  int value = QString::fromStdString(params.get("VisualStyleBlendThreshold")).toInt();
  visual_style_threshold_settings->setLabel(QString::number(value) + " mph");

  list->addItem(visual_style_threshold_settings);

  // Visuals: Radar Tracks Delay
  visual_radar_tracks_delay_settings = new OptionControlSP("VisualRadarTracksDelay", tr("Adjust Visual Radar Tracks Delay"),
                                      tr("Delays radar tracks to better match what you see through the camera."),
                                      "", {0, 100}, 10, false, nullptr, true);

  connect(visual_radar_tracks_delay_settings, &OptionControlSP::updateLabels, [=]() {
    float radar_tracks_delay_value = QString::fromStdString(params.get("VisualRadarTracksDelay")).toFloat();
    visual_radar_tracks_delay_settings->setLabel(QString::number(radar_tracks_delay_value, 'f', 1) + " s");
  });

  float radar_tracks_delay_value = QString::fromStdString(params.get("VisualRadarTracksDelay")).toFloat();
  visual_radar_tracks_delay_settings->setLabel(QString::number(radar_tracks_delay_value, 'f', 1) + " s");

  list->addItem(visual_radar_tracks_delay_settings);

  // Visuals: Display Metrics below Chevron
  std::vector<QString> chevron_info_settings_texts{tr("Off"), tr("Distance"), tr("Speed"), tr("Time"), tr("All")};
  chevron_info_settings = new ButtonParamControlSP(
    "ChevronInfo", tr("Display Metrics Below Chevron"), tr("Display useful metrics below the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control)."),
    "",
    chevron_info_settings_texts,
    200);
  chevron_info_settings->showDescription();
  list->addItem(chevron_info_settings);
  param_watcher->addParam("ChevronInfo");

  // Visuals: Developer UI Info (Dev UI)
  std::vector<QString> dev_ui_settings_texts{tr("Off"), tr("Right"), tr("Right &&\nBottom")};
  dev_ui_settings = new ButtonParamControlSP(
    "DevUIInfo", tr("Developer UI"), tr("Display real-time parameters and metrics from various sources."),
    "",
    dev_ui_settings_texts,
    380);
  list->addItem(dev_ui_settings);

  sunnypilotScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(sunnypilotScroller);

  main_layout->addWidget(sunnypilotScreen);
}

void VisualsPanel::paramsRefresh() {
  if (!isVisible()) {
    return;
  }

  for (auto toggle : toggles) {
    toggle.second->refresh();
  }

  if (chevron_info_settings) {
    chevron_info_settings->refresh();
  }
  if (dev_ui_settings) {
    dev_ui_settings->refresh();
  }
  if (visual_style_settings) {
    visual_style_settings->refresh();
  }
}
