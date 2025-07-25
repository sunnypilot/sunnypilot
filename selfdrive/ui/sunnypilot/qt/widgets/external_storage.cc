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

ExternalStorageControl::ExternalStorageControl() :
  ButtonControl(tr("External Storage"), "", tr("Extend your comma device's storage by inserting a USB drive into the aux port.")) {

  QObject::connect(this, &ButtonControl::clicked, [=]() {
    if (text() == tr("CHECK")) {
      setText(tr("checking"));
      setEnabled(false);
      mountStorage();
    } else if (text() == tr("MOUNT")) {
      setText(tr("mounting"));
      setEnabled(false);
      mountStorage();
    } else if (text() == tr("UNMOUNT")) {
      setText(tr("unmounting"));
      setEnabled(false);
      unmountStorage();
    } else if (text() == tr("FORMAT")) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to format this drive? This will erase all data."), tr("Format"), this)) {
        formatStorage();
      }
    }
  });
  refresh();
}

void ExternalStorageControl::refresh() {
  QProcess *mntCheck = new QProcess(this);
  connect(mntCheck, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished), this, [=](int, QProcess::ExitStatus) {
    bool isMounted = !mntCheck->readAllStandardOutput().trimmed().isEmpty();
    mntCheck->deleteLater();

    QProcess *fsCheck = new QProcess(this);
    connect(fsCheck, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished), this, [=](int, QProcess::ExitStatus) {
      bool hasFs = fsCheck->exitCode() == 0;
      fsCheck->deleteLater();

      if (!hasFs) {
        setValue(tr("insert drive"));
        setText(tr("CHECK"));
        setEnabled(true);
        return;
      }

      QProcess *labelCheck = new QProcess(this);
      connect(labelCheck, static_cast<void(QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished), this, [=](int, QProcess::ExitStatus) {
        bool isInit = labelCheck->exitCode() == 0;
        labelCheck->deleteLater();

        if (!isInit) {
          setValue(tr("needs format"));
          setText(tr("FORMAT"));
        } else if (isMounted) {
          QtConcurrent::run([=]() {
            QProcess df;
            df.start("sh", QStringList() << "-c" << "df -h /mnt/external_realdata | awk 'NR==2 {print $3 \"/\" $2}'");
            df.waitForFinished();
            QString info = df.readAllStandardOutput().trimmed();

            QMetaObject::invokeMethod(this, [=]() {
              setValue(info);
              setText(tr("UNMOUNT"));
              setEnabled(true);
            }, Qt::QueuedConnection);
          });
          return;
        } else {
          setValue("");
          setText(tr("MOUNT"));
        }

        setEnabled(true);
      });
      labelCheck->start("sh", QStringList() << "-c" << "sudo blkid /dev/sdg1 | grep -q 'LABEL=\"openpilot\"'");
    });
    fsCheck->start("sh", QStringList() << "-c" << "lsblk -f /dev/sdg1 | grep -q ext4");
  });
  mntCheck->start("sh", QStringList() << "-c" << "findmnt -n /mnt/external_realdata");
}

void ExternalStorageControl::mountStorage() {
  setText(tr("mounting"));
  setEnabled(false);
  QCoreApplication::processEvents();

  QtConcurrent::run([=]() {
    QProcess process;
    process.start("sh", QStringList() << "-c" <<
      "sudo mount -o remount,rw / && "
      "sudo mkdir -p /mnt/external_realdata && "
      "grep -q '/dev/sdg1 /mnt/external_realdata' /etc/fstab || "
      "echo '/dev/sdg1 /mnt/external_realdata ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab && "
      "sudo systemctl daemon-reexec && "
      "sudo chown -R $(whoami):$(whoami) /mnt/external_realdata && "
      "sudo chmod -R 775 /mnt/external_realdata && "
      "sudo mount -o remount,ro / && "
      "sudo mount /mnt/external_realdata");
    process.waitForFinished();

    QMetaObject::invokeMethod(this, [=]() {
      refresh();
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::unmountStorage() {
  setText(tr("unmounting"));
  setEnabled(false);
  QCoreApplication::processEvents();

  QtConcurrent::run([=]() {
    QProcess process;
    process.start("sh", QStringList() << "-c" << "sudo umount /mnt/external_realdata");
    process.waitForFinished();

    QMetaObject::invokeMethod(this, [=]() {
      refresh();
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::formatStorage() {
  setText(tr("unmounting"));
  setEnabled(false);
  QCoreApplication::processEvents();

  QtConcurrent::run([=]() {
    QProcess umount;
    umount.start("sh", QStringList() << "-c" << "sudo umount /mnt/external_realdata");
    umount.waitForFinished();

    QMetaObject::invokeMethod(this, [=]() {
      runFormat();
    }, Qt::QueuedConnection);
  });
}

void ExternalStorageControl::runFormat() {
  setText(tr("formatting"));
  setEnabled(false);
  QCoreApplication::processEvents();

  QtConcurrent::run([=]() {
    QProcess *process = new QProcess();
    process->start("sh", QStringList() << "-c" << "sudo mkfs.ext4 -F /dev/sdg1");
    process->waitForFinished();

    int exitCode = process->exitCode();
    QProcess::ExitStatus exitStatus = process->exitStatus();
    delete process;

    if (exitCode == 0 && exitStatus == QProcess::NormalExit) {
      QProcess::execute("sh", QStringList() << "-c" << "sudo e2label /dev/sdg1 openpilot");
      QMetaObject::invokeMethod(this, [=]() {
        mountStorage();
      }, Qt::QueuedConnection);
    } else {
      QMetaObject::invokeMethod(this, [=]() {
        qWarning() << "Formatting failed with exit code" << exitCode;
        setText(tr("FORMAT"));
        setEnabled(true);
      }, Qt::QueuedConnection);
    }
  });
}

void ExternalStorageControl::showEvent(QShowEvent *event) {
  ButtonControl::showEvent(event);
  QTimer::singleShot(100, this, &ExternalStorageControl::refresh);
}
