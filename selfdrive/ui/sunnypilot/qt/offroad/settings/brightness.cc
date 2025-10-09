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
  {"2", "10"},
  {"3", "20"},
  {"4", "30"},
  {"5", "40"},
  {"6", "50"},
  {"7", "60"},
  {"8", "70"},
  {"9", "80"},
  {"10", "90"},
  {"11", "100"}
};

Brightness::Brightness() : OptionControlSP(
  "Brightness",
  tr("Global Brightness"),
  tr("Overrides the brightness of the device. This applies to both onroad and offroad screens. "),
  "../assets/offroad/icon_blank.png",
  {0, 11}, 1, true, &brightness_options) {

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
