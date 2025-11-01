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
  constexpr int oemSteeringMinKmh = 48; // minimum speed for OEM lane departure avoidance (enforced by Tesla firmware)
  bool is_metric = params.getBool("IsMetric");
  QString unit = is_metric ? "km/h" : "mph";
  int display_value_coop;
  int display_value_oem;
  if (is_metric) {
    display_value_coop = coopSteeringMinKmh;
    display_value_oem = oemSteeringMinKmh;
  } else {
    display_value_coop = static_cast<int>(std::round(coopSteeringMinKmh * KM_TO_MILE));
    display_value_oem = static_cast<int>(std::round(oemSteeringMinKmh * KM_TO_MILE));
  }
  const QString coop_desc = tr("Allows the driver to provide limited steering input while openpilot is engaged.\n\nOnly works above %1 %3.\n\nWarning: May experience steering oscillations below %2 %3 during turns, recommend disabling if you experience these.")
                                .arg(display_value_coop)
                                .arg(display_value_oem)
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
  coopSteeringToggle->setConfirmation(true, false);
}

void TeslaSettings::updateSettings() {
  coopSteeringToggle->setEnabled(offroad);
}
