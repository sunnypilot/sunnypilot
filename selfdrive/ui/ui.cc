#include "selfdrive/ui/ui.h"

#include <algorithm>
#include <cassert>
#include <cmath>

#include <QtConcurrent>

#include "common/transformations/orientation.hpp"
#include "common/params.h"
#include "common/swaglog.h"
#include "common/util.h"
#include "common/watchdog.h"
#include "qt/network/sunnylink/models/role_model.h"
#include "system/hardware/hw.h"

#define BACKLIGHT_DT 0.05
#define BACKLIGHT_TS 10.00

// Projects a point in car to space to the corresponding point in full frame
// image space.
static bool calib_frame_to_full_frame(const UIState *s, float in_x, float in_y, float in_z, QPointF *out) {
  const float margin = 1000.0f;
  const QRectF clip_region{-margin, -margin, s->fb_w + 2 * margin, s->fb_h + 2 * margin};

  const vec3 pt = (vec3){{in_x, in_y, in_z}};
  const vec3 Ep = matvecmul3(s->scene.wide_cam ? s->scene.view_from_wide_calib : s->scene.view_from_calib, pt);
  const vec3 KEp = matvecmul3(s->scene.wide_cam ? ECAM_INTRINSIC_MATRIX : FCAM_INTRINSIC_MATRIX, Ep);

  // Project.
  QPointF point = s->car_space_transform.map(QPointF{KEp.v[0] / KEp.v[2], KEp.v[1] / KEp.v[2]});
  if (clip_region.contains(point)) {
    *out = point;
    return true;
  }
  return false;
}

int get_path_length_idx(const cereal::XYZTData::Reader &line, const float path_height) {
  const auto line_x = line.getX();
  int max_idx = 0;
  for (int i = 1; i < line_x.size() && line_x[i] <= path_height; ++i) {
    max_idx = i;
  }
  return max_idx;
}

void update_leads(UIState *s, const cereal::RadarState::Reader &radar_state, const cereal::XYZTData::Reader &line) {
  for (int i = 0; i < 2; ++i) {
    auto lead_data = (i == 0) ? radar_state.getLeadOne() : radar_state.getLeadTwo();
    if (lead_data.getStatus()) {
      float z = line.getZ()[get_path_length_idx(line, lead_data.getDRel())];
      calib_frame_to_full_frame(s, lead_data.getDRel(), -lead_data.getYRel(), z + 1.22, &s->scene.lead_vertices[i]);
    }
  }
}

void update_line_data(const UIState *s, const cereal::XYZTData::Reader &line,
                      float y_off, float z_off_left, float z_off_right, QPolygonF *pvd, int max_idx, bool allow_invert=true) {
  const auto line_x = line.getX(), line_y = line.getY(), line_z = line.getZ();
  QPointF left, right;
  pvd->clear();
  for (int i = 0; i <= max_idx; i++) {
    // highly negative x positions  are drawn above the frame and cause flickering, clip to zy plane of camera
    if (line_x[i] < 0) continue;

    bool l = calib_frame_to_full_frame(s, line_x[i], line_y[i] - y_off, line_z[i] + z_off_left, &left);
    bool r = calib_frame_to_full_frame(s, line_x[i], line_y[i] + y_off, line_z[i] + z_off_right, &right);
    if (l && r) {
      // For wider lines the drawn polygon will "invert" when going over a hill and cause artifacts
      if (!allow_invert && pvd->size() && left.y() > pvd->back().y()) {
        continue;
      }
      pvd->push_back(left);
      pvd->push_front(right);
    }
  }
}

