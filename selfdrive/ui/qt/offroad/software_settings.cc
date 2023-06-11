#include "selfdrive/ui/qt/offroad/settings.h"

#include <cassert>
#include <cmath>
#include <string>

#include <QDebug>
#include <QLabel>

#include "common/params.h"
#include "common/util.h"
#include "common/model.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "system/hardware/hw.h"


void SoftwarePanel::checkForUpdates() {
  std::system("pkill -SIGUSR1 -f selfdrive.updated");
}

SoftwarePanel::SoftwarePanel(QWidget* parent) : ListWidget(parent) {
  currentModelLbl = new LabelControl(tr("Current Driving Model"), CURRENT_MODEL);
  addItem(currentModelLbl);

  onroadLbl = new QLabel(tr("Updates are only downloaded while the car is off."));
  onroadLbl->setStyleSheet("font-size: 50px; font-weight: 400; text-align: left; padding-top: 30px; padding-bottom: 30px;");
  addItem(onroadLbl);

  // current version
  versionLbl = new LabelControl(tr("Current Version"), "");
  addItem(versionLbl);

  // download update btn
  downloadBtn = new ButtonControl(tr("Download"), tr("CHECK"));
  connect(downloadBtn, &ButtonControl::clicked, [=]() {
    downloadBtn->setEnabled(false);
    if (downloadBtn->text() == tr("CHECK")) {
      checkForUpdates();
    } else {
      std::system("pkill -SIGHUP -f selfdrive.updated");
    }
  });
  addItem(downloadBtn);

  // install update btn
  installBtn = new ButtonControl(tr("Install Update"), tr("INSTALL"));
  connect(installBtn, &ButtonControl::clicked, [=]() {
    installBtn->setEnabled(false);
    params.putBool("DoReboot", true);
  });
  addItem(installBtn);

  // branch selecting
  targetBranchBtn = new ButtonControl(tr("Target Branch"), tr("SELECT"));
  connect(targetBranchBtn, &ButtonControl::clicked, [=]() {
    auto current = params.get("GitBranch");
    QStringList branches = QString::fromStdString(params.get("UpdaterAvailableBranches")).split(",");
    for (QString b : {current.c_str(), "devel-staging", "devel", "nightly", "master-ci", "master"}) {
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
  });
  if (!params.getBool("IsTestedBranch")) {
    addItem(targetBranchBtn);
  }

  osmUpdateLbl = new QLabel(tr("Database updates can be downloaded while the car is off."));
  osmUpdateLbl->setStyleSheet("font-size: 50px; font-weight: 400; text-align: left; padding-top: 30px; padding-bottom: 30px;");
  addItem(osmUpdateLbl);

  osmUpdateBtn = new ButtonControl(tr("OpenStreetMap Database Update"), tr("CHECK"));
  connect(osmUpdateBtn, &ButtonControl::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reboot and perform a database update?\nEstimated time: 30-90 minutes"), tr("Reboot"), parent)) {
      params.putBool("OsmDbUpdatesCheck", true);
      Hardware::reboot();
    }
  });
  addItem(osmUpdateBtn);

  osmDownloadBtn = new ButtonControl(tr("OpenStreetMap Database"), tr("SELECT"));
  connect(osmDownloadBtn, &ButtonControl::clicked, [=]() {
    std::vector<std::tuple<QString, QString, QString, QString>> locations = getOsmLocations();
    QString initTitle = QString::fromStdString(params.get("OsmLocationTitle"));
    QString currentTitle = ((initTitle == "== None ==") || (initTitle.length() == 0)) ? "== None ==" : initTitle;

    QStringList locationTitles;
    for (auto& loc : locations) {
      locationTitles.push_back(std::get<0>(loc));
    }

    QString selection = MultiOptionDialog::getSelection(tr("Select your location"), locationTitles, currentTitle, this);
    if (!selection.isEmpty()) {
      params.put("OsmLocal", "1");
      params.put("OsmLocationTitle", selection.toStdString());
      for (auto& loc : locations) {
        if (std::get<0>(loc) == selection) {
          params.put("OsmLocationName", std::get<1>(loc).toStdString());
          params.put("OsmWayTest", std::get<2>(loc).toStdString());
          params.put("OsmLocationUrl", std::get<3>(loc).toStdString());
          break;
        }
      }
      osmDownloadBtn->setValue(selection);
      if (selection != "== None ==") {
        if (ConfirmationDialog::confirm(tr("Are you sure you want to reboot to start downloading the selected database? Estimated time: 30-90 minutes"), tr("Reboot"), parent)) {
          params.putBool("OsmDbUpdatesCheck", true);
          Hardware::reboot();
        }
      }
    }
    updateLabels();
  });
  addItem(osmDownloadBtn);

  // uninstall button
  auto uninstallBtn = new ButtonControl(tr("Uninstall %1").arg(getBrand()), tr("UNINSTALL"));
  connect(uninstallBtn, &ButtonControl::clicked, [&]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to uninstall?"), tr("Uninstall"), this)) {
      params.putBool("DoUninstall", true);
    }
  });
  addItem(uninstallBtn);

  fs_watch = new QFileSystemWatcher(this);
  QObject::connect(fs_watch, &QFileSystemWatcher::fileChanged, [=](const QString path) {
    updateLabels();
  });

  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    updateLabels();
  });

  updateLabels();
}

