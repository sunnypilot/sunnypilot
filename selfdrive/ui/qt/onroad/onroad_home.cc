#include "selfdrive/ui/qt/onroad/onroad_home.h"

#include <QPainter>
#include <QStackedLayout>

#ifdef ENABLE_MAPS
#include "selfdrive/ui/qt/maps/map_helpers.h"
#include "selfdrive/ui/qt/maps/map_panel.h"
#endif
#include "selfdrive/ui/qt/onroad_settings_panel.h"

#include "selfdrive/ui/qt/util.h"

OnroadWindow::OnroadWindow(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout  = new QVBoxLayout(this);
  main_layout->setMargin(UI_BORDER_SIZE);
  QStackedLayout *stacked_layout = new QStackedLayout;
  stacked_layout->setStackingMode(QStackedLayout::StackAll);
  main_layout->addLayout(stacked_layout);

  nvg = new AnnotatedCameraWidget(VISION_STREAM_ROAD, this);

  QWidget * split_wrapper = new QWidget;
  split = new QHBoxLayout(split_wrapper);
  split->setContentsMargins(0, 0, 0, 0);
  split->setSpacing(0);
  split->addWidget(nvg);

  if (getenv("DUAL_CAMERA_VIEW")) {
    CameraWidget *arCam = new CameraWidget("camerad", VISION_STREAM_ROAD, true, this);
    split->insertWidget(0, arCam);
  }

  if (getenv("MAP_RENDER_VIEW")) {
    CameraWidget *map_render = new CameraWidget("navd", VISION_STREAM_MAP, false, this);
    split->insertWidget(0, map_render);
  }

  stacked_layout->addWidget(split_wrapper);

  alerts = new OnroadAlerts(this);
  alerts->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(alerts);

  // setup stacking order
  alerts->raise();

  setAttribute(Qt::WA_OpaquePaintEvent);
  QObject::connect(uiState(), &UIState::uiUpdate, this, &OnroadWindow::updateState);
  QObject::connect(uiState(), &UIState::offroadTransition, this, &OnroadWindow::offroadTransition);
  QObject::connect(uiState(), &UIState::primeChanged, this, &OnroadWindow::primeChanged);
}

void OnroadWindow::updateState(const UIState &s) {
  if (!s.scene.started) {
    return;
  }

  if (s.scene.map_on_left || s.scene.mapbox_fullscreen) {
    split->setDirection(QBoxLayout::LeftToRight);
  } else {
    split->setDirection(QBoxLayout::RightToLeft);
  }

  alerts->updateState(s);
  nvg->updateState(s);

  QColor bgColor = bg_colors[s.status];
  if (bg != bgColor) {
    // repaint border
    bg = bgColor;
    update();
  }
}


void OnroadWindow::mousePressEvent(QMouseEvent* e) {
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
  if (onroad_settings != nullptr && !isMapVisible()) {
    if (wakeScreenTimeout()) {
      onroad_settings->setVisible(false);
    }
  }
  // propagation event to parent(HomeWindow)
  QWidget::mousePressEvent(e);
}

void OnroadWindow::createMapWidget() {
#ifdef ENABLE_MAPS
  auto m = new MapPanel(get_mapbox_settings());
  map = m;

  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindow::mapPanelRequested);
  QObject::connect(m, &MapPanel::mapPanelRequested, this, &OnroadWindow::onroadSettingsPanelNotRequested);
  QObject::connect(nvg->map_settings_btn, &MapSettingsButton::clicked, m, &MapPanel::toggleMapSettings);
  nvg->map_settings_btn->setEnabled(true);

  m->setFixedWidth(uiState()->scene.mapbox_fullscreen ? topWidget(this)->width() :
                                                        topWidget(this)->width() / 2 - UI_BORDER_SIZE);
  split->insertWidget(0, m);

  // hidden by default, made visible when navRoute is published
  m->setVisible(false);
#endif
}

void OnroadWindow::createOnroadSettingsWidget() {
  auto os = new OnroadSettingsPanel(this);
  onroad_settings = os;

  QObject::connect(os, &OnroadSettingsPanel::onroadSettingsPanelRequested, this, &OnroadWindow::onroadSettingsPanelRequested);
  QObject::connect(os, &OnroadSettingsPanel::onroadSettingsPanelRequested, this, &OnroadWindow::mapPanelNotRequested);
  QObject::connect(nvg->onroad_settings_btn, &OnroadSettingsButton::clicked, os, &OnroadSettingsPanel::toggleOnroadSettings);
  nvg->onroad_settings_btn->setEnabled(true);

  os->setFixedWidth(topWidget(this)->width() / 2.6 - UI_BORDER_SIZE);
  split->insertWidget(0, os);

  // hidden by default
  os->setVisible(false);
}

void OnroadWindow::offroadTransition(bool offroad) {
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

  alerts->clear();
}

void OnroadWindow::updateMapSize(const UIScene &scene) {
  map->setFixedWidth(scene.mapbox_fullscreen ? topWidget(this)->width() :
                                               topWidget(this)->width() / 2 - UI_BORDER_SIZE);
  split->insertWidget(0, map);
}

void OnroadWindow::primeChanged(bool prime) {
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

void OnroadWindow::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.fillRect(rect(), QColor(bg.red(), bg.green(), bg.blue(), 255));
}
