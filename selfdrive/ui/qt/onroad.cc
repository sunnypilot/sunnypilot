#include "selfdrive/ui/qt/onroad.h"

#include <cmath>

#include <QDebug>
#include <iomanip>
#include <sstream>
#include <QString>

#include "selfdrive/common/timing.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/common/params.h"
#ifdef ENABLE_MAPS
#include "selfdrive/ui/qt/maps/map.h"
#include "selfdrive/ui/qt/maps/map_helpers.h"
#endif

OnroadWindow::OnroadWindow(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout  = new QVBoxLayout(this);
  main_layout->setMargin(bdr_s);
  QStackedLayout *stacked_layout = new QStackedLayout;
  stacked_layout->setStackingMode(QStackedLayout::StackAll);
  main_layout->addLayout(stacked_layout);

  QStackedLayout *road_view_layout = new QStackedLayout;
  road_view_layout->setStackingMode(QStackedLayout::StackAll);
  nvg = new NvgWindow(VISION_STREAM_RGB_BACK, this);
  road_view_layout->addWidget(nvg);
  hud = new OnroadHud(this);
  road_view_layout->addWidget(hud);

  buttons = new ButtonsWindow(this);
  QObject::connect(this, &OnroadWindow::updateStateSignal, buttons, &ButtonsWindow::updateState);
  QObject::connect(nvg, &NvgWindow::resizeSignal, [=] (int w) {
    buttons->setFixedWidth(w);
  });
  stacked_layout->addWidget(buttons);

  QWidget * split_wrapper = new QWidget;
  split = new QHBoxLayout(split_wrapper);
  split->setContentsMargins(0, 0, 0, 0);
  split->setSpacing(0);
  split->addLayout(road_view_layout);

  stacked_layout->addWidget(split_wrapper);

  alerts = new OnroadAlerts(this);
  alerts->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(alerts);

  // setup stacking order
  alerts->raise();

  setAttribute(Qt::WA_OpaquePaintEvent);
  QObject::connect(this, &OnroadWindow::updateStateSignal, this, &OnroadWindow::updateState);
  QObject::connect(this, &OnroadWindow::offroadTransitionSignal, this, &OnroadWindow::offroadTransition);
}

void OnroadWindow::updateState(const UIState &s) {
  QColor bgColor = bg_colors[s.status];
  Alert alert = Alert::get(*(s.sm), s.scene.started_frame, s.scene.display_debug_alert_frame);
  if (s.sm->updated("controlsState") || !alert.equal({})) {
    if (alert.type == "controlsUnresponsive") {
      bgColor = bg_colors[STATUS_ALERT];
    }
    alerts->updateAlert(alert, bgColor);
  }

  hud->updateState(s);

  if (bg != bgColor) {
    // repaint border
    bg = bgColor;
    update();
  }
}

void issue_debug_snapshot(SubMaster &sm) {
  auto longitudinal_plan = sm["longitudinalPlan"].getLongitudinalPlan();
  auto live_map_data = sm["liveMapData"].getLiveMapData();
  auto car_state = sm["carState"].getCarState();

  auto t = std::time(nullptr);
  auto tm = *std::localtime(&t);
  std::ostringstream param_name_os;
  param_name_os << std::put_time(&tm, "%Y-%m-%d--%H-%M-%S");

  std::ostringstream os;
  os.setf(std::ios_base::fixed);
  os.precision(2);
  os << "Datetime: " << param_name_os.str() << ", vEgo: " << car_state.getVEgo() * 3.6 << "\n\n";
  os.precision(6);
  os << "Location: (" << live_map_data.getLastGpsLatitude() << ", " << live_map_data.getLastGpsLongitude()  << ")\n";
  os.precision(2);
  os << "Bearing: " << live_map_data.getLastGpsBearingDeg() << "; ";
  os << "GPSSpeed: " << live_map_data.getLastGpsSpeed() * 3.6 << "\n\n";
  os.precision(1);
  os << "Speed Limit: " << live_map_data.getSpeedLimit() * 3.6 << ", ";
  os << "Valid: " << live_map_data.getSpeedLimitValid() << "\n";
  os << "Speed Limit Ahead: " << live_map_data.getSpeedLimitAhead() * 3.6 << ", ";
  os << "Valid: " << live_map_data.getSpeedLimitAheadValid() << ", ";
  os << "Distance: " << live_map_data.getSpeedLimitAheadDistance() << "\n";
  os << "Turn Speed Limit: " << live_map_data.getTurnSpeedLimit() * 3.6 << ", ";
  os << "Valid: " << live_map_data.getTurnSpeedLimitValid() << ", ";
  os << "End Distance: " << live_map_data.getTurnSpeedLimitEndDistance() << ", ";
  os << "Sign: " << live_map_data.getTurnSpeedLimitSign() << "\n\n";

  const auto turn_speeds = live_map_data.getTurnSpeedLimitsAhead();
  os << "Turn Speed Limits Ahead:\n";
  os << "VALUE\tDIST\tSIGN\n";

  if (turn_speeds.size() == 0) {
    os << "-\t-\t-" << "\n\n";
  } else {
    const auto distances = live_map_data.getTurnSpeedLimitsAheadDistances();
    const auto signs = live_map_data.getTurnSpeedLimitsAheadSigns();
    for(int i = 0; i < turn_speeds.size(); i++) {
      os << turn_speeds[i] * 3.6 << "\t" << distances[i] << "\t" << signs[i] << "\n";
    }
    os << "\n";
  }

  os << "SPEED LIMIT CONTROLLER:\n";
  os << "sl: " << longitudinal_plan.getSpeedLimit() * 3.6  << ", ";
  os << "state: " << int(longitudinal_plan.getSpeedLimitControlState()) << ", ";
  os << "isMap: " << longitudinal_plan.getIsMapSpeedLimit() << "\n\n";

  os << "TURN SPEED CONTROLLER:\n";
  os << "speed: " << longitudinal_plan.getTurnSpeed() * 3.6 << ", ";
  os << "state: " << int(longitudinal_plan.getTurnSpeedControlState()) << "\n\n";

  os << "VISION TURN CONTROLLER:\n";
  os << "speed: " << longitudinal_plan.getVisionTurnSpeed() * 3.6 << ", ";
  os << "state: " << int(longitudinal_plan.getVisionTurnControllerState());

  Params().put(param_name_os.str().c_str(), os.str().c_str(), os.str().length());
  QUIState::ui_state.scene.display_debug_alert_frame = sm.frame;
}

