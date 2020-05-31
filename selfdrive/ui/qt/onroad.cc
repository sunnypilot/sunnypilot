#include "selfdrive/ui/qt/onroad.h"

#include <cmath>
#include <chrono>

#include <QDebug>
#include <iomanip>
#include <sstream>
#include <QString>
#include <QMouseEvent>
#include <QPainterPath>

#include "common/timing.h"
#include "selfdrive/ui/qt/util.h"
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

  nvg = new NvgWindow(VISION_STREAM_ROAD, this);

  QWidget * split_wrapper = new QWidget;
  split = new QHBoxLayout(split_wrapper);
  split->setContentsMargins(0, 0, 0, 0);
  split->setSpacing(0);
  split->addWidget(nvg);

  stacked_layout->addWidget(split_wrapper);

  alerts = new OnroadAlerts(this);
  alerts->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(alerts);

  // setup stacking order
  alerts->raise();

  setAttribute(Qt::WA_OpaquePaintEvent);
  QObject::connect(uiState(), &UIState::uiUpdate, this, &OnroadWindow::updateState);
  QObject::connect(uiState(), &UIState::offroadTransition, this, &OnroadWindow::offroadTransition);
}

void OnroadWindow::updateState(const UIState &s) {
  QColor bgColor = bg_colors[s.status];
  Alert alert = Alert::get(*(s.sm), s.scene.started_frame, s.scene.display_debug_alert_frame);
  if (s.sm->updated("controlsState") || !alert.equal({})) {
    if (alert.type == "controlsUnresponsive") {
      bgColor = bg_colors[STATUS_ALERT];
    } else if (alert.type == "controlsUnresponsivePermanent") {
      bgColor = bg_colors[STATUS_DISENGAGED];
    }
    alerts->updateAlert(alert, bgColor);
  }

  nvg->updateState(s);

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
  uiState()->scene.display_debug_alert_frame = sm.frame;
}

void OnroadWindow::mousePressEvent(QMouseEvent* e) {
  bool sidebarVisible = geometry().x() > 0;
  bool propagate_event = true;

  SubMaster &sm = *(uiState()->sm);
  auto car_state = sm["carState"].getCarState();
  auto longitudinal_plan = sm["longitudinalPlan"].getLongitudinalPlan();
  const QRect dlp_btn_rect = QRect(bdr_s * 2 + 220, rect().bottom() - footer_h / 2 - 100, 192, 192);
  const QRect gac_btn_rect = QRect(bdr_s * 2 + 220 + 222, rect().bottom() - footer_h / 2 - 100, 192, 192);
  const QRect speed_limit_touch_rect = speed_sgn_rc.adjusted(-50, -50, 50, 50);
  const QRect debug_tap_rect = QRect(rect().center().x() - 200, rect().center().y() - 200, 400, 400);
  int gac_tr = -1;

  if (longitudinal_plan.getSpeedLimit() > 0.0 && speed_limit_touch_rect.contains(e->x(), e->y())) {
    // If touching the speed limit sign area when visible
    uiState()->scene.last_speed_limit_sign_tap = seconds_since_boot();
    Params().putBool("LastSpeedLimitSignTap", 1);
    Params().putBool("LastSpeedLimitSignTap", 0);
    uiState()->scene.speed_limit_control_enabled = !uiState()->scene.speed_limit_control_enabled;
    Params().putBool("SpeedLimitControl", uiState()->scene.speed_limit_control_enabled);
    propagate_event = false;
  } else if (uiState()->scene.debug_snapshot_enabled && debug_tap_rect.contains(e->x(), e->y())) {
    issue_debug_snapshot(sm);
    propagate_event = false;
  } else if (uiState()->scene.end_to_end && dlp_btn_rect.contains(e->x(), e->y())) {
    uiState()->scene.dynamic_lane_profile = uiState()->scene.dynamic_lane_profile + 1;
    if (uiState()->scene.dynamic_lane_profile > 2) {
      uiState()->scene.dynamic_lane_profile = 0;
    }
    if (uiState()->scene.dynamic_lane_profile == 0) {
      Params().put("DynamicLaneProfile", "0", 1);
    } else if (uiState()->scene.dynamic_lane_profile == 1) {
      Params().put("DynamicLaneProfile", "1", 1);
    } else if (uiState()->scene.dynamic_lane_profile == 2) {
      Params().put("DynamicLaneProfile", "2", 1);
    }
    propagate_event = false;
  } else if (uiState()->scene.gap_adjust_cruise && (uiState()->scene.gap_adjust_cruise_mode != 0) && uiState()->scene.longitudinal_control && gac_btn_rect.contains(e->x(), e->y())) {
    gac_tr = car_state.getGapAdjustCruiseTr() - 1;
    if (gac_tr < 1) {
      if (uiState()->scene.car_make == 1) gac_tr = 4;
      if (gac_tr < 0) {
        if (uiState()->scene.car_make == 2) gac_tr = 2;
        else if (uiState()->scene.car_make == 3) gac_tr = 3;
      }
    }
    if (gac_tr == 4) {
      Params().put("GapAdjustCruiseTr", "4", 1);
    } else if (gac_tr == 3) {
      Params().put("GapAdjustCruiseTr", "3", 1);
    } else if (gac_tr == 2) {
      Params().put("GapAdjustCruiseTr", "2", 1);
    } else if (gac_tr == 1) {
      Params().put("GapAdjustCruiseTr", "1", 1);
    } else if (gac_tr == 0) {
      Params().put("GapAdjustCruiseTr", "0", 1);
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
    bool custom_mapbox = Params().getBool("CustomMapbox") && QString::fromStdString(Params().get("CustomMapboxTokenSk")) != "";
    if (map == nullptr && (uiState()->prime_type || !MAPBOX_TOKEN.isEmpty() || custom_mapbox)) {
      MapWindow * m = new MapWindow(get_mapbox_settings());
      map = m;

      QObject::connect(uiState(), &UIState::offroadTransition, m, &MapWindow::offroadTransition);

      m->setFixedWidth(topWidget(this)->width() / 2);
      split->addWidget(m, 0, Qt::AlignRight);

      // Make map visible after adding to split
      m->offroadTransition(offroad);
    }
  }
#endif

  alerts->updateAlert({}, bg);

  // update stream type
  bool wide_cam = Hardware::TICI() && Params().getBool("EnableWideCamera");
  nvg->setStreamType(wide_cam ? VISION_STREAM_WIDE_ROAD : VISION_STREAM_ROAD);
}

void OnroadWindow::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.fillRect(rect(), QColor(bg.red(), bg.green(), bg.blue(), 255));
}

