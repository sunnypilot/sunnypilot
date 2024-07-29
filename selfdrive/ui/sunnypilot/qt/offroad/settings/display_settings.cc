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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display_settings.h"

#include <tuple>
#include <vector>

DisplayPanel::DisplayPanel(QWidget *parent) : ListWidgetSP(parent, false) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "OnroadScreenOffEvent",
      tr("Driving Screen Off: Non-Critical Events"),
      QString("%1<br>"
              "<h4>%2</h4><br>"
              "<h4>%3</h4><br>")
      .arg(tr("When <b>Driving Screen Off Timer</b> is not set to <b>\"Always On\"</b>:"))
      .arg(tr("Enabled: Wake the brightness of the screen to display all events."))
      .arg(tr("Disabled: Wake the brightness of the screen to display critical events.")),
      "../assets/offroad/icon_blank.png",
    }
  };

  // General: Max Time Offroad (Shutdown timer)
  auto max_time_offroad = new MaxTimeOffroad();
  connect(max_time_offroad, &OptionControlSP::updateLabels, max_time_offroad, &MaxTimeOffroad::refresh);
  addItem(max_time_offroad);

  // General: Onroad Screen Off (Auto Onroad Screen Timer)
  onroad_screen_off = new OnroadScreenOff();
  onroad_screen_off->setUpdateOtherToggles(true);
  connect(onroad_screen_off, &OptionControlSP::updateLabels, onroad_screen_off, &OnroadScreenOff::refresh);
  connect(onroad_screen_off, &OptionControlSP::updateOtherToggles, this, &DisplayPanel::updateToggles);
  addItem(onroad_screen_off);

  // General: Onroad Screen Off Brightness
  onroad_screen_off_brightness = new OnroadScreenOffBrightness();
  connect(onroad_screen_off_brightness, &OptionControlSP::updateLabels, onroad_screen_off_brightness, &OnroadScreenOffBrightness::refresh);
  addItem(onroad_screen_off_brightness);

  // General: Brightness Control (Global)
  auto brightness_control = new BrightnessControl();
  connect(brightness_control, &OptionControlSP::updateLabels, brightness_control, &BrightnessControl::refresh);

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "OnroadScreenOffEvent") {
      // General: Brightness Control (Global)
      addItem(brightness_control);
    }
  }
}

void DisplayPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void DisplayPanel::updateToggles() {
  if (!isVisible()) {
    return;
  }

  // toggle names to update when OnroadScreenOff is toggled
  onroad_screen_off_brightness->setVisible(QString::fromStdString(params.get("OnroadScreenOff")) != "-2");
  toggles["OnroadScreenOffEvent"]->setVisible(QString::fromStdString(params.get("OnroadScreenOff")) != "-2");
}

// Max Time Offroad (Shutdown timer)
MaxTimeOffroad::MaxTimeOffroad() : OptionControlSP(
  "MaxTimeOffroad",
  tr("Max Time Offroad"),
  tr("Device is automatically turned off after a set time when the engine is turned off (off-road) after driving (on-road)."),
  "../assets/offroad/icon_blank.png",
  {0, 12}) {

  refresh();
}

void MaxTimeOffroad::refresh() {
  QString option = QString::fromStdString(params.get("MaxTimeOffroad"));
  QString second = tr("s");
  QString minute = tr("m");
  QString hour = tr("hr");
  if (option == "0") {
    setLabel(tr("Always On"));
  } else if (option == "1") {
    setLabel(tr("Immediate"));
  } else if (option == "2") {
    setLabel("30 " + second);
  } else if (option == "3") {
    setLabel("1 " + minute);
  } else if (option == "4") {
    setLabel("3 " + minute);
  } else if (option == "5") {
    setLabel("5 " + minute);
  } else if (option == "6") {
    setLabel("10 " + minute);
  } else if (option == "7") {
    setLabel("30 " + minute);
  } else if (option == "8") {
    setLabel("1 " + hour);
  } else if (option == "9") {
    setLabel("3 " + hour);
  } else if (option == "10") {
    setLabel("5 " + hour);
  } else if (option == "11") {
    setLabel("10 " + hour);
  } else if (option == "12") {
    setLabel("30 " + hour);
  }
}

// Onroad Screen Off (Auto Onroad Screen Timer)
OnroadScreenOff::OnroadScreenOff() : OptionControlSP(
  "OnroadScreenOff",
  tr("Driving Screen Off Timer"),
  tr("Turn off the device screen or reduce brightness to protect the screen after driving starts. It automatically brightens or turns on when a touch or event occurs."),
  "../assets/offroad/icon_blank.png",
  {-2, 10}) {

  refresh();
}

void OnroadScreenOff::refresh() {
  QString option = QString::fromStdString(params.get("OnroadScreenOff"));
  QString second = tr("s");
  QString minute = tr("min");
  if (option == "-2") {
    setLabel(tr("Always On"));
  } else if (option == "-1") {
    setLabel("15 " + second);
  } else if (option == "0") {
    setLabel("30 " + second);
  } else {
    setLabel(option + " " + minute);
  }
}

// Onroad Screen Off Brightness
OnroadScreenOffBrightness::OnroadScreenOffBrightness() : OptionControlSP(
  "OnroadScreenOffBrightness",
  tr("Driving Screen Off Brightness (%)"),
  tr("When using the Driving Screen Off feature, the brightness is reduced according to the automatic brightness ratio."),
  "../assets/offroad/icon_blank.png",
  {0, 100},
  10) {

  refresh();
}

void OnroadScreenOffBrightness::refresh() {
  QString option = QString::fromStdString(params.get("OnroadScreenOffBrightness"));
  if (option == "0") {
    setLabel(tr("Dark"));
  } else {
    setLabel(option);
  }
}

// Brightness Control (Global)
BrightnessControl::BrightnessControl() : OptionControlSP(
  "BrightnessControl",
  tr("Brightness"),
  tr("Manually adjusts the global brightness of the screen."),
  "../assets/offroad/icon_blank.png",
  {0, 100},
  5) {

  refresh();
}

void BrightnessControl::refresh() {
  QString option = QString::fromStdString(params.get("BrightnessControl"));
  QString percentage = " %";
  if (option == "0") {
    setLabel(tr("Auto"));
  } else {
    setLabel(option + percentage);
  }
}