void OnroadWindow::mousePressEvent(QMouseEvent* e) {
  bool sidebarVisible = geometry().x() > 0;
  bool propagate_event = true;

    // Toggle speed limit control enabled
  SubMaster &sm = *(QUIState::ui_state.sm);
  auto longitudinal_plan = sm["longitudinalPlan"].getLongitudinalPlan();
  const QRect speed_limit_touch_rect = speed_sgn_rc.adjusted(-50, -50, 50, 50);
  const QRect debug_tap_rect = QRect(rect().center().x() - 200, rect().center().y() - 200, 400, 400);
  const QRect dev_ui_touch_rect = max_speed_rc;

  if (longitudinal_plan.getSpeedLimit() > 0.0 && speed_limit_touch_rect.contains(e->x(), e->y())) {
    // If touching the speed limit sign area when visible
    QUIState::ui_state.scene.last_speed_limit_sign_tap = seconds_since_boot();
    Params().putBool("LastSpeedLimitSignTap", 1);
    Params().putBool("LastSpeedLimitSignTap", 0);
    QUIState::ui_state.scene.speed_limit_control_enabled = !QUIState::ui_state.scene.speed_limit_control_enabled;
    Params().putBool("SpeedLimitControl", QUIState::ui_state.scene.speed_limit_control_enabled);
    propagate_event = false;
  }
  else if (QUIState::ui_state.scene.debug_snapshot_enabled && debug_tap_rect.contains(e->x(), e->y())) {
    issue_debug_snapshot(*(QUIState::ui_state.sm));
    propagate_event = false;
  }
  else if (QUIState::ui_state.scene.show_debug_ui && dev_ui_touch_rect.contains(e->x(), e->y())) {
    QUIState::ui_state.scene.dev_ui_enabled = QUIState::ui_state.scene.dev_ui_enabled + 1;
    if (QUIState::ui_state.scene.dev_ui_enabled > 2) {
      QUIState::ui_state.scene.dev_ui_enabled = 0;
    }
    if (QUIState::ui_state.scene.dev_ui_enabled == 0) {
      Params().put("DevUI", "0", 1);
    } else if (QUIState::ui_state.scene.dev_ui_enabled == 1) {
      Params().put("DevUI", "1", 1);
    } else if (QUIState::ui_state.scene.dev_ui_enabled == 2) {
      Params().put("DevUI", "2", 1);
    }
    propagate_event = false;
  }
  else if (map != nullptr) {
    map->setVisible(!sidebarVisible && !map->isVisible());
  }
  // propagation event to parent(HomeWindow)
  if (propagate_event) {
    QWidget::mousePressEvent(e);
  }
}

void OnroadWindow::offroadTransition(bool offroad) {
#ifdef ENABLE_MAPS
  if (!offroad) {
    if (map == nullptr && (QUIState::ui_state.has_prime || !MAPBOX_TOKEN.isEmpty())) {
      MapWindow * m = new MapWindow(get_mapbox_settings());
      m->setFixedWidth(topWidget(this)->width() / 2);
      QObject::connect(this, &OnroadWindow::offroadTransitionSignal, m, &MapWindow::offroadTransition);
      split->addWidget(m, 0, Qt::AlignRight);
      map = m;
    }
  }
#endif

  alerts->updateAlert({}, bg);

  // update stream type
  bool wide_cam = Hardware::TICI() && Params().getBool("EnableWideCamera");
  nvg->setStreamType(wide_cam ? VISION_STREAM_RGB_WIDE : VISION_STREAM_RGB_BACK);
}

void OnroadWindow::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.fillRect(rect(), QColor(bg.red(), bg.green(), bg.blue(), 255));
}

// ***** onroad widgets *****

ButtonsWindow::ButtonsWindow(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout  = new QVBoxLayout(this);

  QWidget *btns_wrapper = new QWidget;
  QHBoxLayout *btns_layout  = new QHBoxLayout(btns_wrapper);
  btns_layout->setSpacing(0);
  btns_layout->setContentsMargins(300, 0, 30, 30);

  main_layout->addWidget(btns_wrapper, 0, Qt::AlignBottom);

  // Dynamic lane profile button
  QString initDlpBtn = "";
  dlpBtn = new QPushButton(initDlpBtn);
  QObject::connect(dlpBtn, &QPushButton::clicked, [=]() {
    QUIState::ui_state.scene.dynamic_lane_profile = QUIState::ui_state.scene.dynamic_lane_profile + 1;
    if (QUIState::ui_state.scene.dynamic_lane_profile > 2) {
      QUIState::ui_state.scene.dynamic_lane_profile = 0;
    }
    if (QUIState::ui_state.scene.dynamic_lane_profile == 0) {
      Params().put("DynamicLaneProfile", "0", 1);
      dlpBtn->setText("Lane\nonly");
    } else if (QUIState::ui_state.scene.dynamic_lane_profile == 1) {
      Params().put("DynamicLaneProfile", "1", 1);
      dlpBtn->setText("Lane\nless");
    } else if (QUIState::ui_state.scene.dynamic_lane_profile == 2) {
      Params().put("DynamicLaneProfile", "2", 1);
      dlpBtn->setText("Auto\nLane");
    }
  });
  dlpBtn->setFixedWidth(200);
  dlpBtn->setFixedHeight(200);
  btns_layout->addWidget(dlpBtn, 0, Qt::AlignLeft);
  btns_layout->addSpacing(35);

  if (QUIState::ui_state.scene.end_to_end) {
    dlpBtn->hide();
  }

  setStyleSheet(R"(
    QPushButton {
      color: white;
      text-align: center;
      padding: 0px;
      border-width: 12px;
      border-style: solid;
      background-color: rgba(75, 75, 75, 0.3);
    }
  )");
}

void ButtonsWindow::updateState(const UIState &s) {
  if (QUIState::ui_state.scene.dynamic_lane_profile == 0) {
    dlpBtn->setStyleSheet(QString("font-size: 45px; border-radius: 100px; border-color: %1").arg(dlpBtnColors.at(0)));
    dlpBtn->setText("Lane\nonly");
  } else if (QUIState::ui_state.scene.dynamic_lane_profile == 1) {
    dlpBtn->setStyleSheet(QString("font-size: 45px; border-radius: 100px; border-color: %1").arg(dlpBtnColors.at(1)));
    dlpBtn->setText("Lane\nless");
  } else if (QUIState::ui_state.scene.dynamic_lane_profile == 2) {
    dlpBtn->setStyleSheet(QString("font-size: 45px; border-radius: 100px; border-color: %1").arg(dlpBtnColors.at(2)));
    dlpBtn->setText("Auto\nLane");
  }
}

