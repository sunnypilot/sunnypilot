#pragma once

#include <QFrame>
#include <QStackedLayout>
#include <QWidget>

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif

class WiFiPromptWidget : public QFrame {
  Q_OBJECT

public:
  explicit WiFiPromptWidget(QWidget* parent = 0);

signals:
  void openSettings(int index = 0, const QString &param = "");

public slots:
  void updateState(const UIState &s);

protected:
  QStackedLayout *stack;
};
