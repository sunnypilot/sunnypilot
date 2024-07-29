/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/widgets/toggle.h"

#include <QPainter>

ToggleSP::ToggleSP(QWidget *parent) : Toggle(parent) {
  _height_rect = 80;
}

void ToggleSP::paintEvent(QPaintEvent *e) {
  this->setFixedHeight(100);
  QPainter p(this);
  p.setPen(Qt::NoPen);
  p.setRenderHint(QPainter::Antialiasing, true);

  // Draw toggle background
  enabled ? green.setRgb(0x1e79e8) : green.setRgb(0x125db8);
  p.setBrush(on ? green : QColor(0x292929));
  p.drawRoundedRect(QRect(0, 10, width(), _height_rect),_height_rect/2, _height_rect/2);

  // Draw toggle circle
  p.setBrush(circleColor);
  p.drawEllipse(QRectF(_x_circle - _radius + 6, 16, 68, 68));
}
