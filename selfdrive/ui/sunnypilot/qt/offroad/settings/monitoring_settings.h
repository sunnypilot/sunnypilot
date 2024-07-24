#pragma once

#include <map>
#include <string>
#include <tuple>
#include <vector>

#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

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