// OnroadAlerts
void OnroadAlerts::updateAlert(const Alert &a, const QColor &color) {
  if (!alert.equal(a) || color != bg) {
    alert = a;
    bg = color;
    update();
  }
}

void OnroadAlerts::paintEvent(QPaintEvent *event) {
  if (alert.size == cereal::ControlsState::AlertSize::NONE) {
    return;
  }
  static std::map<cereal::ControlsState::AlertSize, const int> alert_sizes = {
    {cereal::ControlsState::AlertSize::SMALL, 271},
    {cereal::ControlsState::AlertSize::MID, 420},
    {cereal::ControlsState::AlertSize::FULL, height()},
  };
  int h = alert_sizes[alert.size];
  QRect r = QRect(0, height() - h, width(), h);

  QPainter p(this);

  // draw background + gradient
  p.setPen(Qt::NoPen);
  p.setCompositionMode(QPainter::CompositionMode_SourceOver);

  p.setBrush(QBrush(bg));
  p.drawRect(r);

  QLinearGradient g(0, r.y(), 0, r.bottom());
  g.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.05));
  g.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0.35));

  p.setCompositionMode(QPainter::CompositionMode_DestinationOver);
  p.setBrush(QBrush(g));
  p.fillRect(r, g);
  p.setCompositionMode(QPainter::CompositionMode_SourceOver);

  // text
  const QPoint c = r.center();
  p.setPen(QColor(0xff, 0xff, 0xff));
  p.setRenderHint(QPainter::TextAntialiasing);
  if (alert.size == cereal::ControlsState::AlertSize::SMALL) {
    configFont(p, "Open Sans", 74, "SemiBold");
    p.drawText(r, Qt::AlignCenter, alert.text1);
  } else if (alert.size == cereal::ControlsState::AlertSize::MID) {
    configFont(p, "Open Sans", 88, "Bold");
    p.drawText(QRect(0, c.y() - 125, width(), 150), Qt::AlignHCenter | Qt::AlignTop, alert.text1);
    configFont(p, "Open Sans", 66, "Regular");
    p.drawText(QRect(0, c.y() + 21, width(), 90), Qt::AlignHCenter, alert.text2);
  } else if (alert.size == cereal::ControlsState::AlertSize::FULL) {
    bool l = alert.text1.length() > 15;
    configFont(p, "Open Sans", l ? 132 : 177, "Bold");
    p.drawText(QRect(0, r.y() + (l ? 240 : 270), width(), 600), Qt::AlignHCenter | Qt::TextWordWrap, alert.text1);
    configFont(p, "Open Sans", 88, "Regular");
    p.drawText(QRect(0, r.height() - (l ? 361 : 420), width(), 300), Qt::AlignHCenter | Qt::TextWordWrap, alert.text2);
  }
}

