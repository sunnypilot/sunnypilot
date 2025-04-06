/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/max_time_offroad.h"


MaxTimeOffroad::MaxTimeOffroad() : OptionControlSP(
  "MaxTimeOffroad",
  tr("Max Time Offroad"),
  tr("Device will automatically shutdown after set time once the engine is turned off."),
  "../assets/offroad/icon_blank.png",
  {0, 10}, 1, true) {

  refresh();
}

void MaxTimeOffroad::refresh() {
  /*
   * Map to define the available options for Max Time Offroad
   * For now, same values also need to be added in power_monitoring.py till we find a better way
   */
  static const QMap<QString, QString> offroadTimeOpts = {
    {"0", "0"},
    {"1", "300"},
    {"2", "600"},
    {"3", "900"},
    {"4", "1800"},
    {"5", "3600"},
    {"6", "7200"},
    {"7", "10800"},
    {"8", "18000"},
    {"9", "43200"},
    {"10", "86400"}
  };

  int intOpt = offroadTimeOpts.value(QString::fromStdString(params.get("MaxTimeOffroad"))).toInt();
  QString strLabel = intOpt==0 ? "Always On" : intOpt<3600 ? QString::number(intOpt/60) + " m" : QString::number(intOpt/3600) + " h";
  setLabel(strLabel);
}