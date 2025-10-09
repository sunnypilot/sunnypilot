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
    if (param_name == "VisualStyle") {
      visual_style_value = param_value.toInt();
    } else if (param_name == "VisualStyleOverhead") {
      visual_style_overhead_value = param_value.toInt();
    } else if (param_name == "VisualRadarTracks") {
      bool radar_tracks_enabled = param_value.toInt() != 0;
      visual_radar_tracks_delay_settings->setVisible(radar_tracks_enabled);
    }
    visual_style_zoom_settings->setVisible(visual_style_value != 0);
    visual_style_overhead_settings->setVisible(visual_style_value != 0);
    visual_style_overhead_zoom_settings->setVisible(visual_style_value != 0 && visual_style_overhead_value != 0);
    visual_style_overhead_threshold_settings->setVisible(visual_style_value != 0 && visual_style_overhead_value != 0);
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
      "GreenLightAlert",
      tr("Green Traffic Light Alert (Beta)"),
      QString("%1<br>"
        "<h4>%2</h4><br>")
        .arg(tr("A chime and on-screen alert will play when the traffic light you are waiting for turns green and you have no vehicle in front of you."))
        .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "",
      false,
    },
    {
      "LeadDepartAlert",
      tr("Lead Departure Alert (Beta)"),
      QString("%1<br>"
        "<h4>%2</h4><br>")
        .arg(tr("A chime and on-screen alert will play when you are stopped, and the vehicle in front of you start moving."))
        .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "",
      false,
    },
    {
      "TrueVEgoUI",
      tr("Speedometer: Always Display True Speed"),
      tr("Always display the true vehicle current speed from wheel speed sensors."),
      "",
      false,
    },
    {
      "VisualRadarTracks",
      tr("Show Radar Tracks"),
      tr("Shows what the cars radar sees."),
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

  // Wide Cam
  std::vector<QString> visual_wide_cam_settings_texts{tr("Auto"), tr("On"), tr("Off")};
  visual_wide_cam_settings = new ButtonParamControlSP(
    "VisualWideCam", tr("Wide Cam"), tr("Override the wide cam view regardless of experimental mode status."),
    "",
    visual_wide_cam_settings_texts,
    250);
  list->addItem(visual_wide_cam_settings);

  // Visual Style
  std::vector<QString> visual_style_settings_texts{tr("Default"), tr("Minimal"), tr("Vision")};
  visual_style_settings = new ButtonParamControlSP(
    "VisualStyle", tr("Visual Style"),
    tr(
      "Switch between different on-road visualization layouts."
      "<ul style='margin-left: 10px; margin-top: 4px;'>"
      "<li><b>Default:</b> Standard OpenPilot layout with camera and path view.</li>"
      "<li><b>Minimal:</b> Clean interface without camera feed or extra elements.</li>"
      "<li><b>Vision:</b> Experimental layout that focuses on model perception and environment.</li>"
      "</ul>"
    ),
    "",
    visual_style_settings_texts,
    380);
  list->addItem(visual_style_settings);

  // Visual Style Zoom
  std::vector<QString> visual_style_zoom_settings_texts{tr("Disabled"), tr("Enabled"), tr("Inverted")};
  visual_style_zoom_settings = new ButtonParamControlSP(
    "VisualStyleZoom", tr("Visual Style Zoom"),
    tr(
      "Enables dynamic zooming based on driving speed in the selected visual style."
      "<ul style='margin-left: 10px; margin-top: 4px;'>"
      "<li><b>Disabled:</b> Keeps the zoom fixed.</li>"
      "<li><b>Enabled:</b> Zooms in at low speed and out at high speed.</li>"
      "<li><b>Inverted:</b> Reverses the zoom behavior.</li>"
      "</ul>"
    ),
    "",
    visual_style_zoom_settings_texts,
    380);
  list->addItem(visual_style_zoom_settings);

  // Visual Style Overhead
  std::vector<QString> visual_style_overhead_settings_texts{tr("Disabled"), tr("Enabled"), tr("Inverted")};
  visual_style_overhead_settings = new ButtonParamControlSP(
    "VisualStyleOverhead", tr("Visual Style Overhead"),
    tr(
      "Toggles an overhead (top-down) camera view for a 2D-style perspective."
      "<ul style='margin-left: 10px; margin-top: 4px;'>"
      "<li><b>Disabled:</b> Keeps the standard forward 3D view.</li>"
      "<li><b>Enabled:</b> Switches to overhead view when active.</li>"
      "<li><b>Inverted:</b> Reverses when the transition happens.</li>"
      "</ul>"
    ),
    "",
    visual_style_overhead_settings_texts,
    380);
  list->addItem(visual_style_overhead_settings);

  // Visual Style Overhead Zoom
  std::vector<QString> visual_style_overhead_zoom_settings_texts{tr("Disabled"), tr("Enabled"), tr("Inverted")};
  visual_style_overhead_zoom_settings = new ButtonParamControlSP(
    "VisualStyleOverheadZoom", tr("Visual Style Overhead Zoom"),
    tr(
      "Controls zooming behavior while in overhead mode."
      "<ul style='margin-left: 10px; margin-top: 4px;'>"
      "<li><b>Disabled:</b> Keeps a fixed zoom level in overhead mode.</li>"
      "<li><b>Enabled:</b> Zooms dynamically based on speed while overhead.</li>"
      "<li><b>Inverted:</b> Opposite zoom direction.</li>"
      "</ul>"
    ),
    "",
    visual_style_overhead_zoom_settings_texts,
    380);
  list->addItem(visual_style_overhead_zoom_settings);

  // Visual Style Overhead Threshold
  visual_style_overhead_threshold_settings = new OptionControlSP(
    "VisualStyleOverheadThreshold", tr("Visual Style Overhead Threshold"),
    tr("Sets the speed (in mph) where the display transitions between normal and overhead view."),
    "", {10, 80}, 5, false, nullptr, false);

  connect(visual_style_overhead_threshold_settings, &OptionControlSP::updateLabels, [=]() {
    int value = QString::fromStdString(params.get("VisualStyleOverheadThreshold")).toInt();
    visual_style_overhead_threshold_settings->setLabel(QString::number(value) + " mph");
  });

  int value = QString::fromStdString(params.get("VisualStyleOverheadThreshold")).toInt();
  visual_style_overhead_threshold_settings->setLabel(QString::number(value) + " mph");

  list->addItem(visual_style_overhead_threshold_settings);

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

  bool radar_tracks_enabled = QString::fromStdString(params.get("VisualRadarTracks")).toInt() != 0;
  visual_radar_tracks_delay_settings->setVisible(radar_tracks_enabled);
  param_watcher->addParam("VisualRadarTracks");

  visual_style_value = QString::fromStdString(params.get("VisualStyle")).toInt();
  visual_style_overhead_value = QString::fromStdString(params.get("VisualStyleOverhead")).toInt();
  visual_style_zoom_settings->setVisible(visual_style_value != 0);
  visual_style_overhead_settings->setVisible(visual_style_value != 0);
  visual_style_overhead_zoom_settings->setVisible(visual_style_value != 0 && visual_style_overhead_value != 0);
  visual_style_overhead_threshold_settings->setVisible(visual_style_value != 0 && visual_style_overhead_value != 0);
  param_watcher->addParam("VisualStyle");
  param_watcher->addParam("VisualStyleOverhead");

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
  if (visual_wide_cam_settings) {
    visual_wide_cam_settings->refresh();
  }
  if (visual_style_settings) {
    visual_style_settings->refresh();
  }
  if (visual_style_zoom_settings) {
    visual_style_zoom_settings->refresh();
  }
  if (visual_style_overhead_settings) {
    visual_style_overhead_settings->refresh();
  }
  if (visual_style_overhead_zoom_settings) {
    visual_style_overhead_zoom_settings->refresh();
  }
}
