#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/util.h"

class CircleWidget : public QObject
{
  Q_OBJECT

public:
  // 建構函式設定位置 (x,y) 與正方形尺寸
  explicit CircleWidget(QObject *parent = nullptr);

  void setup(float min = -180.0, float max = 180.0, QString unitStr = "°", int widgetSize = 192);
  void setoffset(int X = 0, int Y = 0);
  void setValue(bool Enabled,bool Active,float Angle1, float Angle2);
  void draw(QPainter &p, const QRect &surface_rect);
  void updateState(const UIState &s);

private:
Params params;
  int x = 0;
  int x_offset = 0;
  int y = 0;
  int y_offset = 0;
  int size = 0;
  float innerArcWidth = 40;

  bool enabled = false;
  bool active = false;
  float minValue = -180.0f;
  float maxValue = 180.0f;
  QString unit = "°";

  float value1 = 0.0f;
  float value2 = 0.0f;
  float angle1 = 0.0f;
  float angle2 = 0.0f;

  const QColor defaultColor = QColor(255, 255, 255);
  const QColor enabledColor = QColor(0, 255, 255);
  const QColor activeColor = QColor(0, 255, 0);

  // 畫弧線 + 尾端光暈
  void drawArcWithTail(QPainter &painter, const QPointF &center,
                       float radius, float penWidth, float angle,
                       QColor colorStart, QColor colorMid, QColor colorEnd);
};
