#pragma once

#include <QStackedLayout>
#include <QWidget>

#include "common/util.h"
#include "selfdrive/ui/qt/widgets/cameraview.h"
#include "selfdrive/ui/ui.h"


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

// container window for the NVG UI
class NvgWindow : public CameraViewWidget {
  Q_OBJECT
  Q_PROPERTY(float speed MEMBER speed);
  Q_PROPERTY(QString speedUnit MEMBER speedUnit);
  Q_PROPERTY(float setSpeed MEMBER setSpeed);
  Q_PROPERTY(float speedLimitMb MEMBER speedLimitMb);
  Q_PROPERTY(bool is_cruise_set MEMBER is_cruise_set);
  Q_PROPERTY(bool has_eu_speed_limit MEMBER has_eu_speed_limit);
  Q_PROPERTY(bool has_us_speed_limit MEMBER has_us_speed_limit);
  Q_PROPERTY(bool is_metric MEMBER is_metric);
  Q_PROPERTY(bool engageable MEMBER engageable);
  Q_PROPERTY(bool dmActive MEMBER dmActive);
  Q_PROPERTY(bool hideDM MEMBER hideDM);
  Q_PROPERTY(int status MEMBER status);
  Q_PROPERTY(bool steerOverride MEMBER steerOverride);
  Q_PROPERTY(bool latActive MEMBER latActive);
  Q_PROPERTY(bool madsEnabled MEMBER madsEnabled);
  Q_PROPERTY(bool endToEnd MEMBER endToEnd);
  Q_PROPERTY(int dynamicLaneProfile MEMBER dynamicLaneProfile);
  Q_PROPERTY(bool is_brakelight_on MEMBER is_brakelight_on);
  Q_PROPERTY(bool standStillTimer MEMBER standStillTimer);
  Q_PROPERTY(bool standStill MEMBER standStill);
  Q_PROPERTY(int standstillElapsedTime MEMBER standstillElapsedTime);
  Q_PROPERTY(int lead_status MEMBER lead_status);
  Q_PROPERTY(float lead_d_rel MEMBER lead_d_rel);
  Q_PROPERTY(float lead_v_rel MEMBER lead_v_rel);
  Q_PROPERTY(float angleSteers MEMBER angleSteers);
  Q_PROPERTY(float steerAngleDesired MEMBER steerAngleDesired);
  Q_PROPERTY(int memoryUsagePercent MEMBER memoryUsagePercent);
  Q_PROPERTY(bool devUiEnabled MEMBER devUiEnabled);
  Q_PROPERTY(int devUiRow MEMBER devUiRow);
  Q_PROPERTY(float gpsAccuracy MEMBER gpsAccuracy);
  Q_PROPERTY(float altitude MEMBER altitude);
  Q_PROPERTY(float vEgo MEMBER vEgo);
  Q_PROPERTY(float aEgo MEMBER aEgo);
  Q_PROPERTY(float steeringTorqueEps MEMBER steeringTorqueEps);
  Q_PROPERTY(float bearingAccuracyDeg MEMBER bearingAccuracyDeg);
  Q_PROPERTY(float bearingDeg MEMBER bearingDeg);
  Q_PROPERTY(bool gapAdjustCruise MEMBER gapAdjustCruise);
  Q_PROPERTY(int gapAdjustCruiseTr MEMBER gapAdjustCruiseTr);
  Q_PROPERTY(bool showHowAlert MEMBER showHowAlert);
  Q_PROPERTY(bool howWarning MEMBER howWarning);
  Q_PROPERTY(bool showVTSC MEMBER showVTSC);
  Q_PROPERTY(QString vtscSpeed MEMBER vtscSpeed);
  Q_PROPERTY(QColor vtscColor MEMBER vtscColor);
  Q_PROPERTY(bool showDebugUI MEMBER showDebugUI);
  Q_PROPERTY(QString roadName MEMBER roadName);
  Q_PROPERTY(bool showSpeedLimit MEMBER showSpeedLimit);
  Q_PROPERTY(float speedLimit MEMBER speedLimit);
  Q_PROPERTY(QString slcSubText MEMBER slcSubText);
  Q_PROPERTY(float slcSubTextSize MEMBER slcSubTextSize);
  Q_PROPERTY(bool mapSourcedSpeedLimit MEMBER mapSourcedSpeedLimit);
  Q_PROPERTY(bool slcActive MEMBER slcActive);
  Q_PROPERTY(bool showTurnSpeedLimit MEMBER showTurnSpeedLimit);
  Q_PROPERTY(QString turnSpeedLimit MEMBER turnSpeedLimit);
  Q_PROPERTY(QString mtscSubText MEMBER mtscSubText);
  Q_PROPERTY(bool mtscActive MEMBER mtscActive);
  Q_PROPERTY(int curveSign MEMBER curveSign);
  Q_PROPERTY(int speedLimitStyle MEMBER speedLimitStyle);
  Q_PROPERTY(int gapAdjustCruiseMode MEMBER gapAdjustCruiseMode);
  Q_PROPERTY(int carMake MEMBER carMake);

public:
  explicit NvgWindow(VisionStreamType type, QWidget* parent = 0);
  void updateState(const UIState &s);

private:
  void drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawText(QPainter &p, int x, int y, const QString &text, int alpha = 255);
  void drawSpeedText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawColoredText(QPainter &p, int x, int y, const QString &text, QColor &color);
  void drawStandstillTimerText(QPainter &p, int x, int y, const char* label, const char* value, QColor &color1, QColor &color2);
  void drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color, const QString &speed, int alpha);
  void drawMadsIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawDlpButton(QPainter &p, int x, int y, int w, int h);
  void drawStandstillTimer(QPainter &p, int x, int y);
  void drawRightDevUi(QPainter &p, int x, int y);
  void drawRightDevUi2(QPainter &p, int x, int y);
  void drawRightDevUiBorder(QPainter &p, int x, int y);
  int drawDevUiElementRight(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  int drawDevUiElementLeft(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  void drawGacButton(QPainter &p, int x, int y, int w, int h);
  void drawCircle(QPainter &p, int x, int y, int r, QBrush bg);
  void drawTurnSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int curv_sign, bool is_active);

  QPixmap engage_img;
  QPixmap dm_img;
  QPixmap mads_imgs[2];
  QPixmap how_img;
  QPixmap map_img;
  QPixmap left_img;
  QPixmap right_img;
  const int radius = 192;
  const int img_size = (radius / 2) * 1.5;
  const int subsign_img_size = 35;
  float speed;
  QString speedUnit;
  float setSpeed;
  float speedLimitMb;
  bool is_cruise_set = false;
  bool is_metric = false;
  bool engageable = false;
  bool dmActive = false;
  bool hideDM = false;
  bool has_us_speed_limit = false;
  bool has_eu_speed_limit = false;
  int status = STATUS_DISENGAGED;
  bool steerOverride = false;
  bool latActive = false;
  bool madsEnabled = false;
  bool endToEnd;
  int dynamicLaneProfile;
  bool is_brakelight_on = false;
  bool standStillTimer;
  bool standStill;
  int standstillElapsedTime;
  int lead_status;
  float lead_d_rel = 0;
  float lead_v_rel = 0;
  float angleSteers = 0;
  float steerAngleDesired = 0;
  int memoryUsagePercent;
  bool devUiEnabled;
  int devUiRow;
  float gpsAccuracy;
  float altitude;
  float vEgo;
  float aEgo;
  float steeringTorqueEps;
  float bearingAccuracyDeg;
  float bearingDeg;
  bool gapAdjustCruise;
  int gapAdjustCruiseTr;
  bool showHowAlert = false;
  bool howWarning = false;
  bool showVTSC = false;
  QString vtscSpeed;
  QColor vtscColor;
  bool showDebugUI = false;
  QString roadName;
  bool showSpeedLimit = false;
  float speedLimit;
  QString slcSubText;
  float slcSubTextSize = 0.0;
  bool mapSourcedSpeedLimit = false;
  bool slcActive = false;
  bool showTurnSpeedLimit = false;
  QString turnSpeedLimit;
  QString mtscSubText;
  bool mtscActive = false;
  int curveSign = 0;
  int speedLimitStyle;
  int gapAdjustCruiseMode;
  int carMake;

protected:
  void paintGL() override;
  void initializeGL() override;
  void showEvent(QShowEvent *event) override;
  void updateFrameMat() override;
  void drawLaneLines(QPainter &painter, const UIState *s);
  void drawLead(QPainter &painter, const cereal::ModelDataV2::LeadDataV3::Reader &lead_data, const QPointF &vd);
  void drawHud(QPainter &p);
  inline QColor redColor(int alpha = 255) { return QColor(201, 34, 49, alpha); }
  inline QColor whiteColor(int alpha = 255) { return QColor(255, 255, 255, alpha); }
  inline QColor blackColor(int alpha = 255) { return QColor(0, 0, 0, alpha); }

  double prev_draw_t = 0;
  FirstOrderFilter fps_filter;
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
  NvgWindow *nvg;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QWidget *map = nullptr;
  QHBoxLayout* split;

private slots:
  void offroadTransition(bool offroad);
  void updateState(const UIState &s);
};
