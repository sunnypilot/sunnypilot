/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/lagd_toggle_settings.h"

LagdToggleSettings::LagdToggleSettings(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);

  // Back button
  PanelBackButton *back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  // lagd toggle
  lagd_toggle_control = new ParamControlSP("LagdToggle", tr("Live Learning Steer Delay"), "", "../assets/offroad/icon_shell.png");
  lagd_toggle_control->showDescription();
  main_layout->addWidget(lagd_toggle_control);

  int liveDelayMaxInt = 30;
  std::string liveDelayBytes = params.get("LiveDelay");
  if (!liveDelayBytes.empty()) {
    capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
      reinterpret_cast<const capnp::word*>(liveDelayBytes.data()),
      liveDelayBytes.size() / sizeof(capnp::word)));
    auto event = msg.getRoot<cereal::Event>();
    if (event.hasLiveDelay()) {
      auto liveDelay = event.getLiveDelay();
      float lateralDelay = liveDelay.getLateralDelay();
      liveDelayMaxInt = static_cast<int>(lateralDelay * 100.0f) + 20;
    }
  }
  // optioncontrol for lagd 'off' state
  delay_control = new OptionControlSP("LagdToggleDelay", tr("Adjust Software Delay"),
                                     tr("The default software delay value is 0.2"),
                                     "", {5, liveDelayMaxInt}, 1, false, nullptr, true, true);

  connect(delay_control, &OptionControlSP::updateLabels, [=]() {
    float value = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
    delay_control->setLabel(QString::number(value, 'f', 2) + "s");
  });
  connect(lagd_toggle_control, &ParamControlSP::toggleFlipped, [=](bool state) {
    delay_control->setVisible(!state);
  });
  delay_control->showDescription();
  main_layout->addWidget(delay_control);
}

void LagdToggleSettings::refresh() {
  // Update toggle descriptions
  QString desc = tr("Enable this for the car to learn and adapt its steering response time. "
                   "Disable to use a fixed steering response time. Keeping this on provides the stock openpilot experience.");
  bool lagdEnabled = params.getBool("LagdToggle");
  if (lagdEnabled) {
    std::string liveDelayBytes = params.get("LiveDelay");
    if (!liveDelayBytes.empty()) {
      capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
        reinterpret_cast<const capnp::word*>(liveDelayBytes.data()),
        liveDelayBytes.size() / sizeof(capnp::word)));
      auto event = msg.getRoot<cereal::Event>();
      if (event.hasLiveDelay()) {
        auto liveDelay = event.getLiveDelay();
        float lateralDelay = liveDelay.getLateralDelay();
        desc += QString("<br><br><b><span style=\"color:#e0e0e0\">%1</span></b> <span style=\"color:#e0e0e0\">%2 s</span>")
                .arg(tr("Live Steer Delay:")).arg(QString::number(lateralDelay, 'f', 2));
      }
    }
  } else {
    std::string carParamsBytes = params.get("CarParamsPersistent");
    if (!carParamsBytes.empty()) {
      capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
        reinterpret_cast<const capnp::word*>(carParamsBytes.data()),
        carParamsBytes.size() / sizeof(capnp::word)));
      auto carParams = msg.getRoot<cereal::CarParams>();
      float steerDelay = carParams.getSteerActuatorDelay();
      float softwareDelay = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
      float totalLag = steerDelay + softwareDelay;
      desc += QString("<br><br><span style=\"color:#e0e0e0\">"
                      "<b>%1</b> %2 s + <b>%3</b> %4 s = <b>%5</b> %6 s</span>")
           .arg(tr("Actuator Delay:"), QString::number(steerDelay, 'f', 2),
                tr("Software Delay:"), QString::number(softwareDelay, 'f', 2),
                tr("Total Delay:"), QString::number(totalLag, 'f', 2));
    }
  }
  lagd_toggle_control->setDescription(desc);
  lagd_toggle_control->showDescription();

  delay_control->setVisible(!params.getBool("LagdToggle"));
  if (delay_control->isVisible()) {
    float value = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
    delay_control->setLabel(QString::number(value, 'f', 2) + "s");
    delay_control->showDescription();
  }
}
