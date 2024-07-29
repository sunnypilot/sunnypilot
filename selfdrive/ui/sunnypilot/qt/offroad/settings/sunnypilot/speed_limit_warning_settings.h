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

#include <map>
#include <string>
#include <vector>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

class SpeedLimitWarningValueOffset : public OptionControlSP {
  Q_OBJECT

public:
  SpeedLimitWarningValueOffset();

  void refresh();

private:
  Params params;
};

class SpeedLimitWarningSettings : public QWidget {
  Q_OBJECT

public:
  explicit SpeedLimitWarningSettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;
  static const std::vector<QString> speed_limit_warning_descriptions;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  SpeedLimitWarningValueOffset *slwvo;
  ButtonParamControlSP *speed_limit_warning_offset_settings;
  ParamControlSP *speed_limit_warning_flash;
  ButtonParamControlSP *speed_limit_warning_settings;
  ParamWatcher *param_watcher;

  QString speedLimitWarningDescriptionBuilder(QString param, std::vector<QString> descriptions) {
    std::string key = param.toStdString();
    int value = atoi(params.get(key).c_str());
    QString description = "";

    for (int i = 0; i < descriptions.size(); i++) {
      if (i == value) {
        description += "<b>" + descriptions[i] + "</b>";
      } else {
        description += descriptions[i];
      }

      if ((i >= 0) && (i < descriptions.size() - 1)) {
        description += "<br>";
      }
    }

    return description;
  }
};

inline const std::vector<QString> SpeedLimitWarningSettings::speed_limit_warning_descriptions{
  tr("Off: When the cruising speed is faster than the speed limit plus the offset, there will be no warning."),
  tr("Display: The speed on the speed limit sign turns red to alert the driver when the cruising speed is faster than the speed limit plus the offset."),
  tr("Chime: The speed on the speed limit sign turns red and chimes to alert the driver when the cruising speed is faster than the speed limit plus the offset."),
};
