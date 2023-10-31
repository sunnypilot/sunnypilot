#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/custom_offsets_settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/lane_change_settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/mads_settings.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

class SpeedLimitValueOffset : public SPOptionControl {
  Q_OBJECT

public:
  SpeedLimitValueOffset();

  void refresh();

private:
  Params params;
};

class TorqueFriction : public SPOptionControl {
  Q_OBJECT

public:
  TorqueFriction();

  void refresh();

private:
  Params params;
};

class TorqueMaxLatAccel : public SPOptionControl {
  Q_OBJECT

public:
  TorqueMaxLatAccel();

  void refresh();

private:
  Params params;
};

class SunnypilotPanel : public QFrame {
  Q_OBJECT

public:
  explicit SunnypilotPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent* event) override;

public slots:
  void updateToggles();

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* sunnypilotScreen = nullptr;
  MadsSettings* mads_settings = nullptr;
  LaneChangeSettings* lane_change_settings = nullptr;
  CustomOffsetsSettings* custom_offsets_settings = nullptr;
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ParamWatcher *param_watcher;

  SpeedLimitValueOffset *slvo;
  TorqueFriction *friction;
  TorqueMaxLatAccel *lat_accel_factor;
  ButtonParamControl *dlp_settings;
  ButtonParamControl *speed_limit_control_settings;
  ButtonParamControl *speed_limit_offset_settings;

  ScrollView *scrollView = nullptr;
};