void update_model(UIState *s,
                  const cereal::ModelDataV2::Reader &model) {
  UIScene &scene = s->scene;
  auto model_position = model.getPosition();
  float max_distance = std::clamp(*(model_position.getX().end() - 1),
                                  MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE);

  // update lane lines
  const auto lane_lines = model.getLaneLines();
  const auto lane_line_probs = model.getLaneLineProbs();
  int max_idx = get_path_length_idx(lane_lines[0], max_distance);
  for (int i = 0; i < std::size(scene.lane_line_vertices); i++) {
    scene.lane_line_probs[i] = lane_line_probs[i];
    update_line_data(s, lane_lines[i], 0.025 * scene.lane_line_probs[i], 0, 0, &scene.lane_line_vertices[i], max_idx);
  }

  // lane barriers for blind spot
  int max_distance_barrier =  40;
  int max_idx_barrier = std::min(max_idx, get_path_length_idx(lane_lines[0], max_distance_barrier));
  update_line_data(s, lane_lines[1], 0, -0.05, -0.6, &scene.lane_barrier_vertices[0], max_idx_barrier, false);
  update_line_data(s, lane_lines[2], 0, -0.05, -0.6, &scene.lane_barrier_vertices[1], max_idx_barrier, false);

  // update road edges
  const auto road_edges = model.getRoadEdges();
  const auto road_edge_stds = model.getRoadEdgeStds();
  for (int i = 0; i < std::size(scene.road_edge_vertices); i++) {
    scene.road_edge_stds[i] = road_edge_stds[i];
    update_line_data(s, road_edges[i], 0.025, 0, 0, &scene.road_edge_vertices[i], max_idx);
  }

  // update path
  auto lead_one = (*s->sm)["radarState"].getRadarState().getLeadOne();
  if (lead_one.getStatus()) {
    const float lead_d = lead_one.getDRel() * 2.;
    max_distance = std::clamp((float)(lead_d - fmin(lead_d * 0.35, 10.)), 0.0f, max_distance);
  }
  max_idx = get_path_length_idx(model_position, max_distance);
  update_line_data(s, model_position, 0.9 - scene.mads_path_range * scene.mads_path_scale, 1.22, 1.22, &scene.track_vertices, max_idx, false);
  update_line_data(s, model_position, 1.0 - scene.mads_path_range * scene.mads_path_scale - 0.1 * scene.mads_path_scale, 1.22, 1.22, &scene.track_edge_vertices, max_idx, false);
}

void update_dmonitoring(UIState *s, const cereal::DriverStateV2::Reader &driverstate, float dm_fade_state, bool is_rhd) {
  UIScene &scene = s->scene;
  const auto driver_orient = is_rhd ? driverstate.getRightDriverData().getFaceOrientation() : driverstate.getLeftDriverData().getFaceOrientation();
  for (int i = 0; i < std::size(scene.driver_pose_vals); i++) {
    float v_this = (i == 0 ? (driver_orient[i] < 0 ? 0.7 : 0.9) : 0.4) * driver_orient[i];
    scene.driver_pose_diff[i] = fabs(scene.driver_pose_vals[i] - v_this);
    scene.driver_pose_vals[i] = 0.8 * v_this + (1 - 0.8) * scene.driver_pose_vals[i];
    scene.driver_pose_sins[i] = sinf(scene.driver_pose_vals[i]*(1.0-dm_fade_state));
    scene.driver_pose_coss[i] = cosf(scene.driver_pose_vals[i]*(1.0-dm_fade_state));
  }

  auto [sin_y, sin_x, sin_z] = scene.driver_pose_sins;
  auto [cos_y, cos_x, cos_z] = scene.driver_pose_coss;

  const mat3 r_xyz = (mat3){{
    cos_x * cos_z,
    cos_x * sin_z,
    -sin_x,

    -sin_y * sin_x * cos_z - cos_y * sin_z,
    -sin_y * sin_x * sin_z + cos_y * cos_z,
    -sin_y * cos_x,

    cos_y * sin_x * cos_z - sin_y * sin_z,
    cos_y * sin_x * sin_z + sin_y * cos_z,
    cos_y * cos_x,
  }};

  // transform vertices
  for (int kpi = 0; kpi < std::size(default_face_kpts_3d); kpi++) {
    vec3 kpt_this = matvecmul3(r_xyz, default_face_kpts_3d[kpi]);
    scene.face_kpts_draw[kpi] = (vec3){{kpt_this.v[0], kpt_this.v[1], (float)(kpt_this.v[2] * (1.0-dm_fade_state) + 8 * dm_fade_state)}};
  }
}

static void update_sockets(UIState *s) {
  s->sm->update(0);
}