// OnroadHud
OnroadHud::OnroadHud(QWidget *parent) : QWidget(parent) {
  engage_img = QPixmap("../assets/img_chffr_wheel.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  dm_img = QPixmap("../assets/img_driver_face.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  how_img = QPixmap("../assets/img_hands_on_wheel.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  map_img = QPixmap("../assets/img_world_icon.png").scaled(subsign_img_size, subsign_img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  left_img = QPixmap("../assets/img_turn_left_icon.png").scaled(subsign_img_size, subsign_img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  right_img = QPixmap("../assets/img_turn_right_icon.png").scaled(subsign_img_size, subsign_img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  mads_imgs[0] = QPixmap("../assets/img_mads_off.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  mads_imgs[1] = QPixmap("../assets/img_mads_on.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);

  connect(this, &OnroadHud::valueChanged, [=] { update(); });
}

void OnroadHud::updateState(const UIState &s) {
  const int SET_SPEED_NA = 255;
  const SubMaster &sm = *(s.sm);
  const auto cs = sm["controlsState"].getControlsState();

  float maxspeed = cs.getVCruise();
  bool cruise_set = maxspeed > 0 && (int)maxspeed != SET_SPEED_NA;
  if (cruise_set && !s.scene.is_metric) {
    maxspeed *= KM_TO_MILE;
  }
  QString maxspeed_str = cruise_set ? QString::number(std::nearbyint(maxspeed)) : "N/A";
  float cur_speed = std::max(0.0, sm["carState"].getCarState().getVEgo() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH));

  setProperty("is_cruise_set", cruise_set);
  setProperty("speed", QString::number(std::nearbyint(cur_speed)));
  setProperty("maxSpeed", maxspeed_str);
  setProperty("speedUnit", s.scene.is_metric ? "km/h" : "mph");
  setProperty("hideDM", cs.getAlertSize() != cereal::ControlsState::AlertSize::NONE);
  setProperty("status", s.status);
  setProperty("is_brakelight_on", sm["carState"].getCarState().getBrakeLights());
  setProperty("madsEnabled", sm["controlsState"].getControlsState().getMadsEnabled());
  setProperty("suspended", sm["controlsState"].getControlsState().getSuspended());

  // update engageability and DM icons at 2Hz
  if (sm.frame % (UI_FREQ / 2) == 0) {
    const auto howState = sm["driverMonitoringState"].getDriverMonitoringState().getHandsOnWheelState();

    setProperty("engageable", cs.getEngageable() || cs.getEnabled());
    setProperty("dmActive", sm["driverMonitoringState"].getDriverMonitoringState().getIsActiveMode());
    setProperty("showHowAlert", howState >= cereal::DriverMonitoringState::HandsOnWheelState::WARNING);
    setProperty("howWarning", howState == cereal::DriverMonitoringState::HandsOnWheelState::WARNING);

    const auto lp = sm["longitudinalPlan"].getLongitudinalPlan();
    const auto vtcState = lp.getVisionTurnControllerState();
    const float vtc_speed = lp.getVisionTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const auto lpSoruce = lp.getLongitudinalPlanSource();
    QColor vtc_color = tcs_colors[int(vtcState)];
    vtc_color.setAlpha(lpSoruce == cereal::LongitudinalPlan::LongitudinalPlanSource::TURN ? 255 : 100);

    setProperty("showVTC", vtcState > cereal::LongitudinalPlan::VisionTurnControllerState::DISABLED);
    setProperty("vtcSpeed", QString::number(std::nearbyint(vtc_speed)));
    setProperty("vtcColor", vtc_color);
    setProperty("showDebugUI", s.scene.show_debug_ui);

    const auto lmd = sm["liveMapData"].getLiveMapData();

    setProperty("roadName", QString::fromStdString(lmd.getCurrentRoadName()));

    const float speed_limit = lp.getSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const float speed_limit_offset = lp.getSpeedLimitOffset() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const float speed_limit_value_offset = lp.getSpeedLimitValueOffset();
    const bool speed_limit_perc_offset = lp.getSpeedLimitPercOffset();
    const auto slcState = lp.getSpeedLimitControlState();
    const bool sl_force_active = s.scene.speed_limit_control_enabled &&
                                 seconds_since_boot() < s.scene.last_speed_limit_sign_tap + 2.0;
    const bool sl_inactive = !sl_force_active && (!s.scene.speed_limit_control_enabled ||
                             slcState == cereal::LongitudinalPlan::SpeedLimitControlState::INACTIVE);
    const bool sl_temp_inactive = !sl_force_active && (s.scene.speed_limit_control_enabled &&
                                  slcState == cereal::LongitudinalPlan::SpeedLimitControlState::TEMP_INACTIVE);
    const int sl_distance = int(lp.getDistToSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
    const QString sl_distance_str(QString::number(sl_distance) + (s.scene.is_metric ? "m" : "f"));
    const QString sl_offset_str(speed_limit_perc_offset ? speed_limit_offset > 0.0 ?
                                "+" + QString::number(std::nearbyint(speed_limit_offset)) : "" :
                                speed_limit_value_offset > 0.0 ? "+" + QString::number(std::nearbyint(speed_limit_value_offset)) :
                                speed_limit_value_offset < 0.0 ? "-" + QString::number(std::nearbyint(speed_limit_value_offset)) : "");
    const QString sl_inactive_str(sl_temp_inactive ? "TEMP" : "");
    const QString sl_substring(sl_inactive || sl_temp_inactive ? sl_inactive_str :
                               sl_distance > 0 ? sl_distance_str : sl_offset_str);

    setProperty("showSpeedLimit", speed_limit > 0.0);
    setProperty("speedLimit", QString::number(std::nearbyint(speed_limit)));
    setProperty("slcSubText", sl_substring);
    setProperty("slcSubTextSize", sl_inactive || sl_temp_inactive || sl_distance > 0 ? 22.2 : 37.0);
    setProperty("mapSourcedSpeedLimit", lp.getIsMapSpeedLimit());
    setProperty("slcActive", !sl_inactive && !sl_temp_inactive);

    const float tsc_speed = lp.getTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const auto tscState = lp.getTurnSpeedControlState();
    const int t_distance = int(lp.getDistToTurn() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
    const QString t_distance_str(QString::number(t_distance) + (s.scene.is_metric ? "m" : "f"));

    setProperty("showTurnSpeedLimit", tsc_speed > 0.0 && (tsc_speed < cur_speed || s.scene.show_debug_ui));
    setProperty("turnSpeedLimit", QString::number(std::nearbyint(tsc_speed)));
    setProperty("tscSubText", t_distance > 0 ? t_distance_str : QString(""));
    setProperty("tscActive", tscState > cereal::LongitudinalPlan::SpeedLimitControlState::TEMP_INACTIVE);
    setProperty("curveSign", lp.getTurnSign());
  }

  const auto leadOne = sm["radarState"].getRadarState().getLeadOne();
  const auto carState = sm["carState"].getCarState();
  const auto gpsLocationExternal = sm["gpsLocationExternal"].getGpsLocationExternal();
  setProperty("lead_d_rel", leadOne.getDRel());
  setProperty("lead_v_rel", leadOne.getVRel());
  setProperty("lead_status", leadOne.getStatus());
  setProperty("angleSteers", carState.getSteeringAngleDeg());
  setProperty("steerAngleDesired", sm["controlsState"].getControlsState().getLateralControlState().getPidState().getSteeringAngleDesiredDeg());
  setProperty("distanceTraveled", sm["controlsState"].getControlsState().getDistanceTraveled());
  setProperty("devUiEnabled", s.scene.dev_ui_enabled);
  setProperty("gpsAccuracy", gpsLocationExternal.getAccuracy());
  setProperty("altitude", gpsLocationExternal.getAltitude());
  setProperty("vEgo", carState.getVEgo());
  setProperty("aEgo", carState.getAEgo());
  setProperty("steeringTorqueEps", carState.getSteeringTorqueEps());
  setProperty("bearingAccuracyDeg", gpsLocationExternal.getBearingAccuracyDeg());
  setProperty("bearingDeg", gpsLocationExternal.getBearingDeg());

  setProperty("standStill", carState.getStandStill());
  setProperty("standstillElapsedTime", sm["lateralPlan"].getLateralPlan().getStandstillElapsed());
}

void OnroadHud::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setRenderHint(QPainter::Antialiasing);

  // Header gradient
  QLinearGradient bg(0, header_h - (header_h / 2.5), 0, header_h);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, width(), header_h, bg);

  // max speed
  QRect rc(bdr_s * 2, bdr_s * 1.5, 184, 202);
  p.setPen(QPen(QColor(0xff, 0xff, 0xff, 100), 10));
  p.setBrush(QColor(0, 0, 0, 100));
  p.drawRoundedRect(rc, 20, 20);
  p.setPen(Qt::NoPen);

  configFont(p, "Open Sans", 48, "Regular");
  drawText(p, rc.center().x(), 118, "MAX", is_cruise_set ? 200 : 100);
  if (is_cruise_set) {
    configFont(p, "Open Sans", 88, is_cruise_set ? "Bold" : "SemiBold");
    drawText(p, rc.center().x(), 212, maxSpeed, 255);
  } else {
    configFont(p, "Open Sans", 80, "SemiBold");
    drawText(p, rc.center().x(), 212, maxSpeed, 100);
  }

  // current speed
  configFont(p, "Open Sans", 176, "Bold");
  drawSpeedText(p, rect().center().x(), 210, speed, is_brakelight_on ? QColor(0xff, 0, 0, 255) : QColor(0xff, 0xff, 0xff, 255));
  configFont(p, "Open Sans", 66, "Regular");
  drawText(p, rect().center().x(), 290, speedUnit, 200);

  if (engageable) {
    if (showDebugUI && showVTC) {
      drawVisionTurnControllerUI(p, rect().right() - 184 - bdr_s, int(bdr_s * 1.5), 184, vtcColor, vtcSpeed, 100);
    } else {
      // engage-ability icon
      drawIcon(p, rect().right() - radius / 2 - bdr_s * 2, radius / 2 + int(bdr_s * 1.5),
               engage_img, bg_colors[status], 1.0);
    }

    // Hands on wheel icon
    if (showHowAlert) {
      drawIcon(p, rect().right() - radius / 2 - bdr_s * 2, int(bdr_s * 1.5) + 2 * radius + bdr_s + radius / 2,
               how_img, bg_colors[howWarning ? STATUS_WARNING : STATUS_ALERT], 1.0);
    }

    // Speed Limit Sign
    if (showSpeedLimit) {
      drawSpeedSign(p, speed_sgn_rc, speedLimit, slcSubText, slcSubTextSize, mapSourcedSpeedLimit, slcActive);
    }

    // Turn Speed Sign
    if (showTurnSpeedLimit) {
      rc.moveTop(speed_sgn_rc.bottom() + bdr_s);
      drawTrunSpeedSign(p, rc, turnSpeedLimit, tscSubText, curveSign, tscActive);
    }

    // Stand Still Timer
    if (standStill) {
      drawStandstillTimer(p, rect().right() - 650, 30 + 160 + 250);
    }
  }

  // dm icon
  if (!hideDM) {
    drawIcon(p, radius / 2 + (bdr_s * 2), rect().bottom() - footer_h / 2,
             dm_img, QColor(0, 0, 0, 70), dmActive ? 1.0 : 0.2);
  }

  // MADS icon
  drawMadsIcon(p, rect().right() - radius / 2 - bdr_s * 2 - 184, radius / 2 + int(bdr_s * 1.5),
           madsEnabled ? suspended ? mads_imgs[0] : mads_imgs[1] : mads_imgs[0], QColor(75, 75, 75, 75), 1.0);

  // Bottom bar road name
  if (showDebugUI && !roadName.isEmpty()) {
    const int h = 60;
    QRect bar_rc(rect().left(), rect().bottom() - h, rect().width(), h);
    p.setBrush(QColor(0, 0, 0, 100));
    p.drawRect(bar_rc);
    configFont(p, "Open Sans", 38, "Bold");
    drawCenteredText(p, bar_rc.center().x(), bar_rc.center().y(), roadName, QColor(255, 255, 255, 200));
  }

  // Right Dev UI
  QRect rc2(rect().right() - (bdr_s * 2), bdr_s * 1.5, 184, 202);
  if (showDebugUI) {
    if (devUiEnabled == 1) {
      drawRightDevUi(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
      drawRightDevUiBorder(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
    } else if (devUiEnabled == 2) {
      drawRightDevUi(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
      drawRightDevUi2(p, rect().right() - 184 - bdr_s * 2 - 184, bdr_s * 2 + rc2.height());
      drawRightDevUiBorder(p, rect().right() - 184 - bdr_s * 2 - 184, bdr_s * 2 + rc2.height());
    }
  }
}

void OnroadHud::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void OnroadHud::drawSpeedText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void OnroadHud::drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y});

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}

void OnroadHud::drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - radius / 2, y - radius / 2, radius, radius);
  p.setOpacity(opacity);
  p.drawPixmap(x - img_size / 2, y - img_size / 2, img);
  p.setOpacity(1.0);
}

