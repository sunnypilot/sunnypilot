#pragma once

#include "selfdrive/ui/qt/onroad/onroad_home.h"

#include "common/params.h"
#include "selfdrive/ui/qt/onroad/alerts.h"
// #include "selfdrive/ui/sunnypilot/qt/onroad/sp_priv_annotated_camera.h"


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
  // AnnotatedCameraWidgetSP *nvg;
  QWidget *map = nullptr;
  QWidget *onroad_settings = nullptr;

  Params params;

protected slots:
  void offroadTransition(bool offroad) override;
  void updateState(const UIStateSP &s) override;
  void primeChanged(bool prime);
  void updateMapSize(const UISceneSP &scene);
};
