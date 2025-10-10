/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/brightness.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display/onroad_screen_brightness.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class DisplayPanel : public QWidget {
  Q_OBJECT

public:
  explicit DisplayPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void refresh();

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* sunnypilotScreen = nullptr;
  ScrollViewSP *sunnypilotScroller = nullptr;
  Params params;
  OnroadScreenBrightnessControl *onroadScreenBrightnessControl = nullptr;
  Brightness *brightness;
  OptionControlSP *interactivityTimeout;
};
