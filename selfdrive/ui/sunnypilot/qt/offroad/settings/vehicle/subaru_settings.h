/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/brand_settings_interface.h"

#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

const int SUBARU_FLAG_GLOBAL_GEN2 = 4;
const int SUBARU_FLAG_HYBRID = 32;

class SubaruSettings : public BrandSettingsInterface {
  Q_OBJECT

public:
  explicit SubaruSettings(QWidget *parent = nullptr);
  void updateSettings() override;

private:
  bool offroad = false;
  bool is_subaru;
  bool has_stop_and_go;

  ParamControl* stopAndGoToggle;
  ParamControl* stopAndGoManualParkingBrakeToggle;

  QString stopAndGoDesc = tr("Experimental feature to enable auto-resume during stop-and-go for certain supported Subaru platforms.");
  QString stopAndGoManualParkingBrakeDesc = tr("Experimental feature to enable stop and go for Subaru Global models with manual handbrake. Models with electric parking brake should keep this disabled. Thanks to martinl for this implementation!");

  QString stopAndGoDisabledMsg() const {
    if (is_subaru && !has_stop_and_go) {
      return tr("This feature is currently not available on this platform.");
    }

    if (!is_subaru) {
      return tr("Start the car to check car compatibility.");
    }

    if (!offroad) {
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to toggle.");
    }

    return QString();
  }

  static QString stopAndGoDescriptionBuilder(const QString &base_description, const QString &custom_description = "") {
    return "<b>" + custom_description + "</b><br><br>" + base_description;
  }
};