// ***** onroad widgets *****

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
    configFont(p, "Inter", 74, "SemiBold");
    p.drawText(r, Qt::AlignCenter, alert.text1);
  } else if (alert.size == cereal::ControlsState::AlertSize::MID) {
    configFont(p, "Inter", 88, "Bold");
    p.drawText(QRect(0, c.y() - 125, width(), 150), Qt::AlignHCenter | Qt::AlignTop, alert.text1);
    configFont(p, "Inter", 66, "Regular");
    p.drawText(QRect(0, c.y() + 21, width(), 90), Qt::AlignHCenter, alert.text2);
  } else if (alert.size == cereal::ControlsState::AlertSize::FULL) {
    bool l = alert.text1.length() > 15;
    configFont(p, "Inter", l ? 132 : 177, "Bold");
    p.drawText(QRect(0, r.y() + (l ? 240 : 270), width(), 600), Qt::AlignHCenter | Qt::TextWordWrap, alert.text1);
    configFont(p, "Inter", 88, "Regular");
    p.drawText(QRect(0, r.height() - (l ? 361 : 420), width(), 300), Qt::AlignHCenter | Qt::TextWordWrap, alert.text2);
  }
}

// NvgWindow

NvgWindow::NvgWindow(VisionStreamType type, QWidget* parent) : fps_filter(UI_FREQ, 3, 1. / UI_FREQ), CameraViewWidget("camerad", type, true, parent) {
  engage_img = loadPixmap("../assets/img_chffr_wheel.png", {img_size, img_size});
  dm_img = loadPixmap("../assets/img_driver_face.png", {img_size, img_size});
  mads_imgs[0] = QPixmap("../assets/img_mads_off.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  mads_imgs[1] = QPixmap("../assets/img_mads_on.png").scaled(img_size, img_size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  how_img = loadPixmap("../assets/img_hands_on_wheel.png", {img_size, img_size});
  map_img = loadPixmap("../assets/img_world_icon.png", {subsign_img_size, subsign_img_size});
  left_img = loadPixmap("../assets/img_turn_left_icon.png", {subsign_img_size, subsign_img_size});
  right_img = loadPixmap("../assets/img_turn_right_icon.png", {subsign_img_size, subsign_img_size});
}

void NvgWindow::updateState(const UIState &s) {
  const int SET_SPEED_NA = 255;
  const SubMaster &sm = *(s.sm);

  const bool cs_alive = sm.alive("controlsState");
  const bool nav_alive = sm.alive("navInstruction") && sm["navInstruction"].getValid();

  const auto cs = sm["controlsState"].getControlsState();

  float set_speed = cs_alive ? cs.getVCruise(): SET_SPEED_NA;
  bool cruise_set = set_speed > 0 && (int)set_speed != SET_SPEED_NA;
  if (cruise_set && !s.scene.is_metric) {
    set_speed *= KM_TO_MILE;
  }

  float cur_speed = cs_alive ? std::max<float>(0.0, sm["carState"].getCarState().getVEgo()) : 0.0;
  cur_speed  *= s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH;

  auto speed_limit_sign = sm["navInstruction"].getNavInstruction().getSpeedLimitSign();
  float speed_limit_mb = nav_alive ? sm["navInstruction"].getNavInstruction().getSpeedLimit() : 0.0;
  speed_limit_mb *= (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);

  setProperty("speedLimitMb", speed_limit_mb);
  setProperty("has_us_speed_limit", nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::MUTCD);
  setProperty("has_eu_speed_limit", nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::VIENNA);

  setProperty("is_cruise_set", cruise_set);
  setProperty("is_metric", s.scene.is_metric);
  setProperty("speed", cur_speed);
  setProperty("setSpeed", set_speed);
  setProperty("speedUnit", s.scene.is_metric ? "km/h" : "mph");
  setProperty("hideDM", cs.getAlertSize() != cereal::ControlsState::AlertSize::NONE);
  setProperty("status", s.status);
  setProperty("steerOverride", sm["carState"].getCarState().getSteeringPressed());
  setProperty("latActive", sm["carState"].getCarState().getLatActive());
  setProperty("madsEnabled", sm["carState"].getCarState().getMadsEnabled());
  setProperty("is_brakelight_on", sm["carState"].getCarState().getBrakeLights());

  // update engageability and DM icons at 2Hz
  if (sm.frame % (UI_FREQ / 2) == 0) {
    const auto howState = sm["driverMonitoringState"].getDriverMonitoringState().getHandsOnWheelState();

    setProperty("engageable", cs.getEngageable() || cs.getEnabled());
    setProperty("dmActive", sm["driverMonitoringState"].getDriverMonitoringState().getIsActiveMode());
    setProperty("showHowAlert", howState >= cereal::DriverMonitoringState::HandsOnWheelState::WARNING);
    setProperty("howWarning", howState == cereal::DriverMonitoringState::HandsOnWheelState::WARNING);

    const auto lp = sm["longitudinalPlan"].getLongitudinalPlan();
    const auto vtscState = lp.getVisionTurnControllerState();
    const float vtsc_speed = lp.getVisionTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const auto lpSource = lp.getLongitudinalPlanSource();
    QColor vtsc_color = vtsc_colors[int(vtscState)];
    vtsc_color.setAlpha(lpSource == cereal::LongitudinalPlan::LongitudinalPlanSource::TURN ? 255 : 100);
    setProperty("showVTSC", vtscState > cereal::LongitudinalPlan::VisionTurnControllerState::DISABLED);
    setProperty("vtscSpeed", QString::number(std::nearbyint(vtsc_speed)));
    setProperty("vtscColor", vtsc_color);
    setProperty("showDebugUI", s.scene.show_debug_ui);
    const auto lmd = sm["liveMapData"].getLiveMapData();
    const uint64_t lmd_fix_time = lmd.getLastGpsTimestamp();
    const uint64_t current_ts = std::chrono::duration_cast<std::chrono::milliseconds>
                                (std::chrono::system_clock::now().time_since_epoch()).count();
    const bool show_road_name = current_ts - lmd_fix_time < 10000; // hide if fix older than 10s
    setProperty("roadName", show_road_name ? QString::fromStdString(lmd.getCurrentRoadName()) : "");

    float speed_limit = lp.getSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
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
    const QString sl_inactive_str(sl_temp_inactive ? "TEMP" : "OFF");
    const QString sl_substring(sl_inactive || sl_temp_inactive ? sl_inactive_str :
                               sl_distance > 0 ? sl_distance_str : sl_offset_str);

    setProperty("showSpeedLimit", speed_limit > 0.0);
    setProperty("speedLimit", speed_limit);
    setProperty("slcSubText", sl_substring);
    setProperty("slcSubTextSize", sl_inactive || sl_temp_inactive || sl_distance > 0 ? 25.0 : 27.0);
    setProperty("mapSourcedSpeedLimit", lp.getIsMapSpeedLimit());
    setProperty("slcActive", !sl_inactive && !sl_temp_inactive);

    const float mtsc_speed = lp.getTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const auto mtscState = lp.getTurnSpeedControlState();
    const int t_distance = int(lp.getDistToTurn() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
    const QString t_distance_str(QString::number(t_distance) + (s.scene.is_metric ? "m" : "f"));

    setProperty("showTurnSpeedLimit", mtsc_speed > 0.0 && (mtsc_speed < cur_speed || s.scene.show_debug_ui));
    setProperty("turnSpeedLimit", QString::number(std::nearbyint(mtsc_speed)));
    setProperty("mtscSubText", t_distance > 0 ? t_distance_str : QString(""));
    setProperty("mtscActive", mtscState > cereal::LongitudinalPlan::SpeedLimitControlState::TEMP_INACTIVE);
    setProperty("curveSign", lp.getTurnSign());
  }

  setProperty("endToEnd", s.scene.end_to_end);
  setProperty("dynamicLaneProfile", s.scene.dynamic_lane_profile);

  const auto carState = sm["carState"].getCarState();
  setProperty("standStillTimer", s.scene.stand_still_timer);
  setProperty("standStill", carState.getStandStill());
  setProperty("standstillElapsedTime", sm["lateralPlan"].getLateralPlan().getStandstillElapsed());
  const auto leadOne = sm["radarState"].getRadarState().getLeadOne();
  const auto gpsLocationExternal = sm["gpsLocationExternal"].getGpsLocationExternal();
  setProperty("lead_d_rel", leadOne.getDRel());
  setProperty("lead_v_rel", leadOne.getVRel());
  setProperty("lead_status", leadOne.getStatus());
  setProperty("angleSteers", carState.getSteeringAngleDeg());
  setProperty("steerAngleDesired", cs.getLateralControlState().getPidState().getSteeringAngleDesiredDeg());
  setProperty("memoryUsagePercent", sm["deviceState"].getDeviceState().getMemoryUsagePercent());
  setProperty("devUiEnabled", s.scene.dev_ui_enabled);
  setProperty("devUiRow", s.scene.dev_ui_row);
  setProperty("gpsAccuracy", gpsLocationExternal.getAccuracy());
  setProperty("altitude", gpsLocationExternal.getAltitude());
  setProperty("vEgo", carState.getVEgo());
  setProperty("aEgo", carState.getAEgo());
  setProperty("steeringTorqueEps", carState.getSteeringTorqueEps());
  setProperty("bearingAccuracyDeg", gpsLocationExternal.getBearingAccuracyDeg());
  setProperty("bearingDeg", gpsLocationExternal.getBearingDeg());

  setProperty("gapAdjustCruise", s.scene.gap_adjust_cruise);
  setProperty("gapAdjustCruiseMode", s.scene.gap_adjust_cruise_mode);
  setProperty("gapAdjustCruiseTr", carState.getGapAdjustCruiseTr());
  setProperty("carMake", s.scene.car_make);

  setProperty("speedLimitStyle", s.scene.speed_limit_style);

  if (s.scene.calibration_valid) {
    CameraViewWidget::updateCalibration(s.scene.view_from_calib);
  } else {
    CameraViewWidget::updateCalibration(DEFAULT_CALIBRATION);
  }
}

void NvgWindow::drawHud(QPainter &p) {
  p.save();

  // Header gradient
  QLinearGradient bg(0, header_h - (header_h / 2.5), 0, header_h);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, width(), header_h, bg);

  QRect rc(bdr_s * 2, bdr_s * 1.5, 184, 202);

  QString speedLimitStr = (speedLimitMb > 1) ? QString::number(std::nearbyint(speedLimitMb)) : "–";
  QString speedLimitStrSlc = showSpeedLimit ? QString::number(std::nearbyint(speedLimit)) : "–";
  QString speedStr = QString::number(std::nearbyint(speed));
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(setSpeed)) : "–";

  // Draw outer box + border to contain set speed and speed limit
  int default_rect_width = 172;
  int rect_width = default_rect_width;
  if (is_metric || has_eu_speed_limit) rect_width = 200;
  if ((!roadName.isEmpty() && speedLimitStyle == 0 && speedLimitStrSlc.size() >= 3) || (has_us_speed_limit && speedLimitStr.size() >= 3)) rect_width = 223;

  int rect_height = 204;
  if ((!roadName.isEmpty() && speedLimitStyle == 0) || has_us_speed_limit) rect_height = 432;
  else if ((!roadName.isEmpty() && speedLimitStyle == 1) || has_eu_speed_limit) rect_height = 392;

  int top_radius = 32;
  int bottom_radius = ((!roadName.isEmpty() && speedLimitStyle == 1) || has_eu_speed_limit) ? 100 : 32;

  QRect set_speed_rect(60 + default_rect_width / 2 - rect_width / 2, 45, rect_width, rect_height);
  p.setPen(QPen(QColor(255, 255, 255, 75), 6));
  p.setBrush(QColor(0, 0, 0, 166));
  drawRoundedRect(p, set_speed_rect, top_radius, top_radius, bottom_radius, bottom_radius);

  // Draw MAX
  if (is_cruise_set) {
    if (status == STATUS_DISENGAGED) {
      p.setPen(QColor(0xff, 0xff, 0xff, 0xff));
    } else if (status == STATUS_OVERRIDE) {
      p.setPen(QColor(0x91, 0x9b, 0x95, 0xff));
    } else if (speedLimit > 0) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimit + 5, speedLimit + 15, speedLimit + 25},
        {QColor(0x80, 0xd8, 0xa6, 0xff), QColor(0xff, 0xe4, 0xbf, 0xff), QColor(0xff, 0xbf, 0xbf, 0xff)}
      ));
    } else if (speedLimitMb > 0) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimitMb + 5, speedLimitMb + 15, speedLimitMb + 25},
        {QColor(0x80, 0xd8, 0xa6, 0xff), QColor(0xff, 0xe4, 0xbf, 0xff), QColor(0xff, 0xbf, 0xbf, 0xff)}
      ));
    } else {
      p.setPen(QColor(0x80, 0xd8, 0xa6, 0xff));
    }
  } else {
    p.setPen(QColor(0xa6, 0xa6, 0xa6, 0xff));
  }
  configFont(p, "Inter", 40, "SemiBold");
  QRect max_rect = getTextRect(p, Qt::AlignCenter, "MAX");
  max_rect.moveCenter({set_speed_rect.center().x(), 0});
  max_rect.moveTop(set_speed_rect.top() + 27);
  p.drawText(max_rect, Qt::AlignCenter, "MAX");

  // Draw set speed
  if (is_cruise_set) {
    if (speedLimit > 0 && status != STATUS_DISENGAGED && status != STATUS_OVERRIDE) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimit + 5, speedLimit + 15, speedLimit + 25},
        {whiteColor(), QColor(0xff, 0x95, 0x00, 0xff), QColor(0xff, 0x00, 0x00, 0xff)}
      ));
    } else if (speedLimitMb > 0 && status != STATUS_DISENGAGED && status != STATUS_OVERRIDE) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimitMb + 5, speedLimitMb + 15, speedLimitMb + 25},
        {whiteColor(), QColor(0xff, 0x95, 0x00, 0xff), QColor(0xff, 0x00, 0x00, 0xff)}
      ));
    } else {
      p.setPen(whiteColor());
    }
  } else {
    p.setPen(QColor(0x72, 0x72, 0x72, 0xff));
  }
  configFont(p, "Inter", 90, "Bold");
  QRect speed_rect = getTextRect(p, Qt::AlignCenter, setSpeedStr);
  speed_rect.moveCenter({set_speed_rect.center().x(), 0});
  speed_rect.moveTop(set_speed_rect.top() + 77);
  p.drawText(speed_rect, Qt::AlignCenter, setSpeedStr);

  // US/Canada (MUTCD style) sign
  if ((!roadName.isEmpty() && speedLimitStyle == 0) || has_us_speed_limit) {
    const int border_width = 6;
    const int sign_width = (speedLimitStrSlc.size() >= 3) ? 199 : 148;
    const int sign_height = 216;

    // White outer square
    QRect sign_rect_outer(set_speed_rect.left() + 12, set_speed_rect.bottom() - 11 - sign_height, sign_width, sign_height);
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, 255));
    p.drawRoundedRect(sign_rect_outer, 24, 24);

    // Smaller white square with black border
    QRect sign_rect(sign_rect_outer.left() + 1.5 * border_width, sign_rect_outer.top() + 1.5 * border_width, sign_width - 3 * border_width, sign_height - 3 * border_width);
    p.setPen(QPen(QColor(0, 0, 0, 255), border_width));
    p.setBrush(QColor(255, 255, 255, 255));
    p.drawRoundedRect(sign_rect, 16, 16);

    // "SPEED"
    configFont(p, "Inter", 28, "SemiBold");
    QRect text_speed_rect = getTextRect(p, Qt::AlignCenter, "SPEED");
    text_speed_rect.moveCenter({sign_rect.center().x(), 0});
    text_speed_rect.moveTop(sign_rect_outer.top() + 22);
    p.drawText(text_speed_rect, Qt::AlignCenter, "SPEED");

    // "LIMIT"
    QRect text_limit_rect = getTextRect(p, Qt::AlignCenter, "LIMIT");
    text_limit_rect.moveCenter({sign_rect.center().x(), 0});
    text_limit_rect.moveTop(sign_rect_outer.top() + 51);
    p.drawText(text_limit_rect, Qt::AlignCenter, "LIMIT");

    // Speed limit value
    configFont(p, "Inter", 70, "Bold");
    QRect speed_limit_rect = getTextRect(p, Qt::AlignCenter, speedLimitStrSlc);
    speed_limit_rect.moveCenter({sign_rect.center().x(), 0});
    speed_limit_rect.moveTop(sign_rect_outer.top() + 85);
    p.drawText(speed_limit_rect, Qt::AlignCenter, speedLimitStrSlc);

    // Speed limit offset value
    configFont(p, "Inter", 32, "Bold");
    QRect speed_limit_offset_rect = getTextRect(p, Qt::AlignCenter, slcSubText);
    speed_limit_offset_rect.moveCenter({sign_rect.center().x(), 0});
    speed_limit_offset_rect.moveTop(sign_rect_outer.top() + 85 + 77);
    p.drawText(speed_limit_offset_rect, Qt::AlignCenter, slcSubText);
  }

  // EU (Vienna style) sign
  if ((!roadName.isEmpty() && speedLimitStyle == 1) || has_eu_speed_limit) {
    int outer_radius = 176 / 2;
    int inner_radius_1 = outer_radius - 6; // White outer border
    int inner_radius_2 = inner_radius_1 - 20; // Red circle

    // Draw white circle with red border
    QPoint center(set_speed_rect.center().x() + 1, set_speed_rect.top() + 204 + outer_radius);
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, 255));
    p.drawEllipse(center, outer_radius, outer_radius);
    p.setBrush(QColor(255, 0, 0, 255));
    p.drawEllipse(center, inner_radius_1, inner_radius_1);
    p.setBrush(QColor(255, 255, 255, 255));
    p.drawEllipse(center, inner_radius_2, inner_radius_2);

    // Speed limit value
    int font_size = (speedLimitStr.size() >= 3) ? 60 : 70;
    configFont(p, "Inter", font_size, "Bold");
    QRect speed_limit_rect = getTextRect(p, Qt::AlignCenter, speedLimitStrSlc);
    speed_limit_rect.moveCenter(center);
    p.setPen(QColor(0, 0, 0, 255));
    p.drawText(speed_limit_rect, Qt::AlignCenter, speedLimitStrSlc);

    // Speed limit offset value
    configFont(p, "Inter", slcSubTextSize, "Bold");
    QRect speed_limit_offset_rect = getTextRect(p, Qt::AlignCenter, slcSubText);
    speed_limit_offset_rect.moveCenter(center);
    speed_limit_offset_rect.moveTop(center.y() + 27);
    p.setPen(QColor(0, 0, 0, 255));
    p.drawText(speed_limit_offset_rect, Qt::AlignCenter, slcSubText);
  }

  // current speed
  configFont(p, "Inter", 176, "Bold");
  drawSpeedText(p, rect().center().x(), 210, speedStr, is_brakelight_on ? QColor(0xff, 0, 0, 255) : QColor(0xff, 0xff, 0xff, 255));
  configFont(p, "Inter", 66, "Regular");
  drawText(p, rect().center().x(), 290, speedUnit, 200);

  int rn_btn = 0;
  if (showDebugUI && !roadName.isEmpty()) rn_btn = 30;

  if (engageable) {
    if (showDebugUI && showVTSC) {
      drawVisionTurnControllerUI(p, rect().right() - 184 - bdr_s, int(bdr_s * 1.5), 184, vtscColor, vtscSpeed, 100);
    } else {
      // engage-ability icon
      drawIcon(p, rect().right() - radius / 2 - bdr_s * 2, radius / 2 + int(bdr_s * 1.5),
               engage_img, bg_colors[status], 1.0);
    }

    // Stand Still Timer
    if (standStillTimer && standStill) {
      drawStandstillTimer(p, rect().right() - 650, 30 + 160 + 250);
    }

    // Hands on wheel icon
    if (showHowAlert) {
      drawIcon(p, rect().right() - radius / 2 - bdr_s * 2, int(bdr_s * 1.5) + 2 * radius + bdr_s + radius / 2,
               how_img, bg_colors[howWarning ? STATUS_WARNING : STATUS_ALERT], 1.0);
    }

    // Turn Speed Sign
    if (showTurnSpeedLimit) {
      rc.moveTop(speed_sgn_rc.bottom() + bdr_s);
      drawTurnSpeedSign(p, rc, turnSpeedLimit, mtscSubText, curveSign, mtscActive);
    }
  }

  // dm icon
  if (!hideDM) {
    drawIcon(p, radius / 2 + (bdr_s * 2), (rect().bottom() - footer_h / 2) - rn_btn,
             dm_img, QColor(0, 0, 0, 70), dmActive ? 1.0 : 0.2);
  }

  // MADS icon
  drawMadsIcon(p, rect().right() - radius / 2 - bdr_s * 2 - 184, radius / 2 + int(bdr_s * 1.5),
               madsEnabled ? (madsEnabled && !latActive) ? mads_imgs[0] : mads_imgs[1] : mads_imgs[0], QColor(75, 75, 75, 75), 1.0);

  // Dynamic Lane Profile Button
  if (endToEnd) {
    drawDlpButton(p, bdr_s * 2 + 220, (rect().bottom() - footer_h / 2 - 100) - rn_btn, 192, 192);
  }

  // Right Dev UI
  QRect rc2(rect().right() - (bdr_s * 2), bdr_s * 1.5, 184, 202);
  if (devUiEnabled) {
    if (devUiRow == 0) {
      drawRightDevUi(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
      drawRightDevUiBorder(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
    } else if (devUiRow == 1) {
      drawRightDevUi(p, rect().right() - 184 - bdr_s * 2, bdr_s * 2 + rc2.height());
      drawRightDevUi2(p, rect().right() - 184 - bdr_s * 2 - 184, bdr_s * 2 + rc2.height());
      drawRightDevUiBorder(p, rect().right() - 184 - bdr_s * 2 - 184, bdr_s * 2 + rc2.height());
    }
  }

  // Gap Adjust Cruise Button
  if (gapAdjustCruise && (gapAdjustCruiseMode != 0) && uiState()->scene.longitudinal_control) {
    drawGacButton(p, bdr_s * 2 + 220 + 222, (rect().bottom() - footer_h / 2 - 100) - rn_btn, 192, 192);
  }

  // Bottom bar road name
  if (showDebugUI && !roadName.isEmpty()) {
    const int h = 60;
    QRect bar_rc(rect().left(), rect().bottom() - h, rect().width(), h);
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(0, 0, 0, 100));
    p.drawRect(bar_rc);
    configFont(p, "Inter", 38, "Bold");
    drawCenteredText(p, bar_rc.center().x(), bar_rc.center().y(), roadName, QColor(255, 255, 255, 200));
  }
  p.restore();
}

