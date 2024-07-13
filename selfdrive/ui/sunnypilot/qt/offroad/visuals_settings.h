#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/widgets/controls.h"

class VisualsPanel : public ListWidget {
  Q_OBJECT

public:
  explicit VisualsPanel(QWidget *parent = nullptr);

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  ButtonParamControl *dev_ui_settings;
  ButtonParamControl *chevron_info_settings;
  ButtonParamControl *sidebar_temp_setting;
};
