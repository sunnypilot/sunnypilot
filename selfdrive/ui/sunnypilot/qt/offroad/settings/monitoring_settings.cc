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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/monitoring_settings.h"

#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

MonitoringPanel::MonitoringPanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "HandsOnWheelMonitoring",
      tr("Enable Hands on Wheel Monitoring"),
      tr("Monitor and alert when driver is not keeping the hands on the steering wheel."),
      "../assets/offroad/icon_blank.png",
    }
  };

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  monitoringScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(monitoringScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  vlayout->addWidget(new ScrollViewSP(list, this), 1);
  main_layout->addWidget(monitoringScreen);
}
