#pragma once

#include <map>
#include <string>

#include "selfdrive/ui/qt/offroad/settings.h"

class TogglesPanelSP : public TogglesPanel {
  Q_OBJECT

public:
  explicit TogglesPanelSP(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

private slots:
  void updateState(const UIStateSP &s);

private:
  ButtonParamControlSP *long_personality_setting;
  ButtonParamControlSP *accel_personality_setting;

  ParamWatcher *param_watcher;
  void updateToggles() override;
};

class SettingsWindowSP : public SettingsWindow {
  Q_OBJECT

public:
  explicit SettingsWindowSP(QWidget* parent = nullptr);

protected:
  struct PanelInfo {
    QString name;
    QWidget *widget;
    QString icon;

    PanelInfo(const QString &name, QWidget *widget, const QString &icon) : name(name), widget(widget), icon(icon) {}
  };
};
