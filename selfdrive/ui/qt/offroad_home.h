#pragma once

#include <QStackedWidget>
#include <QWidget>

#include "common/params.h"
#include "selfdrive/ui/qt/body.h"
#include "selfdrive/ui/qt/onroad/onroad_home.h"
#include "selfdrive/ui/qt/widgets/offroad_alerts.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/onroad_home.h"
#include "selfdrive/ui/sunnypilot/qt/sidebar.h"
#define OnroadWindow OnroadWindowSP
#define OffroadHomeImp OffroadHomeSP
#define LayoutWidget LayoutWidgetSP
#define Sidebar SidebarSP
#define ElidedLabel ElidedLabelSP
#else
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/onroad/onroad_home.h"
#include "selfdrive/ui/qt/sidebar.h"
#endif

class OffroadHome : public QFrame {
  Q_OBJECT

public:
  void do_work(QWidget*& home_widget);
  explicit OffroadHome(QWidget* parent = 0);

signals:
  void openSettings(int index = 0, const QString &param = "");

protected:
  QStackedLayout* center_layout;
  QWidget* home_widget;
  QHBoxLayout *home_layout;
  QStackedWidget *left_widget;

private:
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;
  void refresh();

  Params params;

  QTimer* timer;
  ElidedLabel* version;
  UpdateAlert *update_widget;
  OffroadAlert* alerts_widget;
  QPushButton* alert_notif;
  QPushButton* update_notif;
};
