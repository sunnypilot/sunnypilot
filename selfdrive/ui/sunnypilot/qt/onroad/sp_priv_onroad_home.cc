#include "selfdrive/ui/sunnypilot/qt/onroad/sp_priv_onroad_home.h"

#include <QPainter>
#include <QStackedLayout>

#ifdef ENABLE_MAPS
#include "selfdrive/ui/qt/maps/map_helpers.h"
#include "selfdrive/ui/qt/maps/map_panel.h"
#endif
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/onroad/sp_priv_onroad_settings_panel.h"
#endif

#include "selfdrive/ui/qt/util.h"

OnroadWindowSP::OnroadWindowSP(QWidget *parent) : OnroadWindow(parent) {
  
  if (getenv("MAP_RENDER_VIEW")) {
    CameraWidget *map_render = new CameraWidget("navd", VISION_STREAM_MAP, false, this);
    split->insertWidget(0, map_render); //TODO: We MIGHT  to override the split variable because it is added on onroad_home.cc and we need to access it before. I am not sure so we will need to test it before 
  }
  QObject::connect(uiState(), &UIState::primeChanged, this, &OnroadWindowSP::primeChanged);
}

void OnroadWindowSP::updateState(const UIState &s) {
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
  UIState *s = uiState();
  UIScene &scene = s->scene;
  if (map != nullptr && !isOnroadSettingsVisible()) {
    if (wakeScreenTimeout()) {
      // Switch between map and sidebar when using navigate on openpilot
      bool sidebarVisible = geometry().x() > 0;
      bool show_map = uiState()->scene.navigate_on_openpilot_deprecated ? sidebarVisible : !sidebarVisible;
      updateMapSize(scene);
      map->setVisible(show_map && !map->isVisible());
    }
  }
#endif
#ifdef SUNNYPILOT
  if (onroad_settings != nullptr && !isMapVisible()) {
    if (wakeScreenTimeout()) {
      onroad_settings->setVisible(false);
    }
  }
  // propagation event to parent(HomeWindow)
  QWidget::mousePressEvent(e);
#endif
}

void OnroadWindowSP::createMapWidget() {
#ifdef ENABLE_MAPS
  auto m = new MapPanel(get_mapbox_settings());
  map = m;

  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindowSP::mapPanelRequested);
  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindowSP::onroadSettingsPanelNotRequested);
  QObject::connect(nvg->map_settings_btn, &MapSettingsButton::clicked, m, &MapPanel::toggleMapSettings);
  nvg->map_settings_btn->setEnabled(true);

  m->setFixedWidth(uiState()->scene.mapbox_fullscreen ? topWidget(this)->width() :
                                                        topWidget(this)->width() / 2 - UI_BORDER_SIZE);
  split->insertWidget(0, m);

  // hidden by default, made visible when navRoute is published
  m->setVisible(false);
#endif
}

void OnroadWindowSP::createOnroadSettingsWidget() {
#ifdef SUNNYPILOT
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
#endif
}

void OnroadWindowSP::offroadTransition(bool offroad) {
  if (!offroad) {
#ifdef ENABLE_MAPS
    if (map == nullptr && (uiState()->hasPrime() || !MAPBOX_TOKEN.isEmpty())) {
      createMapWidget();
    }
#endif
    if (onroad_settings == nullptr) {
      createOnroadSettingsWidget();
    }
  }

  OnroadWindow::offroadTransition(offroad); // Carry on with the parent class offroadTransition method
}

void OnroadWindowSP::updateMapSize(const UIScene &scene) {
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
