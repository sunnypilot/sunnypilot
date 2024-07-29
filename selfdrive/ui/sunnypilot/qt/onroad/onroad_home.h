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

#pragma once

#include "selfdrive/ui/qt/onroad/onroad_home.h"

#include "common/params.h"

class OnroadWindowSP : public OnroadWindow {
  Q_OBJECT

public:
  OnroadWindowSP(QWidget* parent = 0);
  bool isMapVisible() const { return map && map->isVisible(); }
  void showMapPanel(bool show) { if (map) map->setVisible(show); }

  bool isOnroadSettingsVisible() const { return onroad_settings && onroad_settings->isVisible(); }
  bool isMapAvailable() const { return map; }
  void mapPanelNotRequested() { if (map) map->setVisible(false); }
  void onroadSettingsPanelNotRequested() { if (onroad_settings) onroad_settings->setVisible(false); }

  bool wakeScreenTimeout() {
    if ((uiStateSP()->scene.sleep_btn != 0 && uiStateSP()->scene.sleep_btn_opacity != 0) ||
        (uiStateSP()->scene.sleep_time != 0 && uiStateSP()->scene.onroadScreenOff != -2)) {
      return true;
        }
    return false;
  }

signals:
  void mapPanelRequested();
  void onroadSettingsPanelRequested();

private:
  void createMapWidget();
  void createOnroadSettingsWidget();
  void mousePressEvent(QMouseEvent* e) override;
  QWidget *map = nullptr;
  QWidget *onroad_settings = nullptr;

  Params params;

protected slots:
  void offroadTransition(bool offroad) override;
  void updateState(const UIStateSP &s) override;
  void primeChanged(bool prime);
  void updateMapSize(const UISceneSP &scene);
};
