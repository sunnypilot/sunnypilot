#include "selfdrive/ui/sunnypilot/qt/sp_priv_home.h"

#include <QHBoxLayout>
#include <QMouseEvent>
#include <QStackedWidget>
#include <QVBoxLayout>

#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/prime.h"

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
  HomeWindow::mousePressEvent(e); // We call it first so that we could potentially override whatever was done by parent
  
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
    if (onroad->wakeScreenTimeout()) {
      sidebar->setVisible(!sidebar->isVisible() && !onroad->isMapVisible());
    }
  }
}
