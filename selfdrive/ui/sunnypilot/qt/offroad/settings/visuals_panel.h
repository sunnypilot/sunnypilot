/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class ScrollViewSP;

class VisualsPanel : public QWidget {
 Q_OBJECT

public:
 explicit VisualsPanel(QWidget *parent = nullptr);

 void paramsRefresh();
 void refreshLongitudinalStatus();

protected:
 QStackedLayout* main_layout = nullptr;
 QWidget* sunnypilotScreen = nullptr;
 ScrollViewSP *sunnypilotScroller = nullptr;
 Params params;
 std::map<std::string, ParamControlSP*> toggles;
 ParamWatcher * param_watcher;
 ButtonParamControlSP *chevron_info_settings;
 ButtonParamControlSP *dev_ui_settings;

 bool has_longitudinal_control = false;
};
