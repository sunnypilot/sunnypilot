#pragma once

#include <QWidget>
#include <QTextEdit>
#include <QVBoxLayout>
#include <QElapsedTimer>
#include <QTimer>
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/ui.h"
using UIStateType = UIStateSP;
#else
#include "selfdrive/ui/ui.h"
using UIStateType = UIState;
#endif

class DebugOverlay : public QWidget {
  Q_OBJECT

public:
  explicit DebugOverlay(QWidget *parent = nullptr);
  void updateState(const UIStateType &s);

private:
  QTextEdit *text_edit;
  Params params;
  QElapsedTimer update_timer;
  QTimer *periodic_timer;
  const UIStateType *latest_state = nullptr;

private slots:
  void onUpdateTimer();
};
