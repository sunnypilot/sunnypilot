/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#pragma once

#include <map>
#include <string>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class AutoLaneChangeTimer : public OptionControlSP {
  Q_OBJECT

public:
  AutoLaneChangeTimer();

  void refresh();

signals:
  void toggleUpdated();

private:
  Params params;
};

class PauseLateralSpeed : public OptionControlSP {
  Q_OBJECT

public:
  PauseLateralSpeed();

  void refresh();

  signals:
    void ToggleUpdated();

private:
  Params params;
};


class LaneChangeSettings : public QWidget {
  Q_OBJECT

public:
  explicit LaneChangeSettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  AutoLaneChangeTimer *auto_lane_change_timer;
  PauseLateralSpeed *pause_lateral_speed;
};
