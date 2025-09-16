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
  if (scene.started && scene.onroadScreenOffControl) {
    auto selfdriveState = (*sm)["selfdriveState"].getSelfdriveState();
    if (scene.screenTouched) {
      reset_onroad_sleep_timer(this);
    } else if (selfdriveState.getAlertSize() != cereal::SelfdriveState::AlertSize::NONE &&
                   selfdriveState.getAlertStatus() != cereal::SelfdriveState::AlertStatus::NORMAL) {
        reset_onroad_sleep_timer(this);
    } else if (scene.onroadScreenOffTimer > 0) {
      scene.onroadScreenOffTimer--;
    } else if (scene.onroadScreenOffTimer < 0) {
      reset_onroad_sleep_timer(this);
    }
  }
}

UIStateSP::UIStateSP(QObject *parent) : UIState(parent) {
  sm = std::make_unique<SubMaster>(std::vector<const char*>{
    "modelV2", "controlsState", "liveCalibration", "radarState", "deviceState",
    "pandaStates", "carParams", "driverMonitoringState", "carState", "driverStateV2",
    "wideRoadCameraState", "managerState", "selfdriveState", "longitudinalPlan",
    "modelManagerSP", "selfdriveStateSP", "longitudinalPlanSP", "backupManagerSP",
    "carControl", "gpsLocationExternal", "gpsLocation", "liveTorqueParameters",
    "carStateSP", "liveParameters"
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

  // Onroad Screen Brightness
  s->scene.onroadScreenOffBrightness = std::atoi(params.get("OnroadScreenOffBrightness").c_str());
  s->scene.onroadScreenOffControl = params.getBool("OnroadScreenOffControl");
  reset_onroad_sleep_timer(s);
}

void reset_onroad_sleep_timer(UIStateSP *s) {
  auto params = Params();
  int onroadTimer = std::atoi(params.get("OnroadScreenOffTimer").c_str());
  if (onroadTimer >= 0 and s->scene.onroadScreenOffControl) {
    s->scene.onroadScreenOffTimer = onroadTimer * UI_FREQ;
  } else {
    s->scene.onroadScreenOffTimer = -1;
  }
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
