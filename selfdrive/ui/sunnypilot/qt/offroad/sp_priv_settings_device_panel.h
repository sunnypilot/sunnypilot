#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/sp_priv_settings.h"

class DevicePanelSP : public DevicePanel {
  Q_OBJECT
public:
  explicit DevicePanelSP(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

private slots:
  void onPinFileChanged(const QString &file_path);
  void refreshPin();
  void forceoffroad();

  void updateLabels();

private:
  ButtonControl *fleetManagerPin;
  QString pin_title = tr("Fleet Manager PIN:") + " ";
  QString pin = "OFF";
  QFileSystemWatcher *fs_watch;

  QPushButton *offroad_btn;
};