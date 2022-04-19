#pragma once

#include <QStackedLayout>
#include <QWidget>
#include <QPushButton>

#include "selfdrive/ui/qt/widgets/cameraview.h"
#include "selfdrive/ui/ui.h"


// ***** onroad widgets *****

class ButtonsWindow : public QWidget {
  Q_OBJECT

public:
  ButtonsWindow(QWidget* parent = 0);

private:
  QPushButton *dlpBtn;

  const QStringList dlpBtnColors = {"#007d00", "#c92231", "#7d007d"};

public slots:
  void updateState(const UIState &s);
};

class OnroadHud : public QWidget {
  Q_OBJECT
  Q_PROPERTY(QString speed MEMBER speed NOTIFY valueChanged);
  Q_PROPERTY(QString speedUnit MEMBER speedUnit NOTIFY valueChanged);
  Q_PROPERTY(QString maxSpeed MEMBER maxSpeed NOTIFY valueChanged);
  Q_PROPERTY(bool is_cruise_set MEMBER is_cruise_set NOTIFY valueChanged);
  Q_PROPERTY(bool engageable MEMBER engageable NOTIFY valueChanged);
  Q_PROPERTY(bool dmActive MEMBER dmActive NOTIFY valueChanged);
  Q_PROPERTY(bool hideDM MEMBER hideDM NOTIFY valueChanged);
  Q_PROPERTY(int status MEMBER status NOTIFY valueChanged);
  Q_PROPERTY(bool is_brakelight_on MEMBER is_brakelight_on NOTIFY valueChanged);
  Q_PROPERTY(bool madsEnabled MEMBER madsEnabled NOTIFY valueChanged);
  Q_PROPERTY(bool suspended MEMBER suspended NOTIFY valueChanged);

  Q_PROPERTY(bool showHowAlert MEMBER showHowAlert NOTIFY valueChanged);
  Q_PROPERTY(bool howWarning MEMBER howWarning NOTIFY valueChanged);

  Q_PROPERTY(bool showVTC MEMBER showVTC NOTIFY valueChanged);
  Q_PROPERTY(QString vtcSpeed MEMBER vtcSpeed NOTIFY valueChanged);
  Q_PROPERTY(QColor vtcColor MEMBER vtcColor NOTIFY valueChanged);
  Q_PROPERTY(bool showDebugUI MEMBER showDebugUI NOTIFY valueChanged);

Q_PROPERTY(QString roadName MEMBER roadName NOTIFY valueChanged);

  Q_PROPERTY(bool showSpeedLimit MEMBER showSpeedLimit NOTIFY valueChanged);
  Q_PROPERTY(QString speedLimit MEMBER speedLimit NOTIFY valueChanged);
  Q_PROPERTY(QString slcSubText MEMBER slcSubText NOTIFY valueChanged);
  Q_PROPERTY(float slcSubTextSize MEMBER slcSubTextSize NOTIFY valueChanged);
  Q_PROPERTY(bool mapSourcedSpeedLimit MEMBER mapSourcedSpeedLimit NOTIFY valueChanged);
  Q_PROPERTY(bool slcActive MEMBER slcActive NOTIFY valueChanged);

  Q_PROPERTY(bool showTurnSpeedLimit MEMBER showTurnSpeedLimit NOTIFY valueChanged);
  Q_PROPERTY(QString turnSpeedLimit MEMBER turnSpeedLimit NOTIFY valueChanged);
  Q_PROPERTY(QString tscSubText MEMBER tscSubText NOTIFY valueChanged);
  Q_PROPERTY(bool tscActive MEMBER tscActive NOTIFY valueChanged);
  Q_PROPERTY(int curveSign MEMBER curveSign NOTIFY valueChanged);

  Q_PROPERTY(int lead_status MEMBER lead_status NOTIFY valueChanged);
  Q_PROPERTY(float lead_d_rel MEMBER lead_d_rel NOTIFY valueChanged);
  Q_PROPERTY(float lead_v_rel MEMBER lead_v_rel NOTIFY valueChanged);
  Q_PROPERTY(float angleSteers MEMBER angleSteers NOTIFY valueChanged);
  Q_PROPERTY(float steerAngleDesired MEMBER steerAngleDesired NOTIFY valueChanged);
  Q_PROPERTY(int distanceTraveled MEMBER distanceTraveled NOTIFY valueChanged);
  Q_PROPERTY(int devUiEnabled MEMBER devUiEnabled NOTIFY valueChanged);
  Q_PROPERTY(float gpsAccuracy MEMBER gpsAccuracy NOTIFY valueChanged);
  Q_PROPERTY(float altitude MEMBER altitude NOTIFY valueChanged);
  Q_PROPERTY(float vEgo MEMBER vEgo NOTIFY valueChanged);
  Q_PROPERTY(float aEgo MEMBER aEgo NOTIFY valueChanged);
  Q_PROPERTY(float steeringTorqueEps MEMBER steeringTorqueEps NOTIFY valueChanged);
  Q_PROPERTY(float bearingAccuracyDeg MEMBER bearingAccuracyDeg NOTIFY valueChanged);
  Q_PROPERTY(float bearingDeg MEMBER bearingDeg NOTIFY valueChanged);

