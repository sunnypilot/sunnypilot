#pragma once

#include <memory>
#include <optional>
#include <string>
#include <vector>

#include <QObject>
#include <QTimer>
#include <QColor>
#include <QFuture>
#include <QPolygonF>
#include <QTransform>

#include "cereal/messaging/messaging.h"
#include "common/mat.h"
#include "common/params.h"
#include "common/timing.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_role_model.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_sponsor_role_model.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/models/sp_priv_user_model.h"
#include "system/hardware/hw.h"

const int UI_BORDER_SIZE = 30;
const int UI_HEADER_HEIGHT = 420;

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

const int UI_FREQ = 20; // Hz
const int BACKLIGHT_OFFROAD = 50;

const float MIN_DRAW_DISTANCE = 10.0;
const float MAX_DRAW_DISTANCE = 100.0;
constexpr mat3 DEFAULT_CALIBRATION = {{ 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0 }};
constexpr mat3 FCAM_INTRINSIC_MATRIX = (mat3){{2648.0, 0.0, 1928.0 / 2,
                                           0.0, 2648.0, 1208.0 / 2,
                                           0.0, 0.0, 1.0}};
// tici ecam focal probably wrong? magnification is not consistent across frame
// Need to retrain model before this can be changed
constexpr mat3 ECAM_INTRINSIC_MATRIX = (mat3){{567.0, 0.0, 1928.0 / 2,
                                           0.0, 567.0, 1208.0 / 2,
                                           0.0, 0.0, 1.0}};


constexpr vec3 default_face_kpts_3d[] = {
  {-5.98, -51.20, 8.00}, {-17.64, -49.14, 8.00}, {-23.81, -46.40, 8.00}, {-29.98, -40.91, 8.00}, {-32.04, -37.49, 8.00},
  {-34.10, -32.00, 8.00}, {-36.16, -21.03, 8.00}, {-36.16, 6.40, 8.00}, {-35.47, 10.51, 8.00}, {-32.73, 19.43, 8.00},
  {-29.30, 26.29, 8.00}, {-24.50, 33.83, 8.00}, {-19.01, 41.37, 8.00}, {-14.21, 46.17, 8.00}, {-12.16, 47.54, 8.00},
  {-4.61, 49.60, 8.00}, {4.99, 49.60, 8.00}, {12.53, 47.54, 8.00}, {14.59, 46.17, 8.00}, {19.39, 41.37, 8.00},
  {24.87, 33.83, 8.00}, {29.67, 26.29, 8.00}, {33.10, 19.43, 8.00}, {35.84, 10.51, 8.00}, {36.53, 6.40, 8.00},
  {36.53, -21.03, 8.00}, {34.47, -32.00, 8.00}, {32.42, -37.49, 8.00}, {30.36, -40.91, 8.00}, {24.19, -46.40, 8.00},
  {18.02, -49.14, 8.00}, {6.36, -51.20, 8.00}, {-5.98, -51.20, 8.00},
};


typedef enum UIStatus {
  STATUS_DISENGAGED,
  STATUS_OVERRIDE,
  STATUS_ENGAGED,
  STATUS_MADS,
} UIStatus;

enum PrimeType {
  UNKNOWN = -2,
  UNPAIRED = -1,
  NONE = 0,
  MAGENTA = 1,
  LITE = 2,
  BLUE = 3,
  MAGENTA_NEW = 4,
  PURPLE = 5,
};

const QColor bg_colors [] = {
  [STATUS_DISENGAGED] = QColor(0x17, 0x33, 0x49, 0xc8),
  [STATUS_OVERRIDE] = QColor(0x91, 0x9b, 0x95, 0xf1),
  [STATUS_ENGAGED] = QColor(0x00, 0xc8, 0x00, 0xf1),
  [STATUS_MADS] = QColor(0x00, 0xc8, 0xc8, 0xf1),
};


const QColor tcs_colors [] = {
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::DISABLED)] =  QColor(0x0, 0x0, 0x0, 0xff),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::ENTERING)] = QColor(0xC9, 0x22, 0x31, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::TURNING)] = QColor(0xDA, 0x6F, 0x25, 0xf1),
  [int(cereal::LongitudinalPlanSP::VisionTurnControllerState::LEAVING)] = QColor(0x17, 0x86, 0x44, 0xf1),
};

