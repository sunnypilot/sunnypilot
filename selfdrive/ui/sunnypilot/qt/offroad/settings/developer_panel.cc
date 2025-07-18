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

  QObject::connect(showAdvancedControls, &ParamControlSP::toggleFlipped, this, [=](bool) {
    AbstractControlSP::UpdateAllAdvancedControls();
    updateToggles(!uiState()->scene.started);
  });
  showAdvancedControls->showDescription();

  // Github Runner Toggle
  enableGithubRunner = new ParamControlSP("EnableGithubRunner", tr("Enable GitHub runner service"), tr("Enables or disables the github runner service."), "");
  addItem(enableGithubRunner);

  // Error log button
  errorLogBtn = new ButtonControlSP(tr("Error Log"), tr("VIEW"), tr("View the error log for sunnypilot crashes."));
  connect(errorLogBtn, &ButtonControlSP::clicked, [=]() {
    std::string txt = util::read_file("/data/community/crashes/error.log");
    ConfirmationDialog::rich(QString::fromStdString(txt), this);
  });
  addItem(errorLogBtn);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &DeveloperPanelSP::updateToggles);
}

void DeveloperPanelSP::updateToggles(bool offroad) {
  bool is_release = params.getBool("IsReleaseBranch");

  enableGithubRunner->setVisible(!is_release);
  errorLogBtn->setVisible(!is_release);
}

void DeveloperPanelSP::showEvent(QShowEvent *event) {
  DeveloperPanel::showEvent(event);
  updateToggles(!uiState()->scene.started);
  AbstractControlSP::UpdateAllAdvancedControls();
}
