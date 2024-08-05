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

#pragma once

#include <memory>
#include <optional>
#include <string>

#include "selfdrive/ui/ui.h"

#include "cereal/messaging/messaging.h"
#include "qt/network/sunnylink/models/role_model.h"
#include "qt/network/sunnylink/models/sponsor_role_model.h"
#include "qt/network/sunnylink/models/user_model.h"
#include "system/hardware/hw.h"

const int UI_ROAD_NAME_MARGIN_X = 14;

struct FeatureStatusText {
  const QStringList dlp_list_text = { "Laneful",    "Laneless", "Auto"};
  const QStringList gac_list_text = { "Aggressive", "Moderate", "Standard", "Relaxed"};
  const QStringList slc_list_text = { "Inactive",   "Temp Off", "Adapting", "Active", "Pre Active"};
};

struct FeatureStatusColor {
  const QStringList dlp_list_color = { "#2020f8",      "#0df87a",  "#0df8f8"            };
  const QStringList gac_list_color = { "#ff4b4b",      "#fcff4b",  "#4bff66", "#6a0ac9" };
  const QStringList slc_list_color = { "#ffffff",      "#ffffff",  "#fcff4b", "#4bff66", "#fcff4b" };
};


const QColor sp_bg_colors [] = {
  [STATUS_DISENGAGED] = bg_colors[STATUS_DISENGAGED],
  [STATUS_OVERRIDE] = bg_colors[STATUS_OVERRIDE],
  [STATUS_ENGAGED] = QColor(0x00, 0xc8, 0x00, 0xf1),
  [STATUS_MADS] = QColor(0x00, 0xc8, 0xc8, 0xf1),
};
#define bg_colors sp_bg_colors // Override the bg_colors array with the sp_bg_colors array

const QColor tcs_colors [] = {
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::DISABLED)] =  QColor(0x0, 0x0, 0x0, 0xff),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::ENTERING)] = QColor(0xC9, 0x22, 0x31, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::TURNING)] = QColor(0xDA, 0x6F, 0x25, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::LEAVING)] = QColor(0x17, 0x86, 0x44, 0xf1),
};

class UIStateSP : public UIState {
  Q_OBJECT

public:
  UIStateSP(QObject* parent = 0);
  void updateStatus() override;

  void setSunnylinkRoles(const std::vector<RoleModel> &roles);
  void setSunnylinkDeviceUsers(const std::vector<UserModel> &users);

  inline std::vector<RoleModel> sunnylinkDeviceRoles() const { return sunnylinkRoles; }
  inline bool isSunnylinkAdmin() const {
    return std::any_of(sunnylinkRoles.begin(), sunnylinkRoles.end(), [](const RoleModel &role) {
      return role.roleType == RoleType::Admin;
    });
  }
  inline bool isSunnylinkSponsor() const {
    return std::any_of(sunnylinkRoles.begin(), sunnylinkRoles.end(), [](const RoleModel &role) {
      return role.roleType == RoleType::Sponsor && role.as<SponsorRoleModel>().roleTier != SponsorTier::Free;
    });
  }
  inline SponsorRoleModel sunnylinkSponsorRole() const {
    std::optional<SponsorRoleModel> sponsorRoleWithHighestTier = std::nullopt;
    for (const auto &role : sunnylinkRoles) {
      if(role.roleType != RoleType::Sponsor)
        continue;
      
      if (auto sponsorRole = role.as<SponsorRoleModel>(); !sponsorRoleWithHighestTier.has_value() || sponsorRoleWithHighestTier->roleTier < sponsorRole.roleTier) {
        sponsorRoleWithHighestTier = sponsorRole;
      }
    }
    return sponsorRoleWithHighestTier.value_or(SponsorRoleModel(RoleType::Sponsor, SponsorTier::Free));
  }
  inline SponsorTier sunnylinkSponsorTier() const {
    return sunnylinkSponsorRole().roleTier;
  }
  inline std::vector<UserModel> sunnylinkDeviceUsers() const { return sunnylinkUsers; }
  inline bool isSunnylinkPaired() const {
    return std::any_of(sunnylinkUsers.begin(), sunnylinkUsers.end(), [](const UserModel &user) {
      return user.user_id.toLower() != "unregisteredsponsor" && user.user_id.toLower() != "temporarysponsor";
    });
  }

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

  bool last_mads_enabled = false;
  bool mads_path_state = false;
  float mads_path_timestep = 4;  // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]
  float mads_path_count = 4;     // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]
};

UIStateSP *uiStateSP();
UIStateSP *uiState();

// device management class
class DeviceSP : public Device {
  Q_OBJECT

public:
  DeviceSP(QObject *parent = 0);
protected:
  void updateBrightness(const UIStateSP &s);
  void updateBrightness(const UIState &s) override { updateBrightness(dynamic_cast<const UIStateSP &>(s)); }
};

DeviceSP *deviceSP();
inline DeviceSP *device() { return deviceSP(); }

void sp_update_model(UIStateSP *s, const cereal::ModelDataV2::Reader &model);
void sp_ui_update_params(UIStateSP *s);
void update_line_data(const UIStateSP *s, const cereal::XYZTData::Reader &line,
                      float y_off, float z_off_left, float z_off_right, QPolygonF *pvd, int max_idx, bool allow_invert);
