/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/tesla_settings.h"
#include "selfdrive/ui/ui.h" // for uiState() signal offroadTransition

TeslaSettings::TeslaSettings(QWidget *parent) : BrandSettingsInterface(parent) {
	coopSteeringToggle = new ParamControlSP(
		"TeslaCoopSteering",
		tr("Cooperative Steering"),
    // TODO:AMY USE USER METRICS AND GET CORRECT MAX VALUES
		tr("Allows the driver to provide steering input while openpilot is engaged. Only works between 15 and 60 mph."),
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
