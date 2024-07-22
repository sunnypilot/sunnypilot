#include "sp_priv_window.h"

MainWindowSP::MainWindowSP(QWidget *parent) : MainWindow(parent, new HomeWindowSP(parent), 
                                                         new SettingsWindowSP(parent), new OnboardingWindowSP(parent)) {
  homeWindow = dynamic_cast<HomeWindowSP*>(MainWindow::homeWindow);
  settingsWindow = dynamic_cast<SettingsWindowSP*>(MainWindow::settingsWindow);
  onboardingWindow = dynamic_cast<OnboardingWindowSP*>(MainWindow::onboardingWindow);
}

void MainWindowSP::closeSettings() {
  MainWindow::closeSettings();
  if (uiState()->scene.started) {
    homeWindow->showSidebar(false);
    if (uiStateSP()->scene.navigate_on_openpilot_deprecated) {
      homeWindow->showMapPanel(true);
    }
  }
}

