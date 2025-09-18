/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_policy.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class SpeedLimitSettings : public QStackedWidget {
  Q_OBJECT

public:
  SpeedLimitSettings(QWidget *parent = nullptr);
  void refresh();
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

private:
  Params params;
  QFrame *subPanelFrame;
  PushButtonSP *speedLimitSource;
  SpeedLimitPolicy *speedLimitPolicyScreen;
};