static void update_state(UIState *s) {
  SubMaster &sm = *(s->sm);
  UIScene &scene = s->scene;
  auto params = Params();

  if (sm.updated("liveCalibration")) {
    auto live_calib = sm["liveCalibration"].getLiveCalibration();
    auto rpy_list = live_calib.getRpyCalib();
    auto wfde_list = live_calib.getWideFromDeviceEuler();
    Eigen::Vector3d rpy;
    Eigen::Vector3d wfde;
    if (rpy_list.size() == 3) rpy << rpy_list[0], rpy_list[1], rpy_list[2];
    if (wfde_list.size() == 3) wfde << wfde_list[0], wfde_list[1], wfde_list[2];
    Eigen::Matrix3d device_from_calib = euler2rot(rpy);
    Eigen::Matrix3d wide_from_device = euler2rot(wfde);
    Eigen::Matrix3d view_from_device;
    view_from_device << 0, 1, 0,
                        0, 0, 1,
                        1, 0, 0;
    Eigen::Matrix3d view_from_calib = view_from_device * device_from_calib;
    Eigen::Matrix3d view_from_wide_calib = view_from_device * wide_from_device * device_from_calib;
    for (int i = 0; i < 3; i++) {
      for (int j = 0; j < 3; j++) {
        scene.view_from_calib.v[i*3 + j] = view_from_calib(i, j);
        scene.view_from_wide_calib.v[i*3 + j] = view_from_wide_calib(i, j);
      }
    }
    scene.calibration_valid = live_calib.getCalStatus() == cereal::LiveCalibrationData::Status::CALIBRATED;
    scene.calibration_wide_valid = wfde_list.size() == 3;
  }
  if (sm.updated("pandaStates")) {
    auto pandaStates = sm["pandaStates"].getPandaStates();
    if (pandaStates.size() > 0) {
      scene.pandaType = pandaStates[0].getPandaType();

      if (scene.pandaType != cereal::PandaState::PandaType::UNKNOWN) {
        scene.ignition = false;
        for (const auto& pandaState : pandaStates) {
          scene.ignition |= pandaState.getIgnitionLine() || pandaState.getIgnitionCan();
        }
      }
    }
  } else if ((s->sm->frame - s->sm->rcv_frame("pandaStates")) > 5*UI_FREQ) {
    scene.pandaType = cereal::PandaState::PandaType::UNKNOWN;
  }
  if (sm.updated("carParams")) {
    scene.longitudinal_control = sm["carParams"].getCarParams().getOpenpilotLongitudinalControl();
  }
  if (sm.updated("wideRoadCameraState")) {
    auto cam_state = sm["wideRoadCameraState"].getWideRoadCameraState();
    float scale = (cam_state.getSensor() == cereal::FrameData::ImageSensor::AR0231) ? 6.0f : 1.0f;
    scene.light_sensor = std::max(100.0f - scale * cam_state.getExposureValPercent(), 0.0f);
  } else if (!sm.allAliveAndValid({"wideRoadCameraState"})) {
    scene.light_sensor = -1;
  }
  scene.started = sm["deviceState"].getDeviceState().getStarted() && scene.ignition && !params.getBool("ForceOffroad");

  scene.world_objects_visible = scene.world_objects_visible ||
                                (scene.started &&
                                 sm.rcv_frame("liveCalibration") > scene.started_frame &&
                                 sm.rcv_frame("modelV2") > scene.started_frame);
  // TODO: SP - Set this dynamically on init with manual toggle or driving model selection
  if (sm.updated("lateralPlanSPDEPRECATED")) {
    scene.dynamic_lane_profile_status = sm["lateralPlanSPDEPRECATED"].getLateralPlanSPDEPRECATED().getDynamicLaneProfileStatus();
  }
  if (sm.updated("controlsState")) {
    scene.controlsState = sm["controlsState"].getControlsState();
  }
  if (sm.updated("longitudinalPlanSP")) {
    for (int i = 0; i < std::size(scene.e2eX); i++) {
      scene.e2eX[i] = sm["longitudinalPlanSP"].getLongitudinalPlanSP().getE2eX()[i];
    }
  }
  if (sm.updated("modelV2SP")) {
    auto model_v2_sp = sm["modelV2SP"].getModelV2SP();
    scene.custom_driving_model_valid = model_v2_sp.getCustomModel();
    scene.driving_model_generation = model_v2_sp.getModelGeneration();
    scene.driving_model_capabilities = model_v2_sp.getModelCapabilities();
  }
}

