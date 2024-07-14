#pragma once

#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"

class MonitoringPanel : public QFrame {
  Q_OBJECT

public:
  explicit MonitoringPanel(QWidget *parent = nullptr);

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* monitoringScreen = nullptr;
  Params params;
  std::map<std::string, ParamControlSP*> toggles;
};