void OnroadHud::drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color,
                                           const QString &vision_speed, int alpha) {
  QRect rvtc(x, y, size, size);
  p.setPen(QPen(color, 10));
  p.setBrush(QColor(0, 0, 0, alpha));
  p.drawRoundedRect(rvtc, 20, 20);
  p.setPen(Qt::NoPen);

  configFont(p, "Open Sans", 56, "SemiBold");
  drawCenteredText(p, rvtc.center().x(), rvtc.center().y(), vision_speed, color);
}

void OnroadHud::drawCircle(QPainter &p, int x, int y, int r, QBrush bg) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - r, y - r, 2 * r, 2 * r);
}

void OnroadHud::drawSpeedSign(QPainter &p, QRect rc, const QString &speed_limit, const QString &sub_text,
                              int subtext_size, bool is_map_sourced, bool is_active) {
  const QColor ring_color = is_active ? QColor(255, 0, 0, 255) : QColor(0, 0, 0, 50);
  const QColor inner_color = QColor(255, 255, 255, is_active ? 255 : 85);
  const QColor text_color = QColor(0, 0, 0, is_active ? 255 : 85);

  const int x = rc.center().x();
  const int y = rc.center().y();
  const int r = rc.width() / 2.0f;

  drawCircle(p, x, y, r, ring_color);
  drawCircle(p, x, y, int(r * 0.8f), inner_color);

  configFont(p, "Open Sans", 89, "Bold");
  drawCenteredText(p, x, y, speed_limit, text_color);
  configFont(p, "Open Sans", subtext_size, "Bold");
  drawCenteredText(p, x, y + 55, sub_text, text_color);

  if (is_map_sourced) {
    p.setPen(Qt::NoPen);
    p.setOpacity(is_active ? 1.0 : 0.3);
    p.drawPixmap(x - subsign_img_size / 2, y - 55 - subsign_img_size / 2, map_img);
    p.setOpacity(1.0);
  }
}

void OnroadHud::drawTrunSpeedSign(QPainter &p, QRect rc, const QString &turn_speed, const QString &sub_text,
                                  int curv_sign, bool is_active) {
  const QColor border_color = is_active ? QColor(255, 0, 0, 255) : QColor(0, 0, 0, 50);
  const QColor inner_color = QColor(255, 255, 255, is_active ? 255 : 85);
  const QColor text_color = QColor(0, 0, 0, is_active ? 255 : 85);

  const int x = rc.center().x();
  const int y = rc.center().y();
  const int width = rc.width();

  const float stroke_w = 15.0;
  const float cS = stroke_w / 2.0 + 4.5;  // half width of the stroke on the corners of the triangle
  const float R = width / 2.0 - stroke_w / 2.0;
  const float A = 0.73205;
  const float h2 = 2.0 * R / (1.0 + A);
  const float h1 = A * h2;
  const float L = 4.0 * R / sqrt(3.0);

  // Draw the internal triangle, compensate for stroke width. Needed to improve rendering when in inactive
  // state due to stroke transparency being different from inner transparency.
  QPainterPath path;
  path.moveTo(x, y - R + cS);
  path.lineTo(x - L / 2.0 + cS, y + h1 + h2 - R - stroke_w / 2.0);
  path.lineTo(x + L / 2.0 - cS, y + h1 + h2 - R - stroke_w / 2.0);
  path.lineTo(x, y - R + cS);
  p.setPen(Qt::NoPen);
  p.setBrush(inner_color);
  p.drawPath(path);

  // Draw the stroke
  QPainterPath stroke_path;
  stroke_path.moveTo(x, y - R);
  stroke_path.lineTo(x - L / 2.0, y + h1 + h2 - R);
  stroke_path.lineTo(x + L / 2.0, y + h1 + h2 - R);
  stroke_path.lineTo(x, y - R);
  p.setPen(QPen(border_color, stroke_w, Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));
  p.setBrush(Qt::NoBrush);
  p.drawPath(stroke_path);

  // Draw the turn sign
  if (curv_sign != 0) {
    p.setPen(Qt::NoPen);
    p.setOpacity(is_active ? 1.0 : 0.3);
    p.drawPixmap(int(x - (subsign_img_size / 2)), int(y - R + stroke_w + 30), curv_sign > 0 ? left_img : right_img);
    p.setOpacity(1.0);
  }

  // Draw the texts.
  configFont(p, "Open Sans", 67, "Bold");
  drawCenteredText(p, x, y + 25, turn_speed, text_color);
  configFont(p, "Open Sans", 22, "Bold");
  drawCenteredText(p, x, y + 65, sub_text, text_color);
}

