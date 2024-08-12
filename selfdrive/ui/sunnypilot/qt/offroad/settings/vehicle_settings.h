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

#include <QApplication>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class VehiclePanel : public QWidget {
  Q_OBJECT

public:
  explicit VehiclePanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;

  QStackedLayout* main_layout = nullptr;
  QWidget* home = nullptr;

  QPushButton* setCarBtn;
  QString set;

  QWidget* home_widget;
  QString prompt_select = tr("Select your car");
};

class SPVehiclesTogglesPanel : public ListWidgetSP {
  Q_OBJECT
public:
  explicit SPVehiclesTogglesPanel(VehiclePanel *parent);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;
  bool is_onroad = false;

  ParamControlSP *hyundaiCruiseMainDefault;
  ParamControlSP *stockLongToyota;
  ParamControlSP *toyotaEnhancedBsm;

  const QString toyotaEnhancedBsmDescription = QString("%1<br><br>"
                                                       "%2")
                                               .arg(tr("sunnypilot will use debugging CAN messages to receive unfiltered BSM signals, allowing detection of more objects."))
                                               .arg(tr("Tested on RAV4 TSS1, Lexus LSS1, Toyota TSS1/1.5, and Prius TSS2."));

  QString toyotaEnhancedBsmDesciptionBuilder(const QString &custom_description) {
    QString description = "<b>" + custom_description + "</b><br><br>" + toyotaEnhancedBsmDescription;
    return description;
  }
};
