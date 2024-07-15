#pragma once

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"

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
