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

#include "selfdrive/ui/sunnypilot/ui.h"

#include <algorithm>
#include <cassert>
#include <cmath>

#include <QtConcurrent>

#include "common/transformations/orientation.hpp"
#include "common/params.h"
#include "common/util.h"
#include "common/watchdog.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/role_model.h"
#include "system/hardware/hw.h"

#define BACKLIGHT_DT 0.05
#define BACKLIGHT_TS 10.00

// Projects a point in car to space to the corresponding point in full frame
// image space.
static bool sp_calib_frame_to_full_frame(const UIStateSP *s, float in_x, float in_y, float in_z, QPointF *out) {
  return calib_frame_to_full_frame(s, in_x, in_y, in_z, out, 1000.0f);
}

//todo: revisit, we could reuse from OG update_model. But this is an overload in this case.
void update_line_data(const UIStateSP *s, const cereal::XYZTData::Reader &line,
                      float y_off, float z_off_left, float z_off_right, QPolygonF *pvd, int max_idx, bool allow_invert=true) {
  const auto line_x = line.getX(), line_y = line.getY(), line_z = line.getZ();
  QPointF left, right;
  pvd->clear();
  for (int i = 0; i <= max_idx; i++) {
    // highly negative x positions  are drawn above the frame and cause flickering, clip to zy plane of camera
    if (line_x[i] < 0) continue;

    bool l = sp_calib_frame_to_full_frame(s, line_x[i], line_y[i] - y_off, line_z[i] + z_off_left, &left);
    bool r = sp_calib_frame_to_full_frame(s, line_x[i], line_y[i] + y_off, line_z[i] + z_off_right, &right);
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

//todo: revisit, we could reuse from OG update_model  
void sp_update_model(UIStateSP *s, const cereal::ModelDataV2::Reader &model) {
  UISceneSP &scene = s->scene;
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

static void sp_update_state(UIStateSP *s) {
  update_state(s);
  SubMaster &sm = *(s->sm);
  UISceneSP &scene = s->scene;
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

void sp_ui_update_params(UIStateSP *s) {
  ui_update_params(s);
  auto params = Params();
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

void UIStateSP::updateStatus() {
  UIState::updateStatus();
  auto params = Params();
  if (scene.started && sm->updated("controlsState")) {
    auto car_control = (*sm)["carControl"].getCarControl();
    auto car_state = (*sm)["carState"].getCarState();
    auto mads_enabled = car_state.getMadsEnabled();
    if (status != STATUS_OVERRIDE) {
      status = mads_enabled && car_control.getLongActive() ? STATUS_ENGAGED : mads_enabled ? STATUS_MADS : STATUS_DISENGAGED;
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

UIStateSP::UIStateSP(QObject *parent) : UIState(parent) {
// todo: Can we simply append to SM?
  sm = std::make_unique<SubMaster, const std::initializer_list<const char *>>({
    "modelV2", "controlsState", "liveCalibration", "radarState", "deviceState",
    "pandaStates", "carParams", "driverMonitoringState", "carState", "liveLocationKalman", "driverStateV2",
    "wideRoadCameraState", "managerState", "navInstruction", "navRoute", "clocks", "longitudinalPlanSP", "liveMapDataSP",
    "carControl", "lateralPlanSPDEPRECATED", "gpsLocation", "gpsLocationExternal", "liveParameters", "liveTorqueParameters",
    "controlsStateSP", "modelV2SP"
  });

  // update timer
  timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &UIStateSP::update);
  timer->start(1000 / UI_FREQ);
}

// Note: This method overrides completely the update method from the parent class intentionally.
void UIStateSP::update() {
  update_sockets(this);
  sp_update_state(this);
  updateStatus();

  if (sm->frame % UI_FREQ == 0) {
    watchdog_kick(nanos_since_boot());
  }
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

DeviceSP::DeviceSP(QObject *parent) : Device(parent){
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &DeviceSP::update);
}

//todo: revisit this
void DeviceSP::updateBrightness(const UIStateSP &s) {
  Device::updateBrightness(s);
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

UIStateSP *uiStateSP() {
  static UIStateSP ui_state;
  return &ui_state;
}
UIStateSP *uiState() { return uiStateSP(); }

DeviceSP *deviceSP() {
  static DeviceSP _device;
  return &_device;
}
