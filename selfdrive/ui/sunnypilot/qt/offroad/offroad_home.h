/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/offroad/offroad_home.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/exit_offroad_button.h"

class OffroadHomeSP : public OffroadHome {
  Q_OBJECT

public:
  explicit OffroadHomeSP(QWidget *parent = 0);

private:
  ExitOffroadButton *btn_exit_offroad;
  QPushButton *offroad_notif;
  Params params;

  void showEvent(QShowEvent *event) override;
  void refreshOffroadStatus();
};