void SoftwarePanel::showEvent(QShowEvent *event) {
  // nice for testing on PC
  installBtn->setEnabled(true);

  updateLabels();
}

void SoftwarePanel::updateLabels() {
  // add these back in case the files got removed
  fs_watch->addPath(QString::fromStdString(params.getParamPath("LastUpdateTime")));
  fs_watch->addPath(QString::fromStdString(params.getParamPath("UpdateFailedCount")));
  fs_watch->addPath(QString::fromStdString(params.getParamPath("UpdaterState")));
  fs_watch->addPath(QString::fromStdString(params.getParamPath("UpdateAvailable")));

  if (!isVisible()) {
    return;
  }

  // updater only runs offroad
  onroadLbl->setVisible(is_onroad);
  downloadBtn->setVisible(!is_onroad);

  QString name = QString::fromStdString(params.get("OsmLocationName"));
  if (!name.isEmpty()) {
    osmUpdateBtn->setVisible(!is_onroad);
  } else {
    params.remove("OsmLocal");
    osmUpdateBtn->setVisible(false);
  }
  osmUpdateLbl->setVisible(is_onroad);
  osmDownloadBtn->setEnabled(!is_onroad);

  // download update
  QString updater_state = QString::fromStdString(params.get("UpdaterState"));
  bool failed = std::atoi(params.get("UpdateFailedCount").c_str()) > 0;
  if (updater_state != "idle") {
    downloadBtn->setEnabled(false);
    downloadBtn->setValue(updater_state);
  } else {
    if (failed) {
      downloadBtn->setText("CHECK");
      downloadBtn->setValue("failed to check for update");
    } else if (params.getBool("UpdaterFetchAvailable")) {
      downloadBtn->setText("DOWNLOAD");
      downloadBtn->setValue("update available");
    } else {
      QString lastUpdate = "never";
      auto tm = params.get("LastUpdateTime");
      if (!tm.empty()) {
        lastUpdate = timeAgo(QDateTime::fromString(QString::fromStdString(tm + "Z"), Qt::ISODate));
      }
      downloadBtn->setText("CHECK");
      downloadBtn->setValue("up to date, last checked " + lastUpdate);
    }
    downloadBtn->setEnabled(true);
  }
  targetBranchBtn->setValue(QString::fromStdString(params.get("UpdaterTargetBranch")));
  osmDownloadBtn->setValue(QString::fromStdString(params.get("OsmLocationTitle")));

  // current + new versions
  versionLbl->setText(QString::fromStdString(params.get("UpdaterCurrentDescription")));
  versionLbl->setDescription(QString::fromStdString(params.get("UpdaterCurrentReleaseNotes")));

  installBtn->setVisible(!is_onroad && params.getBool("UpdateAvailable"));
  installBtn->setValue(QString::fromStdString(params.get("UpdaterNewDescription")));
  installBtn->setDescription(QString::fromStdString(params.get("UpdaterNewReleaseNotes")));

  update();
}
