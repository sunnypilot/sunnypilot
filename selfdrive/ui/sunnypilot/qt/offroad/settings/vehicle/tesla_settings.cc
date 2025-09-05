/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/tesla_settings.h"
#include "selfdrive/ui/ui.h" // for uiState() signal offroadTransition
#include "common/params.h"
#include "common/util.h"

TeslaSettings::TeslaSettings(QWidget *parent) : BrandSettingsInterface(parent) {
	constexpr int coopSteeringMinMph = 15; // minimum speed for cooperative steering (enforced by Tesla firmware)
	Params params;
	bool is_metric = params.getBool("IsMetric");
  QString unit = is_metric ? "km/h" : "mph";
  float display_value = stored_mph;
  if (is_metric) {
    display_value = stored_mph * MILE_TO_KM;
  }
	const QString coop_desc = tr("Allows the driver to provide limited steering input while openpilot is engaged. Only works above %1 %2.")
																.arg(threshold_display)
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

	QObject::connect(uiState(), &UIState::offroadTransition, this, &TeslaSettings::offroadTransition);
	offroadTransition(!uiState()->scene.started);
}

void TeslaSettings::updateSettings() {
}

void TeslaSettings::offroadTransition(bool offroad) {
	coopSteeringToggle->setEnabled(offroad);
}