void OnroadHud::drawMadsIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - 133 / 2, y - 133 / 2, 133, 133); // same as img_size == 266x266
  p.setOpacity(opacity);
  p.drawPixmap(x - img_size / 2, y - img_size / 2, img); // img_size == 266x266
  p.setOpacity(1.0);
}

void OnroadHud::drawColoredText(QPainter &p, int x, int y, const QString &text, QColor &color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

int OnroadHud::drawDevUiElementRight(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color) {
  configFont(p, "Open Sans", 30 * 2, "SemiBold");
  drawColoredText(p, x + 92, y + 80, QString(value), color);

  configFont(p, "Open Sans", 28, "Regular");
  drawText(p, x + 92, y + 80 + 42, QString(label), 255);

  if (strlen(units) > 0) {
    p.save();
    p.translate(x + 54 + 30 - 3 + 92, y + 37 + 25);
    p.rotate(-90);
    drawText(p, 0, 0, QString(units), 255);
    p.restore();
  }

  return 110;
}

int OnroadHud::drawDevUiElementLeft(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color) {
  configFont(p, "Open Sans", 30 * 2, "SemiBold");
  drawColoredText(p, x + 92, y + 80, QString(value), color);

  configFont(p, "Open Sans", 28, "Regular");
  drawText(p, x + 92, y + 80 + 42, QString(label), 255);

  if (strlen(units) > 0) {
    p.save();
    p.translate(x + 11, y + 37 + 25);
    p.rotate(90);
    drawText(p, 0, 0, QString(units), 255);
    p.restore();
  }

  return 110;
}

void OnroadHud::drawStandstillTimerText(QPainter &p, int x, int y, const char* label, const char* value, QColor &color1, QColor &color2) {
  configFont(p, "Open Sans", 125, "SemiBold");
  drawColoredText(p, x, y, QString(label), color1);

  configFont(p, "Open Sans", 150, "SemiBold");
  drawColoredText(p, x, y + 150, QString(value), color2);
}

void OnroadHud::drawRightDevUi(QPainter &p, int x, int y) {
  int rh = 5;
  int ry = y;

  // Add Relative Distance to Primary Lead Car
  // Unit: Meters
  if (true) {
    char val_str[16];
    char units_str[8];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (lead_status) {
      // Orange if close, Red if very close
      if (lead_d_rel < 5) {
        valueColor = QColor(255, 0, 0, 255);
      } else if (lead_d_rel < 15) {
        valueColor = QColor(255, 188, 0, 255);
      }
      snprintf(val_str, sizeof(val_str), "%d", (int)lead_d_rel);
    } else {
      snprintf(val_str, sizeof(val_str), "-");
    }

    snprintf(units_str, sizeof(units_str), "m");

    rh += drawDevUiElementRight(p, x, ry, val_str, "REL DIST", units_str, valueColor);
    ry = y + rh;
  }

  // Add Relative Velocity vs Primary Lead Car
  // Unit: kph if metric, else mph
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

     if (lead_status) {
       // Red if approaching faster than 10mph
       // Orange if approaching (negative)
       if (lead_v_rel < -4.4704) {
        valueColor = QColor(255, 0, 0, 255);
       } else if (lead_v_rel < 0) {
         valueColor = QColor(255, 188, 0, 255);
       }

       if (speedUnit == "mph") {
         snprintf(val_str, sizeof(val_str), "%d", (int)(lead_v_rel * 2.236936)); //mph
       } else {
         snprintf(val_str, sizeof(val_str), "%d", (int)(lead_v_rel * 3.6)); //kph
       }
     } else {
       snprintf(val_str, sizeof(val_str), "-");
     }

    rh += drawDevUiElementRight(p, x, ry, val_str, "REL SPEED", speedUnit.toStdString().c_str(), valueColor);
    ry = y + rh;
  }

  // Add Real Steering Angle
  // Unit: Degrees
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);
    if (madsEnabled && !suspended) {
      valueColor = QColor(0, 255, 0, 255);
    } else {
      valueColor = QColor(255, 255, 255, 255);
    }

    // Red if large steering angle
    // Orange if moderate steering angle
    if (std::fabs(angleSteers) > 50) {
      valueColor = QColor(255, 0, 0, 255);
    } else if (std::fabs(angleSteers) > 30) {
      valueColor = QColor(255, 188, 0, 255);
    }

    snprintf(val_str, sizeof(val_str), "%.1f%s%s", angleSteers , "°", "");

    rh += drawDevUiElementRight(p, x, ry, val_str, "REAL STEER", "", valueColor);
    ry = y + rh;
  }

  // Add Desired Steering Angle
  // Unit: Degrees
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (madsEnabled && !suspended) {
      // Red if large steering angle
      // Orange if moderate steering angle
      if (std::fabs(angleSteers) > 50) {
        valueColor = QColor(255, 0, 0, 255);
      } else if (std::fabs(angleSteers) > 30) {
        valueColor = QColor(255, 188, 0, 255);
      }

      snprintf(val_str, sizeof(val_str), "%.1f%s%s", steerAngleDesired, "°", "");
    } else {
      snprintf(val_str, sizeof(val_str), "-");
    }

    rh += drawDevUiElementRight(p, x, ry, val_str, "DESIR STEER", "", valueColor);
    ry = y + rh;
  }

  // Add Traveled Distance in Current Drive
  // Unit: Km if metric, else Miles
  if (true) {
    char val_str[16];
    char units_str[8];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (speedUnit == "mph") {
      snprintf(val_str, sizeof(val_str), "%.1f", (distanceTraveled * METER_TO_MILE)); //miles
      snprintf(units_str, sizeof(units_str), "mi");
    } else {
      snprintf(val_str, sizeof(val_str), "%.1f", (distanceTraveled * 0.001)); //kilometers
      snprintf(units_str, sizeof(units_str), "km");
    }

    rh += drawDevUiElementRight(p, x, ry, val_str, "TRIP", units_str, valueColor);
    ry = y + rh;
  }

  rh += 25;
  p.setBrush(QColor(0, 0, 0, 0));
  QRect ldu(x, y, 184, rh);
  //p.drawRoundedRect(ldu, 20, 20);
}

