#include "selfdrive/ui/qt/onroad.h"

#include <cmath>
#include <chrono>

#include <QDebug>
#include <iomanip>
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

  if (s.scene.map_on_left) {
    split->setDirection(QBoxLayout::LeftToRight);
  } else {
    split->setDirection(QBoxLayout::RightToLeft);
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

  UIState *s = uiState();
  UIScene &scene = s->scene;
  SubMaster &sm = *(uiState()->sm);
  auto longitudinal_plan = sm["longitudinalPlan"].getLongitudinalPlan();
  auto car_state = sm["carState"].getCarState();
  auto controls_state = sm["controlsState"].getControlsState();

  QRect dlp_btn_rect = QRect(bdr_s * 2 + 220, (rect().bottom() - footer_h / 2 - 75), 150, 150);
  QRect gac_btn_rect = QRect(bdr_s * 2 + 220 + 180, (rect().bottom() - footer_h / 2 - 75), 150, 150);
  QRect debug_tap_rect = QRect(rect().center().x() - 200, rect().center().y() - 200, 400, 400);
  QRect speed_limit_touch_rect = speed_sgn_rc.adjusted(-50, -50, 50, 50);

  if (scene.dynamic_lane_profile_toggle && dlp_btn_rect.contains(e->x(), e->y())) {
    scene.dynamic_lane_profile++;
    scene.dynamic_lane_profile = scene.dynamic_lane_profile > 2 ? 0 : scene.dynamic_lane_profile;
    params.put("DynamicLaneProfile", std::to_string(scene.dynamic_lane_profile));
    propagate_event = false;
  } else if (scene.gac && scene.gac_mode != 0 && scene.longitudinal_control && !controls_state.getExperimentalMode() &&
             car_state.getCruiseState().getAvailable() && gac_btn_rect.contains(e->x(), e->y())) {
    scene.gac_tr--;
    scene.gac_tr = scene.gac_tr < scene.gac_min ? scene.gac_max : scene.gac_tr;
    params.put("GapAdjustCruiseTr", std::to_string(scene.gac_tr));
    propagate_event = false;
  } else if (longitudinal_plan.getSpeedLimit() > 0.0 && speed_limit_touch_rect.contains(e->x(), e->y())) {
    // If touching the speed limit sign area when visible
    scene.last_speed_limit_sign_tap = seconds_since_boot();
    scene.speed_limit_control_enabled = !scene.speed_limit_control_enabled;
    params.putBool("SpeedLimitControl", scene.speed_limit_control_enabled);
    propagate_event = false;
  } else if (scene.debug_snapshot_enabled && debug_tap_rect.contains(e->x(), e->y())) {
    issue_debug_snapshot(sm);
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

      m->setFixedWidth(topWidget(this)->width() / (Params().getBool("MapboxFullScreen")? 1 : 2));
      split->insertWidget(0, m);

      // Make map visible after adding to split
      m->offroadTransition(offroad);
    }
  }
#endif

  alerts->updateAlert({}, bg);
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


ExperimentalButton::ExperimentalButton(QWidget *parent) : QPushButton(parent) {
  setVisible(false);
  setFixedSize(btn_size, btn_size);
  setCheckable(true);

  params = Params();
  engage_img = loadPixmap("../assets/img_chffr_wheel.png", {img_size, img_size});
  experimental_img = loadPixmap("../assets/img_experimental.svg", {img_size, img_size});

  QObject::connect(this, &QPushButton::toggled, [=](bool checked) {
    params.putBool("ExperimentalMode", checked);
  });
}

void ExperimentalButton::updateState(const UIState &s) {
  const SubMaster &sm = *(s.sm);

  // button is "visible" if engageable or enabled
  const auto cs = sm["controlsState"].getControlsState();
  const auto lp = sm["longitudinalPlan"].getLongitudinalPlan();
  setVisible((cs.getEngageable() || cs.getEnabled()) && !(lp.getVisionTurnControllerState() > cereal::LongitudinalPlan::VisionTurnControllerState::DISABLED));

  // button is "checked" if experimental mode is enabled
  setChecked(sm["controlsState"].getControlsState().getExperimentalMode());

  // disable button when experimental mode is not available, or has not been confirmed for the first time
  const auto cp = sm["carParams"].getCarParams();
  const bool experimental_mode_available = cp.getExperimentalLongitudinalAvailable() ? params.getBool("ExperimentalLongitudinalEnabled") : cp.getOpenpilotLongitudinalControl();
  setEnabled(params.getBool("ExperimentalModeConfirmed") && experimental_mode_available);
}

void ExperimentalButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setRenderHint(QPainter::Antialiasing);

  QPoint center(btn_size / 2, btn_size / 2);
  QPixmap img = isChecked() ? experimental_img : engage_img;

  p.setOpacity(1.0);
  p.setPen(Qt::NoPen);
  p.setBrush(QColor(0, 0, 0, 166));
  p.drawEllipse(center, btn_size / 2, btn_size / 2);
  p.setOpacity(isDown() ? 0.8 : 1.0);
  p.drawPixmap((btn_size - img_size) / 2, (btn_size - img_size) / 2, img);
}


