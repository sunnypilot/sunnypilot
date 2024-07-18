#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"

#include <algorithm>
#include <cmath>

#include <QtConcurrent>

#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_role_model.h"

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

void update_model(UIStateSP *s,
                  const cereal::ModelDataV2::Reader &model) {
  UISceneSP &scene = s->scene_sp;
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

static void update_state(UIStateSP *s) {
  SubMaster &sm = *(s->sm);
  UISceneSP &scene = s->scene_sp;
  auto params = Params();

  scene.started = sm["deviceState"].getDeviceState().getStarted() && scene.ignition && !params.getBool("ForceOffroad");

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

void ui_update_params(UIStateSP *s) {
  UISceneSP &scene = s->scene_sp;
  auto params = Params();
  scene.map_on_left = params.getBool("NavSettingLeftSide");

  scene.visual_brake_lights = params.getBool("BrakeLights");
  scene.onroadScreenOff = std::atoi(params.get("OnroadScreenOff").c_str());
  scene.onroadScreenOffBrightness = std::atoi(params.get("OnroadScreenOffBrightness").c_str());
  scene.onroadScreenOffEvent = params.getBool("OnroadScreenOffEvent");
  scene.stand_still_timer = params.getBool("StandStillTimer");
  scene.show_debug_ui = params.getBool("ShowDebugUI");
  scene.hide_vego_ui = params.getBool("HideVEgoUi");
  scene.true_vego_ui = params.getBool("TrueVEgoUi");
  scene.chevron_data = std::atoi(params.get("ChevronInfo").c_str());
  scene.dev_ui_info = std::atoi(params.get("DevUIInfo").c_str());
  scene.button_auto_hide = params.getBool("ButtonAutoHide");
  scene.reverse_dm_cam = params.getBool("ReverseDmCam");
  scene.e2e_long_alert_light = params.getBool("EndToEndLongAlertLight");
  scene.e2e_long_alert_lead = params.getBool("EndToEndLongAlertLead");
  scene.e2e_long_alert_ui = params.getBool("EndToEndLongAlertUI");
  scene.map_3d_buildings = params.getBool("Map3DBuildings");
  scene.live_torque_toggle = params.getBool("LiveTorque");
  scene.torqued_override = params.getBool("TorquedOverride");
  scene.speed_limit_control_engage_type = std::atoi(params.get("SpeedLimitEngageType").c_str());
  scene.mapbox_fullscreen = params.getBool("MapboxFullScreen");
  scene.speed_limit_warning_flash = params.getBool("SpeedLimitWarningFlash");
  scene.speed_limit_warning_type = std::atoi(params.get("SpeedLimitWarningType").c_str());
  scene.speed_limit_warning_value_offset = std::atoi(params.get("SpeedLimitWarningValueOffset").c_str());
  scene.speed_limit_control_enabled = params.getBool("EnableSlc");
  scene.feature_status_toggle = params.getBool("FeatureStatus");
  scene.onroad_settings_toggle = params.getBool("OnroadSettings");

  // Handle Onroad Screen Off params
  if (scene.onroadScreenOff > 0) {
    scene.osoTimer = scene.onroadScreenOff * 60 * UI_FREQ;
  } else if (scene.onroadScreenOff == 0) {
    scene.osoTimer = 30 * UI_FREQ;
  } else if (scene.onroadScreenOff == -1) {
    scene.osoTimer = 15 * UI_FREQ;
  } else {
    scene.osoTimer = -1;
  }
}

void UIStateSP::updateStatus() {
  auto params = Params();
  if (scene_sp.started && sm->updated("controlsState")) {
    auto controls_state = (*sm)["controlsState"].getControlsState();
    auto car_control = (*sm)["carControl"].getCarControl();
    auto car_state = (*sm)["carState"].getCarState();
    auto mads_enabled = car_state.getMadsEnabled();
    auto state = controls_state.getState();
    if (state == cereal::ControlsState::OpenpilotState::PRE_ENABLED || state == cereal::ControlsState::OpenpilotState::OVERRIDING) {
      status_sp = STATUS_OVERRIDE_SP;
    } else {
      status_sp = car_state.getMadsEnabled() ? car_control.getLongActive() ? STATUS_ENGAGED_SP : STATUS_MADS_SP : STATUS_DISENGAGED_SP;
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
    scene_sp.mads_path_scale = mads_path_count * (1 / mads_path_timestep);
  }

  if (scene_sp.started) {
    // Auto hide UI button state machine
    {
      if (scene_sp.button_auto_hide) {
        if (scene_sp.touch_to_wake) {
          scene_sp.sleep_btn = 30 * UI_FREQ;
        } else if (scene_sp.sleep_btn > 0) {
          scene_sp.sleep_btn--;
        } else if (scene_sp.sleep_btn == -1) {
          scene_sp.sleep_btn = 30 * UI_FREQ;
        }
        // Check if the sleep button should be fading in
        if (scene_sp.sleep_btn_fading_in) {
          // Increase the opacity of the sleep button by a small amount
          if (scene_sp.sleep_btn_opacity < 20) {
            scene_sp.sleep_btn_opacity+= 10;
          }
          if (scene_sp.sleep_btn_opacity >= 20) {
            // If the opacity has reached its maximum value, stop fading in
            scene_sp.sleep_btn_fading_in = false;
            scene_sp.sleep_btn_opacity = 20;
          }
        } else if (scene_sp.sleep_btn == 0) {
          // Fade out the sleep button as before
          if (scene_sp.sleep_btn_opacity > 0) {
            scene_sp.sleep_btn_opacity-= 2;
          }
        } else {
          // Set the opacity of the sleep button to its maximum value
          scene_sp.sleep_btn_opacity = 20;
        }
      } else {
        scene_sp.sleep_btn_opacity = 20;
      }
    }

    // Onroad Screen Off Brightness + Timer + Global Brightness
    {
      if (scene_sp.onroadScreenOff != -2 && scene_sp.touched2) {
        scene_sp.sleep_time = scene_sp.osoTimer;
      } else if (scene_sp.onroadScreenOff != -2 &&
                 ((scene_sp.controlsState.getAlertSize() != cereal::ControlsState::AlertSize::NONE) &&
                  ((scene_sp.controlsState.getAlertStatus() == cereal::ControlsState::AlertStatus::NORMAL && scene_sp.onroadScreenOffEvent) ||
                   (scene_sp.controlsState.getAlertStatus() != cereal::ControlsState::AlertStatus::NORMAL)))) {
        scene_sp.sleep_time = scene_sp.osoTimer;
      } else if (scene_sp.sleep_time > 0 && scene_sp.onroadScreenOff != -2) {
        scene_sp.sleep_time--;
      } else if (scene_sp.sleep_time == -1 && scene_sp.onroadScreenOff != -2) {
        scene_sp.sleep_time = scene_sp.osoTimer;
      }
    }
  }

  if (sm->frame % UI_FREQ == 0) { // Update every 1 Hz
    scene_sp.sidebar_temp_options = std::atoi(params.get("SidebarTemperatureOptions").c_str());
  }

  scene_sp.brightness = std::atoi(params.get("BrightnessControl").c_str());
}

UIStateSP::UIStateSP(QObject *parent) : UIState(parent) {
}

void UIStateSP::update() {
  update_state(this);
  updateStatus();
  UIState::update();
  emit uiUpdate(*this);
}

void UIStateSP::setSunnylinkRoles(const std::vector<RoleModel>& roles) {
  sunnylinkRoles = roles;
  emit sunnylinkRolesChanged(roles);
}

void UIStateSP::setSunnylinkDeviceUsers(const std::vector<UserModel>& users) {
  sunnylinkUsers = users;
  emit sunnylinkDeviceUsersChanged(users);
}

DeviceSP::DeviceSP(QObject *parent) : Device(parent) {
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &DeviceSP::update);
}

void DeviceSP::update(const UIStateSP &s) {
  updateBrightness(s);
  updateWakefulness(s);
}

void DeviceSP::updateBrightness(const UIStateSP &s) {
  UISceneSP scene = s.scene_sp;
  float clipped_brightness = offroad_brightness;
  if (scene.started && scene.light_sensor > 0) {
    clipped_brightness = scene.light_sensor;

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
  } else if (scene.started && scene.sleep_time == 0 && scene.onroadScreenOff != -2) {
    brightness = scene.onroadScreenOffBrightness * 0.01 * brightness;
  } else if (scene.brightness) {
    brightness = scene.brightness * 0.99;
  }

  if (brightness != last_brightness) {
    if (!brightness_future.isRunning()) {
      brightness_future = QtConcurrent::run(Hardware::set_brightness, brightness);
      last_brightness = brightness;
    }
  }
}

UIStateSP *uiStateSP() {
  static UIStateSP ui_state_sp;
  return &ui_state_sp;
}

DeviceSP *deviceSP() {
  static DeviceSP _device_sp;
  return &_device_sp;
}
