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
      "HideVEgoUI",
      tr("Speedometer: Hide from Onroad Screen"),
      tr("When enabled, the speedometer on the onroad screen is not displayed."),
      "",
      false,
    },
    {
      "ShowTurnSignals",
      tr("Display Turn Signals"),
      tr("When enabled, visual turn indicators are drawn on the HUD."),
      "",
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

  QObject::connect(uiState(), &UIState::offroadTransition, this, &VisualsPanel::refreshLongitudinalStatus);

  refreshLongitudinalStatus();
}

void VisualsPanel::refreshLongitudinalStatus() {
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    has_longitudinal_control = hasLongitudinalControl(CP);
  } else {
    has_longitudinal_control = false;
  }

  if (chevron_info_settings) {
    QString chevronEnabledDescription = tr("Display useful metrics below the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control).");
    QString chevronNoLongDescription = tr("This feature requires openpilot longitudinal control to be available.");

    if (has_longitudinal_control) {
      chevron_info_settings->setDescription(chevronEnabledDescription);
    } else {
      // Reset to "Off" when longitudinal not available
      params.put("ChevronInfo", "0");
      chevron_info_settings->setDescription(chevronNoLongDescription);
    }

    // Enable only when longitudinal is available
    chevron_info_settings->setEnabled(has_longitudinal_control);
    chevron_info_settings->refresh();
  }
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
}
