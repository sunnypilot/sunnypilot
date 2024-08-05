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

#include "selfdrive/ui/sunnypilot/qt/home.h"

#include <QHBoxLayout>
#include <QMouseEvent>
#include <common/swaglog.h>

#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/util.h"

// HomeWindowSP: the container for the offroad and onroad UIs
HomeWindowSP::HomeWindowSP(QWidget* parent) : HomeWindow(parent){    
  QObject::connect(onroad, &OnroadWindow::mapPanelRequested, this, [=] { sidebar->hide(); });
  QObject::connect(onroad, &OnroadWindow::onroadSettingsPanelRequested, this, [=] { sidebar->hide(); });
}

void HomeWindowSP::showMapPanel(bool show) {
  onroad->showMapPanel(show);
}

void HomeWindowSP::updateState(const UIState &s) { //OVERRIDE
  HomeWindow::updateState(s);

  uiStateSP()->scene.map_visible = onroad->isMapVisible();
  uiStateSP()->scene.onroad_settings_visible = onroad->isOnroadSettingsVisible();
}

void HomeWindowSP::mousePressEvent(QMouseEvent* e) {
  // We are not calling the parent for the time being because it only handles sidebar, and the sidebar code conflicts
  //  with ours as we turn off the sidebar after it was turned on by the parent when the tap happens beyond the 300px of the left. 
  // HomeWindow::mousePressEvent(e);  
  
  if (uiStateSP()->scene.started) {
    if (uiStateSP()->scene.onroadScreenOff != -2) {
      uiStateSP()->scene.touched2 = true;
      QTimer::singleShot(500, []() { uiStateSP()->scene.touched2 = false; });
    }
    if (uiStateSP()->scene.button_auto_hide) {
      uiStateSP()->scene.touch_to_wake = true;
      uiStateSP()->scene.sleep_btn_fading_in = true;
      QTimer::singleShot(500, []() { uiStateSP()->scene.touch_to_wake = false; });
    }
  }

  // TODO: a very similar, but not identical call is made by parent. Which made me question if I should override it here... 
  //  Will have to revisit later if this is not behaving as expected. 
  // Handle sidebar collapsing
  if ((onroad->isVisible() || body->isVisible()) && (!sidebar->isVisible() || e->x() > sidebar->width())) {
    LOGD("HomeWindowSP sidebar->isVisible() [%d] | e->x() [%d] | sidebar->width() [%d]", sidebar->isVisible(), e->x(), sidebar->width());
    if (onroad->wakeScreenTimeout()) {
      LOGD("HomeWindowSP wakeScreenTimeout() [%d]", onroad->wakeScreenTimeout());
      sidebar->setVisible(!sidebar->isVisible() && !onroad->isMapVisible());
    }
  }
}
