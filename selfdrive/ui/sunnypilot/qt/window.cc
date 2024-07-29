/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "window.h"

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
