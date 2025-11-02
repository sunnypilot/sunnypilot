/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/developer_panel.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/external_storage.h"
#include "selfdrive/ui/qt/widgets/input.h"

DeveloperPanelSP::DeveloperPanelSP(SettingsWindow *parent) : DeveloperPanel(parent) {

  #ifndef __APPLE__
  addItem(new ExternalStorageControl());
  #endif

  // Advanced Controls Toggle
  showAdvancedControls = new ParamControlSP("ShowAdvancedControls", tr("Show Advanced Controls"), tr("Toggle visibility of advanced sunnypilot controls.\nThis only toggles the visibility of the controls; it does not toggle the actual control enabled/disabled state."), "");
  addItem(showAdvancedControls);

  QObject::connect(showAdvancedControls, &ParamControlSP::toggleFlipped, this, [=](bool) {
    AbstractControlSP::UpdateAllAdvancedControls();
    updateToggles(!uiState()->scene.started);
  });
  showAdvancedControls->showDescription();

  // Github Runner Toggle
  enableGithubRunner = new ParamControlSP("EnableGithubRunner", tr("Enable GitHub runner service"), tr("Enables or disables the github runner service."), "", this, true);
  addItem(enableGithubRunner);

  // Copyparty Toggle
  enableCopyparty = new ParamControlSP("EnableCopyparty", tr("Enable Copyparty service"), tr("Copyparty is a very capable file server, you can use it to download your routes, view your logs and even make some edits on some files from your browser. Requires you to connect to your comma locally via it's IP on port 8080."), "", this, false);
  addItem(enableCopyparty);

  // Copyparty Password
  copypartyPasswordBtn = new ButtonControlSP(tr("Copyparty Password"), tr("SET"), tr("Set a password to secure access to your Copyparty file server. Leave empty for no password protection. Reboot required to apply changes."));

  connect(copypartyPasswordBtn, &ButtonControlSP::clicked, [=]() {
    QString current_password = QString::fromStdString(params.get("CopypartyPassword"));
    QString new_password = InputDialog::getText(tr("Set Copyparty Password"), this,
                                               tr("Enter a password to protect your Copyparty server.\nLeave empty to disable password protection."),
                                               true, -1, current_password);
    if (!new_password.isNull() && new_password != current_password) {
      params.put("CopypartyPassword", new_password.toStdString());
      updateCopypartyPasswordButton();

      // Ask user if they want to reboot now to apply changes
      if (ConfirmationDialog::confirm(tr("Password saved. Reboot now to apply changes?"), tr("Reboot"), this)) {
        params.putBool("DoReboot", true);
      }
    }
  });
  addItem(copypartyPasswordBtn);

  // Quickboot Mode Toggle
  prebuiltToggle = new ParamControlSP("QuickBootToggle", tr("Enable Quickboot Mode"), tr(""), "", this, true);
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
    QFileInfo file("/data/community/crashes/error.log");
    QString text;
    if (file.exists()) {
      text = "<b>" + file.lastModified().toString("dd-MMM-yyyy hh:mm:ss ").toUpper() + "</b><br><br>";
    }
    text += QString::fromStdString(util::read_file("/data/community/crashes/error.log"));
    ConfirmationDialog::rich(text, this);
  });
  addItem(errorLogBtn);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &DeveloperPanelSP::updateToggles);
}

void DeveloperPanelSP::updateToggles(bool offroad) {
  bool disable_updates = params.getBool("DisableUpdates");
  bool is_release = params.getBool("IsReleaseBranch") || params.getBool("IsReleaseSpBranch");
  bool is_tested = params.getBool("IsTestedBranch");
  bool is_development = params.getBool("IsDevelopmentBranch");

  updateCopypartyPasswordButton();
  prebuiltToggle->setVisible(!is_release && !is_tested && !is_development);
  prebuiltToggle->setEnabled(disable_updates);
  params.putBool("QuickBootToggle", QFile::exists("/data/openpilot/prebuilt"));
  prebuiltToggle->refresh();

  prebuiltToggle->setDescription(disable_updates
    ? tr("When toggled on, this creates a prebuilt file to allow accelerated boot times. When toggled off, "
         "it immediately removes the prebuilt file so compilation of locally edited cpp files can be made. "
         "<br><br><b>To edit C++ files locally on device, you MUST first turn off this toggle so the changes can recompile.</b>")
    : tr("Quickboot mode requires updates to be disabled.<br>Enable 'Disable Updates' in the Software panel first."));
  prebuiltToggle->showDescription();

  enableGithubRunner->setVisible(!is_release);
  errorLogBtn->setVisible(!is_release);
  showAdvancedControls->setEnabled(true);

  joystickToggle->setVisible(!is_release);
  longManeuverToggle->setVisible(!is_release);
}

void DeveloperPanelSP::updateCopypartyPasswordButton() {
  QString password = QString::fromStdString(params.get("CopypartyPassword"));
  if (password.isEmpty()) {
    copypartyPasswordBtn->setValue(tr("Not Set"));
    copypartyPasswordBtn->setText(tr("SET"));
  } else {
    copypartyPasswordBtn->setValue(tr("••••••••"));
    copypartyPasswordBtn->setText(tr("CHANGE"));
  }
}

void DeveloperPanelSP::showEvent(QShowEvent *event) {
  DeveloperPanel::showEvent(event);
  AbstractControlSP::UpdateAllAdvancedControls();
  updateToggles(!uiState()->scene.started);
  updateCopypartyPasswordButton();
}
