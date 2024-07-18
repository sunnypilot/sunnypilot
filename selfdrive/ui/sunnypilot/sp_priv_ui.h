#pragma once

#include "selfdrive/ui/ui.h"

#include <optional>
#include <vector>

#include <QColor>

#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_role_model.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_sponsor_role_model.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_user_model.h"

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

const float DRIVING_PATH_WIDE = 0.9;
const float DRIVING_PATH_NARROW = 0.25;

typedef enum UIStatusSP {
  STATUS_DISENGAGED_SP = STATUS_DISENGAGED,
  STATUS_OVERRIDE_SP = STATUS_OVERRIDE,
  STATUS_ENGAGED_SP = STATUS_ENGAGED,
  STATUS_MADS_SP,
} UIStatusSP;

const QColor bg_colors_sp [] = {
  [STATUS_DISENGAGED_SP] = QColor(0x17, 0x33, 0x49, 0xc8),
  [STATUS_OVERRIDE_SP] = QColor(0x91, 0x9b, 0x95, 0xf1),
  [STATUS_ENGAGED_SP] = QColor(0x00, 0xc8, 0x00, 0xf1),
  [STATUS_MADS_SP] = QColor(0x00, 0xc8, 0xc8, 0xf1),
};

const QColor tcs_colors [] = {
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::DISABLED)] =  QColor(0x0, 0x0, 0x0, 0xff),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::ENTERING)] = QColor(0xC9, 0x22, 0x31, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::TURNING)] = QColor(0xDA, 0x6F, 0x25, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::LEAVING)] = QColor(0x17, 0x86, 0x44, 0xf1),
};

typedef struct UISceneSP : UIScene {
  cereal::ControlsState::Reader controlsState;

  // Debug UI
  bool show_debug_ui;

  // Speed limit control
  bool speed_limit_control_enabled;
  int speed_limit_control_policy;
  double last_speed_limit_sign_tap;

  // modelV2
  QPolygonF track_edge_vertices;
  QPolygonF lane_barrier_vertices[2];

  bool navigate_on_openpilot_deprecated = false;
  cereal::AccelerationPersonality accel_personality;

  bool map_on_left;

  int dynamic_lane_profile;
  bool dynamic_lane_profile_status = true;

  bool visual_brake_lights;

  int onroadScreenOff, osoTimer, brightness, onroadScreenOffBrightness, awake;
  bool onroadScreenOffEvent;
  int sleep_time = -1;
  bool touched2 = false;

  bool stand_still_timer;

  bool hide_vego_ui, true_vego_ui;

  int chevron_data;

  bool gac;
  int longitudinal_personality;
  int longitudinal_accel_personality;

  bool map_visible;
  int dev_ui_info;
  bool live_torque_toggle;

  bool touch_to_wake = false;
  int sleep_btn = -1;
  bool sleep_btn_fading_in = false;
  int sleep_btn_opacity = 20;
  bool button_auto_hide;

  bool reverse_dm_cam;

  bool e2e_long_alert_light, e2e_long_alert_lead, e2e_long_alert_ui;
  float e2eX[13] = {0};

  int sidebar_temp_options;

  float mads_path_scale = DRIVING_PATH_WIDE - DRIVING_PATH_NARROW;
  float mads_path_range = DRIVING_PATH_WIDE - DRIVING_PATH_NARROW;  // 0.9 - 0.25 = 0.65

  bool onroad_settings_visible;

  bool map_3d_buildings;

  bool torqued_override;

  bool dynamic_experimental_control;

  int speed_limit_control_engage_type;

  bool mapbox_fullscreen;

  bool speed_limit_warning_flash;
  int speed_limit_warning_type;
  int speed_limit_warning_value_offset;

  bool custom_driving_model_valid;
  cereal::ModelGeneration driving_model_generation;
  uint32_t driving_model_capabilities;

  bool feature_status_toggle;
  bool onroad_settings_toggle;

  bool dynamic_personality;
} UISceneSP;

class UIStateSP : public UIState {
  Q_OBJECT

public:
  UIStateSP(QObject* parent = nullptr);
  void updateStatus();
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
      if (role.roleType != RoleType::Sponsor)
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

  UIStatusSP status_sp;
  UISceneSP scene_sp = {};

signals:
  void uiUpdate(const UIStateSP &s);
  void sunnylinkRoleChanged(bool subscriber);
  void sunnylinkRolesChanged(std::vector<RoleModel> roles);
  void sunnylinkDeviceUsersChanged(std::vector<UserModel> users);

private slots:
  void update();

private:
  std::vector<RoleModel> sunnylinkRoles = {};
  std::vector<UserModel> sunnylinkUsers = {};

  bool last_mads_enabled = false;
  bool mads_path_state = false;
  float mads_path_timestep = 4;  // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]
  float mads_path_count = 4;     // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]

public slots:
  void update(const UIStateSP &s);
};

UIStateSP *uiStateSP();

class DeviceSP : public Device {
  Q_OBJECT

public:
  DeviceSP(QObject *parent = nullptr);
  void updateBrightness(const UIStateSP &s);

protected:
  void updateBrightness(const UIState &s);

public slots:
  void update(const UIStateSP &s);
};

DeviceSP *deviceSP();

void update_model(UIState *s,
                  const cereal::ModelDataV2::Reader &model);
void update_line_data(const UIState *s, const cereal::XYZTData::Reader &line,
                      float y_off, float z_off_left, float z_off_right, QPolygonF *pvd, int max_idx, bool allow_invert);
