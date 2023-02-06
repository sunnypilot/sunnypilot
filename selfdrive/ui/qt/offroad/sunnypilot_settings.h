#pragma once

#include <QApplication>
#include <QStackedLayout>
#include <QPushButton>
#include <QStackedWidget>
#include <QWidget>

#include "selfdrive/ui/qt/widgets/controls.h"

class SPGeneralPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPGeneralPanel(QWidget *parent = nullptr);

private:
  QVBoxLayout *main_layout;
  ParamControl *endToEndLongAlert;
};

class SPControlsPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPControlsPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

private:
  Params params;

  QVBoxLayout *main_layout;
  QWidget *madsMainControl;
  QVBoxLayout *madsSubControl;
  QWidget *dlpMain;
  QVBoxLayout *dlpSub;
  QWidget *customOffsetsMain;
  QVBoxLayout *customOffsetsSub;
  QWidget *gacMain;
  QVBoxLayout *gacSub;
  QWidget *torqueMain;
  QVBoxLayout *torqueSub;
  QWidget *customTorqueMain;
  QVBoxLayout *customTorqueSub;
  QWidget *speedLimitMain;
  QVBoxLayout *speedLimitSub;
  QWidget *speedOffsetMain;
  QVBoxLayout *speedOffsetSub;

  ParamControl *madsControl;
  ParamControl *disengageLateralOnBrake;
  ParamControl *accMadsCombo;
  ParamControl *belowSpeed;
  ParamControl *dlpControl;
  ParamControl *dlpCurve;
  ParamControl *customOffsets;
  ParamControl *gapAdjustCruise;
  ParamControl *torqueLateral;
  ParamControl *customTorqueLateral;
  ParamControl *liveTorque;
  ParamControl *speedLimitControl;
  ParamControl *speedPercControl;
  ParamControl *osmLocalDb;

  void updateToggles();
};

class SPVehiclesPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPVehiclesPanel(QWidget *parent = nullptr);

private:
  Params params;

  QStackedLayout* main_layout = nullptr;
  QWidget* home = nullptr;

  QWidget* home_widget;

  ParamControl *eScc;
  ParamControl *stockLongToyota;
};

class SPVisualsPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPVisualsPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

private:
  Params params;

  QWidget *devUiMain;
  QVBoxLayout *devUiSub;
  QWidget *mapboxMain;
  QVBoxLayout *mapboxSub;

  ParamControl *devUi;
  ParamControl *customMapbox;
  ParamControl *mapboxFullScreen;

  void updateToggles();
};

class MaxTimeOffroad : public AbstractControl {
  Q_OBJECT

public:
  MaxTimeOffroad();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class OnroadScreenOff : public AbstractControl {
  Q_OBJECT

public:
  OnroadScreenOff();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class OnroadScreenOffBrightness : public AbstractControl {
  Q_OBJECT

public:
  OnroadScreenOffBrightness();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class BrightnessControl : public AbstractControl {
  Q_OBJECT

public:
  BrightnessControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class CameraOffset : public AbstractControl {
  Q_OBJECT

public:
  CameraOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class PathOffset : public AbstractControl {
  Q_OBJECT

public:
  PathOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class AutoLaneChangeTimer : public AbstractControl {
  Q_OBJECT

public:
  AutoLaneChangeTimer();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class GapAdjustCruiseMode : public AbstractControl {
  Q_OBJECT

public:
  GapAdjustCruiseMode();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class TorqueFriction : public AbstractControl {
  Q_OBJECT

public:
  TorqueFriction();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class TorqueMaxLatAccel : public AbstractControl {
  Q_OBJECT

public:
  TorqueMaxLatAccel();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class SpeedLimitStyle : public AbstractControl {
  Q_OBJECT

public:
  SpeedLimitStyle();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class SpeedLimitValueOffset : public AbstractControl {
  Q_OBJECT

public:
  SpeedLimitValueOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class VwAccType : public AbstractControl {
  Q_OBJECT

public:
  VwAccType();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class DevUiRow : public AbstractControl {
  Q_OBJECT

public:
  DevUiRow();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};
