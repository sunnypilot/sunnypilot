#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/custom_offsets_settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/lane_change_settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/mads_settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/speed_limit_control_settings.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

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
  SubPanelButton *slcSettings = nullptr;
  SlcSettings* slc_settings = nullptr;
  LaneChangeSettings* lane_change_settings = nullptr;
  CustomOffsetsSettings* custom_offsets_settings = nullptr;
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ParamWatcher *param_watcher;

  TorqueFriction *friction;
  TorqueMaxLatAccel *lat_accel_factor;
  ButtonParamControl *dlp_settings;

  ScrollView *scrollView = nullptr;

  const QString nnff_description = QString("%1<br>"
                                           "%2")
                                   .arg(tr("Formerly known as <b>\"NNFF\"</b>, this replaces the lateral <b>\"torque\"</b> controller with one using a neural network trained on each car's (actually, each separate EPS firmware) driving data for increased controls accuracy."))
                                   .arg(tr("Contact @twilsonco in the sunnypilot Discord server with feedback, or to provide log data for your car if your car is currently unsupported."));

  QString nnffDescriptionBuilder(const QString &custom_description) {
    QString description = "<b>" + custom_description + "</b><br><br>" + nnff_description;
    return description;
  }
};
