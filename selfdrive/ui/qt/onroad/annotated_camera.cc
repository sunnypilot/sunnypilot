#include "selfdrive/ui/qt/onroad/annotated_camera.h"

#include <algorithm>
#include <cmath>
#include <QMouseEvent>
#include <QPainterPath>

#include "common/swaglog.h"
#include "selfdrive/ui/qt/onroad/buttons.h"
#include "selfdrive/ui/qt/util.h"

static std::pair<QString, QColor> getFeatureStatus(int value, QStringList text_list, QStringList color_list,
                                                   bool condition, QString off_text) {

  QString text("Error");
  QColor color("#ffffff");

  for (int i = 0; i < text_list.size() && i < color_list.size(); ++i) {
    if (value == i) {
      text = condition ? text_list[i] : off_text;
      color = condition ? QColor(color_list[i]) : QColor("#ffffff");
      break;  // Exit the loop once a match is found
    }
  }

  return {text, color};
}


// Window that shows camera view and variety of info drawn on top
AnnotatedCameraWidget::AnnotatedCameraWidget(VisionStreamType type, QWidget* parent) : fps_filter(UI_FREQ, 3, 1. / UI_FREQ), CameraWidget("camerad", type, true, parent) {
  pm = std::make_unique<PubMaster, const std::initializer_list<const char *>>({"uiDebug"});
  e2e_state = std::make_unique<PubMaster, const std::initializer_list<const char *>>({"e2eLongStateSP"});

  main_layout = new QVBoxLayout(this);
  main_layout->setMargin(UI_BORDER_SIZE);
  main_layout->setSpacing(0);

  experimental_btn = new ExperimentalButton(this);
  main_layout->addWidget(experimental_btn, 0, Qt::AlignTop | Qt::AlignRight);

  onroad_settings_btn = new OnroadSettingsButton(this);

  map_settings_btn = new MapSettingsButton(this);

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

  QObject::connect(uiState(), &UIState::offroadTransition, this, &AnnotatedCameraWidget::offroadTransition);
#endif

  buttons_layout = new QHBoxLayout();
  buttons_layout->setContentsMargins(0, 0, 10, 20);
  main_layout->addLayout(buttons_layout);
  updateButtonsLayout();
}

void AnnotatedCameraWidget::mousePressEvent(QMouseEvent* e) {
  bool propagate_event = true;

  UIState *s = uiState();
  UIScene &scene = s->scene;
  const SubMaster &sm = *(s->sm);
  const auto longitudinal_plan_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();

  if (longitudinal_plan_sp.getSpeedLimit() > 0.0 && sl_sign_rect.contains(e->x(), e->y())) {
    // If touching the speed limit sign area when visible
    scene.last_speed_limit_sign_tap = seconds_since_boot();
    params.putBool("LastSpeedLimitSignTap", true);
    scene.speed_limit_control_enabled = !scene.speed_limit_control_enabled;
    params.putBool("EnableSlc", scene.speed_limit_control_enabled);
    propagate_event = false;
  }

  if (propagate_event) {
    QWidget::mousePressEvent(e);
  }
}

#ifdef ENABLE_DASHCAM
void AnnotatedCameraWidget::offroadTransition(bool offroad) {
  if (offroad) {
    if (recorder) recorder->stop();

    roadName = "";
  }
}
#endif

void AnnotatedCameraWidget::updateButtonsLayout() {
  QLayoutItem *item;
  while ((item = buttons_layout->takeAt(0)) != nullptr) {
    delete item;
  }

  buttons_layout->setContentsMargins(0, 0, 10, rn_offset != 0 ? rn_offset + 10 : 20);

  buttons_layout->addSpacing(onroad_settings_btn->isVisible() ? 216 : 0);
  buttons_layout->addWidget(onroad_settings_btn, 0, Qt::AlignBottom | Qt::AlignLeft);

  buttons_layout->addStretch(1);

#ifdef ENABLE_DASHCAM
  buttons_layout->addWidget(recorder, 0, Qt::AlignBottom | Qt::AlignRight);
#endif

  buttons_layout->addSpacing(map_settings_btn->isVisible() ? 30 : 0);
  buttons_layout->addWidget(map_settings_btn, 0, Qt::AlignBottom | Qt::AlignRight);
}

