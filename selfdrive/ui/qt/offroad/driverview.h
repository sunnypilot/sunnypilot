#pragma once

#include "selfdrive/ui/qt/widgets/cameraview.h"
#include "selfdrive/ui/qt/onroad/driver_monitoring.h"
#include "selfdrive/ui/qt/widgets/input.h"

#ifdef SUNNYPILOT
#define Device DeviceSP
#endif

class DriverViewWindow : public CameraWidget {
  Q_OBJECT
public:
  explicit DriverViewWindow(QWidget *parent);
  void paintGL() override;
  mat4 calcFrameMatrix() override;
  DriverMonitorRenderer driver_monitor;
};

class DriverViewDialog : public DialogBase {
  Q_OBJECT
public:
  DriverViewDialog(QWidget *parent);
  void done(int r) override;
};
