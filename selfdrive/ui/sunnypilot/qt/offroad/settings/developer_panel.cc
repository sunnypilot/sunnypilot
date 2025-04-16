/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/developer_panel.h"

DeveloperPanelSP::DeveloperPanelSP(SettingsWindowSP *parent) : DeveloperPanel(parent) {

  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", "Custom ACC Speed Increments", "Some description here", "", this);
  AddWidgetAt(3, customAccIncrement);

}
