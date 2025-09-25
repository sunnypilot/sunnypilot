/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/ui.h"

#include "common/watchdog.h"

void UIStateSP::updateStatus() {
  UIState::updateStatus();
}

UIStateSP::UIStateSP(QObject *parent) : UIState(parent) {
  sm = std::make_unique<SubMaster>(std::vector<const char*>{
    "modelV2", "controlsState", "liveCalibration", "radarState", "deviceState",
    "pandaStates", "carParams", "driverMonitoringState", "carState", "driverStateV2",
    "wideRoadCameraState", "managerState", "selfdriveState", "longitudinalPlan",
    "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
    "carControl", "gpsLocationExternal", "gpsLocation", "liveTorqueParameters",
    "carStateSP", "liveParameters", "liveMapDataSP", "liveTracks"
  });

  // update timer
  timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &UIStateSP::update);
  timer->start(1000 / UI_FREQ);

  // Param watcher for UIScene param updates
  param_watcher = new ParamWatcher(this);
  connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    ui_update_params_sp(this);
  });
  param_watcher->addParam("DevUIInfo");
  param_watcher->addParam("StandstillTimer");
  param_watcher->addParam("VisualStyle");
  param_watcher->addParam("VisualStyleBlend");
  param_watcher->addParam("VisualStyleOverheadBlend");
  param_watcher->addParam("VisualStyleBlendThreshold");
  param_watcher->addParam("VisualRadarTracks");
  param_watcher->addParam("VisualRadarTracksDelay");
  param_watcher->addParam("VisualWideCam");
  param_watcher->addParam("VisualFPS");
}

// This method overrides completely the update method from the parent class intentionally.
void UIStateSP::update() {
  update_sockets(this);
  update_state(this);
  updateStatus();

  if (sm->frame % UI_FREQ == 0) {
    watchdog_kick(nanos_since_boot());
  }
  emit uiUpdate(*this);
}

void ui_update_params_sp(UIStateSP *s) {
  auto params = Params();
  s->scene.dev_ui_info = std::atoi(params.get("DevUIInfo").c_str());
  s->scene.standstill_timer = params.getBool("StandstillTimer");
  s->scene.speed_limit_mode = std::atoi(params.get("SpeedLimitMode").c_str());
  s->scene.road_name = params.getBool("RoadNameToggle");
  s->scene.visual_style = QString::fromStdString(params.get("VisualStyle")).toInt();
  s->scene.visual_style_blend = QString::fromStdString(params.get("VisualStyleBlend")).toInt();
  s->scene.visual_style_overhead_blend = QString::fromStdString(params.get("VisualStyleOverheadBlend")).toInt();
  s->scene.visual_style_blend_threshold = QString::fromStdString(params.get("VisualStyleBlendThreshold")).toInt();
  s->scene.visual_radar_tracks = QString::fromStdString(params.get("VisualRadarTracks")).toInt();
  s->scene.visual_radar_tracks_delay = QString::fromStdString(params.get("VisualRadarTracksDelay")).toFloat();
  s->scene.visual_wide_cam = QString::fromStdString(params.get("VisualWideCam")).toInt();
  s->scene.visual_fps = QString::fromStdString(params.get("VisualFPS")).toInt();
}

DeviceSP::DeviceSP(QObject *parent) : Device(parent) {
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &DeviceSP::update);
  QObject::connect(this, &Device::displayPowerChanged, this, &DeviceSP::handleDisplayPowerChanged);
}

UIStateSP *uiStateSP() {
  static UIStateSP ui_state;
  return &ui_state;
}

void UIStateSP::setSunnylinkRoles(const std::vector<RoleModel>& roles) {
  sunnylinkRoles = roles;
  emit sunnylinkRolesChanged(roles);
}

void UIStateSP::setSunnylinkDeviceUsers(const std::vector<UserModel>& users) {
  sunnylinkUsers = users;
  emit sunnylinkDeviceUsersChanged(users);
}

DeviceSP *deviceSP() {
  static DeviceSP _device;
  return &_device;
}

void DeviceSP::handleDisplayPowerChanged(bool on) {
  // if enabled, trigger offroad mode when device goes to sleep
  if (params.get("DeviceBootMode") == "1" && not on) {
    params.putBool("OffroadMode", true);
  }
}
