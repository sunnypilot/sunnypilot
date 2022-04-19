#pragma once

#include <QPushButton>
#include <QStackedWidget>
#include <QWidget>
#include <QStackedLayout>

#include "selfdrive/ui/qt/widgets/controls.h"

class ForceCarRecognition : public QWidget
{
  Q_OBJECT

public:
  explicit ForceCarRecognition(QWidget* parent = 0);

private:

signals:
  void backPress();
  void selectedCar();
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