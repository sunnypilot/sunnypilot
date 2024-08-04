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

#include "selfdrive/ui/sunnypilot/qt/onroad/onroad_home.h"


#ifdef ENABLE_MAPS
#include "selfdrive/ui/sunnypilot/qt/maps/map_helpers.h"
#include "selfdrive/ui/qt/maps/map_panel.h"
#endif
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/onroad/onroad_settings_panel.h"
#endif

#include "common/swaglog.h"
#include "selfdrive/ui/qt/util.h"

OnroadWindowSP::OnroadWindowSP(QWidget *parent) : OnroadWindow(parent) {
  // QObject::disconnect(uiState(), &UIState::uiUpdate, this, &OnroadWindow::updateState);
  // QObject::disconnect(uiState(), &UIState::offroadTransition, this, &OnroadWindow::offroadTransition);

  if (getenv("MAP_RENDER_VIEW")) {
    CameraWidget *map_render = new CameraWidget("navd", VISION_STREAM_MAP, false, this);
    split->insertWidget(0, map_render); //TODO: We MIGHT  to override the split variable because it is added on onroad_home.cc and we need to access it before. I am not sure so we will need to test it before 
  }
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &OnroadWindowSP::updateState);
  QObject::connect(uiStateSP(), &UIStateSP::offroadTransition, this, &OnroadWindowSP::offroadTransition);
}

void OnroadWindowSP::updateState(const UIStateSP &s) {
  if (!s.scene.started) {
    return;
  }

  if (s.scene.map_on_left || s.scene.mapbox_fullscreen) {
    split->setDirection(QBoxLayout::LeftToRight);
  } else {
    split->setDirection(QBoxLayout::RightToLeft);
  }
  
  OnroadWindow::updateState(s); // Carry on with the parent class updateState method
}


void OnroadWindowSP::mousePressEvent(QMouseEvent* e) {
#ifdef ENABLE_MAPS
  UIStateSP *s = uiStateSP();
  UISceneSP &scene = s->scene;
  if (map != nullptr && !isOnroadSettingsVisible()) {
    if (wakeScreenTimeout()) {
      // Switch between map and sidebar when using navigate on openpilot
      bool sidebarVisible = geometry().x() > 0;
      bool show_map = uiStateSP()->scene.navigate_on_openpilot_deprecated ? sidebarVisible : !sidebarVisible;
      updateMapSize(scene);
      map->setVisible(show_map && !map->isVisible());
    }
  }
#endif
  if (onroad_settings != nullptr && !isMapVisible()) {
    if (wakeScreenTimeout()) {
      onroad_settings->setVisible(false);
    }
  }
  // propagation event to parent(HomeWindow)
  QWidget::mousePressEvent(e);
}

void OnroadWindowSP::createMapWidget() {
#ifdef ENABLE_MAPS
  LOGD("Creating map widget");
  auto m = new MapPanel(get_mapbox_settings());
  map = m;

  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindowSP::mapPanelRequested);
  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindowSP::onroadSettingsPanelNotRequested);
  QObject::connect(nvg->map_settings_btn, &MapSettingsButton::clicked, m, &MapPanel::toggleMapSettings);
  nvg->map_settings_btn->setEnabled(true);

  m->setFixedWidth(uiStateSP()->scene.mapbox_fullscreen ? topWidget(this)->width() :
                                                        topWidget(this)->width() / 2 - UI_BORDER_SIZE);
  split->insertWidget(0, m);

  // hidden by default, made visible when navRoute is published
  m->setVisible(false);
#endif
}

void OnroadWindowSP::createOnroadSettingsWidget() {
  auto os = new OnroadSettingsPanel(this);
  onroad_settings = os;

  QObject::connect(os, &OnroadSettingsPanel::onroadSettingsPanelRequested, this, &OnroadWindowSP::onroadSettingsPanelRequested);
  QObject::connect(os, &OnroadSettingsPanel::onroadSettingsPanelRequested, this, &OnroadWindowSP::mapPanelNotRequested);
  QObject::connect(nvg->onroad_settings_btn, &OnroadSettingsButton::clicked, os, &OnroadSettingsPanel::toggleOnroadSettings);
  nvg->onroad_settings_btn->setEnabled(true);

  os->setFixedWidth(topWidget(this)->width() / 2.6 - UI_BORDER_SIZE);
  split->insertWidget(0, os);

  // hidden by default
  os->setVisible(false);
}

void OnroadWindowSP::offroadTransition(bool offroad) {

  if (!offroad) {
#ifdef ENABLE_MAPS
    LOGD("We'd like to create the map widget, the condition is map is [%s] and hasPrime is [%s] and MAPBOX_TOKEN is [%s]", map == nullptr ? "null" : "not null", uiStateSP()->hasPrime() ? "true" : "false", MAPBOX_TOKEN.isEmpty()  ? "empty" : "not empty");
    if (map == nullptr && (uiStateSP()->hasPrime() || !MAPBOX_TOKEN.isEmpty())) {
      createMapWidget();
    }
#else
    LOGD("Maps are disabled");
#endif
    if (onroad_settings == nullptr) {
      createOnroadSettingsWidget();
    }
  }

  OnroadWindow::offroadTransition(offroad); // Carry on with the parent class offroadTransition method
}

void OnroadWindowSP::updateMapSize(const UISceneSP &scene) {
  map->setFixedWidth(scene.mapbox_fullscreen ? topWidget(this)->width() :
                                               topWidget(this)->width() / 2 - UI_BORDER_SIZE);
  split->insertWidget(0, map);
}

void OnroadWindowSP::primeChanged(bool prime) {
#ifdef ENABLE_MAPS
  if (map && (!prime && MAPBOX_TOKEN.isEmpty())) {
    nvg->map_settings_btn->setEnabled(false);
    nvg->map_settings_btn->setVisible(false);
    map->deleteLater();
    map = nullptr;
  } else if (!map && (prime || !MAPBOX_TOKEN.isEmpty())) {
    createMapWidget();
  }
#endif
}
