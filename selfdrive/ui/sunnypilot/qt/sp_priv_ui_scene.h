#pragma once
#include "selfdrive/ui/ui.h"

const float DRIVING_PATH_WIDE = 0.9;
const float DRIVING_PATH_NARROW = 0.25;

typedef struct UISceneSP : public UIScene {
    cereal::ControlsState::Reader controlsState;

    // Debug UI
    bool show_debug_ui;

    // Speed limit control
    bool speed_limit_control_enabled;
    int speed_limit_control_policy;
    double last_speed_limit_sign_tap;
    
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