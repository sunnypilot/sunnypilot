#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/turnsignal_ui.h"

TurnSignalWidget::TurnSignalWidget(QWidget *parent) : QObject(parent)
{
  y = 140;
  size = 120;
  arrowSize = 60;
  distance = 200;
}

void TurnSignalWidget::updateState(const UIState &s)
{
  ShowTurnSignals = params.getBool("TurnSignals");

  const SubMaster &sm = *(s.sm);
  const auto car_state = sm["carState"].getCarState();
  left_blinker = car_state.getLeftBlinker();
  right_blinker = car_state.getRightBlinker();
}

void TurnSignalWidget::draw(QPainter &p, const QRect &surface_rect)
{
  // 取得中心位置
  x = surface_rect.center().x();
  if (ShowTurnSignals)
  {
    blinker_frame++;
    blinkerPulse(blinker_frame);
    if (left_blinker)
    {
      drawTurnSignal(p, x - distance, y, true); // 左箭頭
    }
    if (right_blinker)
    {
      drawTurnSignal(p, x + distance, y, false); // 右箭頭
    }
  }
  else
  {
    blinker_frame = 0;
  }
}

void TurnSignalWidget::drawTurnSignal(QPainter &p, int circleX, int circleY, bool isLeft)
{
  // 根據 blinkState 設定顏色
  QColor circleColor = blinkState ? circle_on : circle_off;
  QColor arrowColor = blinkState ? arrow_on : arrow_off;

  // 畫圓圈
  p.setPen(Qt::NoPen);
  p.setBrush(circleColor);
  p.drawEllipse(circleX - size / 2, circleY - size / 2, size, size);

  // 計算箭頭座標
  // 計算 x 軸 凸出距離
  int ArrowtipOffset = arrowSize / 2;
  // 計算 x 軸 + 凸出距離
  int ArrowtipX = circleX + (isLeft ? -ArrowtipOffset : +ArrowtipOffset);
  // 箭頭外側尖端，高度固定在中間
  int ArrowtipY = circleY;
  // 箭頭高點
  int ArrowYU = circleY - arrowSize / 2;
  // 箭頭低點
  int ArrowYD = ArrowYU + arrowSize;

  // 尖端多邊形
  p.setPen(Qt::NoPen);
  p.setBrush(arrowColor);
  QPolygon arrowPolygon;
  arrowPolygon << QPoint(ArrowtipX, ArrowtipY)
               << QPoint(circleX, ArrowYU)
               << QPoint(circleX, ArrowYD)
               << QPoint(ArrowtipX, ArrowtipY);
  p.drawPolygon(arrowPolygon);

  // 尾巴矩形
  QRect tailRect;
  int tailSize = arrowSize / 2;
  int tailX = isLeft ? circleX : circleX - tailSize;
  int tailY = circleY - tailSize / 2;

  tailRect = QRect(tailX, tailY, tailSize, tailSize);

  p.fillRect(tailRect, arrowColor);
}

void TurnSignalWidget::blinkerPulse(int frame)
{
  if (frame % UI_FREQ < (UI_FREQ / 2))
  {
    blinkState = true;
  }
  else
  {
    blinkState = false;
  }
}
