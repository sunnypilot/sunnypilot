/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/slc/speed_limit_control.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class SpeedLimitControlWarning : public QWidget {
  Q_OBJECT

public:
  SpeedLimitControlWarning(QWidget *parent = nullptr);

  void refresh();
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

private:
  Params params;

  ButtonParamControlSP *slc_warning_settings;
  ButtonParamControlSP *slc_warning_offset_settings;
  OptionControlSP *slc_warning_offset;

  static QString warningDescription(SLCWarningType type = SLCWarningType::OFF) {
    QString off_str = tr("⦿ Off: No Warning");
    QString display_str = tr("⦿ Display: Speed Limit Sign will visually alert");
    QString chime_str = tr("⦿ Chime: Speed Limit Sign will visually alert along with an audible chime");

    if (type == SLCWarningType::DISPLAY) {
      display_str = "<font color='white'><b>" + display_str + "</b></font>";
    } else if (type == SLCWarningType::CHIME) {
      chime_str = "<font color='white'><b>" + chime_str + "</b></font>";
    } else {
      off_str = "<font color='white'><b>" + off_str + "</b></font>";
    }

    return QString("%1<br>%2<br>%3")
             .arg(off_str)
             .arg(display_str)
             .arg(chime_str);
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
