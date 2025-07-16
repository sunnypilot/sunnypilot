/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/developer_panel.h"

DeveloperPanelSP::DeveloperPanelSP(SettingsWindow *parent) : DeveloperPanel(parent) {
  // Github Runner Toggle
  enableGithubRunner = new ParamControlSP("EnableGithubRunner", tr("Enable GitHub runner service"), tr("Enables or disables the github runner service."), "");
  addItem(enableGithubRunner);

  // Fastboot Mode Toggle
  prebuiltToggle = new ParamControlSP("FastBootToggle", tr("Enable Fastboot Mode"), tr(""), "");
  addItem(prebuiltToggle);

  QObject::connect(prebuiltToggle, &ParamControl::toggleFlipped, [=](bool state) {
    QString prebuiltPath = "/data/openpilot/prebuilt";
    state ? QFile(prebuiltPath).open(QIODevice::WriteOnly) : QFile::remove(prebuiltPath);
    prebuiltToggle->refresh();
  });
  prebuiltToggle->setVisible(false);

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
  bool is_tested = params.getBool("IsTestedBranch");
  bool is_development = params.getBool("IsDevelopmentBranch");
  bool disable_updates = params.getBool("DisableUpdates");

  prebuiltToggle->setVisible(!is_release && !is_tested && !is_development);
  prebuiltToggle->setEnabled(offroad && disable_updates);

  params.putBool("FastBootToggle", QFile::exists("/data/openpilot/prebuilt"));
  prebuiltToggle->refresh();

  prebuiltToggle->setDescription(disable_updates
    ? tr("When toggled on, this creates a prebuilt file so you don't need to compile every device boot. When toggled off, "
         "it immediately removes the prebuilt file so compilation of locally edited cpp files can be made. "
         "<br><br><b>To edit C++ files locally on device, you MUST first turn off this toggle so the changes can recompile.</b>")
    : tr("Fastboot mode requires updates to be disabled.<br>Enable 'Disable Updates' in the Software panel first."));

  enableGithubRunner->setVisible(!is_release);
  errorLogBtn->setVisible(!is_release && !is_tested);
}

void DeveloperPanelSP::showEvent(QShowEvent *event) {
  DeveloperPanel::showEvent(event);
  updateToggles(!uiState()->scene.started);
  prebuiltToggle->showDescription();
}
