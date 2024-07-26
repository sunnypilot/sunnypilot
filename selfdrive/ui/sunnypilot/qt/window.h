#pragma once

#include "selfdrive/ui/qt/window.h"
#include "selfdrive/ui/sunnypilot/qt/home.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "offroad/settings/onboarding.h"

class MainWindowSP : public MainWindow {
    Q_OBJECT

public:
explicit MainWindowSP(QWidget *parent = 0);

private:
    HomeWindowSP *homeWindow;
    SettingsWindowSP *settingsWindow;
    OnboardingWindowSP *onboardingWindow;
    void closeSettings() override;
};
