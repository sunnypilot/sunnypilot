/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/user_model.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/role_model.h"
#include "selfdrive/ui/ui.h"

class UIStateSP : public UIState {
  Q_OBJECT

public:
  UIStateSP(QObject *parent = 0);
  void updateStatus() override;
  void setSunnylinkRoles(const std::vector<RoleModel> &roles);
  void setSunnylinkDeviceUsers(const std::vector<UserModel> &users);

  signals:
  void sunnylinkRoleChanged(bool subscriber);
  void sunnylinkRolesChanged(std::vector<RoleModel> roles);
  void sunnylinkDeviceUsersChanged(std::vector<UserModel> users);
  void uiUpdate(const UIStateSP &s);

private slots:
  void update() override;  

private:
  std::vector<RoleModel> sunnylinkRoles = {};
  std::vector<UserModel> sunnylinkUsers = {};
};

UIStateSP *uiStateSP();
inline UIStateSP *uiState() { return uiStateSP(); };

// device management class
class DeviceSP : public Device {
  Q_OBJECT

public:
  DeviceSP(QObject *parent = 0);
};

DeviceSP *deviceSP();
inline DeviceSP *device() { return deviceSP(); }
