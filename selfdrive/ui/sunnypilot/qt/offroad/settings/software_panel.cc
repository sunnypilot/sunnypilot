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
    InputDialog d(tr("Search Branch"), this, tr("Enter search keywords, or leave blank to list all branches."), false);
      d.setMinLength(0);
      const int ret = d.exec();
      if (ret) {
        searchBranches(d.text());
      }
  });

  // Disable Updates toggle
  disableUpdatesToggle = new ParamControl("DisableUpdates",
    tr("Disable Updates"),
    tr("When enabled, software updates will be disabled. <b>This requires a reboot to take effect.</b>"),
    "../assets/icons/icon_warning.png",
    this);
  addItem(disableUpdatesToggle);
  connect(disableUpdatesToggle, &ParamControl::toggleFlipped, this, &SoftwarePanelSP::handleDisableUpdatesToggled);
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
  QString msg = state ? tr("Disabling updates requires a reboot. Reboot now?")
                      : tr("Enabling updates requires a reboot. Reboot now?");
  if (ConfirmationDialog::confirm(msg, tr("Reboot"), this)) {
    params.putBool("DoReboot", true);
  } else {
    // Reset param to previous state if cancelled
    params.putBool("DisableUpdates", !state);
    disableUpdatesToggle->refresh();
  }
}
