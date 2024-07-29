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

#pragma once

#include <memory>

#include "selfdrive/ui/qt/sidebar.h"

#include "selfdrive/ui/sunnypilot/ui.h"

class SidebarSP : public Sidebar {
  Q_OBJECT
  Q_PROPERTY(ItemStatus sunnylinkStatus MEMBER sunnylink_status NOTIFY valueChanged);
  Q_PROPERTY(QString sidebarTemp MEMBER sidebar_temp_str NOTIFY valueChanged);

public:
  explicit SidebarSP(QWidget* parent = 0);

public slots:
  void updateState(const UIStateSP &s);

protected:
  const QColor progress_color = QColor(3, 132, 252);
  const QColor disabled_color = QColor(128, 128, 128);

  ItemStatus sunnylink_status;

private:
  Params params;
  void DrawSidebar(QPainter &p) override;
  QString sidebar_temp = "0";
  QString sidebar_temp_str = "0";
};