AnnotatedCameraWidget::AnnotatedCameraWidget(VisionStreamType type, QWidget* parent) : last_update_params(0), fps_filter(UI_FREQ, 3, 1. / UI_FREQ), CameraWidget("camerad", type, true, parent) {
  pm = std::make_unique<PubMaster, const std::initializer_list<const char *>>({"uiDebug"});

  QVBoxLayout *main_layout  = new QVBoxLayout(this);
  main_layout->setMargin(bdr_s);
  main_layout->setSpacing(0);

  experimental_btn = new ExperimentalButton(this);
  main_layout->addWidget(experimental_btn, 0, Qt::AlignTop | Qt::AlignRight);

  dm_img = loadPixmap("../assets/img_driver_face.png", {img_size + 5, img_size + 5});
  map_img = loadPixmap("../assets/img_world_icon.png", {subsign_img_size, subsign_img_size});
  left_img = loadPixmap("../assets/img_turn_left_icon.png", {subsign_img_size, subsign_img_size});
  right_img = loadPixmap("../assets/img_turn_right_icon.png", {subsign_img_size, subsign_img_size});

  // screen recoder - neokii

#ifdef ENABLE_DASHCAM
  record_timer = std::make_shared<QTimer>();
  QObject::connect(record_timer.get(), &QTimer::timeout, [=]() {
    if (recorder) {
      recorder->update_screen();
    }
  });
  record_timer->start(1000/UI_FREQ);

  recorder = new ScreenRecoder(this);
  main_layout->addWidget(recorder);
  main_layout->addWidget(recorder, 0, Qt::AlignRight | Qt::AlignBottom);
#endif
}

#ifdef ENABLE_DASHCAM
void AnnotatedCameraWidget::offroadTransition(bool offroad) {
  if (offroad && recorder) {
    recorder->stop(false);
  }
}
#endif

