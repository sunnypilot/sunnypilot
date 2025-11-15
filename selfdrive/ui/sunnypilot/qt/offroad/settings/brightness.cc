/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/brightness.h"

Brightness::Brightness() : OptionControlSP(
  "Brightness",
  tr("Global Brightness"),
  tr("Overrides the brightness of the device. This applies to both onroad and offroad screens. "),
  "../assets/offroad/icon_blank.png",
  {-5, 100}, 5, true) {

  refresh();
}

void Brightness::refresh() {
  const int brightness = QString::fromStdString(params.get("Brightness")).toInt();
  
  QString label;
  if (brightness == 0) {
    label = tr("Auto");
  } else if (brightness < 5) {
    label = tr("Auto (Dark)");
  } else {
    const int value = brightness;
    label = QString("%1").arg(value);
  }
  
  setLabel(label);
}
