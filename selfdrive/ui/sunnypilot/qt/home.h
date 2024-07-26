#pragma once

#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QStackedLayout>
#include <QTimer>
#include <QWidget>

#include "common/params.h"
#include "selfdrive/ui/qt/offroad/driverview.h"
#include "selfdrive/ui/qt/body.h"
#include "selfdrive/ui/qt/widgets/offroad_alerts.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/qt/home.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/sidebar.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/onroad_home.h"
#define OnroadWindow OnroadWindowSP
#else
#include "selfdrive/ui/qt/sidebar.h"
#include "selfdrive/ui/qt/onroad/onroad_home.h"
#endif

class HomeWindowSP : public HomeWindow {
  Q_OBJECT

public:
  explicit HomeWindowSP(QWidget* parent = 0);

public slots:
  void showMapPanel(bool show);

protected:
  void mousePressEvent(QMouseEvent* e) override;
private slots:
  void updateState(const UIState &s) override;
};
