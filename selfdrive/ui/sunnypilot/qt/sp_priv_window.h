#pragma once

#include "selfdrive/ui/qt/window.h"
#include "selfdrive/ui/sunnypilot/qt/sp_priv_home.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_settings.h"

class MainWindowSP : public MainWindow {
    Q_OBJECT

public:
explicit MainWindowSP(QWidget *parent = 0);

private:
    HomeWindowSP *homeWindow;
    SettingsWindowSP *settingsWindow;
    void closeSettings() override;
};
