#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"

class VisualsPanel : public ListWidget {
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