void AnnotatedCameraWidget::updateState(const UIState &s) {
  const int SET_SPEED_NA = 255;
  const SubMaster &sm = *(s.sm);

  const bool cs_alive = sm.alive("controlsState");
  const bool nav_alive = sm.alive("navInstruction") && sm["navInstruction"].getValid();
  const auto cs = sm["controlsState"].getControlsState();
  const auto cs_sp = sm["controlsStateSP"].getControlsStateSP();
  const auto car_state = sm["carState"].getCarState();
  const auto nav_instruction = sm["navInstruction"].getNavInstruction();
  const auto car_control = sm["carControl"].getCarControl();
  const auto radar_state = sm["radarState"].getRadarState();
  const auto is_gps_location_external = sm.rcv_frame("gpsLocationExternal") > 1;
  const auto gpsLocation = is_gps_location_external ? sm["gpsLocationExternal"].getGpsLocationExternal() : sm["gpsLocation"].getGpsLocation();
  const auto ltp = sm["liveTorqueParameters"].getLiveTorqueParameters();
  const auto lateral_plan_sp = sm["lateralPlanSPDEPRECATED"].getLateralPlanSPDEPRECATED();
  car_params = sm["carParams"].getCarParams();

  // Handle older routes where vCruiseCluster is not set
  float v_cruise = cs.getVCruiseCluster() == 0.0 ? cs.getVCruise() : cs.getVCruiseCluster();
  setSpeed = cs_alive ? v_cruise : SET_SPEED_NA;
  is_cruise_set = setSpeed > 0 && (int)setSpeed != SET_SPEED_NA;
  if (is_cruise_set && !s.scene.is_metric) {
    setSpeed *= KM_TO_MILE;
  }

  // Handle older routes where vEgoCluster is not set
  v_ego_cluster_seen = v_ego_cluster_seen || car_state.getVEgoCluster() != 0.0;
  float v_ego = v_ego_cluster_seen ? car_state.getVEgoCluster() : car_state.getVEgo();
  v_ego = s.scene.true_vego_ui ? car_state.getVEgo() : v_ego;
  speed = cs_alive ? std::max<float>(0.0, v_ego) : 0.0;
  speed *= s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH;

  auto speed_limit_sign = nav_instruction.getSpeedLimitSign();
  speedLimit = nav_alive ? nav_instruction.getSpeedLimit() : 0.0;
  speedLimit *= (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);

  has_us_speed_limit = (nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::MUTCD);
  has_eu_speed_limit = (nav_alive && speed_limit_sign == cereal::NavInstruction::SpeedLimitSign::VIENNA);
  is_metric = s.scene.is_metric;
  speedUnit =  s.scene.is_metric ? tr("km/h") : tr("mph");
  hideBottomIcons = (cs.getAlertSize() != cereal::ControlsState::AlertSize::NONE);
  status = s.status;

  // TODO: Add minimum speed?
  left_blindspot = cs_alive && car_state.getLeftBlindspot();
  right_blindspot = cs_alive && car_state.getRightBlindspot();

  steerOverride = car_state.getSteeringPressed();
  gasOverride = car_state.getGasPressed();
  latActive = car_control.getLatActive();
  madsEnabled = car_state.getMadsEnabled();

  brakeLights = car_state.getBrakeLightsDEPRECATED() && s.scene.visual_brake_lights;

  standStillTimer = s.scene.stand_still_timer;
  standStill = car_state.getStandstill();
  standstillElapsedTime = lateral_plan_sp.getStandstillElapsed();

  hideVEgoUi = s.scene.hide_vego_ui;

  splitPanelVisible = s.scene.map_visible || s.scene.onroad_settings_visible;

  // ############################## DEV UI START ##############################
  lead_d_rel = radar_state.getLeadOne().getDRel();
  lead_v_rel = radar_state.getLeadOne().getVRel();
  lead_status = radar_state.getLeadOne().getStatus();
  lateralState = QString::fromStdString(cs_sp.getLateralState());
  angleSteers = car_state.getSteeringAngleDeg();
  steerAngleDesired = cs.getLateralControlState().getPidState().getSteeringAngleDesiredDeg();
  curvature = cs.getCurvature();
  roll = sm["liveParameters"].getLiveParameters().getRoll();
  memoryUsagePercent = sm["deviceState"].getDeviceState().getMemoryUsagePercent();
  devUiInfo = s.scene.dev_ui_info;
  gpsAccuracy = is_gps_location_external ? gpsLocation.getHorizontalAccuracy() : 1.0; //External reports accuracy, internal does not.
  altitude = gpsLocation.getAltitude();
  vEgo = car_state.getVEgo();
  aEgo = car_state.getAEgo();
  steeringTorqueEps = car_state.getSteeringTorqueEps();
  bearingAccuracyDeg = gpsLocation.getBearingAccuracyDeg();
  bearingDeg = gpsLocation.getBearingDeg();
  torquedUseParams = (ltp.getUseParams() || s.scene.live_torque_toggle) && !s.scene.torqued_override;
  latAccelFactorFiltered = ltp.getLatAccelFactorFiltered();
  frictionCoefficientFiltered = ltp.getFrictionCoefficientFiltered();
  liveValid = ltp.getLiveValid();
  // ############################## DEV UI END ##############################

  btnPerc = s.scene.sleep_btn_opacity * 0.05;

  left_blinker = car_state.getLeftBlinker();
  right_blinker = car_state.getRightBlinker();
  lane_change_edge_block = lateral_plan_sp.getLaneChangeEdgeBlockDEPRECATED();

  // update engageability/experimental mode button
  experimental_btn->updateState(s);

  // update onroad settings button state
  onroad_settings_btn->updateState(s);

#ifdef ENABLE_DASHCAM
  // update screen recorder button
  recorder->updateState(s);
#endif

  // update buttons layout
  updateButtonsLayout();

  // update DM icon
  auto dm_state = sm["driverMonitoringState"].getDriverMonitoringState();
  dmActive = dm_state.getIsActiveMode();
  rightHandDM = dm_state.getIsRHD();
  // DM icon transition
  dm_fade_state = std::clamp(dm_fade_state+0.2*(0.5-dmActive), 0.0, 1.0);

  // hide map settings button for alerts and flip for right hand DM
  if (map_settings_btn->isEnabled()) {
    map_settings_btn->setVisible(!hideBottomIcons);
    main_layout->setAlignment(map_settings_btn, (rightHandDM ? Qt::AlignLeft : Qt::AlignRight) | Qt::AlignBottom);
  }

  // hide onroad settings button for alerts and flip for right hand DM
  if (onroad_settings_btn->isEnabled()) {
    onroad_settings_btn->setVisible(!hideBottomIcons);
    main_layout->setAlignment(onroad_settings_btn, (rightHandDM ? Qt::AlignRight : Qt::AlignLeft) | Qt::AlignBottom);
  }

#ifdef ENABLE_DASHCAM
  // hide screen recorder button for alerts and flip for right hand DM
  if (recorder->isEnabled()) {
    recorder->setVisible(!hideBottomIcons);
    main_layout->setAlignment(recorder, (rightHandDM ? Qt::AlignLeft : Qt::AlignRight) | Qt::AlignBottom);
  }
#endif

  const auto lp_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();
  slcState = lp_sp.getSpeedLimitControlState();

  speedLimitControlToggle = s.scene.speed_limit_control_enabled;

  const auto vtcState = lp_sp.getVisionTurnControllerState();
  const float vtc_speed = lp_sp.getVisionTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
  const auto lpSoruce = lp_sp.getLongitudinalPlanSource();
  QColor vtc_color = tcs_colors[int(vtcState)];
  vtc_color.setAlpha(lpSoruce == cereal::LongitudinalPlanSP::LongitudinalPlanSource::TURN ? 255 : 100);

  showVTC = vtcState > cereal::LongitudinalPlanSP::VisionTurnControllerState::DISABLED;
  vtcSpeed = QString::number(std::nearbyint(vtc_speed));
  vtcColor = vtc_color;
  showDebugUI = s.scene.show_debug_ui;

  const auto lmd_sp = sm["liveMapDataSP"].getLiveMapDataSP();

  const auto data_type = int(lmd_sp.getDataType());
  const QString data_type_draw(data_type == 2 ? "🌐  " : "");
  roadName = QString::fromStdString(lmd_sp.getCurrentRoadName());
  roadName = !roadName.isEmpty() ? data_type_draw + roadName : "";

  float speed_limit_slc = lp_sp.getSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
  const float speed_limit_offset = lp_sp.getSpeedLimitOffset() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
  const bool sl_force_active = speedLimitControlToggle &&
                               seconds_since_boot() < s.scene.last_speed_limit_sign_tap + 2.0;
  const bool sl_inactive = !sl_force_active && (!speedLimitControlToggle ||
                           slcState == cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE);
  const bool sl_temp_inactive = !sl_force_active && (speedLimitControlToggle &&
                                slcState == cereal::LongitudinalPlanSP::SpeedLimitControlState::TEMP_INACTIVE);
  const bool sl_pre_active = !sl_force_active && (speedLimitControlToggle &&
                             slcState == cereal::LongitudinalPlanSP::SpeedLimitControlState::PRE_ACTIVE);
  const int sl_distance = int(lp_sp.getDistToSpeedLimit() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
  const QString sl_distance_str(QString::number(sl_distance) + (s.scene.is_metric ? "m" : "f"));
  const QString sl_offset_str(speed_limit_offset > 0.0 ? speed_limit_offset < 0.0 ?
                              "-" + QString::number(std::nearbyint(std::abs(speed_limit_offset))) :
                              "+" + QString::number(std::nearbyint(speed_limit_offset)) : "");
  const QString sl_inactive_str(sl_temp_inactive && s.scene.speed_limit_control_engage_type == 0 ? "TEMP" : "");
  const QString sl_substring(sl_inactive || sl_temp_inactive || sl_pre_active ? sl_inactive_str :
                             sl_distance > 0 ? sl_distance_str : sl_offset_str);

  showSpeedLimit = speed_limit_slc > 0.0;
  speedLimitSLC = speed_limit_slc;
  speedLimitSLCOffset = speed_limit_offset;
  slcSubText = sl_substring;
  slcSubTextSize = sl_inactive || sl_temp_inactive || sl_distance > 0 ? 25.0 : 27.0;
  mapSourcedSpeedLimit = lp_sp.getIsMapSpeedLimit();
  slcActive = !sl_inactive && !sl_temp_inactive;
  overSpeedLimit = showSpeedLimit && s.scene.speed_limit_warning_type != 0 &&
                   (std::nearbyint(speed_limit_slc + s.scene.speed_limit_warning_value_offset) < std::nearbyint(speed));
  plus_arrow_up_img = loadPixmap("../assets/img_plus_arrow_up", {105, 105});
  minus_arrow_down_img = loadPixmap("../assets/img_minus_arrow_down", {105, 105});

  const float tsc_speed = lp_sp.getTurnSpeed() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH);
  const auto tscState = lp_sp.getTurnSpeedControlState();
  const int t_distance = int(lp_sp.getDistToTurn() * (s.scene.is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
  const QString t_distance_str(QString::number(t_distance) + (s.scene.is_metric ? "m" : "f"));

  showTurnSpeedLimit = tsc_speed > 0.0 && std::round(tsc_speed) < 224 && (tsc_speed < speed || s.scene.show_debug_ui);
  turnSpeedLimit = QString::number(std::nearbyint(tsc_speed));
  tscSubText = t_distance > 0 ? t_distance_str : QString("");
  tscActive = tscState > cereal::LongitudinalPlanSP::SpeedLimitControlState::TEMP_INACTIVE;
  curveSign = lp_sp.getTurnSign();

  // TODO: Add toggle variables to cereal, and parse from cereal
  longitudinalPersonality = s.scene.longitudinal_personality;
  dynamicLaneProfile = s.scene.dynamic_lane_profile;
  mpcMode = QString::fromStdString(lp_sp.getE2eBlended());
  mpcMode = (mpcMode == "blended") ? mpcMode.replace(0, 1, mpcMode[0].toUpper()) : mpcMode.toUpper();

  static int reverse_delay = 0;
  bool reverse_allowed = false;
  if (int(car_state.getGearShifter()) != 4) {
    reverse_delay = 0;
    reverse_allowed = false;
  } else {
    reverse_delay += 50;
    if (reverse_delay >= 1000) {
      reverse_allowed = true;
    }
  }

  reversing = reverse_allowed;

  cruiseStateEnabled = car_state.getCruiseState().getEnabled();

  int e2eLStatus = 0;
  static bool chime_sent = false;
  static int chime_count = 0;
  int chime_prompt = 0;
  static float last_lead_distance = -1;
  const float lead_distance = radar_state.getLeadOne().getDRel();

  if (s.scene.e2eX[12] > 30 && car_state.getVEgo() < 1.0) {
    e2eLStatus = 2;
  } else if ((s.scene.e2eX[12] > 0 && s.scene.e2eX[12] < 80) || s.scene.e2eX[12] < 0) {
    e2eLStatus = 1;
  } else {
    e2eLStatus = 0;
  }

  if (!car_state.getStandstill()) {
    chime_prompt = 0;
    chime_sent = false;
    chime_count = 0;

    if (last_lead_distance != -1) {
      last_lead_distance = -1;
    }
  }

  if ((cruiseStateEnabled || car_state.getBrakeLightsDEPRECATED()) && !car_state.getGasPressed() && car_state.getStandstill()) {
    if (e2eLStatus == 2 && !radar_state.getLeadOne().getStatus()) {
      if (chime_sent) {
        chime_count = 0;
      } else {
        chime_count += 1;
      }
      if (s.scene.e2e_long_alert_light && chime_count >= 2 && !chime_sent) {
        chime_prompt = 1;
        chime_sent = true;
      } else {
        chime_prompt = 0;
      }
    } else if (radar_state.getLeadOne().getStatus()) {
      if ((last_lead_distance == -1) || (lead_distance < last_lead_distance)) {
        last_lead_distance = lead_distance;
      }
      if (s.scene.e2e_long_alert_lead && (lead_distance - last_lead_distance > 1.0) && !chime_sent) {
        chime_prompt = 2;
        chime_sent = true;
      } else {
        chime_prompt = 0;
      }
    } else {
      chime_prompt = 0;
    }
  } else {
  }

  e2eStatus = chime_prompt;
  e2eState = e2eLStatus;
  e2eLongAlertUi = s.scene.e2e_long_alert_ui;
  dynamicExperimentalControlToggle = s.scene.dynamic_experimental_control;
  speedLimitWarningFlash = s.scene.speed_limit_warning_flash;
  experimentalMode = cs.getExperimentalMode();

  featureStatusToggle = s.scene.feature_status_toggle;

  experimental_btn->setVisible(!(showDebugUI && showVTC));
  drivingModelGen = s.scene.driving_model_gen;
}

void AnnotatedCameraWidget::drawHud(QPainter &p) {
  p.save();

  // Header gradient
  QLinearGradient bg(0, UI_HEADER_HEIGHT - (UI_HEADER_HEIGHT / 2.5), 0, UI_HEADER_HEIGHT);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, width(), UI_HEADER_HEIGHT, bg);

  QString speedLimitStr = (speedLimit > 1) ? QString::number(std::nearbyint(speedLimit)) : "–";
  QString speedLimitStrSlc = showSpeedLimit ? QString::number(std::nearbyint(speedLimitSLC)) : "–";
  QString speedStr = QString::number(std::nearbyint(speed));
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(setSpeed)) : "–";
  const bool isNavSpeedLimit = has_us_speed_limit || has_eu_speed_limit;

  // Draw outer box + border to contain set speed and speed limit
  const int sign_margin = 12;
  const int us_sign_height = slcSubText == "" ? 186 : 216;
  const int eu_sign_size = 176;

  const QSize default_size = {172, 204};
  QSize set_speed_size = default_size;
  if (is_metric || has_eu_speed_limit) set_speed_size.rwidth() = 200;
  if ((mapSourcedSpeedLimit && !is_metric && speedLimitStrSlc.size() >= 3) ||
      (has_us_speed_limit && speedLimitStr.size() >= 3)) set_speed_size.rwidth() = 223;

  if ((mapSourcedSpeedLimit && !is_metric) || has_us_speed_limit) set_speed_size.rheight() += us_sign_height + sign_margin;
  else if ((mapSourcedSpeedLimit && is_metric) || has_eu_speed_limit) set_speed_size.rheight() += eu_sign_size + sign_margin;

  int top_radius = 32;
  int bottom_radius = ((mapSourcedSpeedLimit && is_metric) || has_eu_speed_limit) ? 100 : 32;

  QRect set_speed_rect(QPoint(60 + (default_size.width() - set_speed_size.width()) / 2, 45), set_speed_size);
  p.setPen(QPen(whiteColor(75), 6));
  p.setBrush(blackColor(166));
  drawRoundedRect(p, set_speed_rect, top_radius, top_radius, bottom_radius, bottom_radius);

  // Draw MAX
  QColor max_color = QColor(0x80, 0xd8, 0xa6, 0xff);
  QColor set_speed_color = whiteColor();
  if (is_cruise_set) {
    if (status == STATUS_DISENGAGED) {
      max_color = whiteColor();
    } else if (status == STATUS_OVERRIDE && gasOverride) {
      max_color = QColor(0x91, 0x9b, 0x95, 0xff);
    } else if (speedLimitSLC > 0) {
      auto interp_color = [=](QColor c1, QColor c2, QColor c3) {
        return speedLimitSLC > 0 ? interpColor(setSpeed, {speedLimitSLC + 5, speedLimitSLC + 15, speedLimitSLC + 25}, {c1, c2, c3}) : c1;
      };
      max_color = interp_color(max_color, QColor(0xff, 0xe4, 0xbf), QColor(0xff, 0xbf, 0xbf));
      set_speed_color = interp_color(set_speed_color, QColor(0xff, 0x95, 0x00), QColor(0xff, 0x00, 0x00));
    } else if (speedLimit > 0) {
      auto interp_color = [=](QColor c1, QColor c2, QColor c3) {
        return speedLimit > 0 ? interpColor(setSpeed, {speedLimit + 5, speedLimit + 15, speedLimit + 25}, {c1, c2, c3}) : c1;
      };
      max_color = interp_color(max_color, QColor(0xff, 0xe4, 0xbf), QColor(0xff, 0xbf, 0xbf));
      set_speed_color = interp_color(set_speed_color, QColor(0xff, 0x95, 0x00), QColor(0xff, 0x00, 0x00));
    }
  } else {
    max_color = QColor(0xa6, 0xa6, 0xa6, 0xff);
    set_speed_color = QColor(0x72, 0x72, 0x72, 0xff);
  }
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(max_color);
  p.drawText(set_speed_rect.adjusted(0, 27, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("MAX"));
  p.setFont(InterFont(90, QFont::Bold));
  p.setPen(set_speed_color);
  p.drawText(set_speed_rect.adjusted(0, 77, 0, 0), Qt::AlignTop | Qt::AlignHCenter, setSpeedStr);

  const QRect sign_rect = set_speed_rect.adjusted(sign_margin, default_size.height(), -sign_margin, -sign_margin);
  sl_sign_rect = sign_rect;

  speedLimitWarning(p, sign_rect, sign_margin);

  // US/Canada (MUTCD style) sign
  if (((mapSourcedSpeedLimit && !is_metric && !isNavSpeedLimit) || has_us_speed_limit) && slcShowSign) {
    p.setPen(Qt::NoPen);
    p.setBrush(whiteColor());
    p.drawRoundedRect(sign_rect, 24, 24);
    p.setPen(QPen(blackColor(), 6));
    p.drawRoundedRect(sign_rect.adjusted(9, 9, -9, -9), 16, 16);

    p.setFont(InterFont(28, QFont::DemiBold));
    p.drawText(sign_rect.adjusted(0, 22, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("SPEED"));
    p.drawText(sign_rect.adjusted(0, 51, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("LIMIT"));
    p.setFont(InterFont(70, QFont::Bold));
    if (overSpeedLimit) p.setPen(QColor(255, 0, 0, 255));
    else p.setPen(blackColor());
    p.drawText(sign_rect.adjusted(0, 85, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedLimitStrSlc);

    // Speed limit offset value
    p.setFont(InterFont(32, QFont::Bold));
    p.setPen(blackColor());
    p.drawText(sign_rect.adjusted(0, 85 + 77, 0, 0), Qt::AlignTop | Qt::AlignHCenter, slcSubText);
  }

  // EU (Vienna style) sign
  if (((mapSourcedSpeedLimit && is_metric && !isNavSpeedLimit) || has_eu_speed_limit) && slcShowSign) {
    p.setPen(Qt::NoPen);
    p.setBrush(whiteColor());
    p.drawEllipse(sign_rect);
    p.setPen(QPen(Qt::red, 20));
    p.drawEllipse(sign_rect.adjusted(16, 16, -16, -16));

    p.setFont(InterFont((speedLimitStrSlc.size() >= 3) ? 60 : 70, QFont::Bold));
    if (overSpeedLimit) p.setPen(QColor(255, 0, 0, 255));
    else p.setPen(blackColor());
    p.drawText(sign_rect, Qt::AlignCenter, speedLimitStrSlc);

    // Speed limit offset value
    p.setFont(InterFont(slcSubTextSize, QFont::Bold));
    p.setPen(blackColor());
    p.drawText(sign_rect.adjusted(0, 27, 0, 0), Qt::AlignTop | Qt::AlignHCenter, slcSubText);
  }

  // current speed
  if (!hideVEgoUi) {
    p.setFont(InterFont(176, QFont::Bold));
    drawColoredText(p, rect().center().x(), 210, speedStr, brakeLights ? QColor(0xff, 0, 0, 255) : QColor(0xff, 0xff, 0xff, 255));
    p.setFont(InterFont(66));
    drawText(p, rect().center().x(), 290, speedUnit, 200);
  }

  if (!reversing) {
    // ####### 1 ROW #######
    QRect bar_rect1(rect().left(), rect().bottom() - 60, rect().width(), 61);
    if (!splitPanelVisible && devUiInfo == 2) {
      p.setPen(Qt::NoPen);
      p.setBrush(QColor(0, 0, 0, 100));
      p.drawRect(bar_rect1);
      drawNewDevUi2(p, bar_rect1.left(), bar_rect1.center().y());
    }

    // ####### 1 COLUMN ########
    QRect rc2(rect().right() - (UI_BORDER_SIZE * 2), UI_BORDER_SIZE * 1.5, 184, 152);
    if (devUiInfo != 0) {
      drawRightDevUi(p, rect().right() - 184 - UI_BORDER_SIZE * 2, UI_BORDER_SIZE * 2 + rc2.height());
    }

    int rn_btn = 0;
    rn_btn = !splitPanelVisible && devUiInfo == 2 ? 35 : 0;
    rn_offset = rn_btn;

    // Stand Still Timer
    if (standStillTimer && standStill && !splitPanelVisible) {
      drawStandstillTimer(p, rect().right() - 650, 30 + 160 + 250);
    }

    // V-TSC
    if (showDebugUI && showVTC) {
      drawVisionTurnControllerUI(p, rect().right() - 184 - (UI_BORDER_SIZE * 1.5), int(UI_BORDER_SIZE * 1.5), 184, vtcColor, vtcSpeed, 100);
    }

    // Bottom bar road name
    if (showDebugUI && !roadName.isEmpty()) {
      int font_size = splitPanelVisible ? 38 : 50;
      int h = splitPanelVisible ? 18 : 26;
      p.setFont(InterFont(font_size, QFont::Bold));
      drawRoadNameText(p, rect().center().x(), h, roadName, QColor(255, 255, 255, 255));
    }

    // Turn Speed Sign
    if (showTurnSpeedLimit) {
      QRect rc = sign_rect;
      rc.moveTop(sign_rect.bottom() + UI_BORDER_SIZE);
      drawTrunSpeedSign(p, rc, turnSpeedLimit, tscSubText, curveSign, tscActive);
    }
  }

  // E2E Status
  if (e2eLongAlertUi && e2eState != 0) {
    drawE2eStatus(p, UI_BORDER_SIZE * 2 + 190, 45, 150, 150, e2eState);
  }

  if (!hideBottomIcons && featureStatusToggle) {
    drawFeatureStatusText(p, UI_BORDER_SIZE * 2 + 370, rect().bottom() - 160 - rn_offset);
  }

  p.restore();
}

void AnnotatedCameraWidget::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void AnnotatedCameraWidget::drawColoredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void AnnotatedCameraWidget::drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y});

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}

void AnnotatedCameraWidget::drawRoadNameText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y});

  QRect real_rect_adjusted(real_rect);
  real_rect_adjusted.adjust(-UI_ROAD_NAME_MARGIN_X, 5, UI_ROAD_NAME_MARGIN_X, 0);
  QPainterPath path;
  path.addRoundedRect(real_rect_adjusted, 10, 10);
  p.setPen(Qt::NoPen);
  p.setBrush(QColor(0, 0, 0, 100));
  p.drawPath(path);

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}

