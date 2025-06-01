/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/expandable_row.h"

enum class SLCEngageType {
  AUTO,
  USER_CONFIRM,
};

inline const char *SLCEngageTypeText[] {
  QT_TR_NOOP("Auto"),
  QT_TR_NOOP("User Confirm")
};

enum class SLCOffsetType {
  NONE,
  FIXED,
  PERCENT,
};

inline const char *SLCOffsetTypeText[] {
  QT_TR_NOOP("None"),
  QT_TR_NOOP("Fixed"),
  QT_TR_NOOP("Percent"),
};

enum class SLCWarningType {
  OFF,
  DISPLAY,
  CHIME,
};

inline const char *SLCWarningTypeText[] {
  QT_TR_NOOP("Off"),
  QT_TR_NOOP("Display"),
  QT_TR_NOOP("Chime")
};

enum class SLCSourcePolicy {
  CAR_ONLY,
  MAP_ONLY,
  CAR_FIRST,
  MAP_FIRST,
  COMBINED
};

inline const char *SLCSourcePolicyText[] {
  QT_TR_NOOP("Car\nOnly"),
  QT_TR_NOOP("Map\nOnly"),
  QT_TR_NOOP("Car\nFirst"),
  QT_TR_NOOP("Map\nFirst"),
  QT_TR_NOOP("Combined")
};

class SpeedLimitControl : public ExpandableToggleRow {
    Q_OBJECT

public:
  SpeedLimitControl(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);
  void refresh();
  void showEvent(QShowEvent *event) override;

signals:
  void slcWarningButtonClicked();
  void slcSourceButtonClicked();

private:
  Params params;
  PushButtonSP *slcWarningControl;
  PushButtonSP *slcSourceControl;
  ButtonParamControlSP *slc_offset_setting;
  OptionControlSP *slc_offset;
  ButtonParamControlSP *slc_engage_setting;

  static QString engageModeDescription(SLCEngageType type = SLCEngageType::AUTO) {
    QString auto_str = tr("⦿ Auto: Automatic speed adjustment based on speed limit data");
    QString user_str = tr("⦿ User Confirm: Asks driver to confirm speed adjustment based on speed limit data");

    if (type == SLCEngageType::USER_CONFIRM) {
      user_str = "<font color='white'><b>" + user_str + "</b></font>";
    } else {
      auto_str = "<font color='white'><b>" + auto_str + "</b></font>";
    }

    return QString("%1<br>%2")
             .arg(auto_str)
             .arg(user_str);
  }

  static QString offsetDescription(SLCOffsetType type = SLCOffsetType::NONE) {
    QString none_str = tr("⦿ None: No Offset");
    QString fixed_str = tr("⦿ Fixed: Adds a fixed offset [Speed Limit + Offset]");
    QString percent_str = tr("⦿ Percent: Adds a percent offset [Speed Limit + (Offset % Speed Limit)]");

    if (type == SLCOffsetType::FIXED) {
      fixed_str = "<font color='white'><b>" + fixed_str + "</b></font>";
    } else if (type == SLCOffsetType::PERCENT) {
      percent_str = "<font color='white'><b>" + percent_str + "</b></font>";
    } else {
      none_str = "<font color='white'><b>" + none_str + "</b></font>";
    }

    return QString("%1<br>%2<br>%3")
             .arg(none_str)
             .arg(fixed_str)
             .arg(percent_str);
  }
};
