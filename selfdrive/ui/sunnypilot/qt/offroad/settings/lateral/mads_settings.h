/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

enum class MadsSteeringMode {
  REMAIN_ACTIVE,
  PAUSE_STEERING,
  DISENGAGE,
};

class MadsSettings : public QWidget {
  Q_OBJECT

public:
  explicit MadsSettings(QWidget *parent = nullptr);

  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

public slots:
  void updateToggles(bool _offroad);

private:
  Params params;
  bool offroad;

  ParamControl *madsMainCruiseToggle;
  ParamControl *madsUnifiedEngagementModeToggle;
  ButtonParamControl *madsSteeringMode;

  static QString madsSteeringModeDescription(MadsSteeringMode mode) {
    QString remain_active_str = tr("Remain Active: ALC will remain active when the brake pedal is pressed.");
    QString pause_steering_str = tr("Pause Steering: ALC will pause steering when the brake pedal is pressed.");
    QString disengage_str = tr("Disengage: ALC will disengage when the brake pedal is pressed.");

    if (mode == MadsSteeringMode::REMAIN_ACTIVE) {
      remain_active_str = "<font color='white'><b>" + remain_active_str + "</b></font>";
    } else if (mode == MadsSteeringMode::PAUSE_STEERING) {
      pause_steering_str = "<font color='white'><b>" + pause_steering_str + "</b></font>";
    } else if (mode == MadsSteeringMode::DISENGAGE) {
      disengage_str = "<font color='white'><b>" + disengage_str + "</b></font>";
    }

    return QString("%1<br><br>%2<br>%3<br>%4")
             .arg(tr("Choose how Automatic Lane Centering (ALC) behaves after the brake pedal is manually pressed in sunnypilot."))
             .arg(remain_active_str)
             .arg(pause_steering_str)
             .arg(disengage_str);
  }
};
