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
  Q_PROPERTY(QString speed MEMBER speed);
  Q_PROPERTY(QString speedUnit MEMBER speedUnit);
  Q_PROPERTY(QString maxSpeed MEMBER maxSpeed);
  Q_PROPERTY(bool is_cruise_set MEMBER is_cruise_set);
  Q_PROPERTY(bool engageable MEMBER engageable);
  Q_PROPERTY(bool dmActive MEMBER dmActive);
  Q_PROPERTY(bool hideDM MEMBER hideDM);
  Q_PROPERTY(int status MEMBER status);
  Q_PROPERTY(bool steerOverride MEMBER steerOverride);
  Q_PROPERTY(bool madsEnabled MEMBER madsEnabled);
  Q_PROPERTY(bool suspended MEMBER suspended);
  Q_PROPERTY(bool endToEnd MEMBER endToEnd);
  Q_PROPERTY(int dynamicLaneProfile MEMBER dynamicLaneProfile);
  Q_PROPERTY(bool showHowAlert MEMBER showHowAlert);
  Q_PROPERTY(bool howWarning MEMBER howWarning);
  Q_PROPERTY(bool showVTSC MEMBER showVTSC);
  Q_PROPERTY(QString vtscSpeed MEMBER vtscSpeed);
  Q_PROPERTY(QColor vtscColor MEMBER vtscColor);
  Q_PROPERTY(bool showDebugUI MEMBER showDebugUI);
  Q_PROPERTY(QString roadName MEMBER roadName);
  Q_PROPERTY(bool showSpeedLimit MEMBER showSpeedLimit);
  Q_PROPERTY(QString speedLimit MEMBER speedLimit);
  Q_PROPERTY(QString slcSubText MEMBER slcSubText);
  Q_PROPERTY(float slcSubTextSize MEMBER slcSubTextSize);
  Q_PROPERTY(bool mapSourcedSpeedLimit MEMBER mapSourcedSpeedLimit);
  Q_PROPERTY(bool slcActive MEMBER slcActive);
  Q_PROPERTY(bool showTurnSpeedLimit MEMBER showTurnSpeedLimit);
  Q_PROPERTY(QString turnSpeedLimit MEMBER turnSpeedLimit);
  Q_PROPERTY(QString mtscSubText MEMBER mtscSubText);
  Q_PROPERTY(bool mtscActive MEMBER mtscActive);
  Q_PROPERTY(int curveSign MEMBER curveSign);
  Q_PROPERTY(bool is_brakelight_on MEMBER is_brakelight_on);

public:
  explicit NvgWindow(VisionStreamType type, QWidget* parent = 0);
  void updateState(const UIState &s);

private:
  void drawIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawText(QPainter &p, int x, int y, const QString &text, int alpha = 255);
  void drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawSpeedText(QPainter &p, int x, int y, const QString &text, QColor color);
  void drawVisionTurnControllerUI(QPainter &p, int x, int y, int size, const QColor &color, const QString &speed,
                                  int alpha);
  void drawCircle(QPainter &p, int x, int y, int r, QBrush bg);
  void drawSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int subtext_size,
                     bool is_map_sourced, bool is_active);
  void drawTurnSpeedSign(QPainter &p, QRect rc, const QString &speed, const QString &sub_text, int curv_sign,
                         bool is_active);
  void drawMadsIcon(QPainter &p, int x, int y, QPixmap &img, QBrush bg, float opacity);
  void drawDlpButton(QPainter &p, int x, int y, int w, int h);

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
  QString speed;
  QString speedUnit;
  QString maxSpeed;
  bool is_cruise_set = false;
  bool engageable = false;
  bool dmActive = false;
  bool hideDM = false;
  int status = STATUS_DISENGAGED;
  bool steerOverride = false;
  bool madsEnabled = false;
  bool suspended = false;
  bool endToEnd;
  int dynamicLaneProfile;
  bool showHowAlert = false;
  bool howWarning = false;
  bool showVTSC = false;
  QString vtscSpeed;
  QColor vtscColor;
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
  QString mtscSubText;
  bool mtscActive = false;
  int curveSign = 0;
  bool is_brakelight_on = false;

protected:
  void paintGL() override;
  void initializeGL() override;
  void showEvent(QShowEvent *event) override;
  void updateFrameMat(int w, int h) override;
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
