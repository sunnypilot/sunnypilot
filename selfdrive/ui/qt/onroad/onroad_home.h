#pragma once

#include "common/params.h"
#include "selfdrive/ui/qt/onroad/alerts.h"
#include "selfdrive/ui/qt/onroad/annotated_camera.h"

class OnroadWindow : public QWidget {
  Q_OBJECT

public:
  OnroadWindow(QWidget* parent = 0);
  bool isMapVisible() const { return map && map->isVisible(); }
  void showMapPanel(bool show) { if (map) map->setVisible(show); }

  bool isOnroadSettingsVisible() const { return onroad_settings && onroad_settings->isVisible(); }
  bool isMapAvailable() const { return map; }
  void mapPanelNotRequested() { if (map) map->setVisible(false); }
  void onroadSettingsPanelNotRequested() { if (onroad_settings) onroad_settings->setVisible(false); }

  bool wakeScreenTimeout() {
    if ((uiState()->scene.sleep_btn != 0 && uiState()->scene.sleep_btn_opacity != 0) ||
        (uiState()->scene.sleep_time != 0 && uiState()->scene.onroadScreenOff != -2)) {
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
  void paintEvent(QPaintEvent *event);
  void mousePressEvent(QMouseEvent* e) override;
  OnroadAlerts *alerts;
  AnnotatedCameraWidget *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QWidget *map = nullptr;
  QWidget *onroad_settings = nullptr;
  QHBoxLayout* split;

  Params params;

private slots:
  void offroadTransition(bool offroad);
  void primeChanged(bool prime);
  void updateState(const UIState &s);
  void updateMapSize(const UIScene &scene);
};
