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

enum class LongitudinalTuningOption {
  OFF,
  DYNAMIC,
  PREDICTIVE,
};

enum class RadarOption {
  OFF,
  LEAD_ONLY,
  FULL_RADAR,
};

class HyundaiSettings : public BrandSettingsInterface {
  Q_OBJECT

public:
  explicit HyundaiSettings(QWidget *parent = nullptr);
  void updateSettings() override;

private:
  bool has_longitudinal_control = false;
  ButtonParamControl *longitudinalTuningToggle = nullptr;
  ButtonParamControl *radarToggle = nullptr;

  static QString toggleDisableMsg(bool _offroad, bool _has_longitudinal_control) {
    if (!_has_longitudinal_control) {
      return tr("This feature can only be used with openpilot longitudinal control enabled.");
    }

    if (!_offroad) {
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to select an option.");
    }

    return QString();
  }

  static QString longitudinalTuningDescription(LongitudinalTuningOption option = LongitudinalTuningOption::OFF) {
    QString off_str = tr("Off: Uses default tuning");
    QString dynamic_str = tr("Dynamic: Adjusts acceleration limits based on current speed");
    QString predictive_str = tr("Predictive: Uses future trajectory data to anticipate needed adjustments");

    if (option == LongitudinalTuningOption::PREDICTIVE) {
      predictive_str = "<font color='white'><b>" + predictive_str + "</b></font>";
    } else if (option == LongitudinalTuningOption::DYNAMIC) {
      dynamic_str = "<font color='white'><b>" + dynamic_str + "</b></font>";
    } else {
      off_str = "<font color='white'><b>" + off_str + "</b></font>";
    }

    return QString("%1<br><br>%2<br>%3<br>%4<br>")
             .arg(tr("Fine-tune your driving experience by adjusting acceleration smoothness with openpilot longitudinal control."))
             .arg(off_str)
             .arg(dynamic_str)
             .arg(predictive_str);
  }

  static QString radarDescription(RadarOption option = RadarOption::OFF) {
    QString off_str = tr("Off: Disables radar tracking. Vision-only vehicle detection.");
    QString lead_only_str = tr("Lead Only: Tracks only the closest vehicle ahead.");
    QString full_radar_str = tr("Full Radar: Tracks all nearby vehicles using radar.");

    if (option == RadarOption::LEAD_ONLY) {
      lead_only_str = "<font color='white'><b>" + lead_only_str + "</b></font>";
    } else if (option == RadarOption::FULL_RADAR) {
      full_radar_str = "<font color='white'><b>" + full_radar_str + "</b></font>";
    } else {
      off_str = "<font color='white'><b>" + off_str + "</b></font>";
    }

    return QString("%1<br><br>%2<br>%3<br>%4<br>")
             .arg(tr("Configure how radar tracks surrounding vehicles — turn it off, track only the lead, or track all."))
             .arg(off_str)
             .arg(lead_only_str)
             .arg(full_radar_str);
  }
};