void OnroadHud::drawRightDevUi2(QPainter &p, int x, int y) {
  int rh = 5;
  int ry = y;


  // Add Acceleration from Car
  // Unit: Meters per Second Squared
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

    snprintf(val_str, sizeof(val_str), "%.1f", aEgo);

    rh += drawDevUiElementLeft(p, x, ry, val_str, "ACCEL", "m/s²", valueColor);
    ry = y + rh;
  }

  // Add Velocity of Primary Lead Car
  // Unit: kph if metric, else mph
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

     if (lead_status) {
       if (speedUnit == "mph") {
         snprintf(val_str, sizeof(val_str), "%d", (int)((lead_v_rel + vEgo) * 2.236936)); //mph
       } else {
         snprintf(val_str, sizeof(val_str), "%d", (int)((lead_v_rel + vEgo) * 3.6)); //kph
       }
     } else {
       snprintf(val_str, sizeof(val_str), "-");
     }

    rh += drawDevUiElementLeft(p, x, ry, val_str, "LEAD SPD", speedUnit.toStdString().c_str(), valueColor);
    ry = y + rh;
  }

  // Add Steering Torque from Car EPS
  // Unit: Newton Meters
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

    snprintf(val_str, sizeof(val_str), "%.1f", std::fabs(steeringTorqueEps));

    rh += drawDevUiElementLeft(p, x, ry, val_str, "EPS TRQ", "N·dm", valueColor);
    ry = y + rh;
  }

  // Add Bearing Degree and Direction from Car (Compass)
  // Unit: Meters
  if (true) {
    char val_str[16];
    char dir_str[8];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (bearingAccuracyDeg != 180.00) {
      snprintf(val_str, sizeof(val_str), "%.0d%s%s", (int)bearingDeg, "°", "");
      if (((bearingDeg >= 337.5) && (bearingDeg <= 360)) || ((bearingDeg >= 0) && (bearingDeg <= 22.5))) {
        snprintf(dir_str, sizeof(dir_str), "N");
      } else if ((bearingDeg > 22.5) && (bearingDeg < 67.5)) {
        snprintf(dir_str, sizeof(dir_str), "NE");
      } else if ((bearingDeg >= 67.5) && (bearingDeg <= 112.5)) {
        snprintf(dir_str, sizeof(dir_str), "E");
      } else if ((bearingDeg > 112.5) && (bearingDeg < 157.5)) {
        snprintf(dir_str, sizeof(dir_str), "SE");
      } else if ((bearingDeg >= 157.5) && (bearingDeg <= 202.5)) {
        snprintf(dir_str, sizeof(dir_str), "S");
      } else if ((bearingDeg > 202.5) && (bearingDeg < 247.5)) {
        snprintf(dir_str, sizeof(dir_str), "SW");
      } else if ((bearingDeg >= 247.5) && (bearingDeg <= 292.5)) {
        snprintf(dir_str, sizeof(dir_str), "W");
      } else if ((bearingDeg > 292.5) && (bearingDeg < 337.5)) {
        snprintf(dir_str, sizeof(dir_str), "NW");
      }
    } else {
      snprintf(dir_str, sizeof(dir_str), "OFF");
      snprintf(val_str, sizeof(val_str), "-");
    }

    rh += drawDevUiElementLeft(p, x, ry, dir_str, val_str, "", valueColor);
    ry = y + rh;
  }

  // Add Altitude of Current Location
  // Unit: Meters
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (gpsAccuracy != 0.00) {
      snprintf(val_str, sizeof(val_str), "%.1f", altitude);
    } else {
      snprintf(val_str, sizeof(val_str), "-");
    }

    rh += drawDevUiElementLeft(p, x, ry, val_str, "ALTITUDE", "m", valueColor);
    ry = y + rh;
  }

  rh += 25;
  p.setBrush(QColor(0, 0, 0, 0));
  QRect ldu(x, y, 184, rh);
  //p.drawRoundedRect(ldu, 20, 20);
}

void OnroadHud::drawRightDevUiBorder(QPainter &p, int x, int y) {
  int rh = 580;
  int rw = 184;
  p.setPen(QPen(QColor(0xff, 0xff, 0xff, 100), 6));
  p.setBrush(QColor(0, 0, 0, 0));
  if (devUiEnabled == 2) {
    rw *= 2;
  }
  QRect ldu(x, y, rw, rh);
  p.drawRoundedRect(ldu, 20, 20);
}

void OnroadHud::drawStandstillTimer(QPainter &p, int x, int y) {
  char lab_str[16];
  char val_str[16];
  int minute = 0;
  int second = 0;
  QColor labelColor = QColor(255, 175, 3, 240);
  QColor valueColor = QColor(255, 255, 255, 240);

  minute = (int)(standstillElapsedTime / 60);
  second = (int)((standstillElapsedTime) - (minute * 60));

  if (standStill) {
    snprintf(lab_str, sizeof(lab_str), "STOP");
    snprintf(val_str, sizeof(val_str), "%01d:%02d", minute, second);
  }

  drawStandstillTimerText(p, x, y, lab_str, val_str, labelColor, valueColor);
}

// NvgWindow
void NvgWindow::initializeGL() {
  CameraViewWidget::initializeGL();
  qInfo() << "OpenGL version:" << QString((const char*)glGetString(GL_VERSION));
  qInfo() << "OpenGL vendor:" << QString((const char*)glGetString(GL_VENDOR));
  qInfo() << "OpenGL renderer:" << QString((const char*)glGetString(GL_RENDERER));
  qInfo() << "OpenGL language version:" << QString((const char*)glGetString(GL_SHADING_LANGUAGE_VERSION));

  prev_draw_t = millis_since_boot();
  setBackgroundColor(bg_colors[STATUS_DISENGAGED]);
}

