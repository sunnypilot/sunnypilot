/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/custom_acc_increment.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/dab_settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class LongitudinalPanel : public QWidget {
  Q_OBJECT

public:
  explicit LongitudinalPanel(QWidget *parent = nullptr);

private:
  QStackedLayout *main_layout = nullptr;
  QWidget *mainScreen = nullptr;
  ScrollViewSP *mainScroller = nullptr;
  CustomAccIncrement *customAccIncrement = nullptr;
  ParamControl *dabToggle = nullptr;
  PushButtonSP *dabSettingsButton = nullptr;
  DabSettings *dabWidget = nullptr;
  ListWidgetSP *listWidget = nullptr;
};
