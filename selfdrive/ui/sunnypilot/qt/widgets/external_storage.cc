/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/widgets/external_storage.h"

#include <QProcess>
#include <QCoreApplication>
#include <QShowEvent>
#include <QTimer>
#include <QtConcurrent>

#include "common/params.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/sunnypilot/ui.h"

ExternalStorageControl::ExternalStorageControl() :
  ButtonControl(tr("External Storage"), "", tr("Extend your comma device's storage by inserting a USB drive into the aux port.")) {

  QObject::connect(this, &ButtonControl::clicked, [=]() {
    if (text() == tr("CHECK") || text() == tr("MOUNT")) {
      mountStorage();
    } else if (text() == tr("UNMOUNT")) {
      unmountStorage();
    } else if (text() == tr("FORMAT")) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to format this drive? This will erase all data."), tr("Format"), this)) {
        formatStorage();
      }
    }
  });

  QObject::connect(uiState(), &UIState::offroadTransition, this, &ExternalStorageControl::updateState);
  updateState(!uiState()->scene.started);

  refresh();
}

void ExternalStorageControl::updateState(bool offroad) {
  setEnabled(offroad);
}

void ExternalStorageControl::debouncedRefresh() {
  if (refreshPending) return;
  refreshPending = true;

  QTimer::singleShot(250, this, [=]() {
    refreshPending = false;
    refresh();
  });
}

void ExternalStorageControl::refresh() {
  QtConcurrent::run([=]() {
    auto run = [](const QString &cmd) {
      QProcess p;
      p.start("sh", QStringList() << "-c" << cmd);
      p.waitForFinished();
      return p.exitCode() == 0;
    };

    bool isMounted = run("findmnt -n /mnt/external_realdata");
    bool hasDrive = run("lsblk -f /dev/sdg");
    bool hasFs = run("lsblk -f /dev/sdg1 | grep -q ext4");
    bool hasLabel = run("sudo blkid /dev/sdg1 | grep -q 'LABEL=\"openpilot\"'");

    QString info;
    if (isMounted && hasLabel) {
      QProcess df;
      df.start("sh", QStringList() << "-c" << "df -h /mnt/external_realdata | awk 'NR==2 {print $3 \"/\" $2}'");
      df.waitForFinished();
      info = df.readAllStandardOutput().trimmed();
    }

    QMetaObject::invokeMethod(this, [=]() {
      if (formatting) {
        setValue(tr("formatting"));
        setText(tr("FORMAT"));
        setEnabled(false);
      } else {
        if (!hasDrive) {
          setValue(tr("insert drive"));
          setText(tr("CHECK"));
        } else if (!hasFs || !hasLabel) {
          setValue(tr("needs format"));
          setText(tr("FORMAT"));
        } else if (isMounted) {
          setValue(info);
          setText(tr("UNMOUNT"));
        } else {
          setValue("drive detected");
          setText(tr("MOUNT"));
        }
        updateState(!uiState()->scene.started);
      }
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::mountStorage() {
  setValue(tr("mounting"));
  setEnabled(false);

  QtConcurrent::run([=]() {
    QProcess process;
    process.start("sh", QStringList() << "-c" <<
      "sudo mount -o remount,rw / && "
      "sudo mkdir -p /mnt/external_realdata && "
      "grep -q '/dev/sdg1 /mnt/external_realdata' /etc/fstab || "
      "echo '/dev/sdg1 /mnt/external_realdata ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab && "
      "sudo systemctl daemon-reexec && "
      "sudo mount /mnt/external_realdata && "
      "sudo chown -R comma:comma /mnt/external_realdata && "
      "sudo chmod -R 775 /mnt/external_realdata && "
      "sudo mount -o remount,ro /");
    process.waitForFinished();

    QMetaObject::invokeMethod(this, [=]() {
      debouncedRefresh();
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::unmountStorage() {
  setValue(tr("unmounting"));
  setEnabled(false);

  QtConcurrent::run([=]() {
    QProcess process;
    process.start("sh", QStringList() << "-c" << "sudo umount /mnt/external_realdata");
    process.waitForFinished();

    QMetaObject::invokeMethod(this, [=]() {
      debouncedRefresh();
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::formatStorage() {
  unmountStorage();
  formatting = true;
  setValue(tr("formatting"));
  setEnabled(false);

  QProcess *process = new QProcess(this);
  connect(process, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
          this, [=](int exitCode, QProcess::ExitStatus status) {
            process->deleteLater();
            formatting = false;
            if (exitCode == 0 && status == QProcess::NormalExit) {
              mountStorage();
            } else {
              setValue(tr("needs format"));
              updateState(!uiState()->scene.started);
            }
          });
  process->start("sh", QStringList() << "-c" <<
    "sudo wipefs -a /dev/sdg && "
    "sudo parted -s /dev/sdg mklabel gpt mkpart primary ext4 0% 100% && "
    "sudo mkfs.ext4 -F -L openpilot /dev/sdg1"
  );
}

void ExternalStorageControl::showEvent(QShowEvent *event) {
  ButtonControl::showEvent(event);
  QTimer::singleShot(100, this, &ExternalStorageControl::debouncedRefresh);
}
