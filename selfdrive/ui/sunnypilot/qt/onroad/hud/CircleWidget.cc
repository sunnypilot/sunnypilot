#include "selfdrive/ui/sunnypilot/qt/onroad/hud/CircleWidget.h"
#include <QRadialGradient>
#include <QConicalGradient>

CircleWidget::CircleWidget(QObject *parent) : QObject(parent)
{
}

void CircleWidget::setup(float min, float max, QString unitStr, int widgetSize)
{
    minValue = min;
    maxValue = max;
    unit = unitStr;
    size = widgetSize;
}

void CircleWidget::setoffset(int X, int Y)
{
    x_offset = X;
    y_offset = Y;
}

void CircleWidget::setValue(bool Enabled, bool Active, float Angle1, float Angle2)
{
    enabled = Enabled;
    active = Active;

    value1 = Angle1;
    angle1 = -180.0f + (Angle1 - minValue) * 360.0f / (maxValue - minValue);
    value2 = Angle2;
    angle2 = -180.0f + (Angle2 - minValue) * 360.0f / (maxValue - minValue);
}

void CircleWidget::updateState(const UIState &s)
{

}

void CircleWidget::draw(QPainter &p, const QRect &surface_rect)
{
    p.setRenderHint(QPainter::Antialiasing, true);

    x = x_offset + surface_rect.topRight().x() - size - UI_BORDER_SIZE;
    y = y_offset + surface_rect.topRight().y() + 240 + UI_BORDER_SIZE;

    // 設定圓心
    QPointF center(x + size / 2.0f, y + size / 2.0f);

    float outerPenWidth = 3; // 外框線寬 (固定)
    // 半徑設定：外圈貼邊，內圈緊貼外圈
    float radiusOuter = size / 2.0f;
    float radiusInner1 = radiusOuter - outerPenWidth / 2.0f - innerArcWidth / 2.0f;
    float radiusInner2 = radiusInner1 - innerArcWidth / 2.0f - innerArcWidth / 2.0f;

    // -----------------------
    // HUD 半透明光暈背景
    // -----------------------
    QRadialGradient bgGlow(center, radiusOuter);
    bgGlow.setColorAt(0.0f, QColor(0, 0, 0, 120)); // 中間更黑
    bgGlow.setColorAt(1.0f, QColor(0, 0, 0, 0));   // 邊緣全透明
    p.setBrush(bgGlow);
    p.setPen(Qt::NoPen);
    p.drawEllipse(center, radiusOuter, radiusOuter);

    // -----------------------
    // 外框圓
    // -----------------------
    QColor outerColor = active ? activeColor : enabled ? enabledColor
                                                       : defaultColor;
    QPen penOuter;
    penOuter.setWidth(outerPenWidth);
    penOuter.setBrush(Qt::NoBrush);
    penOuter.setColor(outerColor);
    p.setPen(penOuter);
    p.drawEllipse(center, radiusOuter, radiusOuter);

    // -----------------------
    // 內圈弧線 + 尾端光暈
    // -----------------------
    drawArcWithTail(p, center, radiusInner1, innerArcWidth, angle1,
                    QColor(0, 255, 0), QColor(255, 255, 0), QColor(255, 0, 0));
    drawArcWithTail(p, center, radiusInner2, innerArcWidth, angle2,
                    QColor(50, 148, 50), QColor(148, 148, 50), QColor(148, 50, 50));

    // -----------------------
    // 中心文字 + 光暈描邊
    // -----------------------
    QString angleText = QString::number(value1, 'f', 1) + unit;
    QFont font = p.font();
    font.setPointSize(size / 8);
    font.setBold(true);
    p.setFont(font);

    // 計算比例 0~1
    float ratio = (qAbs(value1) - 0) / (maxValue);
    ratio = std::clamp(ratio, 0.0f, 1.0f);

    // 根據比例線性插值顏色 (綠 → 黃 → 紅)
    QColor textcolor;
    if (ratio < 0.5f)
    {
        // 綠色 → 黃色
        float t = ratio / 0.5f;
        textcolor.setRgbF(0.0f + t * 1.0f, 1.0f, 0.0f); // R 從0→1, G=1
    }
    else
    {
        // 黃色 → 紅色
        float t = (ratio - 0.5f) / 0.5f;
        textcolor.setRgbF(1.0f, 1.0f - t * 1.0f, 0.0f); // R=1, G從1→0
    }

    // 使用 QRectF 畫文字，避免 QPointF 對齊錯誤
    QRectF textRect(center.x() - size / 2, center.y() - size / 2, size, size);

    // 光暈描邊
    textcolor.setAlpha(120);
    QPen glowPen(textcolor);
    p.setPen(glowPen);
    p.drawText(textRect.translated(1, 1), Qt::AlignCenter, angleText);
    p.drawText(textRect.translated(-1, -1), Qt::AlignCenter, angleText);

    // 正文字
    QPen TextPen;
    textcolor.setAlpha(255);
    TextPen.setColor(textcolor);
    p.setPen(TextPen);
    p.drawText(textRect, Qt::AlignCenter, angleText);
}

void CircleWidget::drawArcWithTail(QPainter &p, const QPointF &center,
                                   float radius, float penWidth, float angle,
                                   QColor colorStart, QColor colorMid, QColor colorEnd)
{
    // 上下限保護
    angle = qBound(-180.0f, angle, 180.0f);

    QRectF rect(center.x() - radius, center.y() - radius, radius * 2, radius * 2);

    // 動態漸層強度
    float factor = qAbs(angle) / 180.0f;
    auto adjustColor = [factor](QColor c)
    {
        int r = static_cast<int>(c.red() * factor + 50 * (1 - factor));
        int g = static_cast<int>(c.green() * factor + 50 * (1 - factor));
        int b = static_cast<int>(c.blue() * factor + 50 * (1 - factor));
        return QColor(r, g, b);
    };

    QColor start = adjustColor(colorStart);
    QColor mid = adjustColor(colorMid);
    QColor end = adjustColor(colorEnd);

    // 畫弧線
    QConicalGradient grad(center, 90);
    grad.setColorAt(0.0f, start);
    grad.setColorAt(0.25f, mid);
    grad.setColorAt(0.5f, end);
    grad.setColorAt(0.75f, mid);
    grad.setColorAt(1.0f, start);

    QPen pen(QBrush(grad), penWidth, Qt::SolidLine, Qt::RoundCap);
    p.setPen(pen);
    p.drawArc(rect, 90 * 16, -angle * 16);

    // 尾端光暈
    float radEnd = (90.0f - angle) * M_PI / 180.0f;
    QPointF endPoint(center.x() + radius * std::cos(radEnd),
                     center.y() - radius * std::sin(radEnd));

    QColor tailColor = end;
    int alpha = 80 + static_cast<int>(100 * factor);
    tailColor.setAlpha(alpha);
    float glowRadius = penWidth * (1.0f + factor);

    QRadialGradient tailGlow(endPoint, glowRadius);
    tailGlow.setColorAt(0.0f, tailColor);
    tailGlow.setColorAt(1.0f, QColor(tailColor.red(), tailColor.green(),
                                    tailColor.blue(), 0));

    p.setBrush(tailGlow);
    p.setPen(Qt::NoPen);
    p.drawEllipse(endPoint, glowRadius, glowRadius);
}