void NvgWindow::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = getTextRect(p, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void NvgWindow::drawSpeedText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void NvgWindow::drawColoredText(QPainter &p, int x, int y, const QString &text, QColor &color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void NvgWindow::drawStandstillTimerText(QPainter &p, int x, int y, const char* label, const char* value, QColor &color1, QColor &color2) {
  configFont(p, "Inter", 125, "SemiBold");
  drawColoredText(p, x, y, QString(label), color1);

  configFont(p, "Inter", 150, "SemiBold");
  drawColoredText(p, x, y + 150, QString(value), color2);
}

void NvgWindow::drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text);
  QRect real_rect = fm.boundingRect(init_rect, 0, text);
  real_rect.moveCenter({x, y});

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}

void NvgWindow::drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - radius / 2, y - radius / 2, radius, radius);
  p.setOpacity(opacity);
  p.drawPixmap(x - img_size / 2, y - img_size / 2, img);
  p.setOpacity(1.0);
}

void NvgWindow::drawMadsIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - 133 / 2, y - 133 / 2, 133, 133); // same as img_size == 266x266
  p.setOpacity(opacity);
  p.drawPixmap(x - img_size / 2, y - img_size / 2, img); // img_size == 266x266
  p.setOpacity(1.0);
}

void NvgWindow::drawDlpButton(QPainter &p, int x, int y, int w, int h) {
  int prev_dynamic_lane_profile = -1;
  QString dlp_text = "";
  QColor dlp_border = QColor(255, 255, 255, 255);

  if (prev_dynamic_lane_profile != dynamicLaneProfile) {
    prev_dynamic_lane_profile = dynamicLaneProfile;
    if (dynamicLaneProfile == 0) {
      dlp_text = "Lane\nonly";
      dlp_border = QColor("#007d00");
    } else if (dynamicLaneProfile == 1) {
      dlp_text = "Lane\nless";
      dlp_border = QColor("#c92231");
    } else if (dynamicLaneProfile == 2) {
      dlp_text = "Auto\nLane";
      dlp_border = QColor("#7d007d");
    }
  }

  QRect dlpBtn(x, y, w, h);
  p.setPen(QPen(dlp_border, 12));
  p.setBrush(QColor(75, 75, 75, 75));
  p.drawEllipse(dlpBtn);
  p.setPen(QColor(Qt::white));
  configFont(p, "Inter", 45, "Regular");
  p.drawText(dlpBtn, Qt::AlignCenter, dlp_text);
}