void AnnotatedCameraWidget::updateState(const UIState &s) {
  const int SET_SPEED_NA = 255;
  const SubMaster &sm = *(s.sm);

  const bool cs_alive = sm.alive("controlsState");
  const bool nav_alive = sm.alive("navInstruction") && sm["navInstruction"].getValid();

  const auto cs = sm["controlsState"].getControlsState();
  const auto car_state = sm["carState"].getCarState();
  const auto car_control = sm["carControl"].getCarControl();

  // Handle older routes where vCruiseCluster is not set
  float v_cruise =  cs.getVCruiseCluster() == 0.0 ? cs.getVCruise() : cs.getVCruiseCluster();
  float set_speed = cs_alive ? v_cruise : SET_SPEED_NA;
  bool cruise_set = set_speed > 0 && (int)set_speed != SET_SPEED_NA;
  if (cruise_set && !s.scene.is_metric) {
    set_speed *= KM_TO_MILE;
  }

  // Handle older routes where vEgoCluster is not set
  float v_ego;
  if ((sm["carState"].getCarState().getVEgoCluster() == 0.0 && !v_ego_cluster_seen) || s.scene.true_vego_ui) {
    v_ego = sm["carState"].getCarState().getVEgo();
  } else {
    v_ego = sm["carState"].getCarState().getVEgoCluster();
    v_ego_cluster_seen = true;
  }
  float cur_speed = cs_alive ? std::max<float>(0.0, v_ego) : 0.0;
  cur_speed *= s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH;

  auto speed_limit_sign = sm["navInstruction"].getNavInstruction().getSpeedLimitSign();
  float speed_limit = nav_alive ? sm["navInstruction"].getNavInstruction().getSpeedLimit() : 0.0;
  speed_limit *= (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);

  setProperty("speedLimit", speed_limit);
  setProperty("has_us_speed_limit", nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::MUTCD);
  setProperty("has_eu_speed_limit", nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::VIENNA);

  // TODO: Add minimum speed?
  setProperty("left_blindspot", cs_alive && sm["carState"].getCarState().getLeftBlindspot());
  setProperty("right_blindspot", cs_alive && sm["carState"].getCarState().getRightBlindspot());

  setProperty("is_cruise_set", cruise_set);
  setProperty("is_metric", s.scene.is_metric);
  setProperty("speed", cur_speed);
  setProperty("setSpeed", set_speed);
  setProperty("speedUnit", s.scene.is_metric ? tr("km/h") : tr("mph"));
  setProperty("hideDM", (cs.getAlertSize() != cereal::ControlsState::AlertSize::NONE));
  setProperty("status", s.status);

  setProperty("steerOverride", car_state.getSteeringPressed());
  setProperty("latActive", car_control.getLatActive());
  setProperty("madsEnabled", car_state.getMadsEnabled());

  setProperty("dynamicLaneProfileToggle", s.scene.dynamic_lane_profile_toggle);
  setProperty("dynamicLaneProfile", s.scene.dynamic_lane_profile);

  setProperty("brakeLights", car_state.getBrakeLights() && s.scene.visual_brake_lights);

  setProperty("standStillTimer", s.scene.stand_still_timer);
  setProperty("standStill", car_state.getStandstill());
  setProperty("standstillElapsedTime", sm["lateralPlan"].getLateralPlan().getStandstillElapsed());

  setProperty("hideVEgoUi", s.scene.hide_vego_ui);

  setProperty("gac", s.scene.gac && s.scene.gac_mode != 0 && s.scene.longitudinal_control && !cs.getExperimentalMode() &&
              car_state.getCruiseState().getAvailable());
  setProperty("gacTr", s.scene.gac_tr);

  // update engageability/experimental mode button
  experimental_btn->updateState(s);

  const auto lp = sm["longitudinalPlan"].getLongitudinalPlan();

  // update DM icons at 2Hz
  if (sm.frame % (UI_FREQ / 2) == 0) {
    setProperty("dmActive", sm["driverMonitoringState"].getDriverMonitoringState().getIsActiveMode());
    setProperty("rightHandDM", sm["driverMonitoringState"].getDriverMonitoringState().getIsRHD());

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
    const uint64_t lmd_fix_time = lmd.getLastGpsTimestamp();
    const uint64_t current_ts = std::chrono::duration_cast<std::chrono::milliseconds>
                              (std::chrono::system_clock::now().time_since_epoch()).count();
    const bool show_road_name = current_ts - lmd_fix_time < 10000; // hide if fix older than 10s
    setProperty("roadName", show_road_name ? QString::fromStdString(lmd.getCurrentRoadName()) : "");

    float speed_limit_slc = lp.getSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const float speed_limit_offset = lp.getSpeedLimitOffset() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
    const auto slcState = lp.getSpeedLimitControlState();
    const bool sl_force_active = s.scene.speed_limit_control_enabled &&
                                 seconds_since_boot() < s.scene.last_speed_limit_sign_tap + 2.0;
    const bool sl_inactive = !sl_force_active && (!s.scene.speed_limit_control_enabled ||
                             slcState == cereal::LongitudinalPlan::SpeedLimitControlState::INACTIVE);
    const bool sl_temp_inactive = !sl_force_active && (s.scene.speed_limit_control_enabled &&
                                  slcState == cereal::LongitudinalPlan::SpeedLimitControlState::TEMP_INACTIVE);
    const int sl_distance = int(lp.getDistToSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
    const QString sl_distance_str(QString::number(sl_distance) + (s.scene.is_metric ? "m" : "f"));
    const QString sl_offset_str(speed_limit_offset > 0.0 ? speed_limit_offset < 0.0 ?
                                "-" + QString::number(std::nearbyint(std::abs(speed_limit_offset))) :
                                "+" + QString::number(std::nearbyint(speed_limit_offset)) : "");
    const QString sl_inactive_str(sl_temp_inactive ? "TEMP" : "");
    const QString sl_substring(sl_inactive || sl_temp_inactive ? sl_inactive_str :
                               sl_distance > 0 ? sl_distance_str : sl_offset_str);

    setProperty("showSpeedLimit", speed_limit_slc > 0.0);
    setProperty("speedLimitSLC", speed_limit_slc);
    setProperty("slcSubText", sl_substring);
    setProperty("slcSubTextSize", sl_inactive || sl_temp_inactive || sl_distance > 0 ? 25.0 : 27.0);
    setProperty("mapSourcedSpeedLimit", lp.getIsMapSpeedLimit());
    setProperty("slcActive", !sl_inactive && !sl_temp_inactive);
    setProperty("overSpeedLimit", (((speed_limit_slc + speed_limit_offset) < cur_speed) && !sl_inactive && !sl_temp_inactive) ||
                                  ((speed_limit_slc < cur_speed) && (speed_limit_slc > 0.0) && (sl_inactive || sl_temp_inactive)));
    setProperty("speedLimitStyle", s.scene.speed_limit_style);

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

  // DM icon transition
  dm_fade_state = fmax(0.0, fmin(1.0, dm_fade_state+0.2*(0.5-(float)(dmActive))));
}

void AnnotatedCameraWidget::drawHud(QPainter &p) {
  p.save();

  // Header gradient
  QLinearGradient bg(0, header_h - (header_h / 2.5), 0, header_h);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, width(), header_h, bg);

  QString speedLimitStr = (speedLimit > 1) ? QString::number(std::nearbyint(speedLimit)) : "–";
  QString speedLimitStrSlc = showSpeedLimit ? QString::number(std::nearbyint(speedLimitSLC)) : "–";
  QString speedStr = QString::number(std::nearbyint(speed));
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(setSpeed)) : "–";

  // Draw outer box + border to contain set speed and speed limit
  int default_rect_width = 172;
  int rect_width = default_rect_width;
  if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 1) || is_metric || has_eu_speed_limit) rect_width = 200;
  if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 0 && speedLimitStrSlc.size() >= 3) ||
      (has_us_speed_limit && speedLimitStr.size() >= 3)) rect_width = 223;

  int rect_height = 204;
  if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 0) || has_us_speed_limit) rect_height = (slcSubText == "" ? 402 : 432);
  else if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 1) || has_eu_speed_limit) rect_height = 392;

  int top_radius = 32;
  int bottom_radius = (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 1) || has_eu_speed_limit) ? 100 : 32;

  QRect set_speed_rect(60 + default_rect_width / 2 - rect_width / 2, 45, rect_width, rect_height);
  p.setPen(QPen(whiteColor(75), 6));
  p.setBrush(blackColor(166));
  drawRoundedRect(p, set_speed_rect, top_radius, top_radius, bottom_radius, bottom_radius);

  // Draw MAX
  if (is_cruise_set) {
    if (status == STATUS_DISENGAGED) {
      p.setPen(whiteColor());
    } else if (status == STATUS_OVERRIDE) {
      p.setPen(QColor(0x91, 0x9b, 0x95, 0xff));
    } else if (speedLimitSLC > 0) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimitSLC + 5, speedLimitSLC + 15, speedLimitSLC + 25},
        {QColor(0x80, 0xd8, 0xa6, 0xff), QColor(0xff, 0xe4, 0xbf, 0xff), QColor(0xff, 0xbf, 0xbf, 0xff)}
      ));
    } else if (speedLimit > 0) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimit + 5, speedLimit + 15, speedLimit + 25},
        {QColor(0x80, 0xd8, 0xa6, 0xff), QColor(0xff, 0xe4, 0xbf, 0xff), QColor(0xff, 0xbf, 0xbf, 0xff)}
      ));
    } else {
      p.setPen(QColor(0x80, 0xd8, 0xa6, 0xff));
    }
  } else {
    p.setPen(QColor(0xa6, 0xa6, 0xa6, 0xff));
  }
  configFont(p, "Inter", 40, "SemiBold");
  QRect max_rect = getTextRect(p, Qt::AlignCenter, tr("MAX"));
  max_rect.moveCenter({set_speed_rect.center().x(), 0});
  max_rect.moveTop(set_speed_rect.top() + 27);
  p.drawText(max_rect, Qt::AlignCenter, tr("MAX"));

  // Draw set speed
  if (is_cruise_set) {
    if (speedLimitSLC > 0 && status != STATUS_DISENGAGED && status != STATUS_OVERRIDE) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimitSLC + 5, speedLimitSLC + 15, speedLimitSLC + 25},
        {whiteColor(), QColor(0xff, 0x95, 0x00, 0xff), QColor(0xff, 0x00, 0x00, 0xff)}
      ));
    } else if (speedLimit > 0 && status != STATUS_DISENGAGED && status != STATUS_OVERRIDE) {
      p.setPen(interpColor(
        setSpeed,
        {speedLimit + 5, speedLimit + 15, speedLimit + 25},
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
  if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 0) || has_us_speed_limit) {
    const int border_width = 6;
    const int sign_width = rect_width - 24;
    int sign_height = (slcSubText == "" ? 186 : 216);

    // White outer square
    QRect sign_rect_outer(set_speed_rect.left() + 12, set_speed_rect.bottom() - 11 - sign_height, sign_width, sign_height);
    p.setPen(Qt::NoPen);
    p.setBrush(whiteColor());
    p.drawRoundedRect(sign_rect_outer, 24, 24);

    // Smaller white square with black border
    QRect sign_rect(sign_rect_outer.left() + 1.5 * border_width, sign_rect_outer.top() + 1.5 * border_width, sign_width - 3 * border_width, sign_height - 3 * border_width);
    p.setPen(QPen(blackColor(), border_width));
    p.setBrush(whiteColor());
    p.drawRoundedRect(sign_rect, 16, 16);

    // "SPEED"
    configFont(p, "Inter", 28, "SemiBold");
    QRect text_speed_rect = getTextRect(p, Qt::AlignCenter, tr("SPEED"));
    text_speed_rect.moveCenter({sign_rect.center().x(), 0});
    text_speed_rect.moveTop(sign_rect_outer.top() + 22);
    p.drawText(text_speed_rect, Qt::AlignCenter, tr("SPEED"));

    // "LIMIT"
    QRect text_limit_rect = getTextRect(p, Qt::AlignCenter, tr("LIMIT"));
    text_limit_rect.moveCenter({sign_rect.center().x(), 0});
    text_limit_rect.moveTop(sign_rect_outer.top() + 51);
    p.drawText(text_limit_rect, Qt::AlignCenter, tr("LIMIT"));

    // Speed limit value
    configFont(p, "Inter", 70, "Bold");
    QRect speed_limit_rect = getTextRect(p, Qt::AlignCenter, speedLimitStrSlc);
    speed_limit_rect.moveCenter({sign_rect.center().x(), 0});
    speed_limit_rect.moveTop(sign_rect_outer.top() + 85);
    if (overSpeedLimit) p.setPen(QColor(255, 0, 0, 255));
    else p.setPen(blackColor());
    p.drawText(speed_limit_rect, Qt::AlignCenter, speedLimitStrSlc);

    // Speed limit offset value
    configFont(p, "Inter", 32, "Bold");
    QRect speed_limit_offset_rect = getTextRect(p, Qt::AlignCenter, slcSubText);
    speed_limit_offset_rect.moveCenter({sign_rect.center().x(), 0});
    speed_limit_offset_rect.moveTop(sign_rect_outer.top() + 85 + 77);
    p.setPen(blackColor());
    p.drawText(speed_limit_offset_rect, Qt::AlignCenter, slcSubText);
  }

  // EU (Vienna style) sign
  if (((!roadName.isEmpty() || showSpeedLimit) && speedLimitStyle == 1) || has_eu_speed_limit) {
    int outer_radius = 176 / 2;
    int inner_radius_1 = outer_radius - 6; // White outer border
    int inner_radius_2 = inner_radius_1 - 20; // Red circle

    // Draw white circle with red border
    QPoint center(set_speed_rect.center().x() + 1, set_speed_rect.top() + 204 + outer_radius);
    p.setPen(Qt::NoPen);
    p.setBrush(whiteColor());
    p.drawEllipse(center, outer_radius, outer_radius);
    p.setBrush(QColor(255, 0, 0, 255));
    p.drawEllipse(center, inner_radius_1, inner_radius_1);
    p.setBrush(whiteColor());
    p.drawEllipse(center, inner_radius_2, inner_radius_2);

    // Speed limit value
    int font_size = (speedLimitStrSlc.size() >= 3) ? 60 : 70;
    configFont(p, "Inter", font_size, "Bold");
    QRect speed_limit_rect = getTextRect(p, Qt::AlignCenter, speedLimitStrSlc);
    speed_limit_rect.moveCenter(center);
    if (overSpeedLimit) p.setPen(QColor(255, 0, 0, 255));
    else p.setPen(blackColor());
    p.drawText(speed_limit_rect, Qt::AlignCenter, speedLimitStrSlc);

    // Speed limit offset value
    configFont(p, "Inter", slcSubTextSize, "Bold");
    QRect speed_limit_offset_rect = getTextRect(p, Qt::AlignCenter, slcSubText);
    speed_limit_offset_rect.moveCenter(center);
    speed_limit_offset_rect.moveTop(center.y() + 27);
    p.setPen(blackColor());
    p.drawText(speed_limit_offset_rect, Qt::AlignCenter, slcSubText);
  }

  // current speed
  if (!hideVEgoUi) {
    configFont(p, "Inter", 176, "Bold");
    drawColoredText(p, rect().center().x(), 210, speedStr, brakeLights ? QColor(0xff, 0, 0, 255) : QColor(0xff, 0xff, 0xff, 255));
    configFont(p, "Inter", 66, "Regular");
    drawText(p, rect().center().x(), 290, speedUnit, 200);
  }

  // Dynamic Lane Profile Button
  if (dynamicLaneProfileToggle) {
    drawDlpButton(p, bdr_s * 2 + 220, (rect().bottom() - footer_h / 2 - 75), 150, 150);
  }

  if (gac) {
    drawGacButton(p, bdr_s * 2 + 220 + 180, (rect().bottom() - footer_h / 2 - 75), 150, 150);
  }

  // Stand Still Timer
  if (standStillTimer && standStill) {
    drawStandstillTimer(p, rect().right() - 650, 30 + 160 + 250);
  }

  // V-TSC
  if (showDebugUI && showVTC) {
    drawVisionTurnControllerUI(p, rect().right() - 184 - bdr_s, int(bdr_s * 1.5), 184, vtcColor, vtcSpeed, 100);
  }

  // Bottom bar road name
  if (showDebugUI && !roadName.isEmpty()) {
    const int h = 38;
    QRect bar_rc(rect().left(), rect().top(), rect().width(), h);
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(0, 0, 0, 100));
    p.drawRect(bar_rc);
    configFont(p, "Inter", 28, "Bold");
    drawCenteredText(p, bar_rc.center().x(), bar_rc.center().y(), roadName, QColor(255, 255, 255, 200));
  }

  // Turn Speed Sign
  if (showTurnSpeedLimit) {
    QRect rc = speed_sgn_rc;
    rc.moveTop(speed_sgn_rc.bottom() + bdr_s);
    drawTrunSpeedSign(p, rc, turnSpeedLimit, tscSubText, curveSign, tscActive);
  }
  p.restore();
}