typedef struct UIScene {
  bool calibration_valid = false;
  bool calibration_wide_valid  = false;
  bool wide_cam = true;
  mat3 view_from_calib = DEFAULT_CALIBRATION;
  mat3 view_from_wide_calib = DEFAULT_CALIBRATION;
  cereal::PandaState::PandaType pandaType;
  cereal::ControlsState::Reader controlsState;

  // Debug UI
  bool show_debug_ui;

  // Speed limit control
  bool speed_limit_control_enabled;
  int speed_limit_control_policy;
  double last_speed_limit_sign_tap;

  // modelV2
  float lane_line_probs[4];
  float road_edge_stds[2];
  QPolygonF track_vertices;
  QPolygonF track_edge_vertices;
  QPolygonF lane_line_vertices[4];
  QPolygonF road_edge_vertices[2];
  QPolygonF lane_barrier_vertices[2];

  // lead
  QPointF lead_vertices[2];

  // DMoji state
  float driver_pose_vals[3];
  float driver_pose_diff[3];
  float driver_pose_sins[3];
  float driver_pose_coss[3];
  vec3 face_kpts_draw[std::size(default_face_kpts_3d)];

  bool navigate_on_openpilot_deprecated = false;
  cereal::LongitudinalPersonality personality;
  cereal::AccelerationPersonality accel_personality;

  float light_sensor = -1;
  bool started, ignition, is_metric, map_on_left, longitudinal_control;
  bool world_objects_visible = false;
  uint64_t started_frame;

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
} UIScene;

class UIState : public QObject {
  Q_OBJECT

public:
  UIState(QObject* parent = 0);
  void updateStatus();
  inline bool engaged() const {
    return scene.started && (*sm)["controlsState"].getControlsState().getEnabled();
  }

  void setPrimeType(PrimeType type);
  inline PrimeType primeType() const { return prime_type; }
  inline bool hasPrime() const { return prime_type > PrimeType::NONE; }

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

  int fb_w = 0, fb_h = 0;

  std::unique_ptr<SubMaster> sm;

  UIStatus status;
  UIScene scene = {};

  QString language;

  QTransform car_space_transform;

signals:
  void uiUpdate(const UIState &s);
  void offroadTransition(bool offroad);
  void primeChanged(bool prime);
  void primeTypeChanged(PrimeType prime_type);

  void sunnylinkRoleChanged(bool subscriber);
  void sunnylinkRolesChanged(std::vector<RoleModel> roles);
  void sunnylinkDeviceUsersChanged(std::vector<UserModel> users);

private slots:
  void update();

private:
  QTimer *timer;
  bool started_prev = false;
  PrimeType prime_type = PrimeType::UNKNOWN;
  std::vector<RoleModel> sunnylinkRoles = {};
  std::vector<UserModel> sunnylinkUsers = {};

  bool last_mads_enabled = false;
  bool mads_path_state = false;
  float mads_path_timestep = 4;  // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]
  float mads_path_count = 4;     // UI runs at 20 Hz, therefore 0.2 second is [0.2 second / (1 / 20 Hz) = 4]
};

UIState *uiState();

// device management class
class Device : public QObject {
  Q_OBJECT

public:
  Device(QObject *parent = 0);
  bool isAwake() { return awake; }
  void setOffroadBrightness(int brightness) {
    offroad_brightness = std::clamp(brightness, 0, 100);
  }

private:
  bool awake = false;
  int interactive_timeout = 0;
  bool ignition_on = false;

  int offroad_brightness = BACKLIGHT_OFFROAD;
  int last_brightness = 0;
  FirstOrderFilter brightness_filter;
  QFuture<void> brightness_future;

  void updateBrightness(const UIState &s);
  void updateWakefulness(const UIState &s);
  void setAwake(bool on);

signals:
  void displayPowerChanged(bool on);
  void interactiveTimeout();

public slots:
  void resetInteractiveTimeout(int timeout = -1);
  void update(const UIState &s);
};

Device *device();

void ui_update_params(UIState *s);
int get_path_length_idx(const cereal::XYZTData::Reader &line, const float path_height);
void update_model(UIState *s,
                  const cereal::ModelDataV2::Reader &model);
void update_dmonitoring(UIState *s, const cereal::DriverStateV2::Reader &driverstate, float dm_fade_state, bool is_rhd);
void update_leads(UIState *s, const cereal::RadarState::Reader &radar_state, const cereal::XYZTData::Reader &line);
void update_line_data(const UIState *s, const cereal::XYZTData::Reader &line,
                      float y_off, float z_off_left, float z_off_right, QPolygonF *pvd, int max_idx, bool allow_invert);
