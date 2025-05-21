#pragma once

#include "selfdrive/ui/qt/onroad/alerts.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/onroad/annotated_camera.h"
#define UIState UIStateSP
#define AnnotatedCameraWidget AnnotatedCameraWidgetSP
#include "selfdrive/ui/sunnypilot/qt/onroad/debug_overlay.h"
#else
#include "selfdrive/ui/qt/onroad/annotated_camera.h"
#endif

class OnroadWindow : public QWidget {
  Q_OBJECT

public:
  OnroadWindow(QWidget* parent = 0);

protected:
  void paintEvent(QPaintEvent *event);
  OnroadAlerts *alerts;
  AnnotatedCameraWidget *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QHBoxLayout* split;
#ifdef SUNNYPILOT
  DebugOverlay *debug_overlay;
#endif

protected slots:
  virtual void offroadTransition(bool offroad);
  virtual void updateState(const UIState &s);
};