// Window that shows camera view and variety of
// info drawn on top

void AnnotatedCameraWidget::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = getTextRect(p, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void AnnotatedCameraWidget::drawColoredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = getTextRect(p, 0, text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void AnnotatedCameraWidget::drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = getTextRect(p, 0, text);
  real_rect.moveCenter({x, y});

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}

void AnnotatedCameraWidget::drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity) {
  p.setOpacity(1.0);  // bg dictates opacity of ellipse
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - btn_size / 2, y - btn_size / 2, btn_size, btn_size);
  p.setOpacity(opacity);
  p.drawPixmap(x - img.size().width() / 2, y - img.size().height() / 2, img);
  p.setOpacity(1.0);
}

void AnnotatedCameraWidget::drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color,
                                                       const QString &vision_speed, int alpha) {
  QRect rvtc(x, y, size, size);
  p.setPen(QPen(color, 10));
  p.setBrush(QColor(0, 0, 0, alpha));
  p.drawRoundedRect(rvtc, 20, 20);
  p.setPen(Qt::NoPen);

  configFont(p, "Inter", 56, "SemiBold");
  drawCenteredText(p, rvtc.center().x(), rvtc.center().y(), vision_speed, color);
}

void AnnotatedCameraWidget::drawDlpButton(QPainter &p, int x, int y, int w, int h) {
  int prev_dynamic_lane_profile = -1;
  QString dlp_text = "";
  QColor dlp_border = QColor(255, 255, 255, 255);

  if (prev_dynamic_lane_profile != dynamicLaneProfile) {
    prev_dynamic_lane_profile = dynamicLaneProfile;
    if (dynamicLaneProfile == 0) {
      dlp_text = tr("Lane\nonly");
      dlp_border = QColor("#2020f8");
    } else if (dynamicLaneProfile == 1) {
      dlp_text = tr("Lane\nless");
      dlp_border = QColor("#0df87a");
    } else if (dynamicLaneProfile == 2) {
      dlp_text = tr("Auto\nLane");
      dlp_border = QColor("#0df8f8");
    }
  }

  QRect dlpBtn(x, y, w, h);
  p.setPen(QPen(dlp_border, 6));
  p.setBrush(QColor(75, 75, 75, 75));
  p.drawEllipse(dlpBtn);
  p.setPen(QColor(Qt::white));
  configFont(p, "Inter", 36, "SemiBold");
  p.drawText(dlpBtn, Qt::AlignCenter, dlp_text);
}

