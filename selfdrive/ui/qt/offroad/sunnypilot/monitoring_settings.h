#pragma once

#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

class MonitoringPanel : public QFrame {
  Q_OBJECT

public:
  explicit MonitoringPanel(QWidget *parent = nullptr);

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* monitoringScreen = nullptr;
  Params params;
  std::map<std::string, ParamControl*> toggles;
};
