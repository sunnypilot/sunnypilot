/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display/onroad_screen_brightness.h"

OnroadScreenBrightnessControl::OnroadScreenBrightnessControl(const QString &param, const QString &title,
                                                             const QString &description, const QString &icon,
                                                             QWidget *parent)
  : ExpandableToggleRow(param, title, description, icon, parent) {
  auto *mainFrame = new QFrame(this);
  auto *mainFrameLayout = new QVBoxLayout();
  mainFrame->setLayout(mainFrameLayout);
  mainFrameLayout->setSpacing(30);
  mainFrameLayout->setContentsMargins(0, 0, 0, 0);

  onroadScreenOffTimer = new OptionControlSP(
    "OnroadScreenOffTimer",
    "Onroad Brightness Delay",
    "",
    "",
    {0, 11}, 1, true, &onroadScreenOffTimerOptions);

  onroadScreenBrightness = new OptionControlSP(
    "OnroadScreenOffBrightness",
    "Onroad Brightness",
    "",
    "",
    {0, 90}, 10, true);

  connect(onroadScreenOffTimer, &OptionControlSP::updateLabels, this, &OnroadScreenBrightnessControl::refresh);
  connect(onroadScreenBrightness, &OptionControlSP::updateLabels, this, &OnroadScreenBrightnessControl::refresh);
  mainFrameLayout->addWidget(onroadScreenBrightness);
  mainFrameLayout->addWidget(onroadScreenOffTimer);

  addItem(mainFrame);

  refresh();
}

void OnroadScreenBrightnessControl::refresh() {
  // Driving Screen Off Timer
  int valTimer = std::atoi(params.get("OnroadScreenOffTimer").c_str());
  std::string labelTimer = (valTimer < 60 ? std::to_string(valTimer) + "s" : std::to_string(valTimer / 60) + "m");
  onroadScreenOffTimer->setLabel(QString::fromStdString(labelTimer));

  // Driving Screen Off Brightness
  std::string valBrightness = params.get("OnroadScreenOffBrightness");
  std::string labelBrightness = (valBrightness == "0" ? " Screen Off" : valBrightness + "%");
  onroadScreenBrightness->setLabel(QString::fromStdString(labelBrightness));
}
