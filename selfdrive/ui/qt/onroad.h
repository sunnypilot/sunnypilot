#pragma once

#include <QPushButton>
#include <QStackedLayout>
#include <QWidget>
#include <QTimer>

#include "common/util.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/widgets/cameraview.h"

#ifdef ENABLE_DASHCAM
#include "selfdrive/ui/qt/screenrecorder/screenrecorder.h"
#endif


const int btn_size = 192;
const int img_size = (btn_size / 4) * 3;
const int subsign_img_size = 35;


// ***** onroad widgets *****
class OnroadAlerts : public QWidget {
  Q_OBJECT

public:
  OnroadAlerts(QWidget *parent = 0) : QWidget(parent) {};
  void updateAlert(const Alert &a, const QColor &color);

protected:
  void paintEvent(QPaintEvent*) override;

private:
  QColor bg;
  Alert alert = {};
};

class ExperimentalButton : public QPushButton {
  Q_OBJECT

public:
  explicit ExperimentalButton(QWidget *parent = 0);
  void updateState(const UIState &s);

private:
  void paintEvent(QPaintEvent *event) override;

  Params params;
  QPixmap engage_img;
  QPixmap experimental_img;
};

// container window for the NVG UI
class AnnotatedCameraWidget : public CameraWidget {
  Q_OBJECT
  Q_PROPERTY(float speed MEMBER speed);
  Q_PROPERTY(QString speedUnit MEMBER speedUnit);
  Q_PROPERTY(float setSpeed MEMBER setSpeed);
  Q_PROPERTY(float speedLimit MEMBER speedLimit);
  Q_PROPERTY(bool is_cruise_set MEMBER is_cruise_set);
  Q_PROPERTY(bool has_eu_speed_limit MEMBER has_eu_speed_limit);
  Q_PROPERTY(bool has_us_speed_limit MEMBER has_us_speed_limit);
  Q_PROPERTY(bool is_metric MEMBER is_metric);
  Q_PROPERTY(bool left_blindspot MEMBER left_blindspot);
  Q_PROPERTY(bool right_blindspot MEMBER right_blindspot);

  Q_PROPERTY(bool dmActive MEMBER dmActive);
  Q_PROPERTY(bool hideDM MEMBER hideDM);
  Q_PROPERTY(bool rightHandDM MEMBER rightHandDM);
  Q_PROPERTY(int status MEMBER status);

  Q_PROPERTY(bool steerOverride MEMBER steerOverride);
  Q_PROPERTY(bool latActive MEMBER latActive);
  Q_PROPERTY(bool madsEnabled MEMBER madsEnabled);

  Q_PROPERTY(bool dynamicLaneProfileToggle MEMBER dynamicLaneProfileToggle);
  Q_PROPERTY(int dynamicLaneProfile MEMBER dynamicLaneProfile);

  Q_PROPERTY(bool brakeLights MEMBER brakeLights);

  Q_PROPERTY(bool standStillTimer MEMBER standStillTimer);
  Q_PROPERTY(bool standStill MEMBER standStill);
  Q_PROPERTY(float standstillElapsedTime MEMBER standstillElapsedTime);

  Q_PROPERTY(bool showVTC MEMBER showVTC);
  Q_PROPERTY(QString vtcSpeed MEMBER vtcSpeed);
  Q_PROPERTY(QColor vtcColor MEMBER vtcColor);
  Q_PROPERTY(bool showDebugUI MEMBER showDebugUI);

  Q_PROPERTY(QString roadName MEMBER roadName);

  Q_PROPERTY(bool showSpeedLimit MEMBER showSpeedLimit);
  Q_PROPERTY(float speedLimitSLC MEMBER speedLimitSLC);
  Q_PROPERTY(QString slcSubText MEMBER slcSubText);
  Q_PROPERTY(float slcSubTextSize MEMBER slcSubTextSize);
  Q_PROPERTY(bool overSpeedLimit MEMBER overSpeedLimit);
  Q_PROPERTY(bool mapSourcedSpeedLimit MEMBER mapSourcedSpeedLimit);
  Q_PROPERTY(bool slcActive MEMBER slcActive);
  Q_PROPERTY(int speedLimitStyle MEMBER speedLimitStyle);

