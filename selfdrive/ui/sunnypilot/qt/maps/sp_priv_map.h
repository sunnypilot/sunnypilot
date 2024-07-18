#pragma once

#include "selfdrive/ui/qt/maps/map.h"

#include <QColor>

class MapWindowSP : public MapWindow {
  Q_OBJECT

public:
  explicit MapWindowSP(const QMapLibre::Settings &settings) : MapWindow(settings) {}

private:
  void initLayers();
  // Blue with normal nav, green when nav is input into the model
  QColor getNavPathColor(bool nav_enabled) {
    return nav_enabled ? QColor("#31ee73") : QColor("#31a1ee");
  }

protected slots:
  void updateState(const UIState &s);

public slots:
  void offroadTransition(bool offroad);
};
