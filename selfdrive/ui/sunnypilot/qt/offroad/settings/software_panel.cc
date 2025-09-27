/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/software_panel.h"

SoftwarePanelSP::SoftwarePanelSP(QWidget *parent) : SoftwarePanel(parent) {
  // branch selector
  QObject::disconnect(targetBranchBtn, nullptr, nullptr, nullptr);
  connect(targetBranchBtn, &ButtonControlSP::clicked, [=]() {
    if (Hardware::get_device_type() == cereal::InitData::DeviceType::TICI) {
      auto current = params.get("GitBranch");
      QStringList allBranches = QString::fromStdString(params.get("UpdaterAvailableBranches")).split(",");
      QStringList branches;
      for (const QString &b : allBranches) {
        if (b.endsWith("-tici")) {
          branches.append(b);
        }
      }

      for (QString b : {current.c_str(), "master-tici", "staging-tici", "release-tici"}) {
        auto i = branches.indexOf(b);
        if (i >= 0) {
          branches.removeAt(i);
          branches.insert(0, b);
        }
      }

      QString cur = QString::fromStdString(params.get("UpdaterTargetBranch"));
      QString selection = MultiOptionDialog::getSelection(tr("Select a branch"), branches, cur, this);
      if (!selection.isEmpty()) {
        params.put("UpdaterTargetBranch", selection.toStdString());
        targetBranchBtn->setValue(QString::fromStdString(params.get("UpdaterTargetBranch")));
        checkForUpdates();
      }
    } else {
      InputDialog d(tr("Search Branch"), this, tr("Enter search keywords, or leave blank to list all branches."), false);
      d.setMinLength(0);
      const int ret = d.exec();
      if (ret) {
        searchBranches(d.text());
      }
    }
  });

  // Disable Updates toggle
  disableUpdatesToggle = new ParamControl("DisableUpdates",
    tr("Disable Updates"),
    tr("When enabled, software updates will be disabled. <b>This requires a reboot to take effect.</b>"),
    "../assets/icons/icon_warning.png",
    this, true);
  disableUpdatesToggle->showDescription();
  addItem(disableUpdatesToggle);
  connect(disableUpdatesToggle, &ParamControl::toggleFlipped, this, &SoftwarePanelSP::handleDisableUpdatesToggled);
  connect(uiState(), &UIState::offroadTransition, this, &SoftwarePanelSP::updateDisableUpdatesToggle);
  updateDisableUpdatesToggle(!uiState()->scene.started);
}

/**
 * @brief Searches for available branches based on a query string, presents the results in a dialog,
 * and updates the target branch if a selection is made.
 *
 * This function filters the list of branches based on the provided query, and displays the filtered branches in a selection dialog.
 * If a branch is selected, the "UpdaterTargetBranch" parameter is updated and a check for updates is triggered.
 * If no branches are found matching the query, an alert dialog is displayed.
 *
 * @param query The search query string.
 */
void SoftwarePanelSP::searchBranches(const QString &query) {

  QStringList branches = QString::fromStdString(params.get("UpdaterAvailableBranches")).split(",");
  QStringList results = searchFromList(query, branches);
  results.sort();

  if (results.isEmpty()) {
    ConfirmationDialog::alert(tr("No branches found for keywords: %1").arg(query), this);
    return;
  }

  QString selected_branch = MultiOptionDialog::getSelection(tr("Select a branch"), results, "", this);

  if (!selected_branch.isEmpty()) {
    params.put("UpdaterTargetBranch", selected_branch.toStdString());
    targetBranchBtn->setValue(selected_branch);
    checkForUpdates();
  }
}

void SoftwarePanelSP::handleDisableUpdatesToggled(bool state) {
  if (ConfirmationDialog::confirm(tr("%1 updates requires a reboot.<br>Reboot now?")
      .arg(state ? "Disabling" : "Enabling"), tr("Reboot"), this)) {
    params.putBool("DoReboot", true);
  } else {
    params.putBool("DisableUpdates", !state);
    disableUpdatesToggle->refresh();
  }
}

void SoftwarePanelSP::updateDisableUpdatesToggle(bool offroad) {
  bool enabled = offroad;
  disableUpdatesToggle->setEnabled(enabled);
  disableUpdatesToggle->setDescription(enabled
    ? tr("When enabled, software updates will be disabled.<br><b>This requires a reboot to take effect.</b>")
    : tr("Please enable always offroad mode or turn off vehicle to adjust these toggles"));
}

void SoftwarePanelSP::showEvent(QShowEvent *event) {
  SoftwarePanel::showEvent(event);
  updateDisableUpdatesToggle(!uiState()->scene.started);
  disableUpdatesToggle->showDescription();
}