void ui_update_params(UIState *s) {
  auto params = Params();
  s->scene.is_metric = params.getBool("IsMetric");
  s->scene.map_on_left = params.getBool("NavSettingLeftSide");

  s->scene.visual_brake_lights = params.getBool("BrakeLights");
  s->scene.onroadScreenOff = std::atoi(params.get("OnroadScreenOff").c_str());
  s->scene.onroadScreenOffBrightness = std::atoi(params.get("OnroadScreenOffBrightness").c_str());
  s->scene.onroadScreenOffEvent = params.getBool("OnroadScreenOffEvent");
  s->scene.stand_still_timer = params.getBool("StandStillTimer");
  s->scene.show_debug_ui = params.getBool("ShowDebugUI");
  s->scene.hide_vego_ui = params.getBool("HideVEgoUi");
  s->scene.true_vego_ui = params.getBool("TrueVEgoUi");
  s->scene.chevron_data = std::atoi(params.get("ChevronInfo").c_str());
  s->scene.dev_ui_info = std::atoi(params.get("DevUIInfo").c_str());
  s->scene.button_auto_hide = params.getBool("ButtonAutoHide");
  s->scene.reverse_dm_cam = params.getBool("ReverseDmCam");
  s->scene.e2e_long_alert_light = params.getBool("EndToEndLongAlertLight");
  s->scene.e2e_long_alert_lead = params.getBool("EndToEndLongAlertLead");
  s->scene.e2e_long_alert_ui = params.getBool("EndToEndLongAlertUI");
  s->scene.map_3d_buildings = params.getBool("Map3DBuildings");
  s->scene.live_torque_toggle = params.getBool("LiveTorque");
  s->scene.torqued_override = params.getBool("TorquedOverride");
  s->scene.speed_limit_control_engage_type = std::atoi(params.get("SpeedLimitEngageType").c_str());
  s->scene.mapbox_fullscreen = params.getBool("MapboxFullScreen");
  s->scene.speed_limit_warning_flash = params.getBool("SpeedLimitWarningFlash");
  s->scene.speed_limit_warning_type = std::atoi(params.get("SpeedLimitWarningType").c_str());
  s->scene.speed_limit_warning_value_offset = std::atoi(params.get("SpeedLimitWarningValueOffset").c_str());
  s->scene.speed_limit_control_enabled = params.getBool("EnableSlc");
  s->scene.feature_status_toggle = params.getBool("FeatureStatus");
  s->scene.onroad_settings_toggle = params.getBool("OnroadSettings");

  // Handle Onroad Screen Off params
  if (s->scene.onroadScreenOff > 0) {
    s->scene.osoTimer = s->scene.onroadScreenOff * 60 * UI_FREQ;
  } else if (s->scene.onroadScreenOff == 0) {
    s->scene.osoTimer = 30 * UI_FREQ;
  } else if (s->scene.onroadScreenOff == -1) {
    s->scene.osoTimer = 15 * UI_FREQ;
  } else {
    s->scene.osoTimer = -1;
  }
}