void NvgWindow::updateFrameMat(int w, int h) {
  CameraViewWidget::updateFrameMat(w, h);

  UIState *s = &QUIState::ui_state;
  s->fb_w = w;
  s->fb_h = h;
  auto intrinsic_matrix = s->wide_camera ? ecam_intrinsic_matrix : fcam_intrinsic_matrix;
  float zoom = ZOOM / intrinsic_matrix.v[0];
  if (s->wide_camera) {
    zoom *= 0.5;
  }
  // Apply transformation such that video pixel coordinates match video
  // 1) Put (0, 0) in the middle of the video
  // 2) Apply same scaling as video
  // 3) Put (0, 0) in top left corner of video
  s->car_space_transform.reset();
  s->car_space_transform.translate(w / 2, h / 2 + y_offset)
      .scale(zoom, zoom)
      .translate(-intrinsic_matrix.v[2], -intrinsic_matrix.v[5]);
}

// shane's colored lane line
void NvgWindow::drawLaneLines(QPainter &painter, const UIScene &scene) {
  UIState *s = &QUIState::ui_state;
  int steerOverride = (*s->sm)["carState"].getCarState().getSteeringPressed();
  bool madsEnabled = (*s->sm)["controlsState"].getControlsState().getMadsEnabled();
  bool suspended = (*s->sm)["controlsState"].getControlsState().getSuspended();
  if (!scene.lateralPlan.dynamicLaneProfileStatus) {
    // lanelines
    for (int i = 0; i < std::size(scene.lane_line_vertices); ++i) {
      if (i == 1 || i == 2) {
        // TODO: can we just use the projected vertices somehow?
        const cereal::ModelDataV2::XYZTData::Reader &line = (*s->sm)["modelV2"].getModelV2().getLaneLines()[i];
        const float default_pos = 1.4;  // when lane poly isn't available
        const float lane_pos = line.getY().size() > 0 ? std::abs(line.getY()[5]) : default_pos;  // get redder when line is closer to car
        float hue = 332.5 * lane_pos - 332.5;  // equivalent to {1.4, 1.0}: {133, 0} (green to red)
        hue = std::fmin(133, fmax(0, hue)) / 360.;  // clip and normalize
        painter.setBrush(QColor::fromHslF(hue, 1.0, 0.50, scene.lane_line_probs[i]));
      } else {
        painter.setBrush(QColor::fromRgbF(1.0, 1.0, 1.0, scene.lane_line_probs[i]));
      }
      painter.drawPolygon(scene.lane_line_vertices[i].v, scene.lane_line_vertices[i].cnt);
    }
    // road edges
    for (int i = 0; i < std::size(scene.road_edge_vertices); ++i) {
      painter.setBrush(QColor::fromRgbF(1.0, 0, 0, std::clamp<float>(1.0 - scene.road_edge_stds[i], 0.0, 1.0)));
      painter.drawPolygon(scene.road_edge_vertices[i].v, scene.road_edge_vertices[i].cnt);
    }
  }
  // paint path
  QLinearGradient bg(0, height(), 0, height() / 4);
  if (madsEnabled) {
    if (steerOverride && !suspended) {
      bg.setColorAt(0, blackColor(80));
      bg.setColorAt(1, blackColor(20));
    } else if (suspended) {
      bg.setColorAt(0, QColor(255, 255, 255));
      bg.setColorAt(1, QColor(255, 255, 255, 0));
    } else {
      bg.setColorAt(0, scene.lateralPlan.dynamicLaneProfileStatus ? redColor() : greenColor());
      bg.setColorAt(1, scene.lateralPlan.dynamicLaneProfileStatus ? redColor(0) : greenColor(0));
    }
  } else {
    bg.setColorAt(0, QColor(255, 255, 255));
    bg.setColorAt(1, QColor(255, 255, 255, 0));
  }
  painter.setBrush(bg);
  painter.drawPolygon(scene.track_vertices.v, scene.track_vertices.cnt);
}

void NvgWindow::drawLead(QPainter &painter, const cereal::ModelDataV2::LeadDataV3::Reader &lead_data, const QPointF &vd, bool openpilot_longitudinal_control) {
  const float speedBuff = 10.;
  const float leadBuff = 40.;
  const float d_rel = lead_data.getX()[0];
  const float v_rel = lead_data.getV()[0];

  float fillAlpha = 0;
  if (d_rel < leadBuff) {
    fillAlpha = 255 * (1.0 - (d_rel / leadBuff));
    if (v_rel < 0) {
      fillAlpha += 255 * (-1 * (v_rel / speedBuff));
    }
    fillAlpha = (int)(fmin(fillAlpha, 255));
  }

  float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * 2.35;
  float x = std::clamp((float)vd.x(), 0.f, width() - sz / 2);
  float y = std::fmin(height() - sz * .6, (float)vd.y());

  float g_xo = sz / 5;
  float g_yo = sz / 10;

  QPointF glow[] = {{x + (sz * 1.35) + g_xo, y + sz + g_yo}, {x, y - g_xo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo}};
  painter.setBrush(openpilot_longitudinal_control ? QColor(218, 202, 37, 255) : QColor(37, 53, 218, 255));
  painter.drawPolygon(glow, std::size(glow));

  // chevron
  QPointF chevron[] = {{x + (sz * 1.25), y + sz}, {x, y}, {x - (sz * 1.25), y + sz}};
  painter.setBrush(redColor(fillAlpha));
  painter.drawPolygon(chevron, std::size(chevron));
}

void NvgWindow::paintGL() {
  CameraViewWidget::paintGL();

  UIState *s = &QUIState::ui_state;
  if (s->scene.world_objects_visible) {
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.setPen(Qt::NoPen);

    drawLaneLines(painter, s->scene);

    if (s->scene.longitudinal_control) {
      auto leads = (*s->sm)["modelV2"].getModelV2().getLeadsV3();
      if (leads[0].getProb() > .5) {
        drawLead(painter, leads[0], s->scene.lead_vertices[0], s->scene.longitudinal_control);
      }
      if (leads[1].getProb() > .5 && (std::abs(leads[1].getX()[0] - leads[0].getX()[0]) > 3.0)) {
        drawLead(painter, leads[1], s->scene.lead_vertices[1], s->scene.longitudinal_control);
      }
    } else {
      auto leads = (*s->sm)["modelV2"].getModelV2().getLeadsV3();
      if (s->scene.carState.radarObjValid) {
        drawLead(painter, leads[0], s->scene.lead_vertices[0], s->scene.longitudinal_control);
      }
    }
  }

  double cur_draw_t = millis_since_boot();
  double dt = cur_draw_t - prev_draw_t;
  if (dt > 66) {
    // warn on sub 15fps
    LOGW("slow frame time: %.2f", dt);
  }
  prev_draw_t = cur_draw_t;
}

void NvgWindow::showEvent(QShowEvent *event) {
  CameraViewWidget::showEvent(event);

  ui_update_params(&QUIState::ui_state);
  prev_draw_t = millis_since_boot();
}
