/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/developer_panel.h"

DeveloperPanelSP::DeveloperPanelSP(SettingsWindow *parent) : DeveloperPanel(parent) {

  // Advanced Controls Toggle
  showAdvancedControls = new ParamControlSP("ShowAdvancedControls", tr("Show Advanced Controls"), tr("Toggle visibility of advanced sunnypilot controls.\nThis only toggles the visibility of the controls; it does not toggle the actual control enabled/disabled state."), "");
  addItem(showAdvancedControls);

}

void DeveloperPanelSP::updateToggles(bool offroad) {

}

void DeveloperPanelSP::showEvent(QShowEvent *event) {
  DeveloperPanel::showEvent(event);
  updateToggles(!uiState()->scene.started);
}
