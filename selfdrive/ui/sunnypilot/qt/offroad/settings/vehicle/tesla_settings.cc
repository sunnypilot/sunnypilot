/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/tesla_settings.h"

TeslaSettings::TeslaSettings(QWidget *parent) : BrandSettingsInterface(parent) {
	coopSteeringToggle = new ParamControlSP(
		"TeslaCoopSteering",
		tr("Cooperative Steering"),
    // TODO:AMY USE USER METRICS AND GET CORRECT MAX VALUES
		tr("Allows the driver to provide steering input while openpilot is engaged. Only works between 15 and 60mph"),
		"",
		this
	);
	list->addItem(coopSteeringToggle);
}

void TeslaSettings::updateSettings() {
}
