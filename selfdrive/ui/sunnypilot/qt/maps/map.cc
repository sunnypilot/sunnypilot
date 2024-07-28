#include "selfdrive/ui/sunnypilot/qt/maps/map.h"

#include "common/swaglog.h"
#include "selfdrive/ui/sunnypilot/qt/maps/map_helpers.h"

MapWindowSP::MapWindowSP(const QMapLibre::Settings &settings) : MapWindow(settings) {
  QObject::disconnect(uiState(), &UIState::uiUpdate, this, &MapWindow::updateState);
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &MapWindowSP::updateState);
}

MapWindowSP::~MapWindowSP() {
  makeCurrent();
}

void MapWindowSP::initLayers() {
  if (!m_map->layerExists("navLayer")) {
    m_map->setPaintProperty("navLayer", "line-color", getNavPathColor(uiStateSP()->scene.navigate_on_openpilot_deprecated));
  }
  if ((!m_map->layerExists("buildingsLayer")) && uiStateSP()->scene.map_3d_buildings) {  // Could put this behind the cellular metered toggle in case it increases data usage
    qDebug() << "Initializing buildingsLayer";
    QVariantMap buildings;
    buildings["id"] = "buildingsLayer";
    buildings["source"] = "composite";
    buildings["source-layer"] = "building";
    buildings["type"] = "fill-extrusion";
    buildings["minzoom"] = 15;
    m_map->addLayer("buildingsLayer", buildings);
    m_map->setFilter("buildingsLayer", QVariantList({"==", "extrude", "true"}));

    QVariantList fillExtrusionHeight = {  // scale buildings as you zoom in
      "interpolate",
      QVariantList{"linear"},
      QVariantList{"zoom"},
      15, 0,
      15.05, QVariantList{"get", "height"}
    };

    QVariantList fillExtrusionBase = {
      "interpolate",
      QVariantList{"linear"},
      QVariantList{"zoom"},
      15, 0,
      15.05, QVariantList{"get", "min_height"}
    };

    QVariantList fillExtrusionOpacity = {
      "interpolate",
      QVariantList{"linear"},
      QVariantList{"zoom"},
      15, 0, // transparent at zoom level 15
      15.5, .6, // fade in
      17, .6, // begin fading out
      20, 0 // fade out when zoomed in
    };

    m_map->setPaintProperty("buildingsLayer", "fill-extrusion-color", QColor("grey"));
    m_map->setPaintProperty("buildingsLayer", "fill-extrusion-opacity", fillExtrusionOpacity);
    m_map->setPaintProperty("buildingsLayer", "fill-extrusion-height", fillExtrusionHeight);
    m_map->setPaintProperty("buildingsLayer", "fill-extrusion-base", fillExtrusionBase);
    m_map->setLayoutProperty("buildingsLayer", "visibility", "visible");
  }
}

void MapWindowSP::updateState(const UIStateSP &s) {
  MapWindow::updateState(s);
  const SubMaster &sm = *(s.sm);

  if (sm.updated("modelV2")) {
    // set path color on change, and show map on rising edge of navigate on openpilot
    auto car_control = sm["carControl"].getCarControl();
    bool nav_enabled = sm["modelV2"].getModelV2().getNavEnabledDEPRECATED() &&
                       (sm["controlsState"].getControlsState().getEnabled() || car_control.getLatActive() || car_control.getLongActive());
    if (nav_enabled != uiStateSP()->scene.navigate_on_openpilot_deprecated) {
      if (loaded_once) {
        m_map->setPaintProperty("navLayer", "line-color", getNavPathColor(nav_enabled));
      }
      if (nav_enabled) {
        emit requestVisible(true);
      }
    }
    uiStateSP()->scene.navigate_on_openpilot_deprecated = nav_enabled;
  }
}

void MapWindowSP::offroadTransition(bool offroad) {
  if (offroad) {
    uiStateSP()->scene.navigate_on_openpilot_deprecated = false;
  }

  MapWindow::offroadTransition(offroad);
}
