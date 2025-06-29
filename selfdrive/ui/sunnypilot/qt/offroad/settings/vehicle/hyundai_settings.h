/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/brand_settings_interface.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/hyundai_live_tuning.h"

#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/input.h"

enum class LongitudinalTuningOption {
  OFF,
  DYNAMIC,
  PREDICTIVE,
};

class HyundaiSettings : public BrandSettingsInterface {
  Q_OBJECT

public:
  explicit HyundaiSettings(QWidget *parent = nullptr);
  void updateSettings() override;

signals:
  void liveTuningOpened();
  void liveTuningClosed();

private:
  bool has_longitudinal_control = false;
  ButtonParamControlSP *longitudinalTuningToggle = nullptr;
  ParamControlSP *customTuningToggle = nullptr;
  HyundaiLiveTuning *liveTuningWidget = nullptr;
  QStackedLayout *main_layout = nullptr;
  QWidget *settingsScreen = nullptr;
  QWidget *customTuningButtonWidget = nullptr;

  static QString toggleDisableMsg(bool _offroad, bool _has_longitudinal_control) {
    if (!_has_longitudinal_control) {
      return tr("This feature can only be used with openpilot longitudinal control enabled.");
    }

    if (!_offroad) {
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to select all available options.");
    }

    return QString();
  }

  static QString customTuningWarningMsg() {
    return tr("Warning: Deviating from the preset tune can introduce undesirable behavior. Use at your own risk.");
  }

  static QString customTuningToggleDescription() {
    return tr("When enabled, custom values override the selected tuning mode. ") + customTuningWarningMsg();
  }

  static QString customTuningDisabledMsg() {
    return tr("Custom tuning is only available when longitudinal tuning is set to Dynamic or Predictive mode.");
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
};