void AnnotatedCameraWidget::drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color,
                                                       const QString &vision_speed, int alpha) {
  QRect rvtc(x, y, size, size);
  p.setPen(QPen(color, 10));
  p.setBrush(QColor(0, 0, 0, alpha));
  p.drawRoundedRect(rvtc, 20, 20);
  p.setPen(Qt::NoPen);

  p.setFont(InterFont(56, QFont::DemiBold));
  drawCenteredText(p, rvtc.center().x(), rvtc.center().y(), vision_speed, color);
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

  p.setFont(InterFont(125, QFont::DemiBold));
  drawColoredText(p, x, y, QString(lab_str), QColor(255, 175, 3, 240));
  p.setFont(InterFont(150, QFont::DemiBold));
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

  p.setFont(InterFont(89, QFont::Bold));
  drawCenteredText(p, x, y, speed_limit, text_color);
  p.setFont(InterFont(subtext_size, QFont::Bold));
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
  const int y = 184 * 2 + UI_BORDER_SIZE + 202;
  const int width = 184;

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
  p.setFont(InterFont(67, QFont::Bold));
  drawCenteredText(p, x, y + 25, turn_speed, text_color);
  p.setFont(InterFont(22, QFont::Bold));
  drawCenteredText(p, x, y + 65, sub_text, text_color);
}

