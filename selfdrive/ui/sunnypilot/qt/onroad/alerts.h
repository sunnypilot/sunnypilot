#pragma once

#include "selfdrive/ui/qt/onroad/alerts.h"
#include "selfdrive/ui/sunnypilot/ui.h"

class OnroadAlertsSP : public OnroadAlerts {
  Q_OBJECT

public:
  OnroadAlertsSP(QWidget *parent = 0) : OnroadAlerts(parent) {}

protected:
  void paintEvent(QPaintEvent*) override;
  Alert getAlert(const SubMaster &sm, uint64_t started_frame);
};
