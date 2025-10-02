/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class LaneTurnDesireControl : public OptionControlSP {
  Q_OBJECT

public:
  LaneTurnDesireControl();

  void refresh();

private:
  Params params;
};

class LaneTurnSettings : public QWidget {
  Q_OBJECT

public:
  explicit LaneTurnSettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

private:
  void refreshLaneTurnValueControl();
  void updateValueControlVisibility();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  LaneTurnDesireControl *laneTurnDesireControl;
  OptionControlSP *laneTurnValueControl;
};
