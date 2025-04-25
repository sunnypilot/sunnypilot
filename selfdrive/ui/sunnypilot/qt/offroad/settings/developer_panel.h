/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/offroad/developer_panel.h"

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/developer/custom_acc_increment.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class DeveloperPanelSP : public DeveloperPanel {
  Q_OBJECT

public:
  explicit DeveloperPanelSP(SettingsWindowSP *parent = 0);

private:
  CustomAccIncrement *customAccIncrement = nullptr;

};
