
/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class DecControllerSubpanel : public QWidget {
  Q_OBJECT

public:
  explicit DecControllerSubpanel(QWidget *parent = nullptr);

protected:
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

private slots:
  void updateToggles();

private:
  void showAllDescriptions();
  Params params;

  ParamControlSP *standstillControl = nullptr;
  ParamControlSP *modelSlowDownControl = nullptr;
  ParamControlSP *fcwControl = nullptr;
  ParamControlSP *hasLeadControl = nullptr;
  ParamControlSP *slowerLeadControl = nullptr;
  ParamControlSP *stoppedLeadControl = nullptr;
  ParamControlSP *distanceBasedControl = nullptr;
  ParamControlSP *speedBasedControl = nullptr;
  ParamControlSP *slownessControl = nullptr;
  ParamControlSP *followLeadControl = nullptr;
  OptionControlSP *distanceValueControl = nullptr;
  OptionControlSP *speedValueControl = nullptr;
};
