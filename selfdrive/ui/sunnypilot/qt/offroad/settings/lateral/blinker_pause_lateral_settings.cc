/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */


#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/blinker_pause_lateral_settings.h"

BlinkerPauseLateralSpeed::BlinkerPauseLateralSpeed() : OptionControlSP(
  "BlinkerMinLateralControlSpeed",
  "",
  "",
  "",
  {0, 255}, 5) {

  refresh();
}

void BlinkerPauseLateralSpeed::refresh() {
  const QString option = QString::fromStdString(params.get("BlinkerMinLateralControlSpeed"));
  const bool is_metric = params.getBool("IsMetric");
  const QString unit = is_metric ? "km/h" : "mph";

  setLabel(option + " " + unit);
}