void NvgWindow::drawStandstillTimer(QPainter &p, int x, int y) {
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

int NvgWindow::drawDevUiElementRight(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color) {
  configFont(p, "Inter", 30 * 2, "SemiBold");
  drawColoredText(p, x + 92, y + 80, QString(value), color);

  configFont(p, "Inter", 28, "Regular");
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

int NvgWindow::drawDevUiElementLeft(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color) {
  configFont(p, "Inter", 30 * 2, "SemiBold");
  drawColoredText(p, x + 92, y + 80, QString(value), color);

  configFont(p, "Inter", 28, "Regular");
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

void NvgWindow::drawRightDevUi(QPainter &p, int x, int y) {
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
    if (madsEnabled && latActive) {
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

    if (madsEnabled && latActive) {
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

  // Add Device Memory Usage
  // Unit: Percent
  if (true) {
    char val_str[16];
    QColor valueColor = QColor(255, 255, 255, 255);

    if (memoryUsagePercent > 75) {
      valueColor = QColor(255, 188, 0, 255);
    }

    snprintf(val_str, sizeof(val_str), "%d%s", (int)memoryUsagePercent, "%");

    rh += drawDevUiElementRight(p, x, ry, val_str, "MEM %", "", valueColor);
    ry = y + rh;
  }

  rh += 25;
  p.setBrush(QColor(0, 0, 0, 0));
  QRect ldu(x, y, 184, rh);
  //p.drawRoundedRect(ldu, 20, 20);
}

void NvgWindow::drawRightDevUi2(QPainter &p, int x, int y) {
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

void NvgWindow::drawRightDevUiBorder(QPainter &p, int x, int y) {
  int rh = 580;
  int rw = 184;
  p.setPen(QPen(QColor(0xff, 0xff, 0xff, 100), 6));
  p.setBrush(QColor(0, 0, 0, 0));
  if (devUiRow == 1) {
    rw *= 2;
  }
  QRect ldu(x, y, rw, rh);
  p.drawRoundedRect(ldu, 20, 20);
}

void NvgWindow::drawGacButton(QPainter &p, int x, int y, int w, int h) {
  int prev_gap_adjust_cruise_tr = -1;
  int init_gap_adjust_cruise_tr = -1;
  bool lock_init = false;
  QString gac_text = "";
  QColor gac_border = QColor(255, 255, 255, 255);

  if ((prev_gap_adjust_cruise_tr != gapAdjustCruiseTr) || (!lock_init && (init_gap_adjust_cruise_tr != uiState()->scene.gap_adjust_cruise_tr))) {
    if (!lock_init && (init_gap_adjust_cruise_tr != uiState()->scene.gap_adjust_cruise_tr)) {
      lock_init = true;
      init_gap_adjust_cruise_tr = uiState()->scene.gap_adjust_cruise_tr;
    } else if (prev_gap_adjust_cruise_tr != gapAdjustCruiseTr) {
      prev_gap_adjust_cruise_tr = gapAdjustCruiseTr;
    }
    if (carMake == 1) {
      if (gapAdjustCruiseTr == 4) {
        gac_text = "Chill\nGap";
        gac_border = QColor("#044389");
      } else if (gapAdjustCruiseTr == 3) {
        gac_text = "Normal\nGap";
        gac_border = QColor("#24a8bc");
      } else if (gapAdjustCruiseTr == 2) {
        gac_text = "Aggro\nGap";
        gac_border = QColor("#fcff4b");
      } else if (gapAdjustCruiseTr == 1) {
        gac_text = "Maniac\nGap";
        gac_border = QColor("#37b868");
      }
    } else if (carMake == 2) {
      if (gapAdjustCruiseTr == 2) {
        gac_text = "Chill\nGap";
        gac_border = QColor("#044389");
      } else if (gapAdjustCruiseTr == 1) {
        gac_text = "Normal\nGap";
        gac_border = QColor("#24a8bc");
      } else if (gapAdjustCruiseTr == 0) {
        gac_text = "Aggro\nGap";
        gac_border = QColor("#fcff4b");
      }
    } else if (carMake == 3) {
      if (gapAdjustCruiseTr == 0) {
        gac_text = "Chill\nGap";
        gac_border = QColor("#044389");
      } else if (gapAdjustCruiseTr == 3) {
        gac_text = "Normal\nGap";
        gac_border = QColor("#24a8bc");
      } else if (gapAdjustCruiseTr == 2) {
        gac_text = "Aggro\nGap";
        gac_border = QColor("#fcff4b");
      } else if (gapAdjustCruiseTr == 1) {
        gac_text = "Maniac\nGap";
        gac_border = QColor("#37b868");
      }
    }
  }

  QRect gacBtn(x, y, w, h);
  p.setPen(QPen(gac_border, 12));
  p.setBrush(QColor(75, 75, 75, 75));
  p.drawEllipse(gacBtn);
  p.setPen(QColor(Qt::white));
  configFont(p, "Inter", 45, "Regular");
  p.drawText(gacBtn, Qt::AlignCenter, gac_text);
}

void NvgWindow::drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color,
                                           const QString &vision_speed, int alpha) {
  QRect rvtsc(x, y, size, size);
  p.setPen(QPen(color, 10));
  p.setBrush(QColor(0, 0, 0, alpha));
  p.drawRoundedRect(rvtsc, 20, 20);
  p.setPen(Qt::NoPen);

  configFont(p, "Inter", 56, "SemiBold");
  drawCenteredText(p, rvtsc.center().x(), rvtsc.center().y(), vision_speed, color);
}

void NvgWindow::drawCircle(QPainter &p, int x, int y, int r, QBrush bg) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - r, y - r, 2 * r, 2 * r);
}

void NvgWindow::drawTurnSpeedSign(QPainter &p, QRect rc, const QString &turn_speed, const QString &sub_text,
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
  configFont(p, "Inter", 67, "Bold");
  drawCenteredText(p, x, y + 25, turn_speed, text_color);
  configFont(p, "Inter", 22, "Bold");
  drawCenteredText(p, x, y + 65, sub_text, text_color);
}


void NvgWindow::initializeGL() {
  CameraViewWidget::initializeGL();
  qInfo() << "OpenGL version:" << QString((const char*)glGetString(GL_VERSION));
  qInfo() << "OpenGL vendor:" << QString((const char*)glGetString(GL_VENDOR));
  qInfo() << "OpenGL renderer:" << QString((const char*)glGetString(GL_RENDERER));
  qInfo() << "OpenGL language version:" << QString((const char*)glGetString(GL_SHADING_LANGUAGE_VERSION));

  prev_draw_t = millis_since_boot();
  setBackgroundColor(bg_colors[STATUS_DISENGAGED]);
}

void NvgWindow::updateFrameMat() {
  CameraViewWidget::updateFrameMat();
  UIState *s = uiState();
  int w = width(), h = height();

  s->fb_w = w;
  s->fb_h = h;

  // Apply transformation such that video pixel coordinates match video
  // 1) Put (0, 0) in the middle of the video
  // 2) Apply same scaling as video
  // 3) Put (0, 0) in top left corner of video
  s->car_space_transform.reset();
  s->car_space_transform.translate(w / 2 - x_offset, h / 2 - y_offset)
      .scale(zoom, zoom)
      .translate(-intrinsic_matrix.v[2], -intrinsic_matrix.v[5]);
}

// Shane's colored lane line
void NvgWindow::drawLaneLines(QPainter &painter, const UIState *s) {
  painter.save();

  const UIScene &scene = s->scene;
  // lanelines
  for (int i = 0; i < std::size(scene.lane_line_vertices); ++i) {
    if (i == 1 || i == 2) {
      // TODO: can we just use the projected vertices somehow?
      const cereal::ModelDataV2::XYZTData::Reader &line = (*s->sm)["modelV2"].getModelV2().getLaneLines()[i];
      const float default_pos = 1.4;  // when lane poly isn't available
      const float lane_pos = line.getY().size() > 0 ? std::abs(line.getY()[5]) : default_pos;  // get redder when line is closer to car
      float hue = 332.5 * lane_pos - 332.5;  // equivalent to {1.4, 1.0}: {133, 0} (green to red)
      hue = std::fmin(133, fmax(0, hue)) / 360.;  // clip and normalize
      painter.setBrush(QColor::fromHslF(hue, 1.0, 0.50, std::clamp<float>(scene.lane_line_probs[i], 0.0, 0.7)));
    } else {
      painter.setBrush(QColor::fromRgbF(1.0, 1.0, 1.0, std::clamp<float>(scene.lane_line_probs[i], 0.0, 0.7)));
    }
    painter.drawPolygon(scene.lane_line_vertices[i].v, scene.lane_line_vertices[i].cnt);
  }

  // road edges
  for (int i = 0; i < std::size(scene.road_edge_vertices); ++i) {
    painter.setBrush(QColor::fromRgbF(1.0, 0, 0, std::clamp<float>(1.0 - scene.road_edge_stds[i], 0.0, 1.0)));
    painter.drawPolygon(scene.road_edge_vertices[i].v, scene.road_edge_vertices[i].cnt);
  }

  // paint path
  QLinearGradient bg(0, height(), 0, height() / 4);
  const auto &orientation = (*s->sm)["modelV2"].getModelV2().getOrientation();
  float orientation_future = 0;
  if (orientation.getZ().size() > 16) {
    orientation_future = std::abs(orientation.getZ()[16]);  // 2.5 seconds
  }
  if (madsEnabled) {
    if (steerOverride && latActive) {
      bg.setColorAt(0, blackColor(80));
      bg.setColorAt(1, blackColor(20));
    } else if (!latActive) {
      bg.setColorAt(0, whiteColor());
      bg.setColorAt(1, whiteColor(0));
    } else if (scene.lateralPlan.dynamicLaneProfileStatus) {
      // straight: 112, in turns: 70
      float curve_hue = fmax(70, 112 - (orientation_future * 420));
      // FIXME: painter.drawPolygon can be slow if hue is not rounded
      curve_hue = int(curve_hue * 100 + 0.5) / 100;

      bg.setColorAt(0.0, QColor::fromHslF(148 / 360., 0.94, 0.51, 0.4));
      bg.setColorAt(0.75 / 1.5, QColor::fromHslF(curve_hue / 360., 1.0, 0.68, 0.35));
      bg.setColorAt(1.0, QColor::fromHslF(curve_hue / 360., 1.0, 0.68, 0.0));
    } else {
      // straight: 204, in turns: 162
      float curve_hue2 = fmax(162, 204 - (orientation_future * 420));
      // FIXME: painter.drawPolygon can be slow if hue is not rounded
      curve_hue2 = int(curve_hue2 * 100 + 0.5) / 100;

      bg.setColorAt(0.0, QColor::fromHslF(240 / 360., 0.94, 0.51, 0.4));
      bg.setColorAt(0.75 / 1.5, QColor::fromHslF(curve_hue2 / 360., 1.0, 0.68, 0.35));
      bg.setColorAt(1.0, QColor::fromHslF(curve_hue2 / 360., 1.0, 0.68, 0.0));
    }
  } else {
    bg.setColorAt(0, whiteColor());
    bg.setColorAt(1, whiteColor(0));
  }
  painter.setBrush(bg);
  painter.drawPolygon(scene.track_vertices.v, scene.track_vertices.cnt);

  painter.restore();
}

void NvgWindow::drawLead(QPainter &painter, const cereal::ModelDataV2::LeadDataV3::Reader &lead_data, const QPointF &vd) {
  painter.save();

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

  QPointF glow[] = {{x + (sz * 1.35) + g_xo, y + sz + g_yo}, {x, y - g_yo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo}};
  painter.setBrush(QColor(218, 202, 37, 255));
  painter.drawPolygon(glow, std::size(glow));

  // chevron
  QPointF chevron[] = {{x + (sz * 1.25), y + sz}, {x, y}, {x - (sz * 1.25), y + sz}};
  painter.setBrush(redColor(fillAlpha));
  painter.drawPolygon(chevron, std::size(chevron));

  painter.restore();
}

void NvgWindow::paintGL() {
  CameraViewWidget::paintGL();

  QPainter painter(this);
  painter.setRenderHint(QPainter::Antialiasing);
  painter.setPen(Qt::NoPen);

  UIState *s = uiState();
  if (s->worldObjectsVisible()) {

    drawLaneLines(painter, s);

    if (s->scene.longitudinal_control) {
      auto leads = (*s->sm)["modelV2"].getModelV2().getLeadsV3();
      if (leads[0].getProb() > .5) {
        drawLead(painter, leads[0], s->scene.lead_vertices[0]);
      }
      if (leads[1].getProb() > .5 && (std::abs(leads[1].getX()[0] - leads[0].getX()[0]) > 3.0)) {
        drawLead(painter, leads[1], s->scene.lead_vertices[1]);
      }
    }
  }

  drawHud(painter);

  double cur_draw_t = millis_since_boot();
  double dt = cur_draw_t - prev_draw_t;
  double fps = fps_filter.update(1. / dt * 1000);
  if (fps < 15) {
    LOGW("slow frame rate: %.2f fps", fps);
  }
  prev_draw_t = cur_draw_t;
}

void NvgWindow::showEvent(QShowEvent *event) {
  CameraViewWidget::showEvent(event);

  ui_update_params(uiState());
  prev_draw_t = millis_since_boot();
}