void AnnotatedCameraWidget::drawGacButton(QPainter &p, int x, int y, int w, int h) {
  int prev_gac_tr = -1;
  QString gac_text = "";
  QColor gac_border = QColor(255, 255, 255, 255);

  if (prev_gac_tr != gacTr) {
    prev_gac_tr = gacTr;
    if (gacTr == 1) {
      gac_text = "Aggro\nGap";
      gac_border = QColor("#ff4b4b");
    } else if (gacTr == 2) {
      gac_text = "Mild\nGap";
      gac_border = QColor("#fcff4b");
    } else {
      gac_text = "Stock\nGap";
      gac_border = QColor("#4bff66");
    }
  }

  QRect gacBtn(x, y, w, h);
  p.setPen(QPen(gac_border, 6));
  p.setBrush(QColor(75, 75, 75, 75));
  p.drawEllipse(gacBtn);
  p.setPen(QColor(Qt::white));
  configFont(p, "Inter", 36, "SemiBold");
  p.drawText(gacBtn, Qt::AlignCenter, gac_text);
}

void AnnotatedCameraWidget::drawStandstillTimer(QPainter &p, int x, int y) {
  char lab_str[16];
  char val_str[16];
  int minute = (int)(standstillElapsedTime / 60);
  int second = (int)((standstillElapsedTime) - (minute * 60));

  if (standStill) {
    snprintf(lab_str, sizeof(lab_str), "STOP");
    snprintf(val_str, sizeof(val_str), "%01d:%02d", minute, second);
  }

  configFont(p, "Inter", 125, "SemiBold");
  drawColoredText(p, x, y, QString(lab_str), QColor(255, 175, 3, 240));
  configFont(p, "Inter", 150, "SemiBold");
  drawColoredText(p, x, y + 150, QString(val_str), QColor(255, 255, 255, 240));
}

