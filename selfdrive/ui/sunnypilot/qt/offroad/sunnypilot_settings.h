#pragma once

#include "common/model.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/custom_offsets_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/lane_change_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/mads_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/speed_limit_control_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/speed_limit_warning_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/speed_limit_policy_settings.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"

class TorqueFriction : public OptionControlSP {
  Q_OBJECT

public:
  TorqueFriction();

  void refresh();

private:
  Params params;
};

class TorqueMaxLatAccel : public OptionControlSP {
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
  SubPanelButton *slwSettings = nullptr;
  SpeedLimitWarningSettings* slw_settings = nullptr;
  SubPanelButton *slpSettings = nullptr;
  SpeedLimitPolicySettings* slp_settings = nullptr;
  LaneChangeSettings* lane_change_settings = nullptr;
  CustomOffsetsSettings* custom_offsets_settings = nullptr;
  Params params;
  std::map<std::string, ParamControlSP*> toggles;
  ParamWatcher *param_watcher;

  TorqueFriction *friction;
  TorqueMaxLatAccel *lat_accel_factor;
  ButtonParamControlSP *dlp_settings;

  ScrollViewSP *scrollView = nullptr;

  const QString nnff_description = QString("%1<br><br>"
                                           "%2")
                                   .arg(tr("Formerly known as <b>\"NNFF\"</b>, this replaces the lateral <b>\"torque\"</b> controller with one using a neural network trained on each car's (actually, each separate EPS firmware) driving data for increased controls accuracy."))
                                   .arg(tr("Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server with feedback, or to provide log data for your car if your car is currently unsupported: ") + "<font color='white'><b>#tuning-nnlc</b></font>");

  QString nnffDescriptionBuilder(const QString &custom_description) {
    QString description = "<b>" + custom_description + "</b><br><br>" + nnff_description;
    return description;
  }

  const QString custom_offsets_description = QString(tr("Add custom offsets to Camera and Path in sunnypilot."));
  const QString dlp_description = QString(tr("Default is Laneless. In Auto mode, sunnnypilot dynamically chooses between Laneline or Laneless model based on lane recognition confidence level on road and certain conditions."));
};
