#pragma once

#include <map>
#include <string>

#include <QButtonGroup>
#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QStackedWidget>
#include <QTimer>
#include <QWidget>

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#endif

// ********** settings window + top-level panels **********
class SettingsWindow : public QFrame {
  Q_OBJECT

public:
  explicit SettingsWindow(QWidget *parent = 0);
  void setCurrentPanel(int index, const QString &param = "");

protected:
  void showEvent(QShowEvent *event) override;

signals:
  void closeSettings();
  void reviewTrainingGuide();
  void showDriverView();
  void expandToggleDescription(const QString &param);

protected:
  QPushButton *sidebar_alert_widget;
  QWidget *sidebar_widget;
  QButtonGroup *nav_btns;
  QStackedWidget *panel_widget;
};

class DevicePanel : public ListWidget {
  Q_OBJECT
public:
  explicit DevicePanel(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

signals:
  void reviewTrainingGuide();
  void showDriverView();

private slots:
  void poweroff();
  void reboot();
  void updateCalibDescription();
  void onPinFileChanged(const QString &file_path);
  void refreshPin();
  void forceoffroad();

  void updateLabels();

private:
  Params params;
  ButtonControl *pair_device;

  ButtonControl *fleetManagerPin;
  QString pin_title = tr("Fleet Manager PIN:") + " ";
  QString pin = "OFF";
  QFileSystemWatcher *fs_watch;

  QPushButton *offroad_btn;
};

class TogglesPanel : public ListWidget {
  Q_OBJECT
public:
  explicit TogglesPanel(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

public slots:
  void expandToggleDescription(const QString &param);

protected slots:
  virtual void updateState(const UIState &s);

protected:
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ButtonParamControl *long_personality_setting;

  virtual void updateToggles();
};

class SoftwarePanel : public ListWidget {
  Q_OBJECT
public:
  explicit SoftwarePanel(QWidget* parent = nullptr);

protected:
  void showEvent(QShowEvent *event) override;
  virtual void updateLabels();
  void checkForUpdates();

  bool is_onroad = false;

  QLabel *onroadLbl;
  LabelControl *currentModelLbl;
  LabelControl *versionLbl;
  ButtonControl *installBtn;
  ButtonControl *downloadBtn;
  ButtonControl *targetBranchBtn;

  Params params;
  ParamWatcher *fs_watch;
};
