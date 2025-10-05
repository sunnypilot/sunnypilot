/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <map>
#include <string>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/blinker_pause_lateral_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/mads_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/neural_network_lateral_control.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/lane_change_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/torque_lateral_control_settings.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class LateralPanel : public QFrame {
  Q_OBJECT

public:
  explicit LateralPanel(SettingsWindowSP *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent* event) override;

public slots:
  void updateToggles(bool _offroad);

private:
  Params params;
  QStackedLayout* main_layout = nullptr;
  QWidget* sunnypilotScreen = nullptr;
  ScrollViewSP *sunnypilotScroller = nullptr;
  bool offroad;

  ParamControl *madsToggle;
  PushButtonSP *madsSettingsButton;
  MadsSettings *madsWidget = nullptr;
  PushButtonSP *laneChangeSettingsButton;
  LaneChangeSettings *laneChangeWidget = nullptr;
  NeuralNetworkLateralControl *nnlcToggle = nullptr;
  BlinkerPauseLateralSettings *blinkerPauseLateralSettings = nullptr;
  ParamControl *torqueLateralControlToggle;
  PushButtonSP *torqueLateralControlSettingsButton;
  TorqueLateralControlSettings *torqueLateralControlWidget = nullptr;

  const QString MADS_BASE_DESC = tr("Enables independent engagements of Automatic Lane Centering (ALC) and Adaptive Cruise Control (ACC).");

  const QString STATUS_MADS_CHECK_COMPATIBILITY = tr("Start the vehicle to check vehicle compatibility.");
  const QString STATUS_MADS_SETTINGS_FULL_COMPATIBILITY = tr("This platform supports all MADS settings.");
  const QString STATUS_MADS_SETTINGS_LIMITED_COMPATIBILITY = tr("This platform supports limited MADS settings.");

  static QString descriptionBuilder(const QString &custom_description, const QString &base_description) {
    return "<font color='white'><b>" + custom_description + "</b></font><br><br>" + base_description;
  }
};
