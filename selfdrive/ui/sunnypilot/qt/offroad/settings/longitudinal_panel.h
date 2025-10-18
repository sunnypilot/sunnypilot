/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/custom_acc_increment.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class LongitudinalPanel : public QWidget {
  Q_OBJECT

public:
  explicit LongitudinalPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;
  void refresh(bool _offroad);

private:
  Params params;
  bool has_longitudinal_control = false;
  bool is_pcm_cruise = false;
  bool has_icbm = false;
  bool offroad = false;

  QStackedLayout *main_layout = nullptr;
  ScrollViewSP *cruisePanelScroller = nullptr;
  QWidget *cruisePanelScreen = nullptr;
  CustomAccIncrement *customAccIncrement = nullptr;
  ParamControl *SmartCruiseControlVision;
  ParamControl *SmartCruiseControlMap;
  ParamControl *intelligentCruiseButtonManagement = nullptr;
  ParamControl *dynamicExperimentalControl = nullptr;
  SpeedLimitSettings *speedLimitScreen;
  PushButtonSP *speedLimitSettings;
};