// ############################## DEV UI START ##############################
void AnnotatedCameraWidget::drawCenteredLeftText(QPainter &p, int x, int y, const QString &text1, QColor color1, const QString &text2, const QString &text3, QColor color2) {
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(text1 + " ");
  QRect real_rect = fm.boundingRect(init_rect, 0, text1 + " ");
  real_rect.moveCenter({x, y});

  QRect init_rect3 = fm.boundingRect(text3);
  QRect real_rect3 = fm.boundingRect(init_rect3, 0, text3);
  real_rect3.moveTop(real_rect.top());
  real_rect3.moveLeft(real_rect.right() + 135);

  QRect init_rect2 = fm.boundingRect(text2);
  QRect real_rect2 = fm.boundingRect(init_rect2, 0, text2);
  real_rect2.moveTop(real_rect.top());
  real_rect2.moveRight(real_rect.right() + 125);

  p.setPen(color1);
  p.drawText(real_rect, Qt::AlignLeft | Qt::AlignVCenter, text1);

  p.setPen(color2);
  p.drawText(real_rect2, Qt::AlignRight | Qt::AlignVCenter, text2);
  p.drawText(real_rect3, Qt::AlignLeft | Qt::AlignVCenter, text3);
}

int AnnotatedCameraWidget::drawDevUiElementRight(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color) {
  p.setFont(InterFont(30 * 2, QFont::Bold));
  drawColoredText(p, x + 92, y + 80, value, color);

  p.setFont(InterFont(28, QFont::Bold));
  drawText(p, x + 92, y + 80 + 42, label, 255);

  if (units.length() > 0) {
    p.save();
    p.translate(x + 54 + 30 - 3 + 92 + 30, y + 37 + 25);
    p.rotate(-90);
    drawText(p, 0, 0, units, 255);
    p.restore();
  }

  return 110;
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getDRel() {
  QString value = lead_status ? QString::number(lead_d_rel, 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Orange if close, Red if very close
    if (lead_d_rel < 5) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_d_rel < 15) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "REL DIST", "m", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getVRel() {
  QString value = lead_status ? QString::number(lead_v_rel * (is_metric ? MS_TO_KPH : MS_TO_MPH), 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Red if approaching faster than 10mph
    // Orange if approaching (negative)
    if (lead_v_rel < -4.4704) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_v_rel < 0) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "REL SPEED", speedUnit, color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getSteeringAngleDeg() {
  QString value = QString("%1%2%3").arg(QString::number(angleSteers, 'f', 1)).arg("°").arg("");
  QColor color = (madsEnabled && latActive) ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  // Red if large steering angle
  // Orange if moderate steering angle
  if (std::fabs(angleSteers) > 180) {
    color = QColor(255, 0, 0, 255);
  } else if (std::fabs(angleSteers) > 90) {
    color = QColor(255, 188, 0, 255);
  }

  return UiElement(value, "REAL STEER", "", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getActualLateralAccel() {
  float actualLateralAccel = (curvature * pow(vEgo, 2)) - (roll * 9.81);

  QString value = QString::number(actualLateralAccel, 'f', 2);
  QColor color = (madsEnabled && latActive) ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "ACTUAL LAT", "m/s²", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getSteeringAngleDesiredDeg() {
  QString value = (madsEnabled && latActive) ? QString("%1%2%3").arg(QString::number(steerAngleDesired, 'f', 1)).arg("°").arg("") : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (madsEnabled && latActive) {
    // Red if large steering angle
    // Orange if moderate steering angle
    if (std::fabs(angleSteers) > 180) {
      color = QColor(255, 0, 0, 255);
    } else if (std::fabs(angleSteers) > 90) {
      color = QColor(255, 188, 0, 255);
    } else {
      color = QColor(0, 255, 0, 255);
    }
  }

  return UiElement(value, "DESIRED STEER", "", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getMemoryUsagePercent() {
  QString value = QString("%1%2").arg(QString::number(memoryUsagePercent, 'd', 0)).arg("%");
  QColor color = (memoryUsagePercent > 85) ? QColor(255, 188, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "RAM", "", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getAEgo() {
  QString value = QString::number(aEgo, 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ACC.", "m/s²", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getVEgoLead() {
  QString value = lead_status ? QString::number((lead_v_rel + vEgo) * (is_metric ? MS_TO_KPH : MS_TO_MPH), 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Red if approaching faster than 10mph
    // Orange if approaching (negative)
    if (lead_v_rel < -4.4704) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_v_rel < 0) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "L.S.", speedUnit, color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getFrictionCoefficientFiltered() {
  QString value = QString::number(frictionCoefficientFiltered, 'f', 3);
  QColor color = liveValid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "FRIC.", "", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getLatAccelFactorFiltered() {
  QString value = QString::number(latAccelFactorFiltered, 'f', 3);
  QColor color = liveValid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "L.A.", "m/s²", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getSteeringTorqueEps() {
  QString value = QString::number(std::fabs(steeringTorqueEps), 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "E.T.", "N·dm", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getBearingDeg() {
  QString value = (bearingAccuracyDeg != 180.00) ? QString("%1%2%3").arg(QString::number(bearingDeg, 'd', 0)).arg("°").arg("") : "-";
  QColor color = QColor(255, 255, 255, 255);
  QString dir_value;

  if (bearingAccuracyDeg != 180.00) {
    if (((bearingDeg >= 337.5) && (bearingDeg <= 360)) || ((bearingDeg >= 0) && (bearingDeg <= 22.5))) {
      dir_value = "N";
    } else if ((bearingDeg > 22.5) && (bearingDeg < 67.5)) {
      dir_value = "NE";
    } else if ((bearingDeg >= 67.5) && (bearingDeg <= 112.5)) {
      dir_value = "E";
    } else if ((bearingDeg > 112.5) && (bearingDeg < 157.5)) {
      dir_value = "SE";
    } else if ((bearingDeg >= 157.5) && (bearingDeg <= 202.5)) {
      dir_value = "S";
    } else if ((bearingDeg > 202.5) && (bearingDeg < 247.5)) {
      dir_value = "SW";
    } else if ((bearingDeg >= 247.5) && (bearingDeg <= 292.5)) {
      dir_value = "W";
    } else if ((bearingDeg > 292.5) && (bearingDeg < 337.5)) {
      dir_value = "NW";
    }
  } else {
    dir_value = "OFF";
  }

  return UiElement(QString("%1 | %2").arg(dir_value).arg(value), "B.D.", "", color);
}

AnnotatedCameraWidget::UiElement AnnotatedCameraWidget::getAltitude() {
  QString value = (gpsAccuracy != 0.00) ? QString::number(altitude, 'f', 1) : "-";
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ALT.", "m", color);
}

void AnnotatedCameraWidget::drawRightDevUi(QPainter &p, int x, int y) {
  int rh = 5;
  int ry = y;

  // Add Relative Distance to Primary Lead Car
  // Unit: Meters
  UiElement dRelElement = getDRel();
  rh += drawDevUiElementRight(p, x, ry, dRelElement.value, dRelElement.label, dRelElement.units, dRelElement.color);
  ry = y + rh;

  // Add Relative Velocity vs Primary Lead Car
  // Unit: kph if metric, else mph
  UiElement vRelElement = getVRel();
  rh += drawDevUiElementRight(p, x, ry, vRelElement.value, vRelElement.label, vRelElement.units, vRelElement.color);
  ry = y + rh;

  // Add Real Steering Angle
  // Unit: Degrees
  UiElement steeringAngleDegElement = getSteeringAngleDeg();
  rh += drawDevUiElementRight(p, x, ry, steeringAngleDegElement.value, steeringAngleDegElement.label, steeringAngleDegElement.units, steeringAngleDegElement.color);
  ry = y + rh;

  if (lateralState == "torque") {
    // Add Actual Lateral Acceleration (roll compensated) when using Torque
    // Unit: m/s²
    UiElement actualLateralAccelElement = getActualLateralAccel();
    rh += drawDevUiElementRight(p, x, ry, actualLateralAccelElement.value, actualLateralAccelElement.label, actualLateralAccelElement.units, actualLateralAccelElement.color);
  } else {
    // Add Desired Steering Angle when using PID
    // Unit: Degrees
    UiElement steeringAngleDesiredDegElement = getSteeringAngleDesiredDeg();
    rh += drawDevUiElementRight(p, x, ry, steeringAngleDesiredDegElement.value, steeringAngleDesiredDegElement.label, steeringAngleDesiredDegElement.units, steeringAngleDesiredDegElement.color);
  }
  ry = y + rh;

  // Add Device Memory (RAM) Usage
  // Unit: Percent
  UiElement memoryUsagePercentElement = getMemoryUsagePercent();
  rh += drawDevUiElementRight(p, x, ry, memoryUsagePercentElement.value, memoryUsagePercentElement.label, memoryUsagePercentElement.units, memoryUsagePercentElement.color);
  ry = y + rh;

  rh += 25;
  p.setBrush(QColor(0, 0, 0, 0));
  QRect ldu(x, y, 184, rh);
}

int AnnotatedCameraWidget::drawNewDevUiElement(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color) {
  p.setFont(InterFont(38, QFont::Bold));
  drawCenteredLeftText(p, x, y, label, whiteColor(), value, units, color);

  return 430;
}

void AnnotatedCameraWidget::drawNewDevUi2(QPainter &p, int x, int y) {
  int rw = 90;

  // Add Acceleration from Car
  // Unit: Meters per Second Squared
  UiElement aEgoElement = getAEgo();
  rw += drawNewDevUiElement(p, rw, y, aEgoElement.value, aEgoElement.label, aEgoElement.units, aEgoElement.color);

  // Add Velocity of Primary Lead Car
  // Unit: kph if metric, else mph
  UiElement vEgoLeadElement = getVEgoLead();
  rw += drawNewDevUiElement(p, rw, y, vEgoLeadElement.value, vEgoLeadElement.label, vEgoLeadElement.units, vEgoLeadElement.color);

  if (torquedUseParams) {
    // Add Friction Coefficient Raw from torqued
    // Unit: None
    UiElement frictionCoefficientFilteredElement = getFrictionCoefficientFiltered();
    rw += drawNewDevUiElement(p, rw, y, frictionCoefficientFilteredElement.value, frictionCoefficientFilteredElement.label, frictionCoefficientFilteredElement.units, frictionCoefficientFilteredElement.color);

    // Add Lateral Acceleration Factor Raw from torqued
    // Unit: m/s²
    UiElement latAccelFactorFilteredElement = getLatAccelFactorFiltered();
    rw += drawNewDevUiElement(p, rw, y, latAccelFactorFilteredElement.value, latAccelFactorFilteredElement.label, latAccelFactorFilteredElement.units, latAccelFactorFilteredElement.color);
  } else {
    // Add Steering Torque from Car EPS
    // Unit: Newton Meters
    UiElement steeringTorqueEpsElement = getSteeringTorqueEps();
    rw += drawNewDevUiElement(p, rw, y, steeringTorqueEpsElement.value, steeringTorqueEpsElement.label, steeringTorqueEpsElement.units, steeringTorqueEpsElement.color);

    // Add Bearing Degree and Direction from Car (Compass)
    // Unit: Meters
    UiElement bearingDegElement = getBearingDeg();
    rw += drawNewDevUiElement(p, rw, y, bearingDegElement.value, bearingDegElement.label, bearingDegElement.units, bearingDegElement.color);
  }

  // Add Altitude of Current Location
  // Unit: Meters
  UiElement altitudeElement = getAltitude();
  rw += drawNewDevUiElement(p, rw, y, altitudeElement.value, altitudeElement.label, altitudeElement.units, altitudeElement.color);
}

// ############################## DEV UI END ##############################

void AnnotatedCameraWidget::drawE2eStatus(QPainter &p, int x, int y, int w, int h, int e2e_long_status) {
  QColor status_color;
  QRect e2eStatusIcon(x, y, w, h);
  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(blackColor(70)));
  p.drawEllipse(e2eStatusIcon);
  e2eStatusIcon -= QMargins(25, 25, 25, 25);
  p.setPen(Qt::NoPen);
  if (e2e_long_status == 2) {
    status_color = QColor::fromRgbF(0.0, 1.0, 0.0, 0.9);
  } else if (e2e_long_status == 1) {
    status_color = QColor::fromRgbF(1.0, 0.0, 0.0, 0.9);
  }
  p.setBrush(QBrush(status_color));
  p.drawEllipse(e2eStatusIcon);
}

void AnnotatedCameraWidget::drawLeftTurnSignal(QPainter &painter, int x, int y, int circle_size, int state) {
  painter.setRenderHint(QPainter::Antialiasing, true);

  QColor circle_color, circle_color_0, circle_color_1;
  QColor arrow_color, arrow_color_0, arrow_color_1;
  if ((left_blindspot || lane_change_edge_block) && !(left_blinker && right_blinker)) {
    circle_color_0 = QColor(164, 0, 1);
    circle_color_1 = QColor(204, 0, 1);
    arrow_color_0 = QColor(72, 1, 1);
    arrow_color_1 = QColor(255, 255, 255);
  } else {
    circle_color_0 = QColor(22, 156, 69);
    circle_color_1 = QColor(30, 215, 96);
    arrow_color_0 = QColor(9, 56, 27);
    arrow_color_1 = QColor(255, 255, 255);
  }

  if (state == 1) {
    circle_color = circle_color_1;
    arrow_color = arrow_color_1;
  } else if (state == 0) {
    circle_color = circle_color_0;
    arrow_color = arrow_color_0;
  }

  // Draw the circle
  int circleX = x;
  int circleY = y;
  painter.setPen(Qt::NoPen);
  painter.setBrush(circle_color);
  painter.drawEllipse(circleX, circleY, circle_size, circle_size);

  // Draw the arrow
  int arrowSize = 50;
  int arrowX = circleX + (circle_size - arrowSize) / 4;
  int arrowY = circleY + (circle_size - arrowSize) / 2;
  painter.setPen(Qt::NoPen);
  painter.setBrush(arrow_color);

  // Draw the arrow shape
  QPolygon arrowPolygon;
  arrowPolygon << QPoint(arrowX + 10, arrowY + arrowSize / 2)
               << QPoint(arrowX + arrowSize - 3, arrowY)
               << QPoint(arrowX + arrowSize, arrowY)
               << QPoint(arrowX + arrowSize, arrowY + arrowSize)
               << QPoint(arrowX + arrowSize - 3, arrowY + arrowSize)
               << QPoint(arrowX + 10, arrowY + arrowSize / 2);
  painter.drawPolygon(arrowPolygon);

  // Draw the tail rectangle
  int tailWidth = arrowSize / 2.25;
  int tailHeight = arrowSize / 2;
  QRect tailRect(arrowX + arrowSize - 3, arrowY + arrowSize / 4, tailWidth, tailHeight);
  painter.fillRect(tailRect, arrow_color);
}

void AnnotatedCameraWidget::drawRightTurnSignal(QPainter &painter, int x, int y, int circle_size, int state) {
  painter.setRenderHint(QPainter::Antialiasing, true);

  QColor circle_color, circle_color_0, circle_color_1;
  QColor arrow_color, arrow_color_0, arrow_color_1;
  if ((right_blindspot || lane_change_edge_block) && !(left_blinker && right_blinker)) {
    circle_color_0 = QColor(164, 0, 1);
    circle_color_1 = QColor(204, 0, 1);
    arrow_color_0 = QColor(72, 1, 1);
    arrow_color_1 = QColor(255, 255, 255);
  } else {
    circle_color_0 = QColor(22, 156, 69);
    circle_color_1 = QColor(30, 215, 96);
    arrow_color_0 = QColor(9, 56, 27);
    arrow_color_1 = QColor(255, 255, 255);
  }

  if (state == 1) {
    circle_color = circle_color_1;
    arrow_color = arrow_color_1;
  } else if (state == 0) {
    circle_color = circle_color_0;
    arrow_color = arrow_color_0;
  }


  // Draw the circle
  int circleX = x;
  int circleY = y;
  painter.setPen(Qt::NoPen);
  painter.setBrush(circle_color);
  painter.drawEllipse(circleX, circleY, circle_size, circle_size);

  // Draw the arrow
  int arrowSize = 50;
  int arrowX = circleX + (circle_size - arrowSize) / 2 + (arrowSize / 2.5) - 3;
  int arrowY = circleY + (circle_size - arrowSize) / 2;
  painter.setPen(Qt::NoPen);
  painter.setBrush(arrow_color);

  // Draw the arrow shape
  QPolygon arrowPolygon;
  arrowPolygon << QPoint(arrowX + arrowSize - 10, arrowY + arrowSize / 2)
               << QPoint(arrowX + 3, arrowY)
               << QPoint(arrowX, arrowY)
               << QPoint(arrowX, arrowY + arrowSize)
               << QPoint(arrowX + 3, arrowY + arrowSize)
               << QPoint(arrowX + arrowSize - 10, arrowY + arrowSize / 2);
  painter.drawPolygon(arrowPolygon);

  // Draw the tail rectangle
  int tailWidth = arrowSize / 2.25;
  int tailHeight = arrowSize / 2;
  QRect tailRect(arrowX - tailWidth + 3, arrowY + arrowSize / 4, tailWidth, tailHeight);
  painter.fillRect(tailRect, arrow_color);
}

int AnnotatedCameraWidget::blinkerPulse(int frame) {
  if (frame % UI_FREQ < (UI_FREQ / 2)) {
    blinker_state = 1;
  } else {
    blinker_state = 0;
  }

  return blinker_state;
}

void AnnotatedCameraWidget::speedLimitSignPulse(int frame) {
  if (frame % UI_FREQ < (UI_FREQ / 2.5)) {
    slcShowSign = false;
  } else {
    slcShowSign = true;
  }
}

void AnnotatedCameraWidget::drawFeatureStatusText(QPainter &p, int x, int y) {
  const FeatureStatusText feature_text;
  const FeatureStatusColor feature_color;
  const QColor text_color = whiteColor();
  const QColor shadow_color = blackColor(38);
  const int text_height = 34;
  const int drop_shadow_size = 2;
  const int eclipse_x_offset = 25;
  const int eclipse_y_offset = 20;
  const int w = 16;
  const int h = 16;

  const bool longitudinal = hasLongitudinalControl(car_params);

  p.setFont(InterFont(32, QFont::Bold));

  // Define a function to draw a feature status button
  auto drawFeatureStatusElement = [&](int value, const QStringList& text_list, const QStringList& color_list, bool condition, const QString& off_text, const QString& label) {
    std::pair<QString, QColor> feature_status = getFeatureStatus(value, text_list, color_list, condition, off_text);
    QRect btn(x - eclipse_x_offset, y - eclipse_y_offset, w, h);
    QRect btn_shadow(x - eclipse_x_offset + drop_shadow_size, y - eclipse_y_offset + drop_shadow_size, w, h);
    p.setPen(Qt::NoPen);
    p.setBrush(shadow_color);
    p.drawEllipse(btn_shadow);
    p.setBrush(feature_status.second);
    p.drawEllipse(btn);
    QString status_text;
    status_text.sprintf("%s: %s", label.toStdString().c_str(), (feature_status.first).toStdString().c_str());
    p.setPen(QPen(shadow_color, 2));
    p.drawText(x + drop_shadow_size, y + drop_shadow_size, status_text);
    p.setPen(QPen(text_color, 2));
    p.drawText(x, y, status_text);
    y += text_height;
  };

  // Driving Personality / Gap Adjust Cruise
  if (longitudinal) {
    drawFeatureStatusElement(longitudinalPersonality, feature_text.gac_list_text, feature_color.gac_list_color, longitudinal, "N/A", "GAP");
  }

  // Dynamic Lane Profile
  if (drivingModelGen == 1) {
    drawFeatureStatusElement(dynamicLaneProfile, feature_text.dlp_list_text, feature_color.dlp_list_color, true, "OFF", "DLP");
  }

  // TODO: Add toggle variables to cereal, and parse from cereal
  if (longitudinal) {
    QColor dec_color((cruiseStateEnabled && dynamicExperimentalControlToggle) ? "#4bff66" : "#ffffff");
    QRect dec_btn(x - eclipse_x_offset, y - eclipse_y_offset, w, h);
    QRect dec_btn_shadow(x - eclipse_x_offset + drop_shadow_size, y - eclipse_y_offset + drop_shadow_size, w, h);
    p.setPen(Qt::NoPen);
    p.setBrush(shadow_color);
    p.drawEllipse(dec_btn_shadow);
    p.setBrush(dec_color);
    p.drawEllipse(dec_btn);
    QString dec_status_text;
    dec_status_text.sprintf("DEC: %s\n", dynamicExperimentalControlToggle ? (experimentalMode ? QString(mpcMode).toStdString().c_str() : QString("Inactive").toStdString().c_str()) : "OFF");
    p.setPen(QPen(shadow_color, 2));
    p.drawText(x + drop_shadow_size, y + drop_shadow_size, dec_status_text);
    p.setPen(QPen(text_color, 2));
    p.drawText(x, y, dec_status_text);
    y += text_height;
  }

  // TODO: Add toggle variables to cereal, and parse from cereal
  // Speed Limit Control
  if (longitudinal || !car_params.getPcmCruiseSpeed()) {
    drawFeatureStatusElement(int(slcState), feature_text.slc_list_text, feature_color.slc_list_color, speedLimitControlToggle, "OFF", "SLC");
  }
}

void AnnotatedCameraWidget::speedLimitWarning(QPainter &p, QRect sign_rect, const int sign_margin) {
  // PRE ACTIVE
  if (slcState == cereal::LongitudinalPlanSP::SpeedLimitControlState::PRE_ACTIVE) {
    int set_speed = std::nearbyint(setSpeed);
    int speed_limit_offsetted = std::nearbyint(speedLimitSLC + speedLimitSLCOffset);

    // Calculate the vertical offset using a sinusoidal function for smooth bouncing
    double bounce_frequency = 2.0 * M_PI / 20.0;  // 20 frames for one full oscillation
    int bounce_offset = 20 * sin(speed_limit_frame * bounce_frequency);  // Adjust the amplitude (20 pixels) as needed

    if (set_speed < speed_limit_offsetted) {
      QPoint iconPosition(sign_rect.right() + sign_margin * 3, sign_rect.center().y() - plus_arrow_up_img.height() / 2 + bounce_offset);
      p.drawPixmap(iconPosition, plus_arrow_up_img);
    } else if (set_speed > speed_limit_offsetted) {
      QPoint iconPosition(sign_rect.right() + sign_margin * 3, sign_rect.center().y() - minus_arrow_down_img.height() / 2 - bounce_offset);
      p.drawPixmap(iconPosition, minus_arrow_down_img);
    }

    speed_limit_frame++;
    speedLimitSignPulse(speed_limit_frame);
  }

  // current speed over speed limit
  else if (overSpeedLimit && speedLimitWarningFlash) {
    speed_limit_frame++;
    speedLimitSignPulse(speed_limit_frame);
  }

  else {
    speed_limit_frame = 0;
    slcShowSign = true;
  }
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

  const auto car_state = sm["carState"].getCarState();

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
  QLinearGradient bg(0, height(), 0, 0);
  if (madsEnabled || car_state.getCruiseState().getEnabled()) {
    if (steerOverride && latActive) {
      bg.setColorAt(0.0, QColor::fromHslF(20 / 360., 0.94, 0.51, 0.17));
      bg.setColorAt(0.5, QColor::fromHslF(20 / 360., 1.0, 0.68, 0.17));
      bg.setColorAt(1.0, QColor::fromHslF(20 / 360., 1.0, 0.68, 0.0));
    } else if (!(latActive || car_state.getCruiseState().getEnabled())) {
      bg.setColorAt(0, whiteColor());
      bg.setColorAt(1, whiteColor(0));
    } else if (sm["controlsState"].getControlsState().getExperimentalMode()) {
      // The first half of track_vertices are the points for the right side of the path
      const auto &acceleration = sm["modelV2"].getModelV2().getAcceleration().getX();
      const int max_len = std::min<int>(scene.track_vertices.length() / 2, acceleration.size());

      for (int i = 0; i < max_len; ++i) {
        // Some points are out of frame
        if (scene.track_vertices[i].y() < 0 || scene.track_vertices[i].y() > height()) continue;

        // Flip so 0 is bottom of frame
        float lin_grad_point = (height() - scene.track_vertices[i].y()) / height();

        // speed up: 120, slow down: 0
        float path_hue = fmax(fmin(60 + acceleration[i] * 35, 120), 0);
        // FIXME: painter.drawPolygon can be slow if hue is not rounded
        path_hue = int(path_hue * 100 + 0.5) / 100;

        float saturation = fmin(fabs(acceleration[i] * 1.5), 1);
        float lightness = util::map_val(saturation, 0.0f, 1.0f, 0.95f, 0.62f);  // lighter when grey
        float alpha = util::map_val(lin_grad_point, 0.75f / 2.f, 0.75f, 0.4f, 0.0f);  // matches previous alpha fade
        bg.setColorAt(lin_grad_point, QColor::fromHslF(path_hue / 360., saturation, lightness, alpha));

        // Skip a point, unless next is last
        i += (i + 2) < max_len ? 1 : 0;
      }

    } else {
      bg.setColorAt(0.0, QColor::fromHslF(148 / 360., 0.94, 0.51, 0.4));
      bg.setColorAt(0.5, QColor::fromHslF(112 / 360., 1.0, 0.68, 0.35));
      bg.setColorAt(1.0, QColor::fromHslF(112 / 360., 1.0, 0.68, 0.0));
    }
  } else {
    bg.setColorAt(0.0, whiteColor(102));
    bg.setColorAt(0.5, whiteColor(89));
    bg.setColorAt(1.0, whiteColor(0));
  }

  painter.setBrush(bg);
  painter.drawPolygon(scene.track_vertices);

  // create path combining track vertices and track edge vertices
  QPainterPath path;
  path.addPolygon(scene.track_vertices);
  path.addPolygon(scene.track_edge_vertices);

  // paint path edges
  QLinearGradient pe(0, height(), 0, height() / 4);
  if (!scene.dynamic_lane_profile_status) {
    pe.setColorAt(0.0, QColor::fromHslF(240 / 360., 0.94, 0.51, 1.0));
    pe.setColorAt(0.5, QColor::fromHslF(204 / 360., 1.0, 0.68, 0.5));
    pe.setColorAt(1.0, QColor::fromHslF(204 / 360., 1.0, 0.68, 0.0));

    painter.setBrush(pe);
    painter.drawPath(path);
  }

  painter.restore();
}

void AnnotatedCameraWidget::drawDriverState(QPainter &painter, const UIState *s) {
  const UIScene &scene = s->scene;

  painter.save();

  // base icon
  int offset = UI_BORDER_SIZE + btn_size / 2;
  int x = rightHandDM ? width() - offset : offset;
  int y = height() - offset - rn_offset;
  float opacity = dmActive ? 0.65 : 0.2;
  drawIcon(painter, QPoint(x, y), dm_img, blackColor(70), opacity);

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
    hha = 0.85 - 0.1 / vc_accel;  // only extend up to 85%
    p.setBrush(QColor(0, 245, 0, 200));
  }
  if (vc_accel < 0) {
    hha = 0.85 + 0.1 / vc_accel; // only extend up to 85%
    p.setBrush(QColor(245, 0, 0, 200));
  }
  if (hha < 0) {
    hha = 0;
  }
  hha = hha * rect_h;
  float wp = 28;
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

  QPointF glow[] = {{x + (sz * 1.35) + g_xo, y + sz + g_yo}, {x, y - g_yo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo}};
  painter.setBrush(QColor(218, 202, 37, 255));
  painter.drawPolygon(glow, std::size(glow));

  // chevron
  QPointF chevron[] = {{x + (sz * 1.25), y + sz}, {x, y}, {x - (sz * 1.25), y + sz}};
  painter.setBrush(redColor(fillAlpha));
  painter.drawPolygon(chevron, std::size(chevron));

  if (num == 0) {  // Display metrics to the 0th lead car
    QStringList chevron_text[2];
    if (chevron_data == 1 || chevron_data == 3) {
      chevron_text[0].append(QString::number(radar_d_rel,'f', 0) + " " + "m");
    }
    if (chevron_data == 2 || chevron_data == 3) {
      chevron_text[chevron_data - 2].append(QString::number((radar_v_rel + v_ego) * (isMetric ? MS_TO_KPH : MS_TO_MPH),'f', 0) + " " + (isMetric ? "km/h" : "mph"));
    }

    int str_w = 200; // Width of the text box, might need adjustment
    int str_h = 50; // Height of the text box, adjust as necessary
    painter.setFont(InterFont(45, QFont::Bold));
    // Calculate the center of the chevron and adjust the text box position
    float text_y = y + sz + 12; // Position the text at the bottom of the chevron
    QRect textRect(x - str_w / 2, text_y, str_w, str_h); // Adjust the rectangle to center the text horizontally at the chevron's bottom
    QPoint shadow_offset(2, 2);
    for (int i = 0; i < 2; ++i) {
      if (!chevron_text[i].isEmpty()) {
        painter.setPen(QColor(0x0, 0x0, 0x0, 200));  // Draw shadow
        painter.drawText(textRect.translated(shadow_offset.x(), shadow_offset.y() + i * str_h), Qt::AlignBottom | Qt::AlignHCenter, chevron_text[i].at(0));
        painter.setPen(QColor(0xff, 0xff, 0xff));  // Draw text
        painter.drawText(textRect.translated(0, i * str_h), Qt::AlignBottom | Qt::AlignHCenter, chevron_text[i].at(0));
        painter.setPen(Qt::NoPen);  // Reset pen to default
      }
    }
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
    bool has_wide_cam = available_streams.count(VISION_STREAM_WIDE_ROAD);
    if (has_wide_cam) {
      float v_ego = sm["carState"].getCarState().getVEgo();
      float steer_angle = sm["carState"].getCarState().getSteeringAngleDeg();
      if ((v_ego < 10) || available_streams.size() == 1 || (std::fabs(steer_angle) > 45)) {
        wide_cam_requested = true;
      } else if ((v_ego > 15) && (std::fabs(steer_angle) < 30)) {
        wide_cam_requested = false;
      }
      wide_cam_requested = wide_cam_requested && sm["controlsState"].getControlsState().getExperimentalMode();
      // for replay of old routes, never go to widecam
      wide_cam_requested = wide_cam_requested && s->scene.calibration_wide_valid;
    }
    CameraWidget::setStreamType(wide_cam_requested ? VISION_STREAM_WIDE_ROAD : VISION_STREAM_ROAD);

    if (reversing && s->scene.reverse_dm_cam) {
      CameraWidget::setStreamType(VISION_STREAM_DRIVER, s->scene.reverse_dm_cam);
    }

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

  if (s->scene.world_objects_visible) {
    update_model(s, model);
    drawLaneLines(painter, s);

    if (s->scene.longitudinal_control && sm.rcv_frame("radarState") > s->scene.started_frame) {
      auto radar_state = sm["radarState"].getRadarState();
      update_leads(s, radar_state, model.getPosition());
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
  if (!hideBottomIcons && (sm.rcv_frame("driverStateV2") > s->scene.started_frame)) {
    update_dmonitoring(s, sm["driverStateV2"].getDriverStateV2(), dm_fade_state, rightHandDM);
    drawDriverState(painter, s);
  }

  drawHud(painter);

  if (left_blinker || right_blinker) {
    blinker_frame++;
    int state = blinkerPulse(blinker_frame);
    int blinker_x = splitPanelVisible ? 150 : 180;
    int blinker_y = splitPanelVisible ? 220 : 90;
    if (left_blinker) {
      drawLeftTurnSignal(painter, rect().center().x() - (blinker_x + blinker_size), blinker_y, blinker_size, state);
    }
    if (right_blinker) {
      drawRightTurnSignal(painter, rect().center().x() + blinker_x, blinker_y, blinker_size, state);
    }
  } else {
    blinker_frame = 0;
  }

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

  MessageBuilder e2e_long_msg;
  auto e2eLongStatus = e2e_long_msg.initEvent().initE2eLongStateSP();
  e2eLongStatus.setStatus(e2eStatus);
  e2e_state->send("e2eLongStateSP", e2e_long_msg);
}

void AnnotatedCameraWidget::showEvent(QShowEvent *event) {
  CameraWidget::showEvent(event);

  ui_update_params(uiState());
  prev_draw_t = millis_since_boot();
}
