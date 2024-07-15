#pragma once

#include <memory>

#include <QFrame>
#include <QMap>
#include "selfdrive/ui/qt/sidebar.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif

class SidebarSP : public Sidebar {
  Q_OBJECT
  Q_PROPERTY(ItemStatus sunnylinkStatus MEMBER sunnylink_status NOTIFY valueChanged);
  Q_PROPERTY(QString sidebarTemp MEMBER sidebar_temp_str NOTIFY valueChanged);

public:
  explicit SidebarSP(QWidget* parent = 0);

public slots:
  void updateState(const UIState &s) override;

protected:
  const QColor progress_color = QColor(3, 132, 252);
  const QColor disabled_color = QColor(128, 128, 128);

  ItemStatus sunnylink_status;

private:
  Params params;
  void DrawSidebar(QPainter &p) override;
  QString sidebar_temp = "0";
  QString sidebar_temp_str = "0";
};