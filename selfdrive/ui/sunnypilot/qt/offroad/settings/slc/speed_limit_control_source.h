/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <qt5/QtWidgets/QWidget>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/slc/speed_limit_control.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class SpeedLimitControlSource : public QWidget {
  Q_OBJECT

public:
  explicit SpeedLimitControlSource(QWidget *parent = nullptr);
  void refresh();
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

private:
  Params params;
  ButtonParamControlSP *slc_policy;

  static QString sourceDescription(SLCSourcePolicy type = SLCSourcePolicy::CAR_ONLY) {
    QString car_only = tr("⦿ Car Only: ");
    QString map_only = tr("⦿ Map Only: ");
    QString car_first = tr("⦿ Car First: ");
    QString map_first = tr("⦿ Map First: ");
    QString combined = tr("⦿ Combined: ");

    if (type == SLCSourcePolicy::CAR_ONLY) {
      car_only = "<font color='white'><b>" + car_only + "</b></font>";
    } else if (type == SLCSourcePolicy::MAP_ONLY) {
      map_only = "<font color='white'><b>" + map_only + "</b></font>";
    } else if (type == SLCSourcePolicy::CAR_FIRST) {
      car_first = "<font color='white'><b>" + car_first + "</b></font>";
    } else if (type == SLCSourcePolicy::MAP_FIRST) {
      map_first = "<font color='white'><b>" + map_first + "</b></font>";
    } else {
      combined = "<font color='white'><b>" + combined + "</b></font>";
    }

    return QString("%1<br>%2<br>%3<br>%4<br>%5")
            .arg(car_only)
            .arg(map_only)
            .arg(car_first)
            .arg(map_first)
            .arg(combined);
  }
};
