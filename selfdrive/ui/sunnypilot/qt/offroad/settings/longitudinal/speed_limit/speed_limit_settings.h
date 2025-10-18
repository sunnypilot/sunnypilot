/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/helpers.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_policy.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class SpeedLimitSettings : public QStackedWidget {
  Q_OBJECT

public:
  SpeedLimitSettings(QWidget *parent = nullptr);
  void refresh();
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

signals:
  void backPress();

private:
  Params params;
  ScrollViewSP *speedLimitScroller;
  QFrame *subPanelFrame;
  ButtonParamControlSP *speed_limit_mode_settings;
  PushButtonSP *speedLimitSource;
  SpeedLimitPolicy *speedLimitPolicyScreen;
  ButtonParamControlSP *speed_limit_offset_settings;
  OptionControlSP *speed_limit_offset;
  bool icbm_available = false;

  static QString offsetDescription(SpeedLimitOffsetType type = SpeedLimitOffsetType::NONE) {
    QString none_str = tr("⦿ None: No Offset");
    QString fixed_str = tr("⦿ Fixed: Adds a fixed offset [Speed Limit + Offset]");
    QString percent_str = tr("⦿ Percent: Adds a percent offset [Speed Limit + (Offset % Speed Limit)]");

    if (type == SpeedLimitOffsetType::FIXED) {
      fixed_str = "<font color='white'><b>" + fixed_str + "</b></font>";
    } else if (type == SpeedLimitOffsetType::PERCENT) {
      percent_str = "<font color='white'><b>" + percent_str + "</b></font>";
    } else {
      none_str = "<font color='white'><b>" + none_str + "</b></font>";
    }

    return QString("%1<br>%2<br>%3")
        .arg(none_str)
        .arg(fixed_str)
        .arg(percent_str);
  }

  static QString modeDescription(SpeedLimitMode mode = SpeedLimitMode::OFF) {
    QString off_str = tr("⦿ Off: Disables the Speed Limit functions.");
    QString info_str = tr("⦿ Information: Displays the current road's speed limit.");
    QString warning_str = tr("⦿ Warning: Provides a warning when exceeding the current road's speed limit.");
    QString assist_str = tr("⦿ Assist: Adjusts the vehicle's cruise speed based on the current road's speed limit when operating the +/- buttons.");

    if (mode == SpeedLimitMode::ASSIST) {
      assist_str = "<font color='white'><b>" + assist_str + "</b></font>";
    } else if (mode == SpeedLimitMode::WARNING) {
      warning_str = "<font color='white'><b>" + warning_str + "</b></font>";
    } else if (mode == SpeedLimitMode::INFORMATION) {
      info_str = "<font color='white'><b>" + info_str + "</b></font>";
    } else {
      off_str = "<font color='white'><b>" + off_str + "</b></font>";
    }

    return QString("%1<br>%2<br>%3<br>%4")
        .arg(off_str)
        .arg(info_str)
        .arg(warning_str)
        .arg(assist_str);
  }

  static std::vector<SpeedLimitMode> getSpeedLimitModeValues() {
    std::vector<SpeedLimitMode> values;
    for (int i = static_cast<int>(SpeedLimitMode::OFF);
         i <= static_cast<int>(SpeedLimitMode::ASSIST); ++i) {
      values.push_back(static_cast<SpeedLimitMode>(i));
    }
    return values;
  }

  static std::vector<int> convertSpeedLimitModeValues(const std::vector<SpeedLimitMode> &modes) {
    std::vector<int> values;
    for (const auto& mode : modes) {
      values.push_back(static_cast<int>(mode));
    }
    return values;
  }
};