void UIState::updateStatus() {
  auto params = Params();
  if (scene.started && sm->updated("controlsState")) {
    auto controls_state = (*sm)["controlsState"].getControlsState();
    auto car_control = (*sm)["carControl"].getCarControl();
    auto car_state = (*sm)["carState"].getCarState();
    auto mads_enabled = car_state.getMadsEnabled();
    auto state = controls_state.getState();
    if (state == cereal::ControlsState::OpenpilotState::PRE_ENABLED || state == cereal::ControlsState::OpenpilotState::OVERRIDING) {
      status = STATUS_OVERRIDE;
    } else {
      status = car_state.getMadsEnabled() ? car_control.getLongActive() ? STATUS_ENGAGED : STATUS_MADS : STATUS_DISENGAGED;
    }

    if (mads_enabled != last_mads_enabled) {
      mads_path_state = true;
    }
    last_mads_enabled = mads_enabled;
    if (mads_path_state) {
      if (mads_enabled) {
        mads_path_count = fmax(mads_path_count - 1, 0);
        if (mads_path_count == 0) {
          mads_path_state = false;
        }
      } else {
        mads_path_count = fmin(mads_path_count + 1, mads_path_timestep);
        if (mads_path_count == mads_path_timestep) {
          mads_path_state = false;
        }
      }
    }
    scene.mads_path_scale = mads_path_count * (1 / mads_path_timestep);
  }

  // Handle onroad/offroad transition
  if (scene.started != started_prev || sm->frame == 1) {
    if (scene.started) {
      status = STATUS_DISENGAGED;
      scene.started_frame = sm->frame;
    }
    started_prev = scene.started;
    scene.world_objects_visible = false;
    emit offroadTransition(!scene.started);
  }

  if (scene.started) {
    // Auto hide UI button state machine
    {
      if (scene.button_auto_hide) {
        if (scene.touch_to_wake) {
          scene.sleep_btn = 30 * UI_FREQ;
        } else if (scene.sleep_btn > 0) {
          scene.sleep_btn--;
        } else if (scene.sleep_btn == -1) {
          scene.sleep_btn = 30 * UI_FREQ;
        }
        // Check if the sleep button should be fading in
        if (scene.sleep_btn_fading_in) {
          // Increase the opacity of the sleep button by a small amount
          if (scene.sleep_btn_opacity < 20) {
            scene.sleep_btn_opacity+= 10;
          }
          if (scene.sleep_btn_opacity >= 20) {
            // If the opacity has reached its maximum value, stop fading in
            scene.sleep_btn_fading_in = false;
            scene.sleep_btn_opacity = 20;
          }
        } else if (scene.sleep_btn == 0) {
          // Fade out the sleep button as before
          if (scene.sleep_btn_opacity > 0) {
            scene.sleep_btn_opacity-= 2;
          }
        } else {
          // Set the opacity of the sleep button to its maximum value
          scene.sleep_btn_opacity = 20;
        }
      } else {
        scene.sleep_btn_opacity = 20;
      }
    }

    // Onroad Screen Off Brightness + Timer + Global Brightness
    {
      if (scene.onroadScreenOff != -2 && scene.touched2) {
        scene.sleep_time = scene.osoTimer;
      } else if (scene.onroadScreenOff != -2 &&
                 ((scene.controlsState.getAlertSize() != cereal::ControlsState::AlertSize::NONE) &&
                  ((scene.controlsState.getAlertStatus() == cereal::ControlsState::AlertStatus::NORMAL && scene.onroadScreenOffEvent) ||
                   (scene.controlsState.getAlertStatus() != cereal::ControlsState::AlertStatus::NORMAL)))) {
        scene.sleep_time = scene.osoTimer;
      } else if (scene.sleep_time > 0 && scene.onroadScreenOff != -2) {
        scene.sleep_time--;
      } else if (scene.sleep_time == -1 && scene.onroadScreenOff != -2) {
        scene.sleep_time = scene.osoTimer;
      }
    }
  }

  if (sm->frame % UI_FREQ == 0) { // Update every 1 Hz
    scene.sidebar_temp_options = std::atoi(params.get("SidebarTemperatureOptions").c_str());
  }

  scene.brightness = std::atoi(params.get("BrightnessControl").c_str());
}

UIState::UIState(QObject *parent) : QObject(parent) {
  sm = std::make_unique<SubMaster, const std::initializer_list<const char *>>({
    "modelV2", "controlsState", "liveCalibration", "radarState", "deviceState",
    "pandaStates", "carParams", "driverMonitoringState", "carState", "liveLocationKalman", "driverStateV2",
    "wideRoadCameraState", "managerState", "navInstruction", "navRoute", "clocks", "longitudinalPlanSP", "liveMapDataSP",
    "carControl", "lateralPlanSPDEPRECATED", "gpsLocation", "gpsLocationExternal", "liveParameters", "liveTorqueParameters",
    "controlsStateSP", "modelV2SP"
  });

  Params params;
  language = QString::fromStdString(params.get("LanguageSetting"));
  auto prime_value = params.get("PrimeType");
  if (!prime_value.empty()) {
    prime_type = static_cast<PrimeType>(std::atoi(prime_value.c_str()));
  }

  // update timer
  timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &UIState::update);
  timer->start(1000 / UI_FREQ);
}

