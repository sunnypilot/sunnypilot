#pragma once

#include "selfdrive/ui/qt/offroad/settings.h"

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
