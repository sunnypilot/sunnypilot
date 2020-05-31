#pragma once

#include <QStackedLayout>
#include <QPushButton>
#include <QStackedWidget>
#include <QWidget>

#include "selfdrive/ui/qt/widgets/controls.h"

class ForceCarRecognition : public QWidget {
  Q_OBJECT

public:
  explicit ForceCarRecognition(QWidget* parent = 0);

private:

signals:
  void backPress();
  void selectedCar();
};

class SPGeneralPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPGeneralPanel(QWidget *parent = nullptr);
};

class SPControlsPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPControlsPanel(QWidget *parent = nullptr);
};

class SPVehiclesPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPVehiclesPanel(QWidget *parent = nullptr);

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* home = nullptr;
  ForceCarRecognition* setCar = nullptr;

  QWidget* home_widget;
};

class SPVisualsPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPVisualsPanel(QWidget *parent = nullptr);
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

class TorqueDeadzoneDeg : public AbstractControl {
  Q_OBJECT

public:
  TorqueDeadzoneDeg();

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
