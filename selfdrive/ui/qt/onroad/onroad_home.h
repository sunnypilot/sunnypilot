#pragma once

#include "selfdrive/ui/qt/onroad/alerts.h"

#if SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/onroad/sp_priv_annotated_camera.h"
#define AnnotatedCameraWidget AnnotatedCameraWidgetSP
#else
#include "selfdrive/ui/qt/onroad/annotated_camera.h"
#endif

class OnroadWindow : public QWidget {
  Q_OBJECT

public:
  OnroadWindow(QWidget* parent = 0);

protected:
  void paintEvent(QPaintEvent *event) override;
  OnroadAlerts *alerts;
  AnnotatedCameraWidget *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QHBoxLayout* split;

protected slots:
  virtual void offroadTransition(bool offroad);
  virtual void updateState(const UIState &s);
};