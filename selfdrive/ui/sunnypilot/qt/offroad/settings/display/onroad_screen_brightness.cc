/*
 *
  * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
  *
  * This file is part of sunnypilot and is licensed under the MIT License.
  * See the LICENSE.md file in the root directory for more details.

 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display/onroad_screen_brightness.h"

OnroadScreenBrightnessControl::OnroadScreenBrightnessControl(const QString &param, const QString &title, const QString &description, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, description, icon, parent) {

 auto *mainFrame = new QFrame(this);
 auto *mainFrameLayout = new QGridLayout();
 mainFrame->setLayout(mainFrameLayout);
 mainFrameLayout->setSpacing(0);

 onroadScreenOffTimer = new  OptionControlSP(
  "OnroadScreenOffTimer",
  "",
  "",
  "",
  {0, 11}, 1, true, &onroadScreenOffTimerOptions);

 onroadScreenBrightness = new  OptionControlSP(
 "OnroadScreenOffBrightness",
 "",
 "",
 "",
 {0, 100}, 10, true, nullptr, false);

 connect(onroadScreenOffTimer, &OptionControlSP::updateLabels, this, &OnroadScreenBrightnessControl::refresh);
 connect(onroadScreenBrightness, &OptionControlSP::updateLabels, this, &OnroadScreenBrightnessControl::refresh);
 onroadScreenOffTimer->setFixedWidth(280);
 onroadScreenBrightness->setFixedWidth(280);
 mainFrameLayout->addWidget(onroadScreenOffTimer, 0, 0, Qt::AlignLeft);
 mainFrameLayout->addWidget(onroadScreenBrightness, 0, 1, Qt::AlignRight);

 addItem(mainFrame);

 refresh();
}

void OnroadScreenBrightnessControl::refresh() {
 // Driving Screen Off Timer
 int valTimer = std::atoi(params.get("OnroadScreenOffTimer").c_str());
 std::string labelTimer = "<span style='font-size: 45px; font-weight: 450; color: #FFFFFF;'>";
 labelTimer += "Delay";
 labelTimer += " <br><span style='font-size: 40px; font-weight: 450; color:rgb(174, 255, 195);'>";
 labelTimer += (valTimer < 60 ? std::to_string(valTimer) + "s" : std::to_string(valTimer / 60) + "m");
 labelTimer += "</span></span>";
 onroadScreenOffTimer->setLabel(QString::fromStdString(labelTimer));

 // Driving Screen Off Brightness
 std::string valBrightness = params.get("OnroadScreenOffBrightness");
 std::string labelBrightness = "<span style='font-size: 45px; font-weight: 450; color: #FFFFFF;'>";
 labelBrightness += "Brightness";
 labelBrightness += " <br><span style='font-size: 40px; font-weight: 450; color:rgb(174, 255, 195);'>";
 labelBrightness += (valBrightness == "0" ? " Screen Off" : valBrightness + "%");
 labelBrightness += "</span></span>";
 onroadScreenBrightness->setLabel(QString::fromStdString(labelBrightness));
}