/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/brightness.h"

// Map of Brightness Options
const QMap<QString, QString> Brightness::brightness_options = {
  {"0", "0"},  // Auto
  {"1", "1"},
  {"2", "5"},
  {"3", "10"},
  {"4", "20"},
  {"5", "30"},
  {"6", "40"},
  {"7", "50"},
  {"8", "60"},
  {"9", "70"},
  {"10", "80"},
  {"11", "90"},
  {"12", "100"}
};

Brightness::Brightness() : OptionControlSP(
  "Brightness",
  tr("Brightness"),
  tr("Overrides the brightness of the device."),
  "../assets/offroad/icon_blank.png",
  {0, 12}, 1, true, &brightness_options) {

  refresh();
}

void Brightness::refresh() {
  const int brightness = QString::fromStdString(params.get("Brightness")).toInt();
  
  QString label;
  if (brightness == 0) {
    label = tr("Auto");
  } else {
    const int value = brightness;
    label = QString("%1").arg(value);
  }
  
  setLabel(label);
}
