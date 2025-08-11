/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class LagdToggleSettings : public QWidget {
  Q_OBJECT
public:
  explicit LagdToggleSettings(QWidget *parent = nullptr);
  void refresh();

signals:
  void backPress();

private:
  Params params;
  ParamControlSP *lagd_toggle_control = nullptr;
  OptionControlSP *delay_control = nullptr;
};
