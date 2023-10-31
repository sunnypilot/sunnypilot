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


#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"

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

private:
  QPushButton *sidebar_alert_widget;
  QWidget *sidebar_widget;
  QButtonGroup *nav_btns;
  QStackedWidget *panel_widget;

  struct PanelInfo {
    QString name;
    QWidget *widget;
    QString icon;

    PanelInfo(const QString &name, QWidget *widget, const QString &icon) : name(name), widget(widget), icon(icon) {}
  };
};

class DevicePanel : public ListWidget {
  Q_OBJECT
public:
  explicit DevicePanel(SettingsWindow *parent);
signals:
  void reviewTrainingGuide();
  void showDriverView();

private slots:
  void poweroff();
  void reboot();
  void updateCalibDescription();
  void onPinFileChanged(const QString &file_path);
  void refreshPin();

private:
  Params params;

  ButtonControl *fleetManagerPin;
  const char *pin_title = "Fleet Manager PIN: ";
  QString pin = "OFF";
  QFileSystemWatcher *fs_watch;
};

class TogglesPanel : public ListWidget {
  Q_OBJECT
public:
  explicit TogglesPanel(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

public slots:
  void expandToggleDescription(const QString &param);
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ButtonParamControl *long_personality_setting;

  ParamWatcher *param_watcher;
};

class SoftwarePanel : public ListWidget {
  Q_OBJECT
public:
  explicit SoftwarePanel(QWidget* parent = nullptr);

private:
  void showEvent(QShowEvent *event) override;
  void updateLabels();
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
