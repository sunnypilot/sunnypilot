/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/tesla_settings.h"
#include "common/params.h"
#include "common/util.h"

TeslaSettings::TeslaSettings(QWidget *parent) : BrandSettingsInterface(parent) {
  constexpr int coopSteeringMinKmh = 23; // minimum speed for cooperative steering (enforced by Tesla firmware)
  Params params;
  bool is_metric = params.getBool("IsMetric");
  QString unit = is_metric ? "km/h" : "mph";
  int display_value;
  if (is_metric) {
    display_value = coopSteeringMinKmh;
  } else {
    display_value = static_cast<int>(std::round(coopSteeringMinKmh * KM_TO_MILE));
  }
  const QString coop_desc = tr("Allows the driver to provide limited steering input while openpilot is engaged. Only works above %1 %2.")
                                .arg(display_value)
                                .arg(unit);

  coopSteeringToggle = new ParamControlSP(
    "TeslaCoopSteering",
    tr("Cooperative Steering"),
    coop_desc,
    "",
    this
  );
  list->addItem(coopSteeringToggle);
  coopSteeringToggle->showDescription();
}

void TeslaSettings::updateSettings() {
}
