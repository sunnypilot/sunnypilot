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

#include "common/params.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/qt/util.h"
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#else
#include "selfdrive/ui/qt/widgets/controls.h"
#endif

class OptionWidget;

class OnroadSettings : public QFrame {
  Q_OBJECT

public:
  explicit OnroadSettings(bool closeable = false, QWidget *parent = nullptr);
  void changeDynamicLaneProfile();
  void changeGapAdjustCruise();
  void changeAccelerationPersonality();
  void changeDynamicPersonality();
  void changeDynamicExperimentalControl();
  void changeSpeedLimitControl();

private:
  void showEvent(QShowEvent *event) override;
  void refresh();

  Params params;

  QVBoxLayout *options_layout;
  OptionWidget *dlp_widget;
  OptionWidget *gac_widget;
  OptionWidget *ap_widget;
  OptionWidget *dynamic_personality_widget;
  OptionWidget *dec_widget;
  OptionWidget *slc_widget;
  ParamWatcher *param_watcher;

signals:
  void closeSettings();
};

class OptionWidget : public QPushButton {
  Q_OBJECT

public:
  explicit OptionWidget(QWidget *parent = nullptr);
  void updateDynamicLaneProfile(QString param);
  void updateGapAdjustCruise(QString param);
  void updateAccelerationPersonality(QString param);
  void updateDynamicPersonality(QString param);
  void updateDynamicExperimentalControl(QString param);
  void updateSpeedLimitControl(QString param);

signals:
  void updateParam();

private:
  QLabel *icon, *title, *subtitle;

  Params params;
};