  Q_PROPERTY(bool showTurnSpeedLimit MEMBER showTurnSpeedLimit);
  Q_PROPERTY(QString turnSpeedLimit MEMBER turnSpeedLimit);
  Q_PROPERTY(QString tscSubText MEMBER tscSubText);
  Q_PROPERTY(bool tscActive MEMBER tscActive);
  Q_PROPERTY(int curveSign MEMBER curveSign);

  Q_PROPERTY(bool hideVEgoUi MEMBER hideVEgoUi);

  Q_PROPERTY(bool gac MEMBER gac);
  Q_PROPERTY(int gacTr MEMBER gacTr);

  Q_PROPERTY(bool mapVisible MEMBER mapVisible);

  // ############################## DEV UI START ##############################
  Q_PROPERTY(bool lead_status MEMBER lead_status);
  Q_PROPERTY(float lead_d_rel MEMBER lead_d_rel);
  Q_PROPERTY(float lead_v_rel MEMBER lead_v_rel);
  Q_PROPERTY(QString lateralState MEMBER lateralState);
  Q_PROPERTY(float angleSteers MEMBER angleSteers);
  Q_PROPERTY(float steerAngleDesired MEMBER steerAngleDesired);
  Q_PROPERTY(float curvature MEMBER curvature);
  Q_PROPERTY(float roll MEMBER roll);
  Q_PROPERTY(int memoryUsagePercent MEMBER memoryUsagePercent);
  Q_PROPERTY(bool devUiEnabled MEMBER devUiEnabled);
  Q_PROPERTY(int devUiInfo MEMBER devUiInfo);
  Q_PROPERTY(float gpsAccuracy MEMBER gpsAccuracy);
  Q_PROPERTY(float altitude MEMBER altitude);
  Q_PROPERTY(float vEgo MEMBER vEgo);
  Q_PROPERTY(float aEgo MEMBER aEgo);
  Q_PROPERTY(float steeringTorqueEps MEMBER steeringTorqueEps);
  Q_PROPERTY(float bearingAccuracyDeg MEMBER bearingAccuracyDeg);
  Q_PROPERTY(float bearingDeg MEMBER bearingDeg);
  Q_PROPERTY(bool torquedUseParams MEMBER torquedUseParams);
  Q_PROPERTY(float latAccelFactorFiltered MEMBER latAccelFactorFiltered);
  Q_PROPERTY(float frictionCoefficientFiltered MEMBER frictionCoefficientFiltered);
  Q_PROPERTY(bool liveValid MEMBER liveValid);
  // ############################## DEV UI END ##############################

public:
  explicit AnnotatedCameraWidget(VisionStreamType type, QWidget* parent = 0);
  void updateState(const UIState &s);

private:
  void drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawText(QPainter &p, int x, int y, const QString &text, int alpha = 255);
  void drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color, const QString &speed,
                                  int alpha);
  void drawCircle(QPainter &p, int x, int y, int r, QBrush bg);
  void drawSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int subtext_size,
                     bool is_map_sourced, bool is_active);
  void drawTrunSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int curv_sign,
                         bool is_active);

  void drawDlpButton(QPainter &p, int x, int y, int w, int h);
  void drawGacButton(QPainter &p, int x, int y, int w, int h);
  void drawColoredText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawStandstillTimer(QPainter &p, int x, int y);

  // ############################## DEV UI START ##############################
  void drawRightDevUi(QPainter &p, int x, int y);
  int drawDevUiElementRight(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  int drawNewDevUiElement(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  void drawNewDevUi2(QPainter &p, int x, int y);
  void drawCenteredLeftText(QPainter &p, int x, int y, const QString &text1, QColor color1, const QString &text2, const QString &text3, QColor color2);
  // ############################## DEV UI END ##############################

  uint64_t last_update_params;

  ExperimentalButton *experimental_btn;
  QPixmap dm_img;
  QPixmap map_img;
  QPixmap left_img;
  QPixmap right_img;
  float speed;
  QString speedUnit;
  float setSpeed;
  float speedLimit;
  bool is_cruise_set = false;
  bool is_metric = false;
  bool dmActive = false;
  bool hideDM = false;
  bool rightHandDM = false;
  float dm_fade_state = 1.0;
  bool has_us_speed_limit = false;
  bool has_eu_speed_limit = false;
  bool v_ego_cluster_seen = false;
  bool left_blindspot = false;
  bool right_blindspot = false;
  int status = STATUS_DISENGAGED;
  std::unique_ptr<PubMaster> pm;

  int skip_frame_count = 0;
  bool wide_cam_requested = false;

  bool steerOverride = false;
  bool latActive = false;
  bool madsEnabled = false;

  bool dynamicLaneProfileToggle;
  int dynamicLaneProfile;

  bool brakeLights;

  bool standStillTimer;
  bool standStill;
  float standstillElapsedTime;

  bool showVTC = false;
  QString vtcSpeed;
  QColor vtcColor;

  bool showDebugUI = false;

  QString roadName;

  bool showSpeedLimit = false;
  float speedLimitSLC;
  QString slcSubText;
  float slcSubTextSize = 0.0;
  bool overSpeedLimit;
  bool mapSourcedSpeedLimit = false;
  bool slcActive = false;

  bool showTurnSpeedLimit = false;
  QString turnSpeedLimit;
  QString tscSubText;
  bool tscActive = false;
  int curveSign = 0;
  int speedLimitStyle;

  bool hideVEgoUi;

  bool gac;
  int gacTr;

  bool mapVisible;

  // ############################## DEV UI START ##############################
  bool lead_status;
  float lead_d_rel = 0;
  float lead_v_rel = 0;
  QString lateralState;
  float angleSteers = 0;
  float steerAngleDesired = 0;
  float curvature;
  float roll;
  int memoryUsagePercent;
  bool devUiEnabled;
  int devUiInfo;
  float gpsAccuracy;
  float altitude;
  float vEgo;
  float aEgo;
  float steeringTorqueEps;
  float bearingAccuracyDeg;
  float bearingDeg;
  bool torquedUseParams;
  float latAccelFactorFiltered;
  float frictionCoefficientFiltered;
  bool liveValid;
  // ############################## DEV UI END ##############################

protected:
  void paintGL() override;
  void initializeGL() override;
  void showEvent(QShowEvent *event) override;
  void updateFrameMat() override;
  void drawLaneLines(QPainter &painter, const UIState *s);
  void drawLead(QPainter &painter, const cereal::RadarState::LeadData::Reader &lead_data, const QPointF &vd, int num, float radar_d_rel, float v_ego, float radar_v_rel, int chevron_data, bool isMetric);
  void drawHud(QPainter &p);
  void drawDriverState(QPainter &painter, const UIState *s);
  void paintEvent(QPaintEvent *event) override;
  inline QColor redColor(int alpha = 255) { return QColor(201, 34, 49, alpha); }
  inline QColor whiteColor(int alpha = 255) { return QColor(255, 255, 255, alpha); }
  inline QColor blackColor(int alpha = 255) { return QColor(0, 0, 0, alpha); }

  double prev_draw_t = 0;
  FirstOrderFilter fps_filter;
  void rocketFuel(QPainter &p);

// neokii
#ifdef ENABLE_DASHCAM
private:
  ScreenRecoder* recorder;
  std::shared_ptr<QTimer> record_timer;

private slots:
  void offroadTransition(bool offroad);
#endif
};

// container for all onroad widgets
class OnroadWindow : public QWidget {
  Q_OBJECT

public:
  OnroadWindow(QWidget* parent = 0);
  bool isMapVisible() const { return map && map->isVisible(); }

private:
  void paintEvent(QPaintEvent *event);
  void mousePressEvent(QMouseEvent* e) override;
  OnroadAlerts *alerts;
  AnnotatedCameraWidget *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QWidget *map = nullptr;
  QHBoxLayout* split;

  Params params;

private slots:
  void offroadTransition(bool offroad);
  void updateState(const UIState &s);
};
