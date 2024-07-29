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

#include "selfdrive/ui/sunnypilot/qt/maps/map.h"

#include "common/swaglog.h"
#include "selfdrive/ui/sunnypilot/qt/maps/map_helpers.h"

const float MAX_ZOOM = 17;
const float MIN_ZOOM = 14;
const float MAX_PITCH = 50;

MapWindowSP::MapWindowSP(const QMapLibre::Settings &settings) : MapWindow(settings) {
  QObject::disconnect(uiState(), &UIState::uiUpdate, this, &MapWindow::updateState);
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &MapWindowSP::updateState);
}

MapWindowSP::~MapWindowSP() {
  makeCurrent();
}

void MapWindowSP::initLayers() {
  // This doesn't work from initializeGL
  if (!m_map->layerExists("modelPathLayer")) {
    qDebug() << "Initializing modelPathLayer";
    QVariantMap modelPath;
    //modelPath["id"] = "modelPathLayer";
    modelPath["type"] = "line";
    modelPath["source"] = "modelPathSource";
    m_map->addLayer("modelPathLayer", modelPath);
    m_map->setPaintProperty("modelPathLayer", "line-color", QColor("red"));
    m_map->setPaintProperty("modelPathLayer", "line-width", 5.0);
    m_map->setLayoutProperty("modelPathLayer", "line-cap", "round");
  }
  if (!m_map->layerExists("navLayer")) {
    qDebug() << "Initializing navLayer";
    QVariantMap nav;
    nav["type"] = "line";
    nav["source"] = "navSource";
    m_map->addLayer("navLayer", nav, "road-intersection");

    QVariantMap transition;
    transition["duration"] = 400;  // ms
    m_map->setPaintProperty("navLayer", "line-color", getNavPathColor(uiStateSP()->scene.navigate_on_openpilot_deprecated));
    m_map->setPaintProperty("navLayer", "line-color-transition", transition);
    m_map->setPaintProperty("navLayer", "line-width", 7.5);
    m_map->setLayoutProperty("navLayer", "line-cap", "round");
  }
  if (!m_map->layerExists("pinLayer")) {
    qDebug() << "Initializing pinLayer";
    m_map->addImage("default_marker", QImage("../assets/navigation/default_marker.svg"));
    QVariantMap pin;
    pin["type"] = "symbol";
    pin["source"] = "pinSource";
    m_map->addLayer("pinLayer", pin);
    m_map->setLayoutProperty("pinLayer", "icon-pitch-alignment", "viewport");
    m_map->setLayoutProperty("pinLayer", "icon-image", "default_marker");
    m_map->setLayoutProperty("pinLayer", "icon-ignore-placement", true);
    m_map->setLayoutProperty("pinLayer", "icon-allow-overlap", true);
    m_map->setLayoutProperty("pinLayer", "symbol-sort-key", 0);
    m_map->setLayoutProperty("pinLayer", "icon-anchor", "bottom");
  }
  if (!m_map->layerExists("carPosLayer")) {
    qDebug() << "Initializing carPosLayer";
    m_map->addImage("label-arrow", QImage("../assets/images/triangle.svg"));

    QVariantMap carPos;
    carPos["type"] = "symbol";
    carPos["source"] = "carPosSource";
    m_map->addLayer("carPosLayer", carPos);
    m_map->setLayoutProperty("carPosLayer", "icon-pitch-alignment", "map");
    m_map->setLayoutProperty("carPosLayer", "icon-image", "label-arrow");
    m_map->setLayoutProperty("carPosLayer", "icon-size", 0.5);
    m_map->setLayoutProperty("carPosLayer", "icon-ignore-placement", true);
    m_map->setLayoutProperty("carPosLayer", "icon-allow-overlap", true);
    // TODO: remove, symbol-sort-key does not seem to matter outside of each layer
    m_map->setLayoutProperty("carPosLayer", "symbol-sort-key", 0);
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
  if (!uiState()->scene.started) {
    return;
  }
  const SubMaster &sm = *(s.sm);
  update();

  // on rising edge of a valid system time, reinitialize the map to set a new token
  if (sm.valid("clocks") && !prev_time_valid) {
    LOGW("Time is now valid, reinitializing map");
    m_settings.setApiKey(get_mapbox_token());
    initializeGL();
  }
  prev_time_valid = sm.valid("clocks");

  if (sm.updated("modelV2")) {
    // set path color on change, and show map on rising edge of navigate on openpilot
    auto car_control = sm["carControl"].getCarControl();
    bool nav_enabled = sm["modelV2"].getModelV2().getNavEnabledDEPRECATED() &&
                       (sm["controlsState"].getControlsState().getEnabled() || car_control.getLatActive() || car_control.getLongActive());
    if (nav_enabled != uiState()->scene.navigate_on_openpilot_deprecated) {
      if (loaded_once) {
        m_map->setPaintProperty("navLayer", "line-color", getNavPathColor(nav_enabled));
      }
      if (nav_enabled) {
        emit requestVisible(true);
      }
    }
    uiState()->scene.navigate_on_openpilot_deprecated = nav_enabled;
  }

  if (sm.updated("liveLocationKalman")) {
    auto locationd_location = sm["liveLocationKalman"].getLiveLocationKalman();
    auto locationd_pos = locationd_location.getPositionGeodetic();
    auto locationd_orientation = locationd_location.getCalibratedOrientationNED();
    auto locationd_velocity = locationd_location.getVelocityCalibrated();
    auto locationd_ecef = locationd_location.getPositionECEF();

    locationd_valid = (locationd_pos.getValid() && locationd_orientation.getValid() && locationd_velocity.getValid() && locationd_ecef.getValid());
    if (locationd_valid) {
      // Check std norm
      auto pos_ecef_std = locationd_ecef.getStd();
      bool pos_accurate_enough = sqrt(pow(pos_ecef_std[0], 2) + pow(pos_ecef_std[1], 2) + pow(pos_ecef_std[2], 2)) < 100;
      locationd_valid = pos_accurate_enough;
    }

    if (locationd_valid) {
      last_position = QMapLibre::Coordinate(locationd_pos.getValue()[0], locationd_pos.getValue()[1]);
      last_bearing = RAD2DEG(locationd_orientation.getValue()[2]);
      velocity_filter.update(std::max(10.0, locationd_velocity.getValue()[0]));
    }
  }

  if (sm.updated("navRoute") && sm["navRoute"].getNavRoute().getCoordinates().size()) {
    auto nav_dest = coordinate_from_param("NavDestination");
    bool allow_open = std::exchange(last_valid_nav_dest, nav_dest) != nav_dest &&
                      nav_dest && !isVisible();
    qWarning() << "Got new navRoute from navd. Opening map:" << allow_open;

    // Show map on destination set/change
    if (allow_open) {
      emit requestSettings(false);
      emit requestVisible(true);
    }
  }

  loaded_once = loaded_once || (m_map && m_map->isFullyLoaded());
  if (!loaded_once) {
    setError(tr("Map Loading"));
    return;
  }
  initLayers();

  if (!locationd_valid) {
    setError(tr("Waiting for GPS"));
  } else if (routing_problem) {
    setError(tr("Waiting for route"));
  } else {
    setError("");
  }

  if (locationd_valid) {
    // Update current location marker
    auto point = coordinate_to_collection(*last_position);
    QMapLibre::Feature feature1(QMapLibre::Feature::PointType, point, {}, {});
    QVariantMap carPosSource;
    carPosSource["type"] = "geojson";
    carPosSource["data"] = QVariant::fromValue<QMapLibre::Feature>(feature1);
    m_map->updateSource("carPosSource", carPosSource);

    // Map bearing isn't updated when interacting, keep location marker up to date
    if (last_bearing) {
      m_map->setLayoutProperty("carPosLayer", "icon-rotate", *last_bearing - m_map->bearing());
    }
  }

  if (interaction_counter == 0) {
    if (last_position) m_map->setCoordinate(*last_position);
    if (last_bearing) m_map->setBearing(*last_bearing);
    m_map->setZoom(util::map_val<float>(velocity_filter.x(), 0, 30, MAX_ZOOM, MIN_ZOOM));
  } else {
    interaction_counter--;
  }

  if (sm.updated("navInstruction")) {
    // an invalid navInstruction packet with a nav destination is only possible if:
    // - API exception/no internet
    // - route response is empty
    // - any time navd is waiting for recompute_countdown
    routing_problem = !sm.valid("navInstruction") && coordinate_from_param("NavDestination").has_value();

    if (sm.valid("navInstruction")) {
      auto i = sm["navInstruction"].getNavInstruction();
      map_eta->updateETA(i.getTimeRemaining(), i.getTimeRemainingTypical(), i.getDistanceRemaining());

      if (locationd_valid) {
        m_map->setPitch(MAX_PITCH); // TODO: smooth pitching based on maneuver distance
        map_instructions->updateInstructions(i);
      }
    } else {
      clearRoute();
    }
  }

  if (sm.rcv_frame("navRoute") != route_rcv_frame) {
    qWarning() << "Updating navLayer with new route";
    auto route = sm["navRoute"].getNavRoute();
    auto route_points = capnp_coordinate_list_to_collection(route.getCoordinates());
    QMapLibre::Feature feature(QMapLibre::Feature::LineStringType, route_points, {}, {});
    QVariantMap navSource;
    navSource["type"] = "geojson";
    navSource["data"] = QVariant::fromValue<QMapLibre::Feature>(feature);
    m_map->updateSource("navSource", navSource);
    m_map->setLayoutProperty("navLayer", "visibility", "visible");

    route_rcv_frame = sm.rcv_frame("navRoute");
    updateDestinationMarker();
  }
}

void MapWindowSP::offroadTransition(bool offroad) {
  if (offroad) {
    uiStateSP()->scene.navigate_on_openpilot_deprecated = false;
  }

  MapWindow::offroadTransition(offroad);
}
