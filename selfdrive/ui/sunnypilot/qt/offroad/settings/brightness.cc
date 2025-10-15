/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/brightness.h"

// Map of Brightness Options
const QMap<QString, QString> Brightness::brightness_options = {
  {"0", "1"},  // Auto (Dark)
  {"1", "0"},  // Auto
  {"2", "5"},
  {"3", "10"},
  {"4", "15"},
  {"5", "20"},
  {"6", "25"},
  {"7", "30"},
  {"8", "35"},
  {"9", "40"},
  {"10", "45"},
  {"11", "50"},
  {"12", "55"},
  {"13", "60"},
  {"14", "65"},
  {"15", "70"},
  {"16", "75"},
  {"17", "80"},
  {"18", "85"},
  {"19", "90"},
  {"20", "95"},
  {"21", "100"}
};

Brightness::Brightness() : OptionControlSP(
  "Brightness",
  tr("Global Brightness"),
  tr("Overrides the brightness of the device. This applies to both onroad and offroad screens. "),
  "../assets/offroad/icon_blank.png",
  {0, 21}, 1, true, &brightness_options) {

  refresh();
}

void Brightness::refresh() {
  const int brightness = QString::fromStdString(params.get("Brightness")).toInt();
  
  QString label;
  if (brightness == 1) {
    label = tr("Auto (Dark)");
  } else if (brightness == 0) {
    label = tr("Auto");
  } else {
    const int value = brightness;
    label = QString("%1").arg(value);
  }
  
  setLabel(label);
}
