#pragma once

#include <memory>
#include <string>
#include <optional>

#include <QObject>
#include <QTimer>
#include <QColor>
#include <QTransform>

#include "cereal/messaging/messaging.h"
#include "selfdrive/common/modeldata.h"
#include "selfdrive/common/params.h"
#include "selfdrive/common/timing.h"

const int bdr_s = 30;
const int header_h = 420;
const int footer_h = 280;

const QRect speed_sgn_rc(bdr_s * 2, bdr_s * 2.5 + 202, 184, 184);
const QRect max_speed_rc(bdr_s * 2, bdr_s * 1.5, 184, 202);

const int UI_FREQ = 20;   // Hz
typedef cereal::CarControl::HUDControl::AudibleAlert AudibleAlert;

// TODO: this is also hardcoded in common/transformations/camera.py
// TODO: choose based on frame input size
const float y_offset = Hardware::EON() ? 0.0 : 150.0;
const float ZOOM = Hardware::EON() ? 2138.5 : 2912.8;

struct Alert {
  QString text1;
  QString text2;
  QString type;
  cereal::ControlsState::AlertSize size;
  AudibleAlert sound;
  bool equal(const Alert &a2) {
    return text1 == a2.text1 && text2 == a2.text2 && type == a2.type && sound == a2.sound;
  }

  static Alert get(const SubMaster &sm, uint64_t started_frame, uint64_t display_debug_alert_frame = 0) {
    if (display_debug_alert_frame > 0 && (sm.frame - display_debug_alert_frame) <= 1 * UI_FREQ) {
      return {"Debug snapshot collected", "",
              "debugTapDetected", cereal::ControlsState::AlertSize::SMALL,
              AudibleAlert::PROMPT};
    } else if (sm.updated("controlsState")) {
      const cereal::ControlsState::Reader &cs = sm["controlsState"].getControlsState();
      return {cs.getAlertText1().cStr(), cs.getAlertText2().cStr(),
              cs.getAlertType().cStr(), cs.getAlertSize(),
              cs.getAlertSound()};
    } else if ((sm.frame - started_frame) > 5 * UI_FREQ) {
      const int CONTROLS_TIMEOUT = 5;
      // Handle controls timeout
      if (sm.rcv_frame("controlsState") < started_frame) {
        // car is started, but controlsState hasn't been seen at all
        return {"openpilot Unavailable", "Waiting for controls to start",
                "controlsWaiting", cereal::ControlsState::AlertSize::MID,
                AudibleAlert::NONE};
      } else if ((nanos_since_boot() - sm.rcv_time("controlsState")) / 1e9 > CONTROLS_TIMEOUT) {
        // car is started, but controls is lagging or died
        return {"TAKE CONTROL IMMEDIATELY", "Controls Unresponsive",
                "controlsUnresponsive", cereal::ControlsState::AlertSize::FULL,
                AudibleAlert::WARNING_IMMEDIATE};
      }
    }
    return {};
  }
};

typedef enum UIStatus {
  STATUS_DISENGAGED,
  STATUS_ENGAGED,
  STATUS_WARNING,
  STATUS_ALERT,
} UIStatus;

const QColor bg_colors [] = {
  [STATUS_DISENGAGED] =  QColor(0x17, 0x33, 0x49, 0xc8),
  [STATUS_ENGAGED] = QColor(0x17, 0x86, 0x44, 0xf1),
  [STATUS_WARNING] = QColor(0xDA, 0x6F, 0x25, 0xf1),
  [STATUS_ALERT] = QColor(0xC9, 0x22, 0x31, 0xf1),
};

const QColor tcs_colors [] = {
  [int(cereal::LongitudinalPlan::VisionTurnControllerState::DISABLED)] =  QColor(0x0, 0x0, 0x0, 0xff),
  [int(cereal::LongitudinalPlan::VisionTurnControllerState::ENTERING)] = QColor(0xC9, 0x22, 0x31, 0xf1),
  [int(cereal::LongitudinalPlan::VisionTurnControllerState::TURNING)] = QColor(0xDA, 0x6F, 0x25, 0xf1),
  [int(cereal::LongitudinalPlan::VisionTurnControllerState::LEAVING)
  ] = QColor(0x17, 0x86, 0x44, 0xf1),
};

typedef struct {
  QPointF v[TRAJECTORY_SIZE * 2];
  int cnt;
} line_vertices_data;

typedef struct UIScene {
  mat3 view_from_calib;
  bool world_objects_visible;

  // Debug UI
  bool show_debug_ui;
  bool debug_snapshot_enabled;
  uint64_t display_debug_alert_frame;

  // Speed limit control
  bool speed_limit_control_enabled;
  bool speed_limit_perc_offset;
  int speed_limit_value_offset;

  double last_speed_limit_sign_tap;
  cereal::PandaState::PandaType pandaType;

  int dynamic_lane_profile;

  bool read_params = false;
  int onroadScreenOff, onroadScreenOffBrightness, osoTimer, brightness, awake;
  bool touched2 = false;

  cereal::CarState::Reader car_state;
  cereal::ControlsState::Reader controls_state;
  cereal::LateralPlan::Reader lateral_plan;

  // modelV2
  float lane_line_probs[4];
  float road_edge_stds[2];
  line_vertices_data track_vertices;
  line_vertices_data lane_line_vertices[4];
  line_vertices_data road_edge_vertices[2];

  // lead
  QPointF lead_vertices[2];

  struct _CarState
  {
    bool radarObjValid;
  } carState;

  float light_sensor, accel_sensor, gyro_sensor;
  bool started, ignition, is_metric, longitudinal_control, end_to_end;
  uint64_t started_frame;

  struct _LateralPlan
  {
    bool dynamicLaneProfileStatus;
  } lateralPlan;

  int dev_ui_enabled;
} UIScene;

typedef struct UIState {
  int fb_w = 0, fb_h = 0;

  std::unique_ptr<SubMaster> sm;

  UIStatus status;
  UIScene scene = {};

  bool awake;
  bool has_prime = false;

  QTransform car_space_transform;
  bool wide_camera;
} UIState;


class QUIState : public QObject {
  Q_OBJECT

public:
  QUIState(QObject* parent = 0);

  // TODO: get rid of this, only use signal
  inline static UIState ui_state = {0};

signals:
  void uiUpdate(const UIState &s);
  void offroadTransition(bool offroad);

private slots:
  void update();

private:
  QTimer *timer;
  bool started_prev = true;
};


// device management class

class Device : public QObject {
  Q_OBJECT

public:
  Device(QObject *parent = 0);

private:
  // auto brightness
  const float accel_samples = 5*UI_FREQ;

  bool awake = false;
  int awake_timeout = 0;
  float accel_prev = 0;
  float gyro_prev = 0;
  int last_brightness = 0;
  FirstOrderFilter brightness_filter;

  QTimer *timer;

  int sleep_time = -1;

  void updateBrightness(const UIState &s);
  void updateWakefulness(const UIState &s);

signals:
  void displayPowerChanged(bool on);

public slots:
  void setAwake(bool on, bool reset);
  void update(const UIState &s);
};

void ui_update_params(UIState *s);