void UIState::update() {
  update_sockets(this);
  update_state(this);
  updateStatus();

  if (sm->frame % UI_FREQ == 0) {
    watchdog_kick(nanos_since_boot());
  }
  emit uiUpdate(*this);
}

void UIState::setPrimeType(PrimeType type) {
  if (type != prime_type) {
    bool prev_prime = hasPrime();

    prime_type = type;
    Params().put("PrimeType", std::to_string(prime_type));
    emit primeTypeChanged(prime_type);

    bool prime = hasPrime();
    if (prev_prime != prime) {
      emit primeChanged(prime);
    }
  }
}

void UIState::setSunnylinkRoles(const std::vector<RoleModel>& roles) {
  sunnylinkRoles = roles;
  emit sunnylinkRolesChanged(roles);
}

void UIState::setSunnylinkDeviceUsers(const std::vector<UserModel>& users) {
  sunnylinkUsers = users;
  emit sunnylinkDeviceUsersChanged(users);
}

Device::Device(QObject *parent) : brightness_filter(BACKLIGHT_OFFROAD, BACKLIGHT_TS, BACKLIGHT_DT), QObject(parent) {
  setAwake(true);
  resetInteractiveTimeout();

  QObject::connect(uiState(), &UIState::uiUpdate, this, &Device::update);
}

void Device::update(const UIState &s) {
  updateBrightness(s);
  updateWakefulness(s);
}

void Device::setAwake(bool on) {
  if (on != awake) {
    awake = on;
    Hardware::set_display_power(awake);
    LOGD("setting display power %d", awake);
    emit displayPowerChanged(awake);
  }
}

void Device::resetInteractiveTimeout(int timeout) {
  if (timeout == -1) {
    timeout = (ignition_on ? 10 : 30);
  }
  interactive_timeout = timeout * UI_FREQ;
}

void Device::updateBrightness(const UIState &s) {
  float clipped_brightness = offroad_brightness;
  if (s.scene.started && s.scene.light_sensor > 0) {
    clipped_brightness = s.scene.light_sensor;

    // CIE 1931 - https://www.photonstophotos.net/GeneralTopics/Exposure/Psychometric_Lightness_and_Gamma.htm
    if (clipped_brightness <= 8) {
      clipped_brightness = (clipped_brightness / 903.3);
    } else {
      clipped_brightness = std::pow((clipped_brightness + 16.0) / 116.0, 3.0);
    }

    // Scale back to 10% to 100%
    clipped_brightness = std::clamp(100.0f * clipped_brightness, 10.0f, 100.0f);
  }

  int brightness = brightness_filter.update(clipped_brightness);
  if (!awake) {
    brightness = 0;
  } else if (s.scene.started && s.scene.sleep_time == 0 && s.scene.onroadScreenOff != -2) {
    brightness = s.scene.onroadScreenOffBrightness * 0.01 * brightness;
  } else if (s.scene.brightness) {
    brightness = s.scene.brightness * 0.99;
  }

  if (brightness != last_brightness) {
    if (!brightness_future.isRunning()) {
      brightness_future = QtConcurrent::run(Hardware::set_brightness, brightness);
      last_brightness = brightness;
    }
  }
}

void Device::updateWakefulness(const UIState &s) {
  bool ignition_just_turned_off = !s.scene.ignition && ignition_on;
  ignition_on = s.scene.ignition;

  if (ignition_just_turned_off) {
    resetInteractiveTimeout();
  } else if (interactive_timeout > 0 && --interactive_timeout == 0) {
    emit interactiveTimeout();
  }

  setAwake(s.scene.ignition || interactive_timeout > 0);
}

UIState *uiState() {
  static UIState ui_state;
  return &ui_state;
}

Device *device() {
  static Device _device;
  return &_device;
}
