#pragma once

#include <map>
#include <string>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class VisualsPanel : public ListWidgetSP {
  Q_OBJECT

public:
  explicit VisualsPanel(QWidget *parent = nullptr);

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  ButtonParamControlSP *dev_ui_settings;
  ButtonParamControlSP *chevron_info_settings;
  ButtonParamControlSP *sidebar_temp_setting;
};