void AnnotatedCameraWidget::drawCircle(QPainter &p, int x, int y, int r, QBrush bg) {
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(x - r, y - r, 2 * r, 2 * r);
}

void AnnotatedCameraWidget::drawSpeedSign(QPainter &p, QRect rc, const QString &speed_limit, const QString &sub_text,
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

void AnnotatedCameraWidget::drawTrunSpeedSign(QPainter &p, QRect rc, const QString &turn_speed, const QString &sub_text,
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


void AnnotatedCameraWidget::initializeGL() {
  CameraWidget::initializeGL();
  qInfo() << "OpenGL version:" << QString((const char*)glGetString(GL_VERSION));
  qInfo() << "OpenGL vendor:" << QString((const char*)glGetString(GL_VENDOR));
  qInfo() << "OpenGL renderer:" << QString((const char*)glGetString(GL_RENDERER));
  qInfo() << "OpenGL language version:" << QString((const char*)glGetString(GL_SHADING_LANGUAGE_VERSION));

  prev_draw_t = millis_since_boot();
  setBackgroundColor(bg_colors[STATUS_DISENGAGED]);
}

void AnnotatedCameraWidget::updateFrameMat() {
  CameraWidget::updateFrameMat();
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

void AnnotatedCameraWidget::drawLaneLines(QPainter &painter, const UIState *s) {
  painter.save();

  const UIScene &scene = s->scene;
  SubMaster &sm = *(s->sm);

  // Shane's colored lanelines
  for (int i = 0; i < std::size(scene.lane_line_vertices); ++i) {
    if (i == 1 || i == 2) {
      // TODO: can we just use the projected vertices somehow?
      const cereal::XYZTData::Reader &line = (*s->sm)["modelV2"].getModelV2().getLaneLines()[i];
      const float default_pos = 1.4;  // when lane poly isn't available
      const float lane_pos = line.getY().size() > 0 ? std::abs(line.getY()[5]) : default_pos;  // get redder when line is closer to car
      float hue = 332.5 * lane_pos - 332.5;  // equivalent to {1.4, 1.0}: {133, 0} (green to red)
      hue = std::fmin(133, fmax(0, hue)) / 360.;  // clip and normalize
      painter.setBrush(QColor::fromHslF(hue, 1.0, 0.50, std::clamp<float>(scene.lane_line_probs[i], 0.0, 0.7)));
    } else {
      painter.setBrush(QColor::fromRgbF(1.0, 1.0, 1.0, std::clamp<float>(scene.lane_line_probs[i], 0.0, 0.7)));
    }
    painter.drawPolygon(scene.lane_line_vertices[i]);
  }

  // TODO: Fix empty spaces when curiving back on itself
  painter.setBrush(QColor::fromRgbF(1.0, 0.0, 0.0, 0.2));
  if (left_blindspot) painter.drawPolygon(scene.lane_barrier_vertices[0]);
  if (right_blindspot) painter.drawPolygon(scene.lane_barrier_vertices[1]);

  // road edges
  for (int i = 0; i < std::size(scene.road_edge_vertices); ++i) {
    painter.setBrush(QColor::fromRgbF(1.0, 0, 0, std::clamp<float>(1.0 - scene.road_edge_stds[i], 0.0, 1.0)));
    painter.drawPolygon(scene.road_edge_vertices[i]);
  }

  // paint path
  QLinearGradient bg(0, height(), 0, height() / 4);
  float start_hue, end_hue;
  if (madsEnabled) {
    if (steerOverride && latActive) {
      bg.setColorAt(0, blackColor(80));
      bg.setColorAt(1, blackColor(20));
    } else if (!latActive) {
      bg.setColorAt(0, whiteColor());
      bg.setColorAt(1, whiteColor(0));
    } else if (sm["controlsState"].getControlsState().getExperimentalMode()) {
      const auto &acceleration = sm["modelV2"].getModelV2().getAcceleration();
      float acceleration_future = 0;
      if (acceleration.getZ().size() > 16) {
        acceleration_future = acceleration.getX()[16];  // 2.5 seconds
      }
      start_hue = 60;
      // speed up: 120, slow down: 0
      end_hue = fmax(fmin(start_hue + acceleration_future * 45, 148), 0);

      // FIXME: painter.drawPolygon can be slow if hue is not rounded
      end_hue = int(end_hue * 100 + 0.5) / 100;

      bg.setColorAt(0.0, QColor::fromHslF(start_hue / 360., 0.97, 0.56, 0.7));
      bg.setColorAt(0.5, QColor::fromHslF(end_hue / 360., 1.0, 0.68, 0.35));
      bg.setColorAt(1.0, QColor::fromHslF(end_hue / 360., 1.0, 0.68, 0.0));
    } else {
      bg.setColorAt(0.0, QColor::fromHslF(148 / 360., 0.94, 0.51, 0.7));
      bg.setColorAt(0.5, QColor::fromHslF(112 / 360., 1.0, 0.68, 0.35));
      bg.setColorAt(1.0, QColor::fromHslF(112 / 360., 1.0, 0.68, 0.0));
    }
  } else {
    bg.setColorAt(0.0, whiteColor(102));
    bg.setColorAt(0.5, whiteColor(89));
    bg.setColorAt(1.0, whiteColor(0));
  }

  if (!scene.dynamic_lane_profile_status) {
    // paint path edges
    QLinearGradient pe(0, height(), 0, height() / 4);
    pe.setColorAt(0.0, whiteColor(102));
    pe.setColorAt(0.5, whiteColor(89));
    pe.setColorAt(1.0, whiteColor(0));
    painter.setBrush(pe);
    painter.drawPolygon(scene.track_edge_vertices);
  }

  painter.setBrush(bg);
  painter.drawPolygon(scene.track_vertices);

  painter.restore();
}

void AnnotatedCameraWidget::drawDriverState(QPainter &painter, const UIState *s) {
  const UIScene &scene = s->scene;

  painter.save();

  // base icon
  int x = rightHandDM ? rect().right() -  (btn_size - 24) / 2 - (bdr_s * 2) : (btn_size - 24) / 2 + (bdr_s * 2);
  int y = rect().bottom() - footer_h / 2;
  float opacity = dmActive ? 0.65 : 0.2;
  drawIcon(painter, x, y, dm_img, blackColor(0), opacity);

  // circle background
  painter.setOpacity(1.0);
  painter.setPen(Qt::NoPen);
  painter.setBrush(blackColor(70));
  painter.drawEllipse(x - btn_size / 2, y - btn_size / 2, btn_size, btn_size);

  // face
  QPointF face_kpts_draw[std::size(default_face_kpts_3d)];
  float kp;
  for (int i = 0; i < std::size(default_face_kpts_3d); ++i) {
    kp = (scene.face_kpts_draw[i].v[2] - 8) / 120 + 1.0;
    face_kpts_draw[i] = QPointF(scene.face_kpts_draw[i].v[0] * kp + x, scene.face_kpts_draw[i].v[1] * kp + y);
  }

  painter.setPen(QPen(QColor::fromRgbF(1.0, 1.0, 1.0, opacity), 5.2, Qt::SolidLine, Qt::RoundCap));
  painter.drawPolyline(face_kpts_draw, std::size(default_face_kpts_3d));

  // tracking arcs
  const int arc_l = 133;
  const float arc_t_default = 6.7;
  const float arc_t_extend = 12.0;
  QColor arc_color = QColor::fromRgbF(0.545 - 0.445 * s->engaged(),
                                      0.545 + 0.4 * s->engaged(),
                                      0.545 - 0.285 * s->engaged(),
                                      0.4 * (1.0 - dm_fade_state));
  float delta_x = -scene.driver_pose_sins[1] * arc_l / 2;
  float delta_y = -scene.driver_pose_sins[0] * arc_l / 2;
  painter.setPen(QPen(arc_color, arc_t_default+arc_t_extend*fmin(1.0, scene.driver_pose_diff[1] * 5.0), Qt::SolidLine, Qt::RoundCap));
  painter.drawArc(QRectF(std::fmin(x + delta_x, x), y - arc_l / 2, fabs(delta_x), arc_l), (scene.driver_pose_sins[1]>0 ? 90 : -90) * 16, 180 * 16);
  painter.setPen(QPen(arc_color, arc_t_default+arc_t_extend*fmin(1.0, scene.driver_pose_diff[0] * 5.0), Qt::SolidLine, Qt::RoundCap));
  painter.drawArc(QRectF(x - arc_l / 2, std::fmin(y + delta_y, y), arc_l, fabs(delta_y)), (scene.driver_pose_sins[0]>0 ? 0 : 180) * 16, 180 * 16);

  painter.restore();
}

void AnnotatedCameraWidget::rocketFuel(QPainter &p) {

  static const int ct_n = 1;
  static float ct;

  int rect_w = rect().width();
  int rect_h = rect().height();

  const int n = 15 + 1; //Add one off screen due to timing issues
  static float t[n];
  int dim_n = (sin(ct / 5) + 1) * (n - 0.01);
  t[dim_n] = 1.0;
  t[(int)(ct/ct_n)] = 1.0;

  UIState *s = uiState();
  float vc_accel0 = (*s->sm)["carState"].getCarState().getAEgo();
  static float vc_accel;
  vc_accel = vc_accel + (vc_accel0 - vc_accel) / 5;
  float hha = 0;
  if (vc_accel > 0) {
    hha = 1 - 0.1 / vc_accel;
    p.setBrush(QColor(0, 245, 0, 200));
  }
  if (vc_accel < 0) {
    hha = 1 + 0.1 / vc_accel;
    p.setBrush(QColor(245, 0, 0, 200));
  }
  if (hha < 0) {
    hha = 0;
  }
  hha = hha * rect_h;
  float wp = 35;
  if (vc_accel > 0) {
    QRect ra = QRect(rect_w - wp, rect_h / 2 - hha / 2, wp, hha / 2);
    p.drawRect(ra);
  } else {
    QRect ra = QRect(rect_w - wp, rect_h / 2, wp, hha / 2);
    p.drawRect(ra);
  }
}

void AnnotatedCameraWidget::drawLead(QPainter &painter, const cereal::RadarState::LeadData::Reader &lead_data, const QPointF &vd,
                                     int num, float radar_d_rel, float v_ego, float radar_v_rel, int chevron_data, bool isMetric) {
  painter.save();

  const float speedBuff = 10.;
  const float leadBuff = 40.;
  const float d_rel = lead_data.getDRel();
  const float v_rel = lead_data.getVRel();

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

  float homebase_h = 12;
  QPointF glow[] = {{x + (sz * 1.35) + g_xo, y + sz + g_yo + homebase_h}, {x + (sz * 1.35) + g_xo, y + sz + g_yo},
                   {x, y - g_yo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo + homebase_h}};
  painter.setBrush(QColor(218, 202, 37, 255));
  painter.drawPolygon(glow, std::size(glow));

  // chevron
  QPointF chevron[] = {{x + (sz * 1.25), y + sz + homebase_h}, {x + (sz * 1.25), y + sz}, {x, y}, {x - (sz * 1.25), y + sz},
                      {x - (sz * 1.25), y + sz + homebase_h}};
  painter.setBrush(redColor(fillAlpha));
  painter.drawPolygon(chevron, std::size(chevron));

  if (num == 0) { // Display the distance to the 0th lead car
    QString dist = "";
    if (chevron_data == 1) dist = QString::number(radar_d_rel,'f', 1) + "m";
    else if (chevron_data == 2) {
      if (isMetric) dist = QString::number((radar_v_rel + v_ego) * 3.6,'f', 0) + "km/h";
      else dist = QString::number((radar_v_rel + v_ego) * 2.236936,'f', 0) + "mph";
    }
    int str_w = 200;
    configFont(painter, "Inter", 44, "SemiBold");
    painter.setPen(QColor(0x0, 0x0, 0x0 , 200)); // Shadow
    float lock_indicator_dx = 2; // Avoid downward cross sights
    painter.drawText(QRect(x + 2 + lock_indicator_dx, y - 50 + 2, str_w, 50), Qt::AlignBottom | Qt::AlignLeft, dist);
    painter.setPen(QColor(0xff, 0xff, 0xff));
    painter.drawText(QRect(x + lock_indicator_dx, y - 50, str_w, 50), Qt::AlignBottom | Qt::AlignLeft, dist);
    painter.setPen(Qt::NoPen);
  }

  painter.restore();
}

void AnnotatedCameraWidget::paintGL() {
}

void AnnotatedCameraWidget::paintEvent(QPaintEvent *event) {
  UIState *s = uiState();
  SubMaster &sm = *(s->sm);
  const double start_draw_t = millis_since_boot();
  const cereal::ModelDataV2::Reader &model = sm["modelV2"].getModelV2();
  const cereal::RadarState::Reader &radar_state = sm["radarState"].getRadarState();

  QPainter painter(this);

  // draw camera frame
  {
    std::lock_guard lk(frame_lock);

    if (frames.empty()) {
      if (skip_frame_count > 0) {
        skip_frame_count--;
        qDebug() << "skipping frame, not ready";
        return;
      }
    } else {
      // skip drawing up to this many frames if we're
      // missing camera frames. this smooths out the
      // transitions from the narrow and wide cameras
      skip_frame_count = 5;
    }

    // Wide or narrow cam dependent on speed
    float v_ego = sm["carState"].getCarState().getVEgo();
    if ((v_ego < 10) || s->wide_cam_only) {
      wide_cam_requested = true;
    } else if (v_ego > 15) {
      wide_cam_requested = false;
    }
    wide_cam_requested = wide_cam_requested && sm["controlsState"].getControlsState().getExperimentalMode();
    // TODO: also detect when ecam vision stream isn't available
    // for replay of old routes, never go to widecam
    wide_cam_requested = wide_cam_requested && s->scene.calibration_wide_valid;
    CameraWidget::setStreamType(wide_cam_requested ? VISION_STREAM_WIDE_ROAD : VISION_STREAM_ROAD);

    s->scene.wide_cam = CameraWidget::getStreamType() == VISION_STREAM_WIDE_ROAD;
    if (s->scene.calibration_valid) {
      auto calib = s->scene.wide_cam ? s->scene.view_from_wide_calib : s->scene.view_from_calib;
      CameraWidget::updateCalibration(calib);
    } else {
      CameraWidget::updateCalibration(DEFAULT_CALIBRATION);
    }
    painter.beginNativePainting();
    CameraWidget::setFrameId(model.getFrameId());
    CameraWidget::paintGL();
    painter.endNativePainting();
  }

  painter.setRenderHint(QPainter::Antialiasing);
  painter.setPen(Qt::NoPen);

  if (s->worldObjectsVisible()) {
    if (sm.rcv_frame("modelV2") > s->scene.started_frame) {
      update_model(s, sm["modelV2"].getModelV2(), sm["uiPlan"].getUiPlan());
      if (sm.rcv_frame("radarState") > s->scene.started_frame) {
        update_leads(s, radar_state, sm["modelV2"].getModelV2().getPosition());
      }
    }

    drawLaneLines(painter, s);

    if (s->scene.longitudinal_control) {
      auto lead_one = radar_state.getLeadOne();
      auto lead_two = radar_state.getLeadTwo();
      float v_ego = sm["carState"].getCarState().getVEgo();
      float radar_d_rel = radar_state.getLeadOne().getDRel();
      float radar_v_rel = radar_state.getLeadOne().getVRel();
      if (lead_one.getStatus()) {
        drawLead(painter, lead_one, s->scene.lead_vertices[0], 0, radar_d_rel, v_ego, radar_v_rel, s->scene.chevron_data, s->scene.is_metric);
      }
      if (lead_two.getStatus() && (std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0)) {
        drawLead(painter, lead_two, s->scene.lead_vertices[1], 1, radar_d_rel, v_ego, radar_v_rel, s->scene.chevron_data, s->scene.is_metric);
      }

      rocketFuel(painter);
    }
  }

  // DMoji
  if (!hideDM && (sm.rcv_frame("driverStateV2") > s->scene.started_frame)) {
    update_dmonitoring(s, sm["driverStateV2"].getDriverStateV2(), dm_fade_state, rightHandDM);
    drawDriverState(painter, s);
  }

  drawHud(painter);

  double cur_draw_t = millis_since_boot();
  double dt = cur_draw_t - prev_draw_t;
  double fps = fps_filter.update(1. / dt * 1000);
  if (fps < 15) {
    LOGW("slow frame rate: %.2f fps", fps);
  }
  prev_draw_t = cur_draw_t;

  // publish debug msg
  MessageBuilder msg;
  auto m = msg.initEvent().initUiDebug();
  m.setDrawTimeMillis(cur_draw_t - start_draw_t);
  pm->send("uiDebug", msg);
}

void AnnotatedCameraWidget::showEvent(QShowEvent *event) {
  CameraWidget::showEvent(event);

  if (millis_since_boot() - last_update_params > 1000 * 5) {
    last_update_params = millis_since_boot();
    ui_update_params(uiState());
  }
  prev_draw_t = millis_since_boot();
}