  Q_PROPERTY(bool standStill MEMBER standStill NOTIFY valueChanged);
  Q_PROPERTY(int standstillElapsedTime MEMBER standstillElapsedTime NOTIFY valueChanged);

public:
  explicit OnroadHud(QWidget *parent);
  void updateState(const UIState &s);

private:
  void drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawText(QPainter &p, int x, int y, const QString &text, int alpha = 255);
  void drawSpeedText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color, const QString &speed,
                                  int alpha);
  void drawCircle(QPainter &p, int x, int y, int r, QBrush bg);
  void drawSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int subtext_size,
                     bool is_map_sourced, bool is_active);
  void drawTrunSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int curv_sign,
                         bool is_active);
  void drawMadsIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawStandstillTimerText(QPainter &p, int x, int y, const char* label, const char* value, QColor &color1, QColor &color2);
  void drawRightDevUi(QPainter &p, int x, int y);
  void drawRightDevUi2(QPainter &p, int x, int y);
  void drawRightDevUiBorder(QPainter &p, int x, int y);
  void drawStandstillTimer(QPainter &p, int x, int y);
  int drawDevUiElementRight(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  int drawDevUiElementLeft(QPainter &p, int x, int y, const char* value, const char* label, const char* units, QColor &color);
  void drawColoredText(QPainter &p, int x, int y, const QString &text, QColor &color);
  void paintEvent(QPaintEvent *event) override;

  QPixmap engage_img;
  QPixmap dm_img;
  QPixmap how_img;
  QPixmap map_img;
  QPixmap left_img;
  QPixmap right_img;
  QPixmap mads_imgs[2];
  const int radius = 192;
  const int img_size = (radius / 2) * 1.5;
  const int subsign_img_size = 35;
  QString speed;
  QString speedUnit;
  QString maxSpeed;
  bool is_cruise_set = false;
  bool engageable = false;
  bool dmActive = false;
  bool hideDM = false;
  int status = STATUS_DISENGAGED;
  bool is_brakelight_on = false;
  bool madsEnabled = false;
  bool suspended = false;

  bool showHowAlert = false;
  bool howWarning = false;

  bool showVTC = false;
  QString vtcSpeed;
  QColor vtcColor;
  bool showDebugUI = false;

  QString roadName;

  bool showSpeedLimit = false;
  QString speedLimit;
  QString slcSubText;
  float slcSubTextSize = 0.0;
  bool mapSourcedSpeedLimit = false;
  bool slcActive = false;

  bool showTurnSpeedLimit = false;
  QString turnSpeedLimit;
  QString tscSubText;
  bool tscActive = false;
  int curveSign = 0;

  int lead_status;
  float lead_d_rel = 0;
  float lead_v_rel = 0;
  float angleSteers = 0;
  float steerAngleDesired = 0;
  int distanceTraveled = 0;
  int devUiEnabled;
  float gpsAccuracy;
  float altitude;
  float vEgo;
  float aEgo;
  float steeringTorqueEps;
  float bearingAccuracyDeg;
  float bearingDeg;

  bool standStill;
  int standstillElapsedTime;

signals:
  void valueChanged();
};

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

public:
  explicit NvgWindow(VisionStreamType type, QWidget* parent = 0) : CameraViewWidget("camerad", type, true, parent) {}

protected:
  void paintGL() override;
  void initializeGL() override;
  void showEvent(QShowEvent *event) override;
  void updateFrameMat(int w, int h) override;
  void drawLaneLines(QPainter &painter, const UIScene &scene);
  void drawLead(QPainter &painter, const cereal::ModelDataV2::LeadDataV3::Reader &lead_data, const QPointF &vd, bool openpilot_longitudinal_control);
  inline QColor redColor(int alpha = 255) { return QColor(201, 34, 49, alpha); }
  inline QColor blackColor(int alpha = 255) { return QColor(0, 0, 0, alpha); }
  inline QColor greenColor(int alpha = 255) { return QColor(49, 201, 34, alpha); }
  inline QColor graceBlueColor(int alpha = 255) { return QColor (34, 49, 201, alpha); }
  double prev_draw_t = 0;

signals:
  void resizeSignal(int w);
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
  OnroadHud *hud;
  OnroadAlerts *alerts;
  NvgWindow *nvg;
  ButtonsWindow *buttons;
  QColor bg = bg_colors[STATUS_DISENGAGED];
  QWidget *map = nullptr;
  QHBoxLayout* split;

signals:
  void updateStateSignal(const UIState &s);
  void offroadTransitionSignal(bool offroad);

private slots:
  void offroadTransition(bool offroad);
  void updateState(const UIState &s);
};
